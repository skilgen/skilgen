from __future__ import annotations

import asyncio
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any, Iterable

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_org_id_optional
from apps.api.api.v8.flags import is_v8, request_flag_cache
from apps.api.api.v8.activity.view_model import (
    feed_event_view,
    risk_band,
    session_view,
    standalone_replay_html,
    replay_timeline,
)
from packages.db.database import get_db
from packages.db.models import AgentSession, Org, Repo, Skill, SkillUsageEvent


router = APIRouter(
    prefix="/v8/orgs/{org_id}",
    tags=["v8-activity"],
    dependencies=[Depends(request_flag_cache)],
)


async def _require_v8(org_id: str, current_org_id: str | None, db: AsyncSession) -> None:
    if current_org_id != org_id:
        raise HTTPException(status_code=403, detail="Org access denied")
    if not await is_v8(org_id, db):
        raise HTTPException(status_code=404, detail="Activity v8 is disabled")


async def _org_from_key(key: str | None, db: AsyncSession) -> str | None:
    if not key:
        return None
    org = (await db.execute(select(Org).where(Org.api_key == key))).scalar_one_or_none()
    return str(org.id) if org else None


async def _repo_in_org(db: AsyncSession, org_id: str, repo_id: str) -> Repo:
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != org_id:
        raise HTTPException(status_code=403, detail="Repo access denied")
    return repo


async def _repos_by_id(db: AsyncSession, repo_ids: Iterable[str]) -> dict[str, Repo]:
    ids = {repo_id for repo_id in repo_ids if repo_id}
    if not ids:
        return {}
    rows = (await db.execute(select(Repo).where(Repo.id.in_(ids)))).scalars().all()
    return {repo.id: repo for repo in rows}


async def _skills_by_id(db: AsyncSession, skill_ids: Iterable[str]) -> dict[str, Skill]:
    ids = {skill_id for skill_id in skill_ids if skill_id}
    if not ids:
        return {}
    rows = (await db.execute(select(Skill).where(Skill.id.in_(ids)))).scalars().all()
    return {skill.id: skill for skill in rows}


async def _sessions_for_events(db: AsyncSession, org_id: str, events: Iterable[SkillUsageEvent]) -> dict[tuple[str, str], AgentSession]:
    pairs = {(event.repo_id, event.session_id) for event in events if event.repo_id and event.session_id}
    if not pairs:
        return {}
    repo_ids = {repo_id for repo_id, _ in pairs}
    session_ids = {session_id for _, session_id in pairs}
    rows = (
        await db.execute(
            select(AgentSession).where(
                AgentSession.org_id == org_id,
                AgentSession.repo_id.in_(repo_ids),
                AgentSession.session_id.in_(session_ids),
            )
        )
    ).scalars().all()
    return {(session.repo_id, session.session_id): session for session in rows}


def _matches_filters(item: dict[str, Any], filters: dict[str, str | None]) -> bool:
    for key, value in filters.items():
        if not value:
            continue
        if key == "risk_band" and item.get("risk_band") != value:
            return False
        if key == "repo_sensitivity_tier" and item.get("repo_sensitivity_tier") != value:
            return False
        if key == "agent_provider" and item.get("agent_provider") != value:
            return False
        if key == "action_class" and item.get("action_class") != value:
            return False
        if key == "outcome" and item.get("outcome") != value:
            return False
        if key == "user" and item.get("user") != value:
            return False
        if key == "skill_id" and item.get("skill_id") != value:
            return False
    return True


async def _feed_items(
    db: AsyncSession,
    org_id: str,
    *,
    limit: int,
    hours: int,
    repo_id: str | None = None,
    filters: dict[str, str | None] | None = None,
) -> list[dict[str, Any]]:
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=hours)
    statement = select(SkillUsageEvent).where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff)
    if repo_id:
        statement = statement.where(SkillUsageEvent.repo_id == repo_id)
    events = (await db.execute(statement.order_by(desc(SkillUsageEvent.loaded_at)).limit(limit * 3))).scalars().all()
    repos = await _repos_by_id(db, [event.repo_id for event in events])
    skills = await _skills_by_id(db, [event.skill_id for event in events])
    sessions = await _sessions_for_events(db, org_id, events)
    items = [
        feed_event_view(
            event,
            repos.get(event.repo_id),
            skills.get(event.skill_id),
            sessions.get((event.repo_id, event.session_id)),
        )
        for event in events
    ]
    active_filters = filters or {}
    return [item for item in items if _matches_filters(item, active_filters)][:limit]


