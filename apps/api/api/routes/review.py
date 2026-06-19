from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Literal

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from apps.api.api.github import get_installation_token
from apps.api.api.services.llm import LLMCallError, LLMNotConfiguredError, call_llm
from packages.db.database import AsyncSessionLocal, get_db
from packages.db.models import Job, Org, PRReview, PRReviewFinding, Repo, ReviewRun, Skill


router = APIRouter(tags=["review"])


class ReviewBody(BaseModel):
    diff: str
    pr_url: str | None = None


class OrgReviewScanBody(BaseModel):
    repo_id: str = Field(min_length=1)
    diff: str = Field(min_length=1, max_length=500_000)
    pr_url: str | None = Field(default=None, max_length=2048)
    pr_number: int | None = None
    title: str | None = Field(default=None, max_length=255)


class RepoPRScanBody(BaseModel):
    repo_id: str | None = None


class ReviewFindingResponse(BaseModel):
    id: str | None = None
    file_path: str
    line_number: int | None
    severity: str
    title: str
    message: str
    skill_id: str | None = None
    skill_name: str | None = None
    rule_id: str | None = None
    suggestion: str | None = None


class PRReviewResponse(BaseModel):
    id: str
    org_id: str
    repo_id: str
    repo_name: str | None = None
    pr_url: str | None
    pr_number: int | None
    title: str | None
    status: str
    summary: str | None
    model_used: str | None
    findings_count: int
    skills_checked: int
    lines_scanned: int
    created_at: datetime
    findings: list[ReviewFindingResponse] = Field(default_factory=list)


class PRReviewHistoryResponse(BaseModel):
    reviews: list[PRReviewResponse]


class PRScanQueuedResponse(BaseModel):
    job_id: str
    status: str = "queued"


class PRScanStatusResponse(BaseModel):
    job_id: str
    status: str
    scanned: int = 0
    queued: int = 0
    skipped: int = 0
    error: str | None = None


def _patterns_from_content(content: str | None) -> list[str]:
    if not content:
        return []
    lines = content.splitlines()
    capture = False
    patterns: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## anti"):
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture and stripped.startswith("-"):
            cleaned = re.sub(r"^[-*]\s*", "", stripped)
            cleaned = re.sub(r"^\*\*(.*?)\*\*:\s*", r"\1 ", cleaned).strip()
            if cleaned:
                patterns.append(cleaned)
    return patterns[:8]


def _changed_lines(diff: str) -> list[dict[str, object]]:
    current_file = "unknown"
    line_number = 0
    rows: list[dict[str, object]] = []
    for raw in diff.splitlines():
        if raw.startswith("+++ b/"):
            current_file = raw.removeprefix("+++ b/")
            continue
        if raw.startswith("@@"):
            match = re.search(r"\+(\d+)", raw)
            line_number = int(match.group(1)) - 1 if match else line_number
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            line_number += 1
            rows.append({"file": current_file, "line": line_number, "text": raw[1:]})
        elif raw and not raw.startswith("-"):
            line_number += 1
    return rows


def _short_pattern(pattern: str) -> str:
    return pattern.split("—")[0].split("-")[0].strip().lower()


def _pattern_matches_text(pattern: str, text: str) -> bool:
    needle = _short_pattern(pattern)
    if len(needle) >= 4 and needle in text:
        return True
    tokens = [
        token
        for token in re.findall(r"[a-z0-9_]+", needle)
        if token not in {"avoid", "never", "dont", "don't", "do", "not", "use", "using", "no"}
    ]
    return bool(tokens) and all(token in text for token in tokens)


