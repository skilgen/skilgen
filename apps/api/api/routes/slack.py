from __future__ import annotations

import asyncio
import hashlib
import hmac
import time
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import parse_qs

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.services.commit_check import _severity_bucket
from apps.api.api.services.standup import build_standup_blocks
from packages.db.database import get_db
from packages.db.models import AgentSession, Org, PRAttribution, PullRequest, Repo, Skill


router = APIRouter(prefix="/webhooks/slack", tags=["slack"])

APP_BASE_URL = "https://app.skillayer.com"


def _verify_slack_signature(request_body: bytes, timestamp: str | None, signature: str | None, signing_secret: str) -> bool:
    if not timestamp or not signature or not signing_secret:
        return False
    try:
        request_ts = int(timestamp)
    except ValueError:
        return False
    if abs(int(time.time()) - request_ts) > 60 * 5:
        return False
    basestring = b"v0:" + timestamp.encode("utf-8") + b":" + request_body
    expected = "v0=" + hmac.new(signing_secret.encode("utf-8"), basestring, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _dt_naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.astimezone(UTC).replace(tzinfo=None) if value.tzinfo else value


def _parse_form(body: bytes) -> dict[str, str]:
    parsed = parse_qs(body.decode("utf-8"), keep_blank_values=True)
    return {key: values[0] if values else "" for key, values in parsed.items()}


def _plain_text(text: str) -> dict[str, str]:
    return {"type": "plain_text", "text": text}


def _mrkdwn(text: str) -> dict[str, str]:
    return {"type": "mrkdwn", "text": text}


def _payload(text: str, blocks: list[dict[str, Any]], *, response_type: str = "ephemeral") -> dict[str, Any]:
    return {"response_type": response_type, "text": text, "blocks": blocks}


def _help_payload() -> dict[str, Any]:
    blocks = [
        {"type": "header", "text": _plain_text("Skillayer command help")},
        {
            "type": "section",
            "text": _mrkdwn(
                "*Commands*\n"
                "- `/skillayer status` - org health and activity\n"
                "- `/skillayer standup [YYYY-MM-DD]` - daily standup summary\n"
                "- `/skillayer leaderboard [7|30|90]` - top developers\n"
                "- `/skillayer check @developer` - developer scorecard"
            ),
        },
        {"type": "divider"},
        {
            "type": "actions",
            "elements": [
                {"type": "button", "text": _plain_text("Open Dashboard"), "url": f"{APP_BASE_URL}/dashboard"}
            ],
        },
    ]
    return _payload("Skillayer help", blocks)


def _config_error(message: str) -> dict[str, Any]:
    return _payload("Skillayer Slack app is not configured", [{"type": "section", "text": _mrkdwn(message)}])


def _finding_counts(attribution: PRAttribution | None) -> tuple[int, int]:
    findings = attribution.skills_violated if attribution and isinstance(attribution.skills_violated, list) else []
    violations = 0
    warnings = 0
    for item in findings:
        if not isinstance(item, dict):
            continue
        if _severity_bucket(item) == "violation":
            violations += 1
        else:
            warnings += 1
    return violations, warnings


async def _post_deferred(response_url: str, payload: dict[str, Any]) -> None:
    if not response_url.startswith(("https://", "http://")):
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(response_url, json=payload)
    except httpx.HTTPError:
        return


async def _load_org(db: AsyncSession, team_id: str | None) -> Org | None:
    if team_id:
        org = (await db.execute(select(Org).where(Org.slack_team_id == team_id))).scalar_one_or_none()
        if org is not None:
            return org
    return None


async def _recent_prs_and_attributions(org_id: str, days: int, db: AsyncSession) -> tuple[list[PullRequest], dict[str, PRAttribution]]:
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days)
    repos = list((await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all())
    repo_ids = [repo.id for repo in repos]
    if not repo_ids:
        return [], {}
    prs = list((await db.execute(select(PullRequest).where(PullRequest.repo_id.in_(repo_ids)))).scalars().all())
    prs = [
        pr
        for pr in prs
        if _dt_naive(pr.opened_at) is not None and _dt_naive(pr.opened_at) >= cutoff
    ]
    pr_ids = [pr.id for pr in prs]
    attributions = (
        list((await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_(pr_ids)))).scalars().all())
        if pr_ids
        else []
    )
    return prs, {attr.pr_id: attr for attr in attributions}


