from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
import os
from typing import Literal

import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import AgentTask, DigestConfig, Org, Repo, Skill, SkillGap, SkillUsageEvent


router = APIRouter(prefix="/orgs/{org_id}/digest", tags=["digest"])


class DigestSendBody(BaseModel):
    recipient_email: str | None = None


class DigestConfigBody(BaseModel):
    title: str = Field(default="Weekly AI Readiness Digest", min_length=1, max_length=255)
    subject: str = Field(default="Your Weekly AI Readiness Report", min_length=1, max_length=255)
    frequency: str = Field(default="weekly", max_length=32)
    recipients: list[str] = Field(default_factory=list)
    widgets: list[str] = Field(default_factory=list)
    layout: dict[str, object] = Field(default_factory=dict)


class DigestPreviewBody(BaseModel):
    config: DigestConfigBody | None = None


class DigestSendNowBody(BaseModel):
    recipient_email: str | None = None
    config: DigestConfigBody | None = None


DEFAULT_WIDGETS = [
    "memory_score",
    "agent_loads",
    "active_repos",
    "top_skill",
    "skill_gaps",
    "roi_multiplier",
]


def _error(status_code: int, detail: str, code: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail, "code": code})


def _config_response(config: DigestConfig) -> dict:
    return {
        "id": config.id,
        "org_id": config.org_id,
        "title": config.title,
        "subject": config.subject,
        "frequency": config.frequency,
        "recipients": list(config.recipients or []),
        "widgets": list(config.widgets or DEFAULT_WIDGETS),
        "layout": dict(config.layout or {}),
        "created_at": config.created_at,
        "updated_at": config.updated_at,
    }


async def _rollback(db: AsyncSession) -> None:
    try:
        await db.rollback()
    except Exception:
        pass


