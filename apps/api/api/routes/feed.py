from __future__ import annotations

import asyncio
import json
from collections import defaultdict
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


def _session_context(domains: list[str]) -> str:
    normalized = {domain.lower() for domain in domains}
    if any("security" in domain for domain in normalized):
        return "Security-sensitive work"
    if "data_schema" in normalized or any("schema" in domain for domain in normalized):
        return "Database or data model changes"
    if "testing_conventions" in normalized or any("test" in domain for domain in normalized):
        return "Writing or fixing tests"
    if "codebase_architecture" in normalized and len(domains) >= 4:
        return "Major architectural change"
    if len(domains) >= 6:
        return "Broad feature development"
    if len(domains) == 1:
        return f"Focused {domains[0]} work"
    return "General development session"


def _quality_signal(scores: list[int]) -> tuple[str, str]:
    avg = sum(scores) / len(scores) if scores else 0
    if avg >= 75:
        return "strong", "Agent loaded high-quality skills - output likely matches your conventions"
    if avg >= 50:
        return "mixed", "Some loaded skills have room for improvement - review output carefully"
    return "weak", "Agent loaded low-quality skills - output may not follow your patterns"


@router.get("/recent")
async def recent_feed(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    actual_org_id = current_org_id or org_id
    events = (await db.execute(select(SkillUsageEvent).where(SkillUsageEvent.org_id == actual_org_id).order_by(desc(SkillUsageEvent.loaded_at)).limit(50))).scalars().all()
    repo_ids = {event.repo_id for event in events}
    skill_ids = {event.skill_id for event in events}
    repos = {repo.id: repo for repo in (await db.execute(select(Repo).where(Repo.id.in_(repo_ids)))).scalars().all()} if repo_ids else {}
    skills = {skill.id: skill for skill in (await db.execute(select(Skill).where(Skill.id.in_(skill_ids)))).scalars().all()} if skill_ids else {}
    grouped: dict[tuple[str, str, str], list[SkillUsageEvent]] = defaultdict(list)
    for event in events:
        grouped[(event.session_id, event.repo_id, event.agent_runtime)].append(event)
    sessions = []
    for (session_id, repo_id, agent_runtime), session_events in grouped.items():
        loaded_at = max(event.loaded_at for event in session_events)
        session_skills = [skills[event.skill_id] for event in session_events if event.skill_id in skills]
        domains = sorted({skill.domain for skill in session_skills if skill.domain})
        signal, reason = _quality_signal([int(skill.score_total or 0) for skill in session_skills])
        repo = repos.get(repo_id)
        sessions.append(
            {
                "id": session_id,
                "session_id": session_id,
                "agent_runtime": agent_runtime,
                "agent": agent_runtime,
                "repo_name": repo.name if repo else "Unknown repo",
                "repo": repo.name if repo else "Unknown repo",
                "loaded_at": loaded_at.isoformat(),
                "ts": loaded_at.isoformat(),
                "skills_loaded": domains,
                "skill": ", ".join(domains[:3]) if domains else "Unknown skill",
                "session_context": _session_context(domains),
                "skill_count": len(domains),
                "quality_signal": signal,
                "quality_reason": reason,
            }
        )
    sessions.sort(key=lambda item: str(item["loaded_at"]), reverse=True)
    return {"events": sessions[:10], "total": len(sessions)}


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
