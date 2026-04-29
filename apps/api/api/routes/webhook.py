from __future__ import annotations

import hashlib
import hmac
import logging
import os
import traceback
from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.analysis import run_analysis
from apps.api.api.services.commit_check import publish_pr_commit_check
from apps.api.api.services.pr_attribution import attribute_pr
from packages.db.config import settings
from packages.db.database import AsyncSessionLocal, get_db
from packages.db.models import AnalysisRun, Commit, Org, PullRequest, Repo


router = APIRouter(tags=["webhook"])
logger = logging.getLogger(__name__)


def _verify_github_signature(body: bytes, signature: str | None) -> None:
    if not settings.GITHUB_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="GITHUB_WEBHOOK_SECRET is not configured")
    if not signature or not signature.startswith("sha256="):
        raise HTTPException(status_code=401, detail="Invalid GitHub signature")
    expected = hmac.new(settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, f"sha256={expected}"):
        raise HTTPException(status_code=401, detail="Invalid GitHub signature")


def _account_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    installation = payload.get("installation") or {}
    account = installation.get("account") or payload.get("organization") or payload.get("sender") or {}
    return dict(account)


async def _upsert_org(db: AsyncSession, payload: dict[str, Any], installation_id: int | None = None) -> Org:
    account = _account_from_payload(payload)
    github_org_id = int(account.get("id") or 0)
    login = str(account.get("login") or f"github-{github_org_id}")
    result = await db.execute(select(Org).where(Org.github_org_id == github_org_id))
    org = result.scalar_one_or_none()
    if org is None:
        org = Org(
            github_org_id=github_org_id,
            login=login,
            name=str(account.get("name") or login),
            github_installation_id=installation_id,
        )
        db.add(org)
        await db.flush()
    else:
        org.login = login
        org.name = str(account.get("name") or login)
        if installation_id and not org.github_installation_id:
            org.github_installation_id = installation_id
    return org


async def _upsert_repo(db: AsyncSession, org: Org, repo_payload: dict[str, Any], installation_id: int | None) -> Repo:
    github_repo_id = int(repo_payload.get("id") or 0)
    result = await db.execute(select(Repo).where(Repo.github_repo_id == github_repo_id))
    repo = result.scalar_one_or_none()
    if repo is None:
        repo = Repo(
            org_id=org.id,
            github_repo_id=github_repo_id,
            github_installation_id=installation_id,
            full_name=str(repo_payload.get("full_name")),
            name=str(repo_payload.get("name")),
            default_branch=str(repo_payload.get("default_branch") or "main"),
            language=repo_payload.get("language"),
            is_active=True,
        )
        db.add(repo)
        await db.flush()
    else:
        repo.org_id = org.id
        repo.github_installation_id = installation_id or repo.github_installation_id
        repo.full_name = str(repo_payload.get("full_name"))
        repo.name = str(repo_payload.get("name"))
        repo.default_branch = str(repo_payload.get("default_branch") or repo.default_branch or "main")
        repo.language = repo_payload.get("language") or repo.language
        repo.is_active = True
    return repo


def _parse_github_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.replace(tzinfo=None)
        except ValueError:
            return None
    return None


def _normalize_pr_state(pr_payload: dict[str, Any]) -> str:
    if pr_payload.get("merged"):
        return "merged"
    state = str(pr_payload.get("state") or "open").lower()
    if state == "closed":
        return "closed"
    return "open"


def _github_user_login(value: Any) -> str | None:
    if isinstance(value, dict):
        return value.get("login") or value.get("username") or value.get("name")
    return None


def _upsert_check_run_raw(raw: dict[str, Any] | None, check_run: dict[str, Any], action: str | None) -> dict[str, Any]:
    existing = dict(raw or {})
    runs = list(existing.get("check_runs") or [])
    name = str(check_run.get("name") or "")
    head_sha = str(check_run.get("head_sha") or "")
    summary = {
        "name": name,
        "head_sha": head_sha,
        "status": check_run.get("status"),
        "conclusion": check_run.get("conclusion"),
        "started_at": check_run.get("started_at"),
        "completed_at": check_run.get("completed_at"),
        "html_url": check_run.get("html_url"),
        "external_id": check_run.get("external_id"),
        "action": action,
        "raw": check_run,
    }
    replaced = False
    for index, item in enumerate(runs):
        if item.get("name") == name and item.get("head_sha") == head_sha:
            runs[index] = summary
            replaced = True
            break
    if not replaced:
        runs.append(summary)
    existing["check_runs"] = runs
    return existing


