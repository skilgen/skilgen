from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.github import get_installation_token
from apps.api.api.pr_comment import (
    build_violation_comment,
    create_skill_review_check_run,
    post_or_update_tracked_violation_comment,
    violation_marker,
)
from apps.api.api.routes.review import _files_to_diff, _skill_pattern_comments, _structured_from_comments
from apps.api.api.services.pr_risk import compute_risk_score
from apps.api.api.services.policy_engine import evaluate_pr_policies
from packages.db.models import PRAttribution, PullRequest, Repo, Skill


@dataclass
class CommitCheckResult:
    violations: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    skills_checked: int
    lines_scanned: int
    runtime_ms: int
    risk_tier: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "violations": self.violations,
            "warnings": self.warnings,
            "skills_checked": self.skills_checked,
            "lines_scanned": self.lines_scanned,
            "runtime_ms": self.runtime_ms,
            "risk_tier": self.risk_tier,
        }


def _severity_bucket(item: dict[str, Any]) -> str:
    severity = str(item.get("severity") or "warning").lower()
    if severity in {"error", "critical", "failure", "fatal"}:
        return "violation"
    return "warning"


async def fetch_commit_diff(repo: Repo, sha: str, base_sha: str | None = None, branch: str | None = None) -> str:
    if not repo.github_installation_id or "/" not in repo.full_name:
        raise ValueError("github_app_not_installed")
    token = await get_installation_token(int(repo.github_installation_id))
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    async with httpx.AsyncClient(timeout=20.0) as client:
        if base_sha:
            response = await client.get(f"https://api.github.com/repos/{repo.full_name}/compare/{base_sha}...{sha}", headers=headers)
            response.raise_for_status()
            files = response.json().get("files") or []
        else:
            response = await client.get(f"https://api.github.com/repos/{repo.full_name}/commits/{sha}", headers=headers)
            response.raise_for_status()
            files = response.json().get("files") or []
    return _files_to_diff([item for item in files if isinstance(item, dict)])


async def run_commit_check(
    repo: Repo,
    sha: str,
    db: AsyncSession,
    *,
    base_sha: str | None = None,
    branch: str | None = None,
    diff: str | None = None,
) -> CommitCheckResult:
    start = time.perf_counter()
    effective_diff = diff if diff is not None else await fetch_commit_diff(repo, sha, base_sha=base_sha, branch=branch)
    skills = list((await db.execute(select(Skill).where(Skill.repo_id == repo.id))).scalars().all())
    comments, line_count = _skill_pattern_comments(skills, effective_diff)
    findings = _structured_from_comments(comments)["findings"]
    violations = [item for item in findings if _severity_bucket(item) == "violation"]
    warnings = [item for item in findings if _severity_bucket(item) == "warning"]
    if violations:
        risk_tier = "red"
    elif warnings:
        risk_tier = "yellow"
    else:
        risk_tier = "green"
    return CommitCheckResult(
        violations=violations,
        warnings=warnings,
        skills_checked=len(skills),
        lines_scanned=line_count,
        runtime_ms=int((time.perf_counter() - start) * 1000),
        risk_tier=risk_tier,
    )


async def publish_pr_commit_check(
    *,
    repo: Repo,
    pr: PullRequest,
    sha: str,
    db: AsyncSession,
    installation_id: int,
    base_sha: str | None = None,
) -> CommitCheckResult:
    result = await run_commit_check(repo, sha, db, base_sha=base_sha)
    attribution = (await db.execute(select(PRAttribution).where(PRAttribution.pr_id == pr.id))).scalar_one_or_none()
    if attribution is None:
        attribution = PRAttribution(
            pr_id=pr.id,
            primary_agent="human",
            confidence=1.0,
            lines_by_agent={"human": int((pr.additions or 0) + (pr.deletions or 0))},
            lines_by_human=int((pr.additions or 0) + (pr.deletions or 0)),
            sessions=[],
            skills_loaded=[],
            skills_violated=[],
        )
        db.add(attribution)
    attribution.skills_violated = result.violations + result.warnings
    await db.commit()
    await compute_risk_score(pr.id, db)
    if hasattr(db, "refresh"):
        await db.refresh(attribution)
    policy_failures = await evaluate_pr_policies(repo.org_id, attribution, db)

    settings_url = "https://app.skillayer.com/dashboard/settings"
    for finding in result.violations + result.warnings:
        marker = violation_marker(
            str(finding.get("file_path") or "unknown"),
            finding.get("line_number") if isinstance(finding.get("line_number"), int) else None,
            str(finding.get("skill_name") or finding.get("title") or "skill"),
            str(finding.get("message") or ""),
        )
        skill_id = finding.get("skill_id")
        skill_url = f"https://app.skillayer.com/dashboard/repos/{repo.id}/skills/{skill_id}" if skill_id else f"https://app.skillayer.com/dashboard/repos/{repo.id}/skills"
        body = build_violation_comment(
            marker=marker,
            skill_name=str(finding.get("skill_name") or finding.get("title") or "Skill"),
            severity=str(finding.get("severity") or "warning"),
            explanation=str(finding.get("message") or ""),
            suggested_fix=str(finding.get("suggestion")) if finding.get("suggestion") else None,
            dashboard_skill_url=skill_url,
            dashboard_settings_url=settings_url,
            dashboard_pr_url=f"https://app.skillayer.com/dashboard/agent-prs/{pr.id}",
        )
        await post_or_update_tracked_violation_comment(
            db=db,
            pr_id=pr.id,
            full_name=repo.full_name,
            pr_number=pr.github_pr_number,
            installation_id=installation_id,
            marker=marker,
            body=body,
        )

    await create_skill_review_check_run(
        full_name=repo.full_name,
        installation_id=installation_id,
        head_sha=sha,
        violations=result.violations,
        warnings=result.warnings,
        skills_checked=result.skills_checked,
        policy_failures=policy_failures,
    )
    return result