def _skill_suggestion(skill: Skill, pattern: str, line_text: str) -> dict[str, object]:
    short = _short_pattern(pattern).strip(".") or "Pattern violation"
    suggested_text = (
        f"### Anti-pattern: {short.title()}\n\n"
        f"**Do not:** {line_text.strip()[:180] or pattern}\n\n"
        f"**Instead:** Follow the {skill.domain} skill conventions and use the approved project helper or pattern.\n\n"
        f"**Why:** This prevents agents from repeating a review finding that your current skill did not make explicit enough.\n"
    )
    return {
        "skill_id": skill.id,
        "domain": skill.domain,
        "current_antipattern_text": pattern,
        "suggested_addition": short,
        "suggested_text": suggested_text,
        "reasoning": "Adding this anti-pattern turns a one-off review comment into reusable guidance for future agent sessions.",
    }


def _skill_pattern_comments(skills: list[Skill], diff: str) -> tuple[list[dict[str, object]], int]:
    lines = _changed_lines(diff)
    comments: list[dict[str, object]] = []
    for row in lines:
        text = str(row["text"]).lower()
        for skill in skills:
            patterns = list(skill.anti_patterns or []) + _patterns_from_content(skill.content)
            for pattern in patterns:
                if _pattern_matches_text(str(pattern), text):
                    comments.append(
                        {
                            "file": row["file"],
                            "line": row["line"],
                            "skill_id": skill.id,
                            "skill_name": skill.domain,
                            "anti_pattern": pattern,
                            "message": f"This line may violate the '{skill.domain}' skill anti-pattern: '{pattern}'",
                            "severity": "warning",
                            "skill_suggestion": _skill_suggestion(skill, str(pattern), str(row["text"])),
                        }
                    )
                    break
    return comments, len(lines)


def _pr_number_from_url(pr_url: str | None) -> int | None:
    if not pr_url:
        return None
    match = re.search(r"/pull/(\d+)", pr_url)
    return int(match.group(1)) if match else None


def _json_from_text(text: str) -> dict[str, Any] | None:
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        value = json.loads(raw)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            value = json.loads(match.group(0))
            return value if isinstance(value, dict) else None
        except json.JSONDecodeError:
            return None


def _structured_from_comments(comments: list[dict[str, object]]) -> dict[str, object]:
    findings = [
        {
            "file_path": str(comment.get("file") or "unknown"),
            "line_number": comment.get("line") if isinstance(comment.get("line"), int) else None,
            "severity": str(comment.get("severity") or "warning"),
            "title": str(comment.get("skill_name") or "Skill anti-pattern"),
            "message": str(comment.get("message") or ""),
            "skill_id": comment.get("skill_id") if isinstance(comment.get("skill_id"), str) else None,
            "skill_name": comment.get("skill_name") if isinstance(comment.get("skill_name"), str) else None,
            "rule_id": "skill_antipattern",
            "suggestion": (comment.get("skill_suggestion") or {}).get("suggested_text") if isinstance(comment.get("skill_suggestion"), dict) else None,
        }
        for comment in comments
    ]
    return {
        "summary": f"{len(findings)} skill-aware finding{'s' if len(findings) != 1 else ''} detected.",
        "findings": findings,
    }


async def _llm_review(org: Org | None, repo: Repo, diff: str, skills: list[Skill], comments: list[dict[str, object]]) -> tuple[dict[str, object], str]:
    settings = dict(org.settings or {}) if org and isinstance(org.settings, dict) else {}
    if not settings.get("llm_provider") and not settings.get("anthropic_api_key_encrypted"):
        return _structured_from_comments(comments), "mocked"
    skill_context = "\n".join(
        f"- {skill.domain}: {skill.skill_path}; anti-patterns: {', '.join(str(item) for item in list(skill.anti_patterns or [])[:4])}"
        for skill in skills[:25]
    )
    system_prompt = """You are Skillayer's PR review engine. Review a git diff against the repository's documented skills.
Return only JSON with this shape:
{"summary":"short summary","findings":[{"file_path":"path","line_number":1,"severity":"info|warning|error","title":"short","message":"specific review comment","skill_id":"optional","skill_name":"optional","rule_id":"optional","suggestion":"optional fix"}]}."""
    user_prompt = f"""Repo: {repo.full_name}
Known skills:
{skill_context or "(none)"}

Heuristic findings already detected:
{json.dumps(comments[:20], default=str)}

Diff:
{diff[:120000]}"""
    try:
        reply = await call_llm(settings, system_prompt, user_prompt, max_tokens=1600)
        structured = _json_from_text(reply)
        if structured and isinstance(structured.get("findings"), list):
            return structured, str(settings.get("llm_model") or settings.get("llm_provider") or "llm")
    except (LLMNotConfiguredError, LLMCallError):
        pass
    return _structured_from_comments(comments), "mocked"


