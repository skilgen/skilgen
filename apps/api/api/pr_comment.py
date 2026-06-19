from __future__ import annotations

import logging
import hashlib

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import PRComment


ScoreDict = dict[str, int]
LOGGER = logging.getLogger("skillayer.pr_comment")


def get_installation_token(installation_id: int) -> str:
    """Fetch a GitHub installation token through the API GitHub helper."""
    from apps.api.api.github import get_installation_token as fetch_installation_token

    return fetch_installation_token(installation_id)


def _score_label(total: int) -> tuple[str, str]:
    """Return the score status emoji and label for a total score."""
    if total >= 85:
        return "🟢", "Excellent"
    if total >= 70:
        return "🟡", "Good"
    if total >= 50:
        return "🟠", "Needs work"
    return "🔴", "Poor"


def _delta_suffix(total: int, base: ScoreDict | None) -> str:
    """Return the total score comparison suffix for the headline."""
    if not base:
        return ""
    delta = total - base.get("total", 0)
    if delta > 0:
        return f" (+{delta} vs base)"
    if delta < 0:
        return f" ({delta} vs base)"
    return " (no change vs base)"


def _delta_cell(current_value: int, base: ScoreDict | None, key: str) -> str:
    """Return markdown-formatted score delta for a table cell."""
    if not base:
        return "—"
    delta = current_value - base.get(key, 0)
    if delta > 0:
        return f"`+{delta}`"
    if delta < 0:
        return f"`{delta}`"
    return "—"


def _response_ok(response: httpx.Response) -> bool:
    """Return whether an HTTPX response completed successfully."""
    return bool(getattr(response, "ok", response.is_success))


def _normalise_domains(domains: list[str] | None) -> list[str]:
    """Return sorted, deduplicated domain names suitable for PR comment badges."""
    if not domains:
        return []
    clean_domains: list[str] = []
    seen: set[str] = set()
    for domain in domains:
        clean = str(domain).strip().strip("/")
        if "/" in clean:
            clean = clean.split("/")[0]
        if not clean or clean in seen:
            continue
        seen.add(clean)
        clean_domains.append(clean)
    return sorted(clean_domains)


def _domains_summary(domains: list[str] | None) -> str:
    """Build the analysed-domain badge summary for the PR comment."""
    clean_domains = _normalise_domains(domains)
    if not clean_domains:
        return ""
    shown = clean_domains[:6]
    more_count = len(clean_domains) - len(shown)
    suffix = f" +{more_count} more" if more_count > 0 else ""
    badges = " ".join(f"`{domain}`" for domain in shown)
    return f"\n**{len(clean_domains)} domains analysed:**\n{badges}{suffix}\n"


def build_comment(
    current: ScoreDict,
    base: ScoreDict | None,
    run_id: str,
    domains: list[str] | None = None,
) -> str:
    """Build the Skillayer pull request score comment body."""
    total = current.get("total", 0)
    emoji, label = _score_label(total)
    delta_line = _delta_suffix(total, base)

    groundedness = current.get("groundedness", 0)
    coverage = current.get("coverage", 0)
    freshness = current.get("freshness", 0)
    structure = current.get("structure", 0)

    return f"""## {emoji} Skilgen Score: {total}/100{delta_line}

**{label}** — AI agent readiness for this branch

| Dimension | Score | Change |
|---|---|---|
| Groundedness | {groundedness}/25 | {_delta_cell(groundedness, base, 'groundedness')} |
| Coverage | {coverage}/25 | {_delta_cell(coverage, base, 'coverage')} |
| Freshness | {freshness}/25 | {_delta_cell(freshness, base, 'freshness')} |
| Structure | {structure}/25 | {_delta_cell(structure, base, 'structure')} |
{_domains_summary(domains)}

<details>
<summary>What is the Skilgen Score?</summary>

The Skilgen Score measures how well your codebase
is documented for AI coding agents.

- **Groundedness** — skills backed by real code evidence
- **Coverage** — % of codebase mapped to skill domains
- **Freshness** — skills up to date with latest changes
- **Structure** — skill files well-formed and complete

[View full report on Skillayer →](https://app.skillayer.com)

</details>

<sub>Powered by [Skillayer](https://skillayer.com) · Run ID: `{run_id[:8]}`</sub>"""


