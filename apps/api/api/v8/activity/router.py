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
    session_feed_event_view,
    standalone_replay_html,
    replay_timeline,
)
from packages.db.database import get_db
from packages.db.models import AgentSession, AuditEvent, Org, Repo, Skill, SkillUsageEvent


router = APIRouter(
    prefix="/v8/orgs/{org_id}",
    tags=["v8-activity"],
    dependencies=[Depends(request_flag_cache)],
)

AGENT_COMPLIANCE_EVENT_TYPES = {
    "agent.compliance",
    "agent_compliance",
    "agent.telemetry",
    "agent_telemetry",
    "coding_agent.compliance",
    "coding_agent.telemetry",
}


def _estimated_cost_usd(model: str | None, input_tokens: int, output_tokens: int) -> float:
    if input_tokens <= 0 and output_tokens <= 0:
        return 0.0
    normalized = str(model or "").lower()
    if "mini" in normalized or "haiku" in normalized or "fast" in normalized:
        input_rate, output_rate = 0.25, 1.25
    elif "opus" in normalized:
        input_rate, output_rate = 15.0, 75.0
    elif "sonnet" in normalized or "claude" in normalized:
        input_rate, output_rate = 3.0, 15.0
    else:
        input_rate, output_rate = 1.25, 10.0
    return round((input_tokens / 1_000_000) * input_rate + (output_tokens / 1_000_000) * output_rate, 6)


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


def _active_feed_filters(
    *,
    hours: int,
    repo_id: str | None,
    skill_id: str | None,
    agent_provider: str | None,
    action_class: str | None,
    outcome: str | None,
    risk_band: str | None,
    repo_sensitivity_tier: str | None,
    user: str | None,
) -> dict[str, int | str]:
    raw: dict[str, int | str | None] = {
        "hours": hours,
        "repo_id": repo_id,
        "skill_id": skill_id,
        "agent_provider": agent_provider,
        "action_class": action_class,
        "outcome": outcome,
        "risk_band": risk_band,
        "repo_sensitivity_tier": repo_sensitivity_tier,
        "user": user,
    }
    return {key: value for key, value in raw.items() if value not in {None, ""}}


def _metadata_value(metadata: object, *keys: str) -> str | None:
    if not isinstance(metadata, dict):
        return None
    for key in keys:
        value = metadata.get(key)
        if value not in {None, ""}:
            return str(value)
    return None


def _metadata_int(metadata: object, *keys: str) -> int:
    if not isinstance(metadata, dict):
        return 0
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str) and value.strip():
            try:
                return int(float(value))
            except ValueError:
                continue
    return 0


def _metadata_float(metadata: object, *keys: str) -> float:
    if not isinstance(metadata, dict):
        return 0.0
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, str) and value.strip():
            try:
                return float(value)
            except ValueError:
                continue
    return 0.0


def _metadata_list(metadata: object, *keys: str) -> list[str]:
    if not isinstance(metadata, dict):
        return []
    values: list[str] = []
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value if item not in {None, ""})
        elif isinstance(value, str) and value.strip():
            values.append(value.strip())
    return values


ACTIVITY_METRIC_KEYS = ("edited_files", "explored_files", "searches", "lists", "commands", "tool_calls", "mcp_tools")
ACTIVITY_DETAIL_KEYS = ("edited_files", "explored_files", "searches", "lists", "commands", "tools")


def _activity_metrics_from_metadata(metadata: object) -> dict[str, int]:
    raw = metadata.get("activity_metrics") if isinstance(metadata, dict) else None
    raw_metrics = raw if isinstance(raw, dict) else {}
    metrics: dict[str, int] = {}
    for key in ACTIVITY_METRIC_KEYS:
        value = raw_metrics.get(key)
        if isinstance(value, bool):
            value = None
        if isinstance(value, int | float):
            metrics[key] = int(value)
        elif isinstance(value, str) and value.strip():
            try:
                metrics[key] = int(float(value))
            except ValueError:
                metrics[key] = _metadata_int(metadata, key)
        else:
            metrics[key] = _metadata_int(metadata, key)
    return metrics