def _pr_raw(current_raw: dict[str, Any] | None, pull_request: dict[str, Any], payload: dict[str, Any], action: str | None) -> dict[str, Any]:
    raw = dict(current_raw or {})
    raw["github"] = pull_request
    raw["last_event"] = action
    raw["repository"] = payload.get("repository") or {}
    raw["sender"] = payload.get("sender") or {}
    raw.setdefault("check_runs", [])
    return raw


async def _upsert_pull_request_record(db: AsyncSession, repo: Repo, payload: dict[str, Any], action: str | None) -> PullRequest:
    pull_request = payload.get("pull_request") or {}
    pr_number = int(payload.get("number") or pull_request.get("number") or 0)
    result = await db.execute(
        select(PullRequest).where(PullRequest.repo_id == repo.id, PullRequest.github_pr_number == pr_number)
    )
    record = result.scalar_one_or_none()
    if record is None:
        record = PullRequest(repo_id=repo.id, github_pr_number=pr_number)
        db.add(record)
        await db.flush()

    user = pull_request.get("user") or {}
    head = pull_request.get("head") or {}
    base = pull_request.get("base") or {}
    record.author_login = user.get("login")
    record.author_type = user.get("type")
    record.head_sha = head.get("sha")
    record.base_sha = base.get("sha")
    record.title = pull_request.get("title")
    record.body = pull_request.get("body")
    record.state = _normalize_pr_state(pull_request)
    record.opened_at = _parse_github_datetime(pull_request.get("created_at"))
    record.merged_at = _parse_github_datetime(pull_request.get("merged_at"))
    record.closed_at = _parse_github_datetime(pull_request.get("closed_at"))
    record.additions = pull_request.get("additions")
    record.deletions = pull_request.get("deletions")
    record.changed_files = pull_request.get("changed_files")
    record.raw = _pr_raw(record.raw, pull_request, payload, action)
    record.updated_at = datetime.utcnow()
    return record


async def _upsert_commit_record(
    db: AsyncSession,
    repo: Repo,
    commit_payload: dict[str, Any],
    pr: PullRequest | None = None,
) -> Commit | None:
    sha = str(commit_payload.get("id") or commit_payload.get("sha") or "")
    if not sha:
        return None
    result = await db.execute(select(Commit).where(Commit.repo_id == repo.id, Commit.sha == sha))
    record = result.scalar_one_or_none()
    if record is None:
        record = Commit(repo_id=repo.id, sha=sha)
        db.add(record)
        await db.flush()

    commit = commit_payload.get("commit") or commit_payload
    author = commit.get("author") or commit_payload.get("author") or {}
    committer = commit.get("committer") or commit_payload.get("committer") or {}
    stats = commit_payload.get("stats") or {}
    record.author_login = _github_user_login(commit_payload.get("author")) or _github_user_login(author)
    record.author_email = author.get("email") if isinstance(author, dict) else None
    record.committer_login = _github_user_login(commit_payload.get("committer")) or _github_user_login(committer)
    record.message = commit.get("message") or commit_payload.get("message")
    record.authored_at = _parse_github_datetime(author.get("date") if isinstance(author, dict) else None)
    record.committed_at = _parse_github_datetime(committer.get("date") if isinstance(committer, dict) else commit_payload.get("timestamp"))
    added = commit_payload.get("added")
    removed = commit_payload.get("removed")
    record.additions = (
        stats.get("additions")
        if isinstance(stats, dict) and "additions" in stats
        else (len(added) if isinstance(added, list) else None)
    )
    record.deletions = (
        stats.get("deletions")
        if isinstance(stats, dict) and "deletions" in stats
        else (len(removed) if isinstance(removed, list) else None)
    )
    if pr is not None:
        record.pr_id = pr.id
    record.raw = commit_payload
    record.updated_at = datetime.utcnow()
    return record