async def find_existing_comment(
    full_name: str,
    pr_number: int,
    installation_id: int,
) -> int | None:
    """Find an existing Skillayer PR comment and return its comment ID."""
    try:
        token = get_installation_token(installation_id)
        url = f"https://api.github.com/repos/{full_name}/issues/{pr_number}/comments"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                },
                timeout=10.0,
            )
            if not _response_ok(response):
                LOGGER.warning("GitHub PR comment lookup failed", extra={"status_code": response.status_code})
                return None
            for comment in response.json():
                body = comment.get("body", "")
                if "Skilgen Score" in body and "Powered by" in body and "skillayer.com" in body:
                    return int(comment["id"])
    except (httpx.HTTPError, RuntimeError, ValueError, KeyError) as exc:
        LOGGER.warning("GitHub PR comment lookup raised", extra={"error": str(exc)})
    return None


async def update_pr_comment(
    full_name: str,
    comment_id: int,
    installation_id: int,
    body: str,
) -> bool:
    """Update an existing Skillayer PR comment."""
    try:
        token = get_installation_token(installation_id)
        url = f"https://api.github.com/repos/{full_name}/issues/comments/{comment_id}"
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                url,
                json={"body": body},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=10.0,
            )
            LOGGER.info("GitHub PR comment updated", extra={"status_code": response.status_code})
            return response.status_code == 200
    except (httpx.HTTPError, RuntimeError) as exc:
        LOGGER.warning("GitHub PR comment update failed", extra={"error": str(exc)})
        return False


async def create_check_run(
    full_name: str,
    installation_id: int,
    head_sha: str,
    run_id: str,
    current_score: ScoreDict,
    score_threshold: int,
) -> bool:
    """Create a GitHub Check Run for a completed Skillayer analysis."""
    conclusion = "success" if current_score.get("total", 0) >= score_threshold else "failure"
    payload = {
        "name": "Skillayer / Skilgen Score",
        "head_sha": head_sha,
        "status": "completed",
        "conclusion": conclusion,
        "output": {
            "title": f"Skilgen Score: {current_score.get('total', 0)}/100",
            "summary": (
                f"Threshold: {score_threshold}/100\n\n"
                f"Run ID: `{run_id[:8]}`"
            ),
        },
    }
    try:
        token = get_installation_token(installation_id)
        url = f"https://api.github.com/repos/{full_name}/check-runs"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=10.0,
            )
            LOGGER.info("GitHub check run created", extra={"status_code": response.status_code})
            return response.status_code == 201
    except (httpx.HTTPError, RuntimeError, KeyError, ValueError) as exc:
        LOGGER.warning("GitHub check run creation failed", extra={"error": str(exc)})
        return False


async def post_pr_comment(
    full_name: str,
    pr_number: int,
    installation_id: int,
    run_id: str,
    current_score: ScoreDict,
    base_score: ScoreDict | None,
    domains: list[str] | None = None,
    head_sha: str | None = None,
    score_threshold: int = 70,
) -> bool:
    """Create or update the PR comment and publish a GitHub Check Run."""
    body = build_comment(current_score, base_score, run_id, domains=domains)

    existing_id = await find_existing_comment(full_name, pr_number, installation_id)
    if existing_id is not None:
        comment_ok = await update_pr_comment(full_name, existing_id, installation_id, body)
    else:
        comment_ok = False
        try:
            token = get_installation_token(installation_id)
            url = f"https://api.github.com/repos/{full_name}/issues/{pr_number}/comments"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"body": body},
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=10.0,
                )
                LOGGER.info("GitHub PR comment posted", extra={"status_code": response.status_code})
                comment_ok = response.status_code == 201
        except (httpx.HTTPError, RuntimeError) as exc:
            LOGGER.warning("GitHub PR comment post failed", extra={"error": str(exc)})

    check_ok = True
    if head_sha:
        check_ok = await create_check_run(
            full_name,
            installation_id,
            head_sha,
            run_id,
            current_score,
            score_threshold,
        )
    return comment_ok and check_ok


def _violation_marker(marker: str) -> str:
    return f"<!-- skillayer-violation:{marker} -->"


def violation_marker(file_path: str, line: int | None, skill_name: str, message: str = "") -> str:
    raw = f"{file_path}:{line or 0}:{skill_name}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def build_violation_comment(
    *,
    marker: str,
    skill_name: str,
    severity: str,
    explanation: str,
    suggested_fix: str | None,
    dashboard_skill_url: str,
    dashboard_settings_url: str,
    dashboard_pr_url: str | None = None,
) -> str:
    fix_line = f"\n> **Suggested fix:** {suggested_fix}\n>" if suggested_fix else ""
    inbox_link = f" · [View in PR Inbox]({dashboard_pr_url})" if dashboard_pr_url else ""
    return f"""{_violation_marker(marker)}
> ⚠️ **{skill_name}** — {severity}
>
> {explanation}
>{fix_line}
> [View skill]({dashboard_skill_url}){inbox_link} · [Configure]({dashboard_settings_url}) · Powered by Skillayer"""