def _activity_details_from_metadata(metadata: object) -> dict[str, list[str]]:
    raw = metadata.get("activity_details") if isinstance(metadata, dict) else None
    raw_details = raw if isinstance(raw, dict) else {}
    details: dict[str, list[str]] = {}
    for key in ACTIVITY_DETAIL_KEYS:
        value = raw_details.get(key)
        if isinstance(value, list):
            details[key] = [str(item) for item in value if item not in {None, ""}]
        else:
            details[key] = _metadata_list(metadata, key)
    return details


def _event_metric_payload(event: AuditEvent) -> dict[str, Any]:
    metadata = event.metadata_json or {}
    input_tokens = _metadata_int(metadata, "tokens_input", "input_tokens", "prompt_tokens")
    output_tokens = _metadata_int(metadata, "tokens_output", "output_tokens", "completion_tokens")
    tokens_total = _metadata_int(metadata, "tokens_total", "total_tokens") or input_tokens + output_tokens
    model = _metadata_value(metadata, "model", "model_name", "model_id")
    explicit_cost = _metadata_float(metadata, "cost_usd", "estimated_cost_usd")
    cost_usd = explicit_cost if explicit_cost > 0 else _estimated_cost_usd(model, input_tokens, output_tokens)
    return {
        "model": model,
        "intelligence_tier": _metadata_value(metadata, "intelligence_tier", "model_tier", "reasoning_tier"),
        "tokens_input": input_tokens,
        "tokens_output": output_tokens,
        "tokens_total": tokens_total,
        "cost_usd": cost_usd,
        "cost_source": _metadata_value(metadata, "cost_source") or ("metadata" if explicit_cost > 0 else "estimated_from_model_tokens"),
        "mcp_tools": _metadata_list(metadata, "mcp_tools"),
        "activity_metrics": _activity_metrics_from_metadata(metadata),
        "activity_details": _activity_details_from_metadata(metadata),
    }


async def _compliance_metrics_by_session(db: AsyncSession, org_id: str, session_ids: Iterable[str]) -> dict[str, dict[str, Any]]:
    ids = {session_id for session_id in session_ids if session_id}
    if not ids:
        return {}
    rows = (
        await db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.org_id == org_id,
                AuditEvent.event_type.in_(sorted(AGENT_COMPLIANCE_EVENT_TYPES)),
                AuditEvent.resource_id.in_(ids),
            )
            .order_by(AuditEvent.created_at)
        )
    ).scalars().all()
    mapped: dict[str, dict[str, Any]] = {}
    for event in rows:
        if not hasattr(event, "metadata_json"):
            continue
        metadata = event.metadata_json or {}
        key = _metadata_value(metadata, "session_id", "agent_session_id", "conversation_id", "thread_id") or event.resource_id
        if not key:
            continue
        metrics = _event_metric_payload(event)
        bucket = mapped.setdefault(
            str(key),
            {"tokens_total": 0, "cost_usd": 0.0, "mcp_tools": set(), "models": Counter(), "model": None, "intelligence_tier": None, "activity_metrics": {metric: 0 for metric in ACTIVITY_METRIC_KEYS}, "activity_details": {detail: [] for detail in ACTIVITY_DETAIL_KEYS}},
        )
        bucket["tokens_total"] = int(bucket["tokens_total"]) + int(metrics["tokens_total"])
        bucket["cost_usd"] = float(bucket["cost_usd"]) + float(metrics["cost_usd"])
        bucket["mcp_tools"].update(metrics["mcp_tools"])
        activity_metrics = metrics.get("activity_metrics")
        if isinstance(activity_metrics, dict):
            for metric in ACTIVITY_METRIC_KEYS:
                bucket["activity_metrics"][metric] = int(bucket["activity_metrics"].get(metric) or 0) + int(activity_metrics.get(metric) or 0)
        activity_details = metrics.get("activity_details")
        if isinstance(activity_details, dict):
            for detail in ACTIVITY_DETAIL_KEYS:
                target = bucket["activity_details"].setdefault(detail, [])
                if isinstance(target, list):
                    for item in activity_details.get(detail) or []:
                        if item not in target:
                            target.append(item)
        if metrics["model"]:
            bucket["models"][str(metrics["model"])] += 1
        if metrics["intelligence_tier"]:
            bucket["intelligence_tier"] = metrics["intelligence_tier"]
    for bucket in mapped.values():
        bucket["model"] = bucket["models"].most_common(1)[0][0] if bucket["models"] else bucket["model"]
        bucket["mcp_tools"] = sorted(bucket["mcp_tools"])
        bucket["cost_usd"] = round(float(bucket["cost_usd"]), 6)
        del bucket["models"]
    return mapped