async def _load_or_create_config(db: AsyncSession, org_id: str) -> DigestConfig:
    config = (await db.execute(select(DigestConfig).where(DigestConfig.org_id == org_id))).scalar_one_or_none()
    if config is not None:
        if not config.widgets:
            config.widgets = DEFAULT_WIDGETS
        return config
    config = DigestConfig(
        org_id=org_id,
        widgets=DEFAULT_WIDGETS,
        recipients=[],
        layout={"columns": 2},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(config)
    await db.flush()
    return config


def _apply_config(config: DigestConfig, body: DigestConfigBody) -> DigestConfig:
    config.title = body.title
    config.subject = body.subject
    config.frequency = body.frequency or "weekly"
    config.recipients = [recipient.strip() for recipient in body.recipients if recipient.strip()]
    config.widgets = body.widgets or DEFAULT_WIDGETS
    config.layout = body.layout or {}
    config.updated_at = datetime.utcnow()
    return config


def _week(value: datetime) -> str:
    year, week, _ = value.isocalendar()
    return f"{year}-W{week:02d}"


def _html_digest(payload: dict, recipient: str) -> str:
    widgets = set(payload.get("widgets") or DEFAULT_WIDGETS)
    metric_cards = []
    if "agent_loads" in widgets:
        metric_cards.append(f"<div style=\"background:#111827;border-radius:14px;padding:16px\"><b>Total Agent Loads</b><div style=\"font-size:32px\">{payload['total_agent_loads']}</div></div>")
    if "active_repos" in widgets:
        metric_cards.append(f"<div style=\"background:#111827;border-radius:14px;padding:16px\"><b>Active Repos</b><div style=\"font-size:32px\">{payload['active_repos']}</div></div>")
    if "roi_multiplier" in widgets:
        metric_cards.append(f"<div style=\"background:#111827;border-radius:14px;padding:16px\"><b>ROI Multiplier</b><div style=\"font-size:32px\">{payload['roi_multiplier'] or 'N/A'}x</div></div>")
    if "memory_score" in widgets:
        metric_cards.append(f"<div style=\"background:#111827;border-radius:14px;padding:16px\"><b>Memory Score</b><div style=\"font-size:32px\">{payload['memory_score']}/100</div></div>")
    top_skill = f"<h2 style=\"color:#C8922A\">Top Skill</h2><p>{payload['top_skill']['name']} · {payload['top_skill']['loads']} loads</p>" if "top_skill" in widgets else ""
    gap_items = "".join(
        f"<li>{gap['pattern']} · {gap['frequency']}</li>"
        for gap in payload["top_gaps"]
    ) or "<li>No gaps detected</li>"
    top_gaps = f"<h2 style=\"color:#C8922A\">Top Gaps</h2><ul>{gap_items}</ul>" if "skill_gaps" in widgets else ""
    return f"""<!doctype html>
<html><body style="margin:0;background:#101018;color:#f8fafc;font-family:Inter,Arial,sans-serif">
  <div style="max-width:680px;margin:0 auto;padding:24px">
    <div style="background:#1A1A2E;border:1px solid #2b2b42;border-radius:18px;padding:24px">
      <h1 style="margin:0;color:#C8922A">{payload.get('title') or 'Weekly AI Readiness Report'}</h1>
      <p style="color:#a1a1aa">Week {payload['week']} for {payload['org_name']} · sent to {recipient}</p>
      <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px">
        {''.join(metric_cards)}
      </div>
      {top_skill}
      {top_gaps}
    </div>
  </div>
</body></html>"""


async def _preview(org_id: str, db: AsyncSession, config_override: DigestConfigBody | None = None) -> dict:
    now = datetime.now(UTC).replace(tzinfo=None)
    week_start = now - timedelta(days=7)
    prev_start = now - timedelta(days=14)
    org = (await db.execute(select(Org).where(Org.id == org_id))).scalar_one_or_none()
    repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
    repo_ids = [repo.id for repo in repos]
    events = (
        (await db.execute(select(SkillUsageEvent).where(SkillUsageEvent.org_id == org_id).order_by(SkillUsageEvent.loaded_at.desc())))
        .scalars()
        .all()
    )
    current_loads = [event for event in events if event.loaded_at >= week_start]
    previous_loads = [event for event in events if prev_start <= event.loaded_at < week_start]
    trend: Literal["up", "down", "flat"] = "flat"
    if len(current_loads) > len(previous_loads):
        trend = "up"
    elif len(current_loads) < len(previous_loads):
        trend = "down"

    skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all() if repo_ids else []
    skills_by_id = {skill.id: skill for skill in skills}
    top_skill_id, top_skill_loads = Counter(event.skill_id for event in current_loads).most_common(1)[0] if current_loads else (None, 0)
    top_skill = skills_by_id.get(top_skill_id) if top_skill_id else None
    try:
        gaps = (await db.execute(select(SkillGap).where(SkillGap.org_id == org_id, SkillGap.status == "open"))).scalars().all()
    except SQLAlchemyError:
        gaps = []
    try:
        tasks = (await db.execute(select(AgentTask).where(AgentTask.org_id == org_id, AgentTask.started_at >= week_start))).scalars().all()
    except SQLAlchemyError:
        tasks = []
    high = [task for task in tasks if task.skill_score_at_task is not None and task.skill_score_at_task >= 70]
    low = [task for task in tasks if task.skill_score_at_task is not None and task.skill_score_at_task < 40]
    high_rate = sum(1 for task in high if task.outcome == "success") / len(high) if high else None
    low_rate = sum(1 for task in low if task.outcome == "success") / len(low) if low else None
    roi = round(min(10, high_rate / low_rate), 1) if high_rate is not None and low_rate and len(high) >= 3 and len(low) >= 3 else None
    load_rate_score = min(100, len(current_loads) * 4)
    coverage_score = min(100, len(skills) * 8)
    gap_penalty = max(0, 100 - len(gaps) * 15)
    memory_score = int(min(100, load_rate_score * 0.4 + coverage_score * 0.4 + gap_penalty * 0.2))
    config = config_override
    if config is None:
        stored = (await db.execute(select(DigestConfig).where(DigestConfig.org_id == org_id))).scalar_one_or_none()
        if stored is not None:
            config = DigestConfigBody(
                title=stored.title,
                subject=stored.subject,
                frequency=stored.frequency,
                recipients=list(stored.recipients or []),
                widgets=list(stored.widgets or DEFAULT_WIDGETS),
                layout=dict(stored.layout or {}),
            )
    widgets = config.widgets if config else DEFAULT_WIDGETS
    payload = {
        "week": _week(now),
        "org_name": org.name if org else "Skillayer",
        "title": config.title if config else "Weekly AI Readiness Digest",
        "subject": config.subject if config else "Your Weekly AI Readiness Report",
        "frequency": config.frequency if config else "weekly",
        "recipients": config.recipients if config else [],
        "widgets": widgets,
        "total_agent_loads": len(events),
        "loads_last_week": len(previous_loads),
        "loads_trend": trend,
        "active_repos": len(repos),
        "top_skill": {"name": top_skill.domain if top_skill else "No skill loaded yet", "loads": top_skill_loads},
        "skill_gap_count": len(gaps),
        "roi_multiplier": roi,
        "top_gaps": [{"pattern": gap.domain, "frequency": gap.failure_count} for gap in sorted(gaps, key=lambda item: item.failure_count, reverse=True)[:3]],
        "memory_score": memory_score,
    }
    payload["html"] = _html_digest(payload, (payload["recipients"] or ["preview@skillayer.com"])[0])
    return payload


@router.get("/config", response_model=None)
async def get_digest_config(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict | JSONResponse:
    actual_org_id = current_org_id or org_id
    try:
        config = await _load_or_create_config(db, actual_org_id)
        await db.commit()
        return _config_response(config)
    except Exception:
        await _rollback(db)
        return _error(400, "Could not load digest config", "DIGEST_CONFIG_LOAD_FAILED")


@router.put("/config", response_model=None)
async def put_digest_config(body: DigestConfigBody, org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict | JSONResponse:
    actual_org_id = current_org_id or org_id
    try:
        config = await _load_or_create_config(db, actual_org_id)
        _apply_config(config, body)
        await db.commit()
        return _config_response(config)
    except Exception:
        await _rollback(db)
        return _error(400, "Could not save digest config", "DIGEST_CONFIG_SAVE_FAILED")


@router.post("/preview", response_model=None)
async def digest_preview_post(body: DigestPreviewBody, org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict | JSONResponse:
    try:
        return await _preview(current_org_id or org_id, db, body.config)
    except Exception:
        await _rollback(db)
        return _error(400, "Could not preview digest", "DIGEST_PREVIEW_FAILED")


@router.get("/preview", response_model=None)
async def digest_preview(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict | JSONResponse:
    try:
        return await _preview(current_org_id or org_id, db)
    except Exception:
        await _rollback(db)
        return _error(400, "Could not preview digest", "DIGEST_PREVIEW_FAILED")


@router.post("/send-now", response_model=None)
async def send_digest_now(body: DigestSendNowBody, org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict | JSONResponse:
    actual_org_id = current_org_id or org_id
    try:
        payload = await _preview(actual_org_id, db, body.config)
        recipient = body.recipient_email or (payload.get("recipients") or ["owner@skillayer.com"])[0]
        return await _send_payload(payload, recipient)
    except Exception:
        await _rollback(db)
        return _error(400, "Could not send digest", "DIGEST_SEND_FAILED")


async def _send_payload(payload: dict, recipient: str) -> dict:
    html = _html_digest(payload, recipient)
    subject = payload.get("subject") or f"Your Weekly AI Readiness Report - Week {payload['week']}"
    sendgrid_key = os.environ.get("SENDGRID_API_KEY")
    if not sendgrid_key:
        print(html)
        return {"sent": False, "to": recipient, "preview": html}
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {sendgrid_key}", "Content-Type": "application/json"},
            json={
                "personalizations": [{"to": [{"email": recipient}]}],
                "from": {"email": "digest@skillayer.com", "name": "Skillayer"},
                "subject": subject,
                "content": [{"type": "text/html", "value": html}],
            },
        )
    return {"sent": response.status_code < 300, "to": recipient, "preview": html if response.status_code >= 300 else None}


@router.post("/send", response_model=None)
async def send_digest(body: DigestSendBody, org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict | JSONResponse:
    actual_org_id = current_org_id or org_id
    try:
        payload = await _preview(actual_org_id, db)
        recipient = body.recipient_email or (payload.get("recipients") or ["owner@skillayer.com"])[0]
        return await _send_payload(payload, recipient)
    except Exception:
        await _rollback(db)
        return _error(400, "Could not send digest", "DIGEST_SEND_FAILED")