async def find_existing_violation_comment(
    full_name: str,
    pr_number: int,
    installation_id: int,
    marker: str,
) -> int | None:
    try:
        token = get_installation_token(installation_id)
        url = f"https://api.github.com/repos/{full_name}/issues/{pr_number}/comments"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
                timeout=10.0,
            )
            if not _response_ok(response):
                return None
            needle = _violation_marker(marker)
            for comment in response.json():
                if needle in str(comment.get("body") or ""):
                    return int(comment["id"])
    except (httpx.HTTPError, RuntimeError, ValueError, KeyError) as exc:
        LOGGER.warning("GitHub violation comment lookup failed", extra={"error": str(exc)})
    return None


async def post_or_update_violation_comment(
    *,
    full_name: str,
    pr_number: int,
    installation_id: int,
    marker: str,
    body: str,
) -> bool:
    existing_id = await find_existing_violation_comment(full_name, pr_number, installation_id, marker)
    if existing_id is not None:
        return await update_pr_comment(full_name, existing_id, installation_id, body)
    try:
        token = get_installation_token(installation_id)
        url = f"https://api.github.com/repos/{full_name}/issues/{pr_number}/comments"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"body": body},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=10.0,
            )
            return response.status_code == 201
    except (httpx.HTTPError, RuntimeError) as exc:
        LOGGER.warning("GitHub violation comment post failed", extra={"error": str(exc)})
        return False


async def post_or_update_tracked_violation_comment(
    *,
    db: AsyncSession,
    pr_id: str,
    full_name: str,
    pr_number: int,
    installation_id: int,
    marker: str,
    body: str,
) -> bool:
    tracked = (
        await db.execute(
            select(PRComment).where(PRComment.pr_id == pr_id, PRComment.violation_hash == marker)
        )
    ).scalar_one_or_none()
    if tracked and tracked.github_comment_id:
        ok = await update_pr_comment(full_name, int(tracked.github_comment_id), installation_id, body)
        if ok:
            await db.commit()
            return True
        tracked.github_comment_id = None

    existing_id = await find_existing_violation_comment(full_name, pr_number, installation_id, marker)
    if existing_id is not None:
        ok = await update_pr_comment(full_name, existing_id, installation_id, body)
        if ok:
            if tracked is None:
                tracked = PRComment(pr_id=pr_id, violation_hash=marker, github_comment_id=existing_id)
                db.add(tracked)
            else:
                tracked.github_comment_id = existing_id
            await db.commit()
        return ok

    try:
        token = get_installation_token(installation_id)
        url = f"https://api.github.com/repos/{full_name}/issues/{pr_number}/comments"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"body": body},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=10.0,
            )
            if response.status_code != 201:
                return False
            github_comment_id = int(response.json().get("id"))
            if tracked is None:
                tracked = PRComment(pr_id=pr_id, violation_hash=marker, github_comment_id=github_comment_id)
                db.add(tracked)
            else:
                tracked.github_comment_id = github_comment_id
            await db.commit()
            return True
    except (httpx.HTTPError, RuntimeError, ValueError, KeyError) as exc:
        LOGGER.warning("GitHub tracked violation comment post failed", extra={"error": str(exc)})
        return False


async def create_skill_review_check_run(
    *,
    full_name: str,
    installation_id: int,
    head_sha: str,
    violations: list[dict],
    warnings: list[dict],
    skills_checked: int,
    policy_failures: list[dict] | None = None,
) -> bool:
    policy_failures = policy_failures or []
    if policy_failures:
        conclusion = "action_required"
    elif violations:
        conclusion = "failure"
    elif warnings:
        conclusion = "neutral"
    else:
        conclusion = "success"
    summary = f"{len(violations)} violations · {len(warnings)} warnings · {skills_checked} skills checked"
    if policy_failures:
        messages = "\n".join(f"- {failure.get('message') or failure.get('name') or 'Policy failed'}" for failure in policy_failures)
        summary = f"{summary}\n\nPolicy Violations\n{messages}"
    payload = {
        "name": "Skillayer Skill Review",
        "head_sha": head_sha,
        "status": "completed",
        "conclusion": conclusion,
        "output": {
            "title": "Skillayer Skill Review",
            "summary": summary,
        },
    }
    try:
        token = get_installation_token(installation_id)
        url = f"https://api.github.com/repos/{full_name}/check-runs"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=10.0,
            )
            return response.status_code == 201
    except (httpx.HTTPError, RuntimeError, KeyError, ValueError) as exc:
        LOGGER.warning("GitHub skill review check run failed", extra={"error": str(exc)})
        return False