@router.get("/activity/feed")
async def activity_feed(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    limit: int = Query(default=50, ge=1, le=200),
    hours: int = Query(default=24, ge=1, le=24 * 30),
    repo_id: str | None = None,
    skill_id: str | None = None,
    agent_provider: str | None = None,
    action_class: str | None = None,
    outcome: str | None = None,
    risk_band_filter: str | None = Query(default=None, alias="risk_band"),
    repo_sensitivity_tier: str | None = None,
    user: str | None = None,
) -> dict[str, Any]:
    await _require_v8(org_id, current_org_id, db)
    items = await _feed_items(
        db,
        org_id,
        limit=limit,
        hours=hours,
        repo_id=repo_id,
        filters={
            "skill_id": skill_id,
            "agent_provider": agent_provider,
            "action_class": action_class,
            "outcome": outcome,
            "risk_band": risk_band_filter,
            "repo_sensitivity_tier": repo_sensitivity_tier,
            "user": user,
        },
    )
    return {"events": items, "total": len(items), "filters": {"hours": hours, "repo_id": repo_id}}


@router.get("/activity/feed/stream")
async def activity_feed_stream(
    org_id: str,
    request: Request,
    key: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> StreamingResponse:
    key_org_id = await _org_from_key(key, db)
    actual_org_id = key_org_id or current_org_id
    await _require_v8(org_id, actual_org_id, db)

    async def generate() -> Any:
        started = datetime.now(UTC)
        sent: set[str] = set()
        while (datetime.now(UTC) - started) < timedelta(minutes=5):
            items = await _feed_items(db, org_id, limit=25, hours=1)
            for item in reversed(items):
                event_id = str(item["id"])
                if event_id in sent:
                    continue
                sent.add(event_id)
                yield f"data: {json.dumps(item)}\n\n"
            if await request.is_disconnected():
                break
            yield ": heartbeat\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Access-Control-Allow-Origin": "*"},
    )


async def _session_skill_map(db: AsyncSession, sessions: Iterable[AgentSession]) -> dict[str, Skill]:
    repo_ids = {session.repo_id for session in sessions}
    if not repo_ids:
        return {}
    skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all()
    mapped: dict[str, Skill] = {}
    for skill in skills:
        mapped[str(skill.id)] = skill
        mapped[str(skill.domain)] = skill
        mapped[str(skill.skill_path)] = skill
    return mapped


def _rollup(items: list[dict[str, Any]]) -> dict[str, Any]:
    providers: dict[str, dict[str, Any]] = {}
    for item in items:
        provider = str(item["agent_provider"])
        row = providers.setdefault(provider, {"agent_provider": provider, "agent": item["agent"], "sessions": 0, "risk_total": 0, "high_risk": 0})
        row["sessions"] += 1
        row["risk_total"] += int(item["risk_score"])
        if item["risk_band"] == "high":
            row["high_risk"] += 1
    for row in providers.values():
        row["avg_risk_score"] = round(row["risk_total"] / max(1, row["sessions"]), 1)
        del row["risk_total"]
    outcomes = Counter(str(item["outcome"]) for item in items)
    return {"providers": sorted(providers.values(), key=lambda row: (-row["sessions"], row["agent_provider"])), "outcomes": dict(outcomes), "total_sessions": len(items)}