async def _upsert_check_run_record(db: AsyncSession, payload: dict[str, Any], action: str | None) -> PullRequest | None:
    repo_payload = payload.get("repository") or {}
    full_name = str(repo_payload.get("full_name") or "")
    result = await db.execute(select(Repo).where(Repo.full_name == full_name))
    repo = result.scalar_one_or_none()
    if repo is None or not repo.is_active:
        return None
    check_run = payload.get("check_run") or {}
    head_sha = str(check_run.get("head_sha") or "")
    if not head_sha:
        return None
    result = await db.execute(select(PullRequest).where(PullRequest.repo_id == repo.id, PullRequest.head_sha == head_sha))
    pr = result.scalar_one_or_none()
    if pr is None:
        return None
    pr.raw = _upsert_check_run_raw(pr.raw, check_run, action)
    pr.updated_at = datetime.utcnow()
    return pr


async def _append_pr_review_event(db: AsyncSession, payload: dict[str, Any], action: str | None) -> PullRequest | None:
    if action != "submitted":
        return None
    repo_payload = payload.get("repository") or {}
    full_name = str(repo_payload.get("full_name") or "")
    result = await db.execute(select(Repo).where(Repo.full_name == full_name))
    repo = result.scalar_one_or_none()
    if repo is None or not repo.is_active:
        return None
    pull_request = payload.get("pull_request") or {}
    pr_number = int(payload.get("number") or pull_request.get("number") or 0)
    result = await db.execute(select(PullRequest).where(PullRequest.repo_id == repo.id, PullRequest.github_pr_number == pr_number))
    pr = result.scalar_one_or_none()
    if pr is None:
        pr = await _upsert_pull_request_record(db, repo, payload, action)
    review = payload.get("review") or {}
    raw = dict(pr.raw or {})
    reviews = list(raw.get("reviews") or [])
    review_id = review.get("id")
    summary = {
        "id": review_id,
        "state": review.get("state"),
        "author_login": _github_user_login(review.get("user")),
        "submitted_at": review.get("submitted_at"),
        "body": review.get("body"),
        "html_url": review.get("html_url"),
        "raw": review,
    }
    replaced = False
    for index, item in enumerate(reviews):
        if item.get("id") == review_id:
            reviews[index] = summary
            replaced = True
            break
    if not replaced:
        reviews.append(summary)
    raw["reviews"] = reviews
    pr.raw = raw
    pr.updated_at = datetime.utcnow()
    return pr


async def publish_to_qstash(body: dict[str, Any]) -> bool:
    token = os.getenv("QSTASH_TOKEN", "")
    if not token:
        print("QSTASH_TOKEN not set")
        return False

    base_url = os.getenv("QSTASH_BASE_URL", "https://qstash-us-east-1.upstash.io")
    url = f"{base_url}/v2/publish/https://api.skillayer.com/worker/analyse"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )
        print(f"QStash response: {response.status_code} {response.text}")
        return 200 <= response.status_code < 300


async def _latest_push_score(db: AsyncSession, repo: Repo) -> dict[str, int] | None:
    """Return the latest complete push score for a repo default branch."""
    result = await db.execute(
        select(
            AnalysisRun.score_total,
            AnalysisRun.score_groundedness,
            AnalysisRun.score_coverage,
            AnalysisRun.score_freshness,
            AnalysisRun.score_structure,
        )
        .where(
            AnalysisRun.repo_id == repo.id,
            AnalysisRun.trigger == "push",
            AnalysisRun.status == "complete",
            AnalysisRun.branch == repo.default_branch,
        )
        .order_by(AnalysisRun.created_at.desc())
        .limit(1)
    )
    row = result.first()
    if row is None:
        return None
    return {
        "total": int(row.score_total or 0),
        "groundedness": int(row.score_groundedness or 0),
        "coverage": int(row.score_coverage or 0),
        "freshness": int(row.score_freshness or 0),
        "structure": int(row.score_structure or 0),
    }


async def _run_development_job(payload: dict[str, Any]) -> None:
    async with AsyncSessionLocal() as db:
        await run_analysis(
            str(payload["run_id"]),
            str(payload["repo_id"]),
            int(payload["installation_id"]),
            str(payload["full_name"]),
            db,
            pr_number=payload.get("pr_number"),
            base_score=payload.get("base_score"),
            head_sha=payload.get("head_sha"),
        )


async def _run_attribution_job(pr_id: str) -> None:
    async with AsyncSessionLocal() as db:
        try:
            await attribute_pr(pr_id, db)
        except Exception:
            logger.exception("PR attribution failed for %s", pr_id)


