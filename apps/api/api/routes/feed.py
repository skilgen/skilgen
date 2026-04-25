from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import Org, Repo, Skill, SkillUsageEvent


router = APIRouter(prefix="/orgs/{org_id}/feed", tags=["feed"])


async def _org_from_key(key: str | None, db: AsyncSession) -> str | None:
    if not key:
        return None
    org = (await db.execute(select(Org).where(Org.api_key == key))).scalar_one_or_none()
    return str(org.id) if org else None


def _event_payload(event: SkillUsageEvent, repo: Repo | None, skill: Skill | None) -> dict:
    return {
        "id": str(event.id),
        "repo": repo.name if repo else "Unknown repo",
        "skill": skill.domain if skill else "Unknown skill",
        "agent": event.agent_runtime,
        "ts": event.loaded_at.isoformat(),
    }


@router.get("/recent")
async def recent_feed(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    actual_org_id = current_org_id or org_id
    events = (await db.execute(select(SkillUsageEvent).where(SkillUsageEvent.org_id == actual_org_id).order_by(desc(SkillUsageEvent.loaded_at)).limit(50))).scalars().all()
    repo_ids = {event.repo_id for event in events}
    skill_ids = {event.skill_id for event in events}
    repos = {repo.id: repo for repo in (await db.execute(select(Repo).where(Repo.id.in_(repo_ids)))).scalars().all()} if repo_ids else {}
    skills = {skill.id: skill for skill in (await db.execute(select(Skill).where(Skill.id.in_(skill_ids)))).scalars().all()} if skill_ids else {}
    return {"events": [_event_payload(event, repos.get(event.repo_id), skills.get(event.skill_id)) for event in events], "total": len(events)}


@router.get("/stream")
async def stream_feed(org_id: str, request: Request, key: str | None = None, db: AsyncSession = Depends(get_db)) -> StreamingResponse:
    actual_org_id = await _org_from_key(key, db) or org_id

    async def generate():
        started = datetime.now(UTC)
        last_sent: set[str] = set()
        last_heartbeat = datetime.now(UTC)
        while (datetime.now(UTC) - started) < timedelta(minutes=5):
            cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=60)
            events = (
                await db.execute(select(SkillUsageEvent).where(SkillUsageEvent.org_id == actual_org_id, SkillUsageEvent.loaded_at >= cutoff).order_by(SkillUsageEvent.loaded_at))
            ).scalars().all()
            for event in events:
                if event.id in last_sent:
                    continue
                repo = (await db.execute(select(Repo).where(Repo.id == event.repo_id))).scalar_one_or_none()
                skill = (await db.execute(select(Skill).where(Skill.id == event.skill_id))).scalar_one_or_none()
                last_sent.add(event.id)
                yield f"data: {json.dumps(_event_payload(event, repo, skill))}\n\n"
            if (datetime.now(UTC) - last_heartbeat) >= timedelta(seconds=5):
                last_heartbeat = datetime.now(UTC)
                yield ": heartbeat\n\n"
            if await request.is_disconnected():
                break
            await asyncio.sleep(2)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Access-Control-Allow-Origin": "*"},
    )