@router.get("/activity/sessions")
async def activity_sessions(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    repo_id: str | None = None,
    agent_provider: str | None = None,
    risk_band_filter: str | None = Query(default=None, alias="risk_band"),
) -> dict[str, Any]:
    await _require_v8(org_id, current_org_id, db)
    statement = select(AgentSession).where(AgentSession.org_id == org_id)
    if repo_id:
        statement = statement.where(AgentSession.repo_id == repo_id)
    if agent_provider:
        statement = statement.where(AgentSession.agent_runtime == agent_provider)
    total = int((await db.execute(select(func.count()).select_from(statement.subquery()))).scalar() or 0)
    sessions = (await db.execute(statement.order_by(desc(AgentSession.created_at)).limit(limit).offset(offset))).scalars().all()
    repos = await _repos_by_id(db, [session.repo_id for session in sessions])
    skills = await _session_skill_map(db, sessions)
    items = [session_view(session, repos.get(session.repo_id), skills) for session in sessions]
    if risk_band_filter:
        items = [item for item in items if item["risk_band"] == risk_band_filter]
    return {"sessions": items, "total": total, "rollup": _rollup(items)}


@router.get("/activity/sessions/rollup")
async def activity_sessions_rollup(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, Any]:
    await _require_v8(org_id, current_org_id, db)
    sessions = (await db.execute(select(AgentSession).where(AgentSession.org_id == org_id).order_by(desc(AgentSession.created_at)).limit(500))).scalars().all()
    repos = await _repos_by_id(db, [session.repo_id for session in sessions])
    skills = await _session_skill_map(db, sessions)
    items = [session_view(session, repos.get(session.repo_id), skills) for session in sessions]
    return _rollup(items)


@router.get("/activity/sessions/{session_id}")
async def activity_session_detail(
    org_id: str,
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, Any]:
    await _require_v8(org_id, current_org_id, db)
    session = (
        await db.execute(
            select(AgentSession).where(
                AgentSession.org_id == org_id,
                or_(AgentSession.id == session_id, AgentSession.session_id == session_id),
            )
        )
    ).scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    repo = await _repo_in_org(db, org_id, session.repo_id)
    skills = await _session_skill_map(db, [session])
    return {"session": session_view(session, repo, skills)}


@router.get("/repos/{repo_id}/activity/sessions/{session_id}/replay")
async def activity_replay(
    org_id: str,
    repo_id: str,
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, Any]:
    await _require_v8(org_id, current_org_id, db)
    repo = await _repo_in_org(db, org_id, repo_id)
    session = (
        await db.execute(
            select(AgentSession).where(
                AgentSession.repo_id == repo_id,
                or_(AgentSession.id == session_id, AgentSession.session_id == session_id),
            )
        )
    ).scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    payload = session_view(session, repo, await _session_skill_map(db, [session]))
    timeline = replay_timeline(session, repo)
    return {"session": payload, "timeline": timeline, "export_html": standalone_replay_html(payload, timeline)}


@router.get("/repos/{repo_id}/activity/heatmap")
async def activity_heatmap(
    org_id: str,
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    hours: int = Query(default=24 * 7, ge=1, le=24 * 90),
    include_deny_rate: bool = False,
) -> dict[str, Any]:
    await _require_v8(org_id, current_org_id, db)
    if repo_id not in {"all", "_all"}:
        await _repo_in_org(db, org_id, repo_id)
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=hours)
    statement = (
        select(
            Repo.id.label("repo_id"),
            Repo.name.label("repo_name"),
            func.extract("hour", SkillUsageEvent.loaded_at).label("hour"),
            func.count(SkillUsageEvent.id).label("action_count"),
        )
        .join(SkillUsageEvent, SkillUsageEvent.repo_id == Repo.id)
        .where(Repo.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff)
        .group_by(Repo.id, Repo.name, "hour")
        .order_by(Repo.name, "hour")
    )
    if repo_id not in {"all", "_all"}:
        statement = statement.where(Repo.id == repo_id)
    result = await db.execute(statement)
    cells = [
        {
            "repo_id": str(row.repo_id),
            "repo_name": str(row.repo_name),
            "hour": int(row.hour),
            "action_count": int(row.action_count),
            "deny_rate": 0.0 if include_deny_rate else None,
        }
        for row in result.all()
    ]
    max_count = max([cell["action_count"] for cell in cells], default=0)
    for cell in cells:
        cell["risk_band"] = risk_band(min(100, int(cell["action_count"]) * 5))
    return {"repo_id": repo_id, "hours": hours, "max_action_count": max_count, "cells": cells}