def _agent_platform_label(value: str) -> str:
    normalized = value.strip().lower().replace("_", "-")
    labels = {
        "codex": "Codex",
        "codex-cli": "Codex",
        "openai-codex": "Codex",
        "claude-code": "Claude Code",
        "claude": "Claude Code",
        "anthropic": "Claude Code",
        "cursor": "Cursor",
        "windsurf": "Windsurf",
        "openai": "OpenAI",
    }
    if normalized in labels:
        return labels[normalized]
    return value.replace("_", " ").replace("-", " ").strip().title() or "Unknown"


def _compliance_activity_item(event: AuditEvent) -> dict[str, Any]:
    metadata = event.metadata_json or {}
    provider = _metadata_value(metadata, "provider", "agent_provider", "source_provider") or event.resource_type or event.event_type
    access_scope = _metadata_value(metadata, "access_scope", "permission_scope", "grant_scope")
    policy_decision = _metadata_value(metadata, "policy_decision", "decision", "outcome")
    severity = str(event.severity or "info").lower()
    risk = 80 if severity == "critical" or access_scope == "full-access" else 55 if severity == "warning" or access_scope else 25
    return {
        "id": event.id,
        "timestamp": event.created_at.isoformat() if event.created_at else None,
        "provider": provider,
        "actor_login": event.actor_login,
        "repo_name": event.repo_name or _metadata_value(metadata, "repo_name", "repo"),
        "model": _metadata_value(metadata, "model", "model_name", "model_id"),
        "intelligence_tier": _metadata_value(metadata, "intelligence_tier", "model_tier", "reasoning_tier"),
        "access_scope": access_scope,
        "policy_decision": policy_decision,
        "source_envelope_hash": _metadata_value(metadata, "source_envelope_hash", "envelope_hash", "event_hash"),
        "summary": event.summary,
        "risk_score": risk,
        "risk_band": risk_band(risk),
    }


def _compliance_session_key(event: AuditEvent) -> str:
    metadata = event.metadata_json or {}
    return (
        _metadata_value(metadata, "session_id", "agent_session_id", "conversation_id", "thread_id")
        or f"event:{event.id}"
    )