def _finding_response(finding: PRReviewFinding, skill_lookup: dict[str, Skill]) -> ReviewFindingResponse:
    skill = skill_lookup.get(finding.skill_id or "")
    return ReviewFindingResponse(
        id=finding.id,
        file_path=finding.file_path,
        line_number=finding.line_number,
        severity=finding.severity,
        title=finding.title,
        message=finding.message,
        skill_id=finding.skill_id,
        skill_name=skill.domain if skill else None,
        rule_id=finding.rule_id,
        suggestion=finding.suggestion,
    )


def _review_response(review: PRReview, repo: Repo | None, findings: list[PRReviewFinding], skill_lookup: dict[str, Skill]) -> PRReviewResponse:
    return PRReviewResponse(
        id=review.id,
        org_id=review.org_id,
        repo_id=review.repo_id,
        repo_name=repo.name if repo else None,
        pr_url=review.pr_url,
        pr_number=review.pr_number,
        title=review.title,
        status=review.status,
        summary=review.summary,
        model_used=review.model_used,
        findings_count=int(review.findings_count or 0),
        skills_checked=int(review.skills_checked or 0),
        lines_scanned=int(review.lines_scanned or 0),
        created_at=review.created_at,
        findings=[_finding_response(finding, skill_lookup) for finding in findings],
    )


def _is_ai_authored(pr: dict[str, Any]) -> tuple[bool, str | None]:
    author = str((pr.get("user") or {}).get("login") or "").lower()
    haystack = " ".join(str(pr.get(key) or "") for key in ("title", "body")).lower()
    if author.endswith("[bot]") or author == "github-actions[bot]":
        return True, author
    keywords = {
        "codex": "Codex",
        "claude": "Claude Code",
        "cursor": "Cursor",
        "copilot": "Copilot",
        "skillayer": "Skillayer",
        "ai generated": "AI agent",
        "automated": "Automation",
        "🤖": "AI agent",
    }
    for keyword, label in keywords.items():
        if keyword in haystack or keyword in author:
            return True, label
    return False, None