async def _status_payload(org: Org, db: AsyncSession) -> dict[str, Any]:
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=30)
    repos = list((await db.execute(select(Repo).where(Repo.org_id == org.id, Repo.is_active.is_(True)))).scalars().all())
    repo_ids = [repo.id for repo in repos]
    skills = list((await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all()) if repo_ids else []
    sessions = list(
        (
            await db.execute(
                select(AgentSession).where(AgentSession.org_id == org.id, AgentSession.session_start >= cutoff)
            )
        )
        .scalars()
        .all()
    )
    prs, attr_by_pr = await _recent_prs_and_attributions(org.id, 30, db)
    agent_prs: dict[str, int] = defaultdict(int)
    clean_prs: dict[str, int] = defaultdict(int)
    for pr in prs:
        attr = attr_by_pr.get(pr.id)
        agent = str(attr.primary_agent if attr else "human")
        violations, _warnings = _finding_counts(attr)
        agent_prs[agent] += 1
        if violations == 0:
            clean_prs[agent] += 1
    top_agent = "No PRs attributed"
    if agent_prs:
        best = sorted(agent_prs, key=lambda agent: (-(clean_prs[agent] / agent_prs[agent]), -agent_prs[agent], agent))[0]
        top_agent = f"`{best}` at {round((clean_prs[best] / agent_prs[best]) * 100, 1)}%"
    blocks = [
        {"type": "header", "text": _plain_text("Skillayer Status")},
        {
            "type": "section",
            "fields": [
                _mrkdwn(f"*Skills*\n{len(skills)}"),
                _mrkdwn(f"*Repos*\n{len(repos)}"),
                _mrkdwn(f"*Sessions 30d*\n{len(sessions)}"),
                _mrkdwn(f"*PRs attributed 30d*\n{len(attr_by_pr)}"),
                _mrkdwn(f"*Top agent compliance*\n{top_agent}"),
            ],
        },
        {"type": "divider"},
        {
            "type": "actions",
            "elements": [
                {"type": "button", "text": _plain_text("Open Dashboard"), "url": f"{APP_BASE_URL}/dashboard"}
            ],
        },
    ]
    return _payload("Skillayer Status", blocks)


async def _developer_rows(org_id: str, days: int, db: AsyncSession) -> list[dict[str, Any]]:
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days)
    repos = list((await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all())
    repo_ids = [repo.id for repo in repos]
    if not repo_ids:
        return []
    sessions = list(
        (
            await db.execute(
                select(AgentSession).where(
                    AgentSession.repo_id.in_(repo_ids),
                    AgentSession.session_start >= cutoff,
                )
            )
        )
        .scalars()
        .all()
    )
    prs, attr_by_pr = await _recent_prs_and_attributions(org_id, days, db)
    rows: dict[str, dict[str, Any]] = {}

    def row(login: str) -> dict[str, Any]:
        return rows.setdefault(
            login,
            {
                "login": login,
                "sessions": 0,
                "prs": 0,
                "violations": 0,
                "warnings": 0,
                "clean_prs": 0,
                "risk": 0,
            },
        )

    for session in sessions:
        login = str(session.engineer_login or "").strip()
        if login:
            row(login)["sessions"] += 1
    for pr in prs:
        login = str(pr.author_login or "").strip()
        if not login:
            continue
        item = row(login)
        item["prs"] += 1
        attr = attr_by_pr.get(pr.id)
        violations, warnings = _finding_counts(attr)
        item["violations"] += violations
        item["warnings"] += warnings
        item["risk"] += int(attr.risk_score or 0) if attr else 0
        if violations == 0:
            item["clean_prs"] += 1

    for item in rows.values():
        prs_count = int(item["prs"])
        item["compliance"] = round((int(item["clean_prs"]) / prs_count) * 100, 1) if prs_count else 100.0
        item["avg_risk"] = round(int(item["risk"]) / prs_count, 1) if prs_count else 0.0
    return sorted(rows.values(), key=lambda item: (-float(item["compliance"]), -int(item["prs"]), -int(item["sessions"]), str(item["login"])))


async def _leaderboard_payload(org: Org, days: int, db: AsyncSession) -> dict[str, Any]:
    rows = await _developer_rows(org.id, days, db)
    if rows:
        lines = "\n".join(
            f"{index}. `{item['login']}` - {item['compliance']}% compliance, {item['prs']} PR(s), {item['sessions']} session(s), {item['violations']} violation(s)"
            for index, item in enumerate(rows[:5], start=1)
        )
    else:
        lines = "No developer activity in this window."
    blocks = [
        {"type": "header", "text": _plain_text(f"Developer Leaderboard ({days}d)")},
        {"type": "section", "text": _mrkdwn(lines)},
        {"type": "divider"},
        {
            "type": "actions",
            "elements": [
                {"type": "button", "text": _plain_text("Full leaderboard"), "url": f"{APP_BASE_URL}/dashboard/teams"}
            ],
        },
    ]
    return _payload("Skillayer developer leaderboard", blocks, response_type="in_channel")


async def _developer_check_payload(org: Org, login: str, db: AsyncSession) -> dict[str, Any]:
    normalized = login.strip().lstrip("@")
    rows = await _developer_rows(org.id, 30, db)
    row = next((item for item in rows if str(item["login"]).lower() == normalized.lower()), None)
    if row is None:
        return _payload(
            f"No Skillayer activity found for {normalized}",
            [{"type": "section", "text": _mrkdwn(f"No recent Skillayer activity found for `{normalized}`.")}],
        )
    blocks = [
        {"type": "header", "text": _plain_text(f"Developer Check: {row['login']}")},
        {
            "type": "section",
            "fields": [
                _mrkdwn(f"*Sessions 30d*\n{row['sessions']}"),
                _mrkdwn(f"*PRs 30d*\n{row['prs']}"),
                _mrkdwn(f"*Violations*\n{row['violations']}"),
                _mrkdwn(f"*Compliance*\n{row['compliance']}%"),
                _mrkdwn(f"*Average risk*\n{row['avg_risk']}"),
            ],
        },
        {"type": "divider"},
        {
            "type": "actions",
            "elements": [
                {"type": "button", "text": _plain_text("Open profile"), "url": f"{APP_BASE_URL}/dashboard/my-code-today?login={row['login']}"}
            ],
        },
    ]
    return _payload(f"Skillayer developer check for {row['login']}", blocks)


def _parse_days(value: str | None, default: int = 30) -> int:
    try:
        days = int(str(value or "").strip() or default)
    except ValueError:
        return default
    return min(180, max(1, days))


@router.post("/command")
async def slack_command(request: Request, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    body = await request.body()
    form = _parse_form(body)
    org = await _load_org(db, form.get("team_id"))
    if org is None:
        return JSONResponse(_config_error("This Slack workspace is not connected to a Skillayer org."))
    if not org.slack_signing_secret:
        return JSONResponse(_config_error("Slack signing secret is not configured in Skillayer settings."))

    if not _verify_slack_signature(
        body,
        request.headers.get("X-Slack-Request-Timestamp"),
        request.headers.get("X-Slack-Signature"),
        org.slack_signing_secret,
    ):
        return JSONResponse({"detail": "Invalid Slack signature"}, status_code=401)

    text = str(form.get("text") or "").strip()
    parts = text.split()
    command = parts[0].lower() if parts else "help"
    response_url = str(form.get("response_url") or "")

    if command == "status":
        payload = await _status_payload(org, db)
    elif command == "standup":
        date_value = parts[1] if len(parts) > 1 else None
        payload = _payload("Skillayer daily standup", await build_standup_blocks(org.id, date_value, db), response_type="in_channel")
    elif command == "leaderboard":
        payload = await _leaderboard_payload(org, _parse_days(parts[1] if len(parts) > 1 else None), db)
    elif command == "check" and len(parts) > 1:
        payload = await _developer_check_payload(org, parts[1], db)
    else:
        payload = _help_payload()

    if response_url:
        asyncio.create_task(_post_deferred(response_url, payload))
    return JSONResponse(payload)