def _compliance_sessions(events: Iterable[AuditEvent]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for event in events:
        metadata = event.metadata_json or {}
        session_id = _compliance_session_key(event)
        provider = _metadata_value(metadata, "provider", "agent_provider", "source_provider") or event.resource_type or event.event_type
        access_scope = _metadata_value(metadata, "access_scope", "permission_scope", "grant_scope")
        intelligence_tier = _metadata_value(metadata, "intelligence_tier", "model_tier", "reasoning_tier")
        model = _metadata_value(metadata, "model", "model_name", "model_id")
        source_record_types = _metadata_list(metadata, "source_record_types", "source_record_type")
        risk = 80 if str(event.severity or "").lower() == "critical" or access_scope == "full-access" else 55 if str(event.severity or "").lower() == "warning" or access_scope else 25
        row = grouped.setdefault(
            session_id,
            {
                "session_id": session_id,
                "provider": provider,
                "actor_login": event.actor_login,
                "repo_name": event.repo_name or _metadata_value(metadata, "repo_name", "repo"),
                "model": model,
                "intelligence_tier": intelligence_tier,
                "access_scopes": set(),
                "source_record_types": set(),
                "event_count": 0,
                "tool_calls": 0,
                "mcp_tools": set(),
                "file_targets": set(),
                "policy_decisions": Counter(),
                "tokens_input": 0,
                "tokens_output": 0,
                "cost_usd": 0.0,
                "errors": 0,
                "risk_score": 0,
                "started_at": event.created_at,
                "last_event_at": event.created_at,
            },
        )
        row["event_count"] += 1
        row["risk_score"] = max(int(row["risk_score"]), risk)
        if event.created_at:
            row["started_at"] = min(row["started_at"], event.created_at) if row["started_at"] else event.created_at
            row["last_event_at"] = max(row["last_event_at"], event.created_at) if row["last_event_at"] else event.created_at
        if access_scope:
            row["access_scopes"].add(access_scope)
        for source_record_type in source_record_types:
            row["source_record_types"].add(source_record_type)
        policy_decision = _metadata_value(metadata, "policy_decision", "decision", "outcome")
        if policy_decision:
            row["policy_decisions"][policy_decision] += 1
        row["tool_calls"] += int(metadata.get("tool_calls") or 0) if isinstance(metadata, dict) else 0
        for key, target in (("mcp_tools", "mcp_tools"), ("file_targets", "file_targets")):
            raw = metadata.get(key) if isinstance(metadata, dict) else []
            if isinstance(raw, list):
                row[target].update(str(item) for item in raw if item not in {None, ""})
        metrics = _event_metric_payload(event)
        row["tokens_input"] += int(metrics["tokens_input"])
        row["tokens_output"] += int(metrics["tokens_output"])
        row["cost_usd"] += float(metrics["cost_usd"])
        row["errors"] += int(metadata.get("error_count") or 0) if isinstance(metadata, dict) else 0

    items: list[dict[str, Any]] = []
    for row in grouped.values():
        started = row["started_at"]
        ended = row["last_event_at"]
        duration = int((ended - started).total_seconds() // 60) if started and ended else None
        items.append(
            {
                "session_id": row["session_id"],
                "provider": row["provider"],
                "actor_login": row["actor_login"],
                "repo_name": row["repo_name"],
                "model": row["model"],
                "intelligence_tier": row["intelligence_tier"],
                "access_scopes": sorted(row["access_scopes"]),
                "source_record_types": sorted(row["source_record_types"]),
                "event_count": row["event_count"],
                "tool_calls": row["tool_calls"],
                "mcp_tools": sorted(row["mcp_tools"]),
                "file_targets": sorted(row["file_targets"]),
                "policy_decisions": dict(row["policy_decisions"]),
                "tokens_input": row["tokens_input"],
                "tokens_output": row["tokens_output"],
                "cost_usd": round(float(row["cost_usd"]), 6),
                "errors": row["errors"],
                "risk_score": row["risk_score"],
                "risk_band": risk_band(row["risk_score"]),
                "started_at": started.isoformat() if started else None,
                "last_event_at": ended.isoformat() if ended else None,
                "duration_minutes": duration,
                "content_retention": "metadata-only",
            }
        )
    return sorted(items, key=lambda item: str(item["last_event_at"] or ""), reverse=True)


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
    active_filters = filters or {}
    if active_filters.get("skill_id"):
        statement = statement.where(SkillUsageEvent.skill_id == active_filters["skill_id"])
    if active_filters.get("agent_provider"):
        statement = statement.where(SkillUsageEvent.agent_runtime == active_filters["agent_provider"])
    page_size = min(max(limit * 3, 200), 1000)
    offset = 0
    scanned = 0
    items: list[dict[str, Any]] = []
    while len(items) < limit and scanned < 5000:
        events = (await db.execute(statement.order_by(desc(SkillUsageEvent.loaded_at)).limit(page_size).offset(offset))).scalars().all()
        if not events:
            break
        repos = await _repos_by_id(db, [event.repo_id for event in events])
        skills = await _skills_by_id(db, [event.skill_id for event in events])
        sessions = await _sessions_for_events(db, org_id, events)
        page_items = [
            feed_event_view(
                event,
                repos.get(event.repo_id),
                skills.get(event.skill_id),
                sessions.get((event.repo_id, event.session_id)),
            )
            for event in events
        ]
        items.extend(item for item in page_items if _matches_filters(item, active_filters))
        scanned += len(events)
        if len(events) < page_size:
            break
        offset += page_size

    session_activity_at = func.coalesce(AgentSession.last_artifact_at, AgentSession.session_start, AgentSession.created_at)
    session_statement = select(AgentSession).where(
        AgentSession.org_id == org_id,
        session_activity_at >= cutoff,
    )
    if repo_id:
        session_statement = session_statement.where(AgentSession.repo_id == repo_id)
    if active_filters.get("agent_provider"):
        session_statement = session_statement.where(AgentSession.agent_runtime == active_filters["agent_provider"])
    sessions = (
        await db.execute(session_statement.order_by(desc(session_activity_at)).limit(limit * 2))
    ).scalars().all()
    if sessions:
        repos = await _repos_by_id(db, [session.repo_id for session in sessions])
        skills = await _session_skill_map(db, sessions)
        existing_sessions = {str(item.get("session_db_id") or "") for item in items if item.get("session_db_id")}
        compliance = await _compliance_metrics_by_session(db, org_id, [session.session_id for session in sessions])
        session_items = [
            session_feed_event_view(session, repos.get(session.repo_id), skills, compliance.get(str(session.session_id)))
            for session in sessions
            if str(session.id) not in existing_sessions
        ]
        items.extend(item for item in session_items if _matches_filters(item, active_filters))

    return sorted(items, key=lambda item: str(item.get("timestamp") or ""), reverse=True)[:limit]


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
    return {
        "events": items,
        "total": len(items),
        "filters": _active_feed_filters(
            hours=hours,
            repo_id=repo_id,
            skill_id=skill_id,
            agent_provider=agent_provider,
            action_class=action_class,
            outcome=outcome,
            risk_band=risk_band_filter,
            repo_sensitivity_tier=repo_sensitivity_tier,
            user=user,
        ),
    }


@router.get("/activity/compliance-events")
async def activity_compliance_events(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    provider: str | None = None,
    actor: str | None = None,
    access_scope: str | None = None,
    hours: int = Query(default=24, ge=1, le=24 * 30),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    await _require_v8(org_id, current_org_id, db)
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=hours)
    filters: list[Any] = [
        AuditEvent.org_id == org_id,
        AuditEvent.created_at >= cutoff,
        AuditEvent.event_type.in_(sorted(AGENT_COMPLIANCE_EVENT_TYPES)),
    ]
    if actor:
        filters.append(AuditEvent.actor_login.ilike(f"%{actor}%"))
    rows = (
        await db.execute(
            select(AuditEvent)
            .where(*filters)
            .order_by(desc(AuditEvent.created_at))
            .limit(limit)
        )
    ).scalars().all()
    items = [_compliance_activity_item(event) for event in rows]
    if provider:
        provider_lower = provider.lower()
        items = [item for item in items if str(item["provider"]).lower() == provider_lower]
    if access_scope:
        items = [item for item in items if item["access_scope"] == access_scope]
    return {
        "events": items,
        "total": len(items),
        "content_retention": "metadata-only",
        "filters": {key: value for key, value in {"hours": hours, "provider": provider, "actor": actor, "access_scope": access_scope}.items() if value not in {None, ""}},
    }


@router.get("/activity/compliance-sessions")
async def activity_compliance_sessions(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    provider: str | None = None,
    actor: str | None = None,
    hours: int = Query(default=24, ge=1, le=24 * 30),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    await _require_v8(org_id, current_org_id, db)
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=hours)
    filters: list[Any] = [
        AuditEvent.org_id == org_id,
        AuditEvent.created_at >= cutoff,
        AuditEvent.event_type.in_(sorted(AGENT_COMPLIANCE_EVENT_TYPES)),
    ]
    if actor:
        filters.append(AuditEvent.actor_login.ilike(f"%{actor}%"))
    rows = (
        await db.execute(
            select(AuditEvent)
            .where(*filters)
            .order_by(desc(AuditEvent.created_at))
            .limit(min(max(limit * 5, limit), 1000))
        )
    ).scalars().all()
    sessions = _compliance_sessions(rows)
    if provider:
        provider_lower = provider.lower()
        sessions = [item for item in sessions if str(item["provider"]).lower() == provider_lower]
    sessions = sessions[:limit]
    return {
        "sessions": sessions,
        "total": len(sessions),
        "content_retention": "metadata-only",
        "filters": {key: value for key, value in {"hours": hours, "provider": provider, "actor": actor}.items() if value not in {None, ""}},
    }


@router.get("/activity/feed/stream")
async def activity_feed_stream(
    org_id: str,
    request: Request,
    key: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
    hours: int = Query(default=1, ge=1, le=24 * 30),
    repo_id: str | None = None,
    skill_id: str | None = None,
    agent_provider: str | None = None,
    action_class: str | None = None,
    outcome: str | None = None,
    risk_band_filter: str | None = Query(default=None, alias="risk_band"),
    repo_sensitivity_tier: str | None = None,
    user: str | None = None,
) -> StreamingResponse:
    key_org_id = await _org_from_key(key, db)
    actual_org_id = key_org_id or current_org_id
    await _require_v8(org_id, actual_org_id, db)

    async def generate() -> Any:
        started = datetime.now(UTC)
        sent: set[str] = set()
        while (datetime.now(UTC) - started) < timedelta(minutes=5):
            items = await _feed_items(
                db,
                org_id,
                limit=25,
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
    compliance = await _compliance_metrics_by_session(db, org_id, [session.session_id for session in sessions])
    items = [session_view(session, repos.get(session.repo_id), skills, compliance.get(str(session.session_id))) for session in sessions]
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
    compliance = await _compliance_metrics_by_session(db, org_id, [session.session_id for session in sessions])
    items = [session_view(session, repos.get(session.repo_id), skills, compliance.get(str(session.session_id))) for session in sessions]
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
    compliance = await _compliance_metrics_by_session(db, org_id, [session.session_id])
    return {"session": session_view(session, repo, skills, compliance.get(str(session.session_id)))}


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
    compliance = await _compliance_metrics_by_session(db, org_id, [session.session_id])
    compliance_events = (
        await db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.org_id == org_id,
                AuditEvent.event_type.in_(sorted(AGENT_COMPLIANCE_EVENT_TYPES)),
                or_(
                    AuditEvent.resource_id == session.session_id,
                    AuditEvent.resource_id == session.id,
                ),
            )
            .order_by(AuditEvent.created_at)
        )
    ).scalars().all()
    payload = session_view(session, repo, await _session_skill_map(db, [session]), compliance.get(str(session.session_id)))
    timeline = replay_timeline(session, repo)
    return {
        "session": payload,
        "timeline": timeline,
        "export_html": standalone_replay_html(payload, timeline),
        "compliance_events": [_compliance_activity_item(event) for event in compliance_events],
    }


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
    if repo_id in {"all", "_all"}:
        trend_days = max(1, min(90, round(hours / 24)))
        today = datetime.now(UTC).replace(tzinfo=None).date()
        trend_labels = [(today - timedelta(days=offset)).isoformat() for offset in range(trend_days - 1, -1, -1)]
        trend_label_set = set(trend_labels)
        session_rows = (
            await db.execute(
                select(AgentSession).where(
                    AgentSession.org_id == org_id,
                    or_(AgentSession.session_start >= cutoff, AgentSession.created_at >= cutoff),
                )
            )
        ).scalars().all()
        event_rows = (
            await db.execute(
                select(AuditEvent)
                .where(
                    AuditEvent.org_id == org_id,
                    AuditEvent.event_type.in_(AGENT_COMPLIANCE_EVENT_TYPES),
                    AuditEvent.created_at >= cutoff,
                )
                .order_by(AuditEvent.created_at)
            )
        ).scalars().all()
        platform_buckets: dict[str, dict[str, Any]] = {}
        model_buckets: dict[tuple[str, str], dict[str, Any]] = {}
        model_counts: Counter[str] = Counter()

        def bucket_for(platform: str) -> dict[str, Any]:
            label = _agent_platform_label(platform)
            key = label.lower().replace(" ", "-")
            return platform_buckets.setdefault(
                key,
                {
                    "repo_id": key,
                    "repo_name": label,
                    "cells": defaultdict(lambda: {"action_count": 0, "messages": 0, "tokens_total": 0, "cost_usd": 0.0, "sessions": set(), "models": Counter(), "days": set()}),
                    "sessions": set(),
                    "messages": 0,
                    "tokens_total": 0,
                    "cost_usd": 0.0,
                    "days": set(),
                    "models": Counter(),
                    "trend": {day: {"sessions": set(), "messages": 0, "tokens_total": 0, "cost_usd": 0.0} for day in trend_labels},
                },
            )

        for session in session_rows:
            when = session.session_start or session.created_at
            if not when:
                continue
            platform = str(session.agent_runtime or "unknown")
            bucket = bucket_for(platform)
            session_key = str(session.session_id or session.id)
            messages = int(session.raw_message_count or 0)
            cell = bucket["cells"][int(when.hour)]
            cell["action_count"] += 1
            cell["messages"] += messages
            cell["sessions"].add(session_key)
            cell["days"].add(when.date().isoformat())
            bucket["sessions"].add(session_key)
            bucket["messages"] += messages
            day_label = when.date().isoformat()
            bucket["days"].add(day_label)
            if day_label in trend_label_set:
                trend = bucket["trend"][day_label]
                trend["sessions"].add(session_key)
                trend["messages"] += messages

        for event in event_rows:
            when = event.created_at
            if not when:
                continue
            metadata = event.metadata_json or {}
            provider = _metadata_value(metadata, "provider", "agent_provider", "source_provider") or str(event.resource_type or "unknown")
            source_record_types = [item.lower() for item in _metadata_list(metadata, "source_record_types", "source_record_type")]
            if provider.lower() == "openai" and any("codex" in item for item in source_record_types):
                provider = "codex"
            model = _metadata_value(metadata, "model", "model_name", "model_id")
            session_key = _metadata_value(metadata, "session_id", "agent_session_id", "conversation_id", "thread_id") or event.resource_id or event.id
            metrics = _event_metric_payload(event)
            tokens_total = int(metrics["tokens_total"])
            cost_usd = float(metrics["cost_usd"])
            messages = _metadata_int(metadata, "message_count", "messages", "raw_message_count") or 1
            bucket = bucket_for(provider)
            cell = bucket["cells"][int(when.hour)]
            cell["action_count"] += 1
            cell["messages"] += messages
            cell["tokens_total"] += tokens_total
            cell["cost_usd"] += cost_usd
            cell["sessions"].add(session_key)
            cell["days"].add(when.date().isoformat())
            bucket["sessions"].add(session_key)
            bucket["messages"] += messages
            bucket["tokens_total"] += tokens_total
            bucket["cost_usd"] += cost_usd
            day_label = when.date().isoformat()
            bucket["days"].add(day_label)
            if day_label in trend_label_set:
                trend = bucket["trend"][day_label]
                trend["sessions"].add(session_key)
                trend["messages"] += messages
                trend["tokens_total"] += tokens_total
                trend["cost_usd"] += cost_usd
            if model:
                bucket["models"][model] += 1
                cell["models"][model] += 1
                model_counts[model] += 1
                model_key = (bucket["repo_name"], model)
                model_bucket = model_buckets.setdefault(
                    model_key,
                    {"platform": bucket["repo_name"], "model": model, "tokens_total": 0, "cost_usd": 0.0, "sessions": set(), "messages": 0},
                )
                model_bucket["tokens_total"] += tokens_total
                model_bucket["cost_usd"] += cost_usd
                model_bucket["sessions"].add(session_key)
                model_bucket["messages"] += messages

        cells: list[dict[str, Any]] = []
        for bucket in platform_buckets.values():
            favorite_model = bucket["models"].most_common(1)[0][0] if bucket["models"] else None
            for hour, cell in bucket["cells"].items():
                actions = int(cell["action_count"])
                cells.append(
                    {
                        "repo_id": bucket["repo_id"],
                        "repo_name": bucket["repo_name"],
                        "hour": int(hour),
                        "action_count": actions,
                        "messages": int(cell["messages"]),
                        "sessions": len(cell["sessions"]),
                        "tokens_total": int(cell["tokens_total"]),
                        "cost_usd": round(float(cell["cost_usd"]), 6),
                        "active_days": len(cell["days"]),
                        "favorite_model": cell["models"].most_common(1)[0][0] if cell["models"] else favorite_model,
                        "deny_rate": 0.0 if include_deny_rate else None,
                        "risk_band": risk_band(min(100, actions * 5)),
                    }
                )
        max_count = max([cell["action_count"] for cell in cells], default=0)
        peak = max(cells, key=lambda cell: (cell["tokens_total"], cell["action_count"]), default=None)
        total_sessions = len({session for bucket in platform_buckets.values() for session in bucket["sessions"]})
        active_trend_days = {
            day
            for bucket in platform_buckets.values()
            for day, values in bucket["trend"].items()
            if len(values["sessions"]) or int(values["messages"]) or int(values["tokens_total"])
        }
        return {
            "repo_id": repo_id,
            "hours": hours,
            "max_action_count": max_count,
            "group_by": "platform",
            "summary": {
                "sessions": total_sessions,
                "messages": sum(int(bucket["messages"]) for bucket in platform_buckets.values()),
                "tokens_total": sum(int(bucket["tokens_total"]) for bucket in platform_buckets.values()),
                "cost_usd": round(sum(float(bucket["cost_usd"]) for bucket in platform_buckets.values()), 6),
                "active_days": len(active_trend_days),
                "peak_hour": int(peak["hour"]) if peak else None,
                "favorite_model": model_counts.most_common(1)[0][0] if model_counts else None,
                "platforms": len(platform_buckets),
            },
            "models": [
                {
                    "platform": str(values["platform"]),
                    "model": str(values["model"]),
                    "tokens_total": int(values["tokens_total"]),
                    "cost_usd": round(float(values["cost_usd"]), 6),
                    "sessions": len(values["sessions"]),
                    "messages": int(values["messages"]),
                }
                for values in sorted(model_buckets.values(), key=lambda item: (-int(item["tokens_total"]), str(item["platform"]), str(item["model"])))
            ],
            "trend": [
                {
                    "platform": str(bucket["repo_name"]),
                    "date": day,
                    "sessions": len(values["sessions"]),
                    "messages": int(values["messages"]),
                    "tokens_total": int(values["tokens_total"]),
                    "cost_usd": round(float(values["cost_usd"]), 6),
                }
                for bucket in sorted(platform_buckets.values(), key=lambda item: str(item["repo_name"]))
                for day, values in bucket["trend"].items()
            ],
            "cells": cells,
        }
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
