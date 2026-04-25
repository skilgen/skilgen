from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
import os
from typing import Literal

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import AgentTask, Org, Repo, Skill, SkillGap, SkillUsageEvent


router = APIRouter(prefix="/orgs/{org_id}/digest", tags=["digest"])


class DigestSendBody(BaseModel):
    recipient_email: str | None = None


def _week(value: datetime) -> str:
    year, week, _ = value.isocalendar()
    return f"{year}-W{week:02d}"


def _html_digest(payload: dict, recipient: str) -> str:
    return f"""<!doctype html>
<html><body style="margin:0;background:#101018;color:#f8fafc;font-family:Inter,Arial,sans-serif">
  <div style="max-width:680px;margin:0 auto;padding:24px">
    <div style="background:#1A1A2E;border:1px solid #2b2b42;border-radius:18px;padding:24px">
      <h1 style="margin:0;color:#C8922A">Weekly AI Readiness Report</h1>
      <p style="color:#a1a1aa">Week {payload['week']} for {payload['org_name']} · sent to {recipient}</p>
      <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px">
        <div style="background:#111827;border-radius:14px;padding:16px"><b>Total Agent Loads</b><div style="font-size:32px">{payload['total_agent_loads']}</div></div>
        <div style="background:#111827;border-radius:14px;padding:16px"><b>Active Repos</b><div style="font-size:32px">{payload['active_repos']}</div></div>
        <div style="background:#111827;border-radius:14px;padding:16px"><b>ROI Multiplier</b><div style="font-size:32px">{payload['roi_multiplier'] or 'N/A'}x</div></div>
        <div style="background:#111827;border-radius:14px;padding:16px"><b>Memory Score</b><div style="font-size:32px">{payload['memory_score']}/100</div></div>
      </div>
      <h2 style="color:#C8922A">Top Skill</h2>
      <p>{payload['top_skill']['name']} · {payload['top_skill']['loads']} loads</p>
      <h2 style="color:#C8922A">Top Gaps</h2>
      <ul>{''.join(f"<li>{gap['pattern']} · {gap['frequency']}</li>" for gap in payload['top_gaps']) or '<li>No gaps detected</li>'}</ul>
    </div>
  </div>
</body></html>"""


async def _preview(org_id: str, db: AsyncSession) -> dict:
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
    gaps = (await db.execute(select(SkillGap).where(SkillGap.org_id == org_id, SkillGap.status == "open"))).scalars().all()
    tasks = (await db.execute(select(AgentTask).where(AgentTask.org_id == org_id, AgentTask.started_at >= week_start))).scalars().all()
    high = [task for task in tasks if task.skill_score_at_task is not None and task.skill_score_at_task >= 70]
    low = [task for task in tasks if task.skill_score_at_task is not None and task.skill_score_at_task < 40]
    high_rate = sum(1 for task in high if task.outcome == "success") / len(high) if high else None
    low_rate = sum(1 for task in low if task.outcome == "success") / len(low) if low else None
    roi = round(min(10, high_rate / low_rate), 1) if high_rate is not None and low_rate and len(high) >= 3 and len(low) >= 3 else None
    load_rate_score = min(100, len(current_loads) * 4)
    coverage_score = min(100, len(skills) * 8)
    gap_penalty = max(0, 100 - len(gaps) * 15)
    memory_score = int(min(100, load_rate_score * 0.4 + coverage_score * 0.4 + gap_penalty * 0.2))
    return {
        "week": _week(now),
        "org_name": org.name if org else "Skillayer",
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


@router.get("/preview")
async def digest_preview(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    return await _preview(current_org_id or org_id, db)


@router.post("/send")
async def send_digest(body: DigestSendBody, org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    actual_org_id = current_org_id or org_id
    payload = await _preview(actual_org_id, db)
    recipient = body.recipient_email or "owner@skillayer.com"
    html = _html_digest(payload, recipient)
    subject = f"Your Weekly AI Readiness Report - Week {payload['week']}"
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