async def _run_pr_commit_check_job(repo_id: str, pr_id: str, sha: str, installation_id: int, base_sha: str | None = None) -> None:
    async with AsyncSessionLocal() as db:
        try:
            repo = await db.get(Repo, repo_id)
            pr = await db.get(PullRequest, pr_id)
            if repo is None or pr is None:
                return
            await publish_pr_commit_check(repo=repo, pr=pr, sha=sha, db=db, installation_id=installation_id, base_sha=base_sha)
        except Exception:
            logger.exception("PR commit check failed for %s", pr_id)


async def _queue_analysis(request: Request, background_tasks: BackgroundTasks, payload: dict[str, Any]) -> bool:
    if settings.DEPLOYMENT_MODE == "saas":
        return await publish_to_qstash(payload)
    elif settings.DEPLOYMENT_MODE == "selfhosted":
        from apps.worker.worker import run_analysis_task

        run_analysis_task.delay(
            payload["run_id"],
            payload["repo_id"],
            payload["installation_id"],
            payload["full_name"],
            payload.get("pr_number"),
            payload.get("base_score"),
            payload.get("head_sha"),
        )
        return True
    elif settings.DEPLOYMENT_MODE in {"development", "bootstrap"}:
        background_tasks.add_task(_run_development_job, payload)
        return True
    else:
        raise HTTPException(status_code=500, detail=f"Unsupported DEPLOYMENT_MODE: {settings.DEPLOYMENT_MODE}")


