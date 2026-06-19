from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date as date_cls, datetime, time, timedelta
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.notifications import post_slack_message
from packages.db.models import AgentSession, Org, PRAttribution, PullRequest, Repo


APP_BASE_URL = "https://app.skillayer.com"


def parse_standup_date(value: str | None) -> date_cls:
    if not value:
        return datetime.utcnow().date()
    try:
        return date_cls.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="date must use YYYY-MM-DD") from exc


def day_bounds(value: date_cls) -> tuple[datetime, datetime]:
    start = datetime.combine(value, time.min)
    return start, start + timedelta(days=1)


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _count_findings(findings: Any) -> tuple[int, int]:
    violations = 0
    warnings = 0
    for item in _as_list(findings):
        if not isinstance(item, dict):
            continue
        severity = str(item.get("severity") or "warning").lower()
        if severity in {"critical", "error", "fatal", "failure"}:
            violations += 1
        else:
            warnings += 1
    return violations, warnings


def _session_file_count(session: AgentSession) -> int:
    return len({str(path) for path in _as_list(session.files_touched) if path})


async def collect_standup_summary(org_id: str, date: str | None, db: AsyncSession) -> dict[str, Any]:
    target_date = parse_standup_date(date)
    start, end = day_bounds(target_date)

    sessions = list(
        (
            await db.execute(
                select(AgentSession).where(
                    AgentSession.org_id == org_id,
                    AgentSession.session_start >= start,
                    AgentSession.session_start < end,
                )
            )
        )
        .scalars()
        .all()
    )

    repos = list((await db.execute(select(Repo).where(Repo.org_id == org_id))).scalars().all())
    repo_ids = [repo.id for repo in repos]
    prs: list[PullRequest] = []
    if repo_ids:
        prs = list(
            (
                await db.execute(
                    select(PullRequest).where(
                        PullRequest.repo_id.in_(repo_ids),
                    )
                )
            )
            .scalars()
            .all()
        )

    daily_prs = [
        pr
        for pr in prs
        if (pr.opened_at and start <= pr.opened_at < end) or (pr.merged_at and start <= pr.merged_at < end)
    ]
    pr_ids = [pr.id for pr in daily_prs]
    attributions: list[PRAttribution] = []
    if pr_ids:
        attributions = list(
            (await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_(pr_ids)))).scalars().all()
        )

    engineer_sessions: dict[str, list[AgentSession]] = defaultdict(list)
    files_changed: set[str] = set()
    skills = Counter()
    for session in sessions:
        login = session.engineer_login or "unknown"
        engineer_sessions[login].append(session)
        files_changed.update(str(path) for path in _as_list(session.files_touched) if path)
        skills.update(str(skill) for skill in _as_list(session.skills_loaded) if skill)

    top_engineers = sorted(
        (
            {
                "login": login,
                "sessions": len(items),
                "files": sum(_session_file_count(item) for item in items),
            }
            for login, items in engineer_sessions.items()
        ),
        key=lambda item: (-int(item["sessions"]), -int(item["files"]), str(item["login"])),
    )[:5]

    violations_total = 0
    warnings_total = 0
    risk_summary = {"red": 0, "yellow": 0, "green": 0}
    for attribution in attributions:
        violations, warnings = _count_findings(attribution.skills_violated)
        violations_total += violations
        warnings_total += warnings
        tier = str(attribution.risk_tier or "green")
        if tier not in risk_summary:
            tier = "green"
        risk_summary[tier] += 1

    return {
        "date": target_date.isoformat(),
        "agent_sessions": len(sessions),
        "files_changed": len(files_changed),
        "prs_opened": sum(1 for pr in daily_prs if pr.opened_at and start <= pr.opened_at < end),
        "prs_merged": sum(1 for pr in daily_prs if pr.merged_at and start <= pr.merged_at < end),
        "top_engineers": top_engineers,
        "top_skills_used": [skill for skill, _count in skills.most_common(5)],
        "violations_total": violations_total,
        "warnings_total": warnings_total,
        "risk_summary": risk_summary,
    }


async def build_standup_blocks(org_id: str, date: str | None, db: AsyncSession) -> list[dict[str, Any]]:
    summary = await collect_standup_summary(org_id, date, db)
    parsed_date = parse_standup_date(summary["date"])
    label = f"{parsed_date.strftime('%B')} {parsed_date.day}, {parsed_date.year}"
    top_engineers = summary["top_engineers"] or [{"login": "No engineers", "sessions": 0, "files": 0}]
    engineer_lines = "\n".join(
        f"• `{item['login']}` — {item['sessions']} session(s), {item['files']} file(s)"
        for item in top_engineers
    )
    top_skills = ", ".join(f"`{skill}`" for skill in summary["top_skills_used"]) or "No skills loaded"
    risk = summary["risk_summary"]
    blocks: list[dict[str, Any]] = [
        {"type": "header", "text": {"type": "plain_text", "text": f"Skillayer Daily Standup — {label}"}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Agent Activity*\n"
                    f"{summary['agent_sessions']} session(s) · {summary['files_changed']} file(s) changed · "
                    f"{summary['prs_opened']} PR(s) opened · {summary['prs_merged']} PR(s) merged"
                ),
            },
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Top Engineers*\n{engineer_lines}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Top Skills Used*\n{top_skills}"}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Risk Summary*\n:red_circle: {risk['red']} red  :large_yellow_circle: {risk['yellow']} yellow  :large_green_circle: {risk['green']} green",
            },
        },
    ]
    if summary["violations_total"] or summary["warnings_total"]:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Violations*\n{summary['violations_total']} violation(s), {summary['warnings_total']} warning(s) across today's PRs.",
                },
            }
        )
    blocks.append(
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Open PR Inbox"},
                    "url": f"{APP_BASE_URL}/dashboard/agent-prs",
                }
            ],
        }
    )
    return blocks


async def send_standup(org_id: str, date: str | None, db: AsyncSession) -> bool:
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    if not org.slack_webhook_url:
        raise HTTPException(status_code=400, detail="Slack webhook URL is not configured")
    blocks = await build_standup_blocks(org_id, date, db)
    await post_slack_message(
        org.slack_webhook_url,
        {
            "text": f"Skillayer Daily Standup for {parse_standup_date(date).isoformat()}",
            "blocks": blocks,
        },
    )
    return True