def _files_to_diff(files: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for item in files:
        filename = str(item.get("filename") or "unknown")
        patch = str(item.get("patch") or "")
        if patch:
            chunks.append(f"diff --git a/{filename} b/{filename}\n--- a/{filename}\n+++ b/{filename}\n{patch}")
    return "\n".join(chunks)


async def _scan_repo_prs_job(job_id: str, org_id: str, repo_id: str | None) -> None:
    scanned = queued = skipped = 0
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        try:
            if job is not None:
                job.status = "running"
                job.result_json = {"scanned": 0, "queued": 0, "skipped": 0}
                await db.commit()
            repo_filters = [Repo.org_id == org_id, Repo.is_active.is_(True)]
            if repo_id:
                repo_filters.append(Repo.id == repo_id)
            repos = list((await db.execute(select(Repo).where(*repo_filters))).scalars().all())
            org = await db.get(Org, org_id)
            async with httpx.AsyncClient(timeout=20.0) as client:
                for repo in repos:
                    try:
                        if not repo.github_installation_id or "/" not in repo.full_name:
                            skipped += 1
                            continue
                        token = await get_installation_token(int(repo.github_installation_id))
                        headers = {
                            "Authorization": f"Bearer {token}",
                            "Accept": "application/vnd.github+json",
                            "X-GitHub-Api-Version": "2022-11-28",
                        }
                        pulls_response = await client.get(
                            f"https://api.github.com/repos/{repo.full_name}/pulls",
                            headers=headers,
                            params={"state": "all", "per_page": 50, "sort": "created", "direction": "desc"},
                        )
                        pulls_response.raise_for_status()
                        for pr in pulls_response.json():
                            if not isinstance(pr, dict):
                                continue
                            scanned += 1
                            pr_number = int(pr.get("number") or 0)
                            if pr_number <= 0:
                                skipped += 1
                                continue
                            existing = (
                                await db.execute(select(PRReview).where(PRReview.repo_id == repo.id, PRReview.pr_number == pr_number).limit(1))
                            ).scalar_one_or_none()
                            if existing is not None:
                                skipped += 1
                                continue
                            files_response = await client.get(f"https://api.github.com/repos/{repo.full_name}/pulls/{pr_number}/files", headers=headers, params={"per_page": 100})
                            files_response.raise_for_status()
                            files = [item for item in files_response.json() if isinstance(item, dict)]
                            diff = _files_to_diff(files)
                            skills = list((await db.execute(select(Skill).where(Skill.repo_id == repo.id))).scalars().all())
                            comments, line_count = _skill_pattern_comments(skills, diff)
                            structured, model_used = await _llm_review(org, repo, diff, skills, comments)
                            findings_payload = structured.get("findings") if isinstance(structured.get("findings"), list) else []
                            ai_authored, agent_hint = _is_ai_authored(pr)
                            now = datetime.utcnow()
                            review = PRReview(
                                org_id=org_id,
                                repo_id=repo.id,
                                pr_url=str(pr.get("html_url") or ""),
                                pr_number=pr_number,
                                title=str(pr.get("title") or f"PR #{pr_number}")[:255],
                                status="complete",
                                summary=str(structured.get("summary") or ("AI-authored PR loaded." if ai_authored else "PR loaded from GitHub."))[:4000],
                                model_used=agent_hint or model_used,
                                findings_count=len(findings_payload),
                                skills_checked=len(skills),
                                lines_scanned=line_count,
                                created_at=now,
                            )
                            db.add(review)
                            await db.flush()
                            skill_ids = {skill.id for skill in skills}
                            persisted = 0
                            for item in findings_payload[:100]:
                                if not isinstance(item, dict):
                                    continue
                                db.add(
                                    PRReviewFinding(
                                        review_id=review.id,
                                        org_id=org_id,
                                        repo_id=repo.id,
                                        skill_id=str(item.get("skill_id")) if item.get("skill_id") in skill_ids else None,
                                        file_path=str(item.get("file_path") or item.get("file") or "unknown")[:1024],
                                        line_number=int(item["line_number"]) if isinstance(item.get("line_number"), int) else None,
                                        severity=str(item.get("severity") or "warning")[:32],
                                        title=str(item.get("title") or "Review finding")[:255],
                                        message=str(item.get("message") or "")[:4000],
                                        rule_id=str(item.get("rule_id"))[:128] if item.get("rule_id") else None,
                                        suggestion=str(item.get("suggestion"))[:4000] if item.get("suggestion") else None,
                                        created_at=now,
                                    )
                                )
                                persisted += 1
                            review.findings_count = persisted
                            queued += 1
                            await db.commit()
                    except Exception as exc:
                        skipped += 1
                        await db.rollback()
                        if job is not None:
                            result = dict(job.result_json or {})
                            errors = list(result.get("errors") or [])
                            errors.append({"repo_id": repo.id, "error": str(exc)[:500]})
                            job.result_json = {"scanned": scanned, "queued": queued, "skipped": skipped, "errors": errors[-10:]}
                            await db.commit()
            if job is not None:
                job.status = "completed"
                job.result_json = {"scanned": scanned, "queued": queued, "skipped": skipped}
                await db.commit()
        except Exception as exc:
            await db.rollback()
            job = await db.get(Job, job_id)
            if job is not None:
                job.status = "failed"
                job.result_json = {"scanned": scanned, "queued": queued, "skipped": skipped, "error": str(exc)}
                await db.commit()


@router.post("/repos/{repo_id}/review")
async def review_diff(repo_id: str, body: ReviewBody, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    skills = (await db.execute(select(Skill).where(Skill.repo_id == repo_id))).scalars().all()
    comments, line_count = _skill_pattern_comments(list(skills), body.diff)
    db.add(ReviewRun(repo_id=repo_id, pr_url=body.pr_url, comment_count=len(comments), skills_checked=len(skills), lines_scanned=line_count))
    await db.commit()
    return {"comments": comments, "skills_checked": len(skills), "lines_scanned": line_count, "repo_id": repo_id}


@router.post("/orgs/{org_id}/review/scan-diff", response_model=PRReviewResponse)
async def scan_org_pr_diff(org_id: str, body: OrgReviewScanBody, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> PRReviewResponse:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    repo = (await db.execute(select(Repo).where(Repo.id == body.repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    org = await db.get(Org, org_id)
    skills = list((await db.execute(select(Skill).where(Skill.repo_id == repo.id))).scalars().all())
    comments, line_count = _skill_pattern_comments(skills, body.diff)
    structured, model_used = await _llm_review(org, repo, body.diff, skills, comments)
    raw_findings = structured.get("findings") if isinstance(structured, dict) else []
    findings_payload = raw_findings if isinstance(raw_findings, list) else []
    now = datetime.utcnow()
    review = PRReview(
        org_id=org_id,
        repo_id=repo.id,
        pr_url=body.pr_url,
        pr_number=body.pr_number or _pr_number_from_url(body.pr_url),
        title=body.title,
        status="complete",
        summary=str(structured.get("summary") or f"{len(findings_payload)} findings detected."),
        model_used=model_used,
        findings_count=len(findings_payload),
        skills_checked=len(skills),
        lines_scanned=line_count,
        created_at=now,
    )
    db.add(review)
    await db.flush()
    persisted_findings: list[PRReviewFinding] = []
    skill_ids = {skill.id for skill in skills}
    for item in findings_payload[:100]:
        if not isinstance(item, dict):
            continue
        finding = PRReviewFinding(
            review_id=review.id,
            org_id=org_id,
            repo_id=repo.id,
            skill_id=str(item.get("skill_id")) if item.get("skill_id") in skill_ids else None,
            file_path=str(item.get("file_path") or item.get("file") or "unknown")[:1024],
            line_number=int(item["line_number"]) if isinstance(item.get("line_number"), int) else None,
            severity=str(item.get("severity") or "warning")[:32],
            title=str(item.get("title") or "Review finding")[:255],
            message=str(item.get("message") or "")[:4000],
            rule_id=str(item.get("rule_id"))[:128] if item.get("rule_id") else None,
            suggestion=str(item.get("suggestion"))[:4000] if item.get("suggestion") else None,
            created_at=now,
        )
        db.add(finding)
        persisted_findings.append(finding)
    review.findings_count = len(persisted_findings)
    db.add(ReviewRun(repo_id=repo.id, pr_url=body.pr_url, comment_count=len(persisted_findings), skills_checked=len(skills), lines_scanned=line_count, created_at=now))
    await db.flush()
    await db.commit()
    return _review_response(review, repo, persisted_findings, {skill.id: skill for skill in skills})


@router.post("/orgs/{org_id}/review/scan-repo-prs", response_model=PRScanQueuedResponse)
async def scan_repo_prs(
    org_id: str,
    background_tasks: BackgroundTasks,
    body: RepoPRScanBody | None = None,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> PRScanQueuedResponse:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    payload = body or RepoPRScanBody()
    try:
        if payload.repo_id:
            repo = (await db.execute(select(Repo).where(Repo.id == payload.repo_id, Repo.org_id == org_id).limit(1))).scalar_one_or_none()
            if repo is None:
                raise HTTPException(status_code=404, detail="Repo not found")
        job = Job(org_id=org_id, type="review.scan_repo_prs", status="queued", result_json={"scanned": 0, "queued": 0, "skipped": 0}, created_at=datetime.utcnow())
        db.add(job)
        await db.flush()
        await db.commit()
        background_tasks.add_task(_scan_repo_prs_job, job.id, org_id, payload.repo_id)
        return PRScanQueuedResponse(job_id=job.id)
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not queue PR scan") from exc


@router.get("/orgs/{org_id}/review/scan-status/{job_id}", response_model=PRScanStatusResponse)
async def scan_repo_prs_status(
    org_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> PRScanStatusResponse:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    job = await db.get(Job, job_id)
    if job is None or job.org_id != org_id or job.type != "review.scan_repo_prs":
        raise HTTPException(status_code=404, detail="Scan job not found")
    result = job.result_json if isinstance(job.result_json, dict) else {}
    return PRScanStatusResponse(
        job_id=job.id,
        status=job.status,
        scanned=int(result.get("scanned") or 0),
        queued=int(result.get("queued") or 0),
        skipped=int(result.get("skipped") or 0),
        error=str(result.get("error")) if result.get("error") else None,
    )


@router.get("/orgs/{org_id}/review/history", response_model=PRReviewHistoryResponse)
async def org_review_history(
    org_id: str,
    source: Literal["ai_agent", "human", "all"] = Query(default="all"),
    repo_id: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> PRReviewHistoryResponse:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    filters = [PRReview.org_id == org_id]
    if repo_id:
        filters.append(PRReview.repo_id == repo_id)
    reviews = (await db.execute(select(PRReview).where(*filters).order_by(desc(PRReview.created_at)).offset(offset).limit(limit))).scalars().all()
    if source != "all":
        want_ai = source == "ai_agent"
        reviews = [review for review in reviews if _is_ai_authored({"title": review.title, "body": review.summary, "user": {"login": review.model_used}})[0] is want_ai]
    repo_ids = {review.repo_id for review in reviews}
    repos = (await db.execute(select(Repo).where(Repo.id.in_(repo_ids)))).scalars().all() if repo_ids else []
    repo_lookup = {repo.id: repo for repo in repos}
    review_ids = [review.id for review in reviews]
    findings = (await db.execute(select(PRReviewFinding).where(PRReviewFinding.review_id.in_(review_ids)).order_by(PRReviewFinding.created_at))).scalars().all() if review_ids else []
    skill_ids = {finding.skill_id for finding in findings if finding.skill_id}
    skills = (await db.execute(select(Skill).where(Skill.id.in_(skill_ids)))).scalars().all() if skill_ids else []
    skill_lookup = {skill.id: skill for skill in skills}
    findings_by_review: dict[str, list[PRReviewFinding]] = defaultdict(list)
    for finding in findings:
        findings_by_review[finding.review_id].append(finding)
    return PRReviewHistoryResponse(reviews=[_review_response(review, repo_lookup.get(review.repo_id), findings_by_review.get(review.id, []), skill_lookup) for review in reviews])


@router.get("/repos/{repo_id}/review/history")
async def review_history(repo_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    runs = (await db.execute(select(ReviewRun).where(ReviewRun.repo_id == repo_id).order_by(desc(ReviewRun.created_at)).limit(20))).scalars().all()
    return {
        "runs": [
            {
                "id": run.id,
                "repo_id": run.repo_id,
                "pr_url": run.pr_url,
                "comment_count": run.comment_count,
                "skills_checked": run.skills_checked,
                "lines_scanned": run.lines_scanned,
                "created_at": run.created_at.isoformat(),
            }
            for run in runs
        ]
    }