@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    x_github_event: str | None = Header(default=None, alias="X-GitHub-Event"),
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
) -> dict[str, Any]:
    body = await request.body()
    _verify_github_signature(body, x_hub_signature_256)
    payload = await request.json()
    action = payload.get("action")

    if x_github_event == "installation":
        installation_id = int((payload.get("installation") or {}).get("id") or 0) or None
        org = await _upsert_org(db, payload, installation_id)
        if action == "created":
            for repo_payload in payload.get("repositories", []):
                await _upsert_repo(db, org, repo_payload, installation_id)
        elif action == "deleted":
            await db.execute(update(Repo).where(Repo.org_id == org.id).values(is_active=False))
            if org.github_installation_id == installation_id:
                org.github_installation_id = None
        await db.commit()
        return {"ok": True}

    if x_github_event == "installation_repositories":
        installation_id = int((payload.get("installation") or {}).get("id") or 0) or None
        org = await _upsert_org(db, payload, installation_id)
        if action == "added":
            for repo_payload in payload.get("repositories_added", []):
                await _upsert_repo(db, org, repo_payload, installation_id)
        elif action == "removed":
            removed_ids = [int(repo.get("id")) for repo in payload.get("repositories_removed", []) if repo.get("id")]
            if removed_ids:
                await db.execute(update(Repo).where(Repo.github_repo_id.in_(removed_ids)).values(is_active=False))
        await db.commit()
        return {"ok": True}

    if x_github_event == "push":
        try:
            repo_payload = payload.get("repository") or {}
            print(f"Push event received for: {repo_payload.get('full_name')}")
            print("Looking up repo in DB...")
            token = os.getenv("QSTASH_TOKEN", "NOT_SET")
            print(f"QSTASH_TOKEN present: {token != 'NOT_SET'}")
            print(f"QSTASH_TOKEN prefix: {token[:8] if token != 'NOT_SET' else 'MISSING'}")
            full_name = str(repo_payload.get("full_name") or "")
            result = await db.execute(select(Repo).where(Repo.full_name == full_name))
            repo = result.scalar_one_or_none()
            if repo is None or not repo.is_active:
                return {"ignored": True}
            linked_pr: PullRequest | None = None
            pr_payload = payload.get("pull_request")
            if isinstance(pr_payload, dict):
                linked_pr = await _upsert_pull_request_record(db, repo, {"pull_request": pr_payload, "number": pr_payload.get("number"), "repository": repo_payload}, action)
            for commit_payload in payload.get("commits") or []:
                await _upsert_commit_record(db, repo, commit_payload, linked_pr)
            run = AnalysisRun(
                repo_id=repo.id,
                trigger="push",
                status="queued",
                commit_sha=payload.get("after"),
                branch=str(payload.get("ref") or "").replace("refs/heads/", ""),
                created_at=datetime.utcnow(),
            )
            db.add(run)
            await db.flush()
            installation_id = int((payload.get("installation") or {}).get("id") or 0)
            repo.github_installation_id = installation_id or repo.github_installation_id
            await db.commit()
            try:
                success = await _queue_analysis(
                    request,
                    background_tasks,
                    {
                        "run_id": run.id,
                        "repo_id": repo.id,
                        "installation_id": installation_id,
                        "full_name": repo.full_name,
                    },
                )
                if not success:
                    print("QStash publish failed - run stays queued")
            except Exception as exc:
                print(f"QStash error: {exc}")
            return {"queued": run.id}
        except Exception as exc:
            logger.error(f"Webhook push handler error: {exc}")
            logger.error(traceback.format_exc())
            print(f"WEBHOOK ERROR: {exc}")
            print(traceback.format_exc())
            raise

    if x_github_event == "pull_request":
        if action not in {"opened", "synchronize", "closed", "merged", "reopened", "edited"}:
            return {"ignored": True}
        try:
            repo_payload = payload.get("repository") or {}
            pull_request = payload.get("pull_request") or {}
            head = pull_request.get("head") or {}
            full_name = str(repo_payload.get("full_name") or "")
            result = await db.execute(select(Repo).where(Repo.full_name == full_name))
            repo = result.scalar_one_or_none()
            if repo is None or not repo.is_active:
                return {"ignored": True}

            pr_number = int(payload.get("number") or pull_request.get("number") or 0)
            pr_record = await _upsert_pull_request_record(db, repo, payload, action)
            for commit_payload in payload.get("commits") or []:
                await _upsert_commit_record(db, repo, commit_payload, pr_record)
            installation_id = int((payload.get("installation") or {}).get("id") or 0)
            base_score = await _latest_push_score(db, repo)
            repo.github_installation_id = installation_id or repo.github_installation_id

            if action in {"closed", "merged", "edited"}:
                await db.commit()
                if action in {"closed", "merged"}:
                    background_tasks.add_task(_run_attribution_job, pr_record.id)
                return {"captured": True, "pr_id": pr_record.id}

            run = AnalysisRun(
                repo_id=repo.id,
                trigger="pull_request",
                status="queued",
                commit_sha=head.get("sha"),
                branch=str(head.get("ref") or ""),
                pr_number=pr_number,
                created_at=datetime.utcnow(),
            )
            db.add(run)
            await db.flush()
            await db.commit()
            if action in {"opened", "synchronize"}:
                background_tasks.add_task(_run_attribution_job, pr_record.id)
                head_sha = str(head.get("sha") or "")
                base_sha = str((pull_request.get("base") or {}).get("sha") or "")
                if head_sha and installation_id:
                    background_tasks.add_task(_run_pr_commit_check_job, repo.id, pr_record.id, head_sha, installation_id, base_sha)

            try:
                success = await _queue_analysis(
                    request,
                    background_tasks,
                    {
                        "run_id": run.id,
                        "repo_id": repo.id,
                        "installation_id": installation_id,
                        "full_name": repo.full_name,
                        "ref": str(head.get("ref") or ""),
                        "pr_number": pr_number,
                        "base_score": base_score,
                        "head_sha": str(head.get("sha") or ""),
                    },
                )
                if not success:
                    print("QStash publish failed - run stays queued")
            except Exception as exc:
                print(f"QStash error: {exc}")
            return {"queued": run.id}
        except Exception as exc:
            logger.error(f"Webhook pull_request handler error: {exc}")
            logger.error(traceback.format_exc())
            print(f"WEBHOOK ERROR: {exc}")
            print(traceback.format_exc())
            raise

    if x_github_event == "pull_request_review":
        try:
            pr = await _append_pr_review_event(db, payload, action)
            if pr is None:
                return {"ignored": True}
            await db.commit()
            return {"captured": True, "pr_id": pr.id}
        except Exception as exc:
            logger.error(f"Webhook pull_request_review handler error: {exc}")
            logger.error(traceback.format_exc())
            raise

    if x_github_event == "check_run":
        try:
            pr = await _upsert_check_run_record(db, payload, action)
            if pr is None:
                return {"ignored": True}
            await db.commit()
            return {"captured": True, "pr_id": pr.id}
        except Exception as exc:
            logger.error(f"Webhook check_run handler error: {exc}")
            logger.error(traceback.format_exc())
            raise

    return {"ignored": True}
