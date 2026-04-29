from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.services.llm import LLMCallError, LLMNotConfiguredError, call_llm
from packages.db.models import AgentSession, AuditEvent, Org, PRAttribution, PullRequest, Repo, Skill

SKILLQL_SYSTEM_PROMPT = """You are SkillQL, a planner for Skillayer analytics queries.
Return ONLY a JSON object. No markdown, no prose.

The object must use this schema:
{
  "intent": "short plain-English intent",
  "data_sources": ["skills" | "agent_sessions" | "pull_requests" | "pr_attributions" | "audit_events"],
  "filters": {
    "time_window_days": number | null,
    "agent_runtime": string | null,
    "risk_tier": "green" | "yellow" | "red" | null,
    "engineer_login": string | null,
    "skill_category": string | null,
    "event_type": string | null
  },
  "group_by": string | null,
  "sort_by": string | null,
  "limit": number,
  "result_format": "table" | "number" | "list" | "timeline"
}

Available data sources and fields:
- skills(domain,skill_category,score_total,load_count_30d,last_loaded_at,updated_at)
- agent_sessions(engineer_login,agent_runtime,session_start,files_touched,skills_loaded,outcome)
- pull_requests(author_login,state,opened_at,merged_at,additions,deletions)
- pr_attributions(primary_agent,confidence,skills_loaded,skills_violated,risk_score,risk_tier)
- audit_events(actor_login,event_type,severity,description,created_at)

Use only these data sources and filters. Prefer the smallest set of data_sources that can answer the question."""

FOLLOWUP_SYSTEM_PROMPT = """Return ONLY a JSON array of exactly 3 short follow-up questions. No markdown, no prose."""

VALID_DATA_SOURCES = {"skills", "agent_sessions", "pull_requests", "pr_attributions", "audit_events"}
VALID_RESULT_FORMATS = {"table", "number", "list", "timeline"}
FILTER_KEYS = {"time_window_days", "agent_runtime", "risk_tier", "engineer_login", "skill_category", "event_type"}


class SkillQLParseError(Exception):
    """Raised when the LLM cannot produce a usable SkillQL plan."""


def _extract_json(text: str) -> Any:
    cleaned = text.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise SkillQLParseError("SkillQL could not parse the query plan. Try a more specific question.") from exc


def _parse_plan(text: str) -> dict[str, Any]:
    payload = _extract_json(text)
    if not isinstance(payload, dict):
        raise SkillQLParseError("SkillQL returned an invalid query plan.")

    sources = payload.get("data_sources")
    if not isinstance(sources, list):
        raise SkillQLParseError("SkillQL did not choose a data source.")
    data_sources = [str(source) for source in sources if str(source) in VALID_DATA_SOURCES]
    if not data_sources:
        raise SkillQLParseError("SkillQL did not choose a supported data source.")

    filters = payload.get("filters") if isinstance(payload.get("filters"), dict) else {}
    safe_filters = {key: filters.get(key) for key in FILTER_KEYS}
    result_format = str(payload.get("result_format") or "table")
    if result_format not in VALID_RESULT_FORMATS:
        result_format = "table"

    try:
        limit = int(payload.get("limit") or 50)
    except (TypeError, ValueError):
        limit = 50

    return {
        "intent": str(payload.get("intent") or "Answer the SkillQL question"),
        "data_sources": data_sources,
        "filters": safe_filters,
        "group_by": str(payload["group_by"]) if payload.get("group_by") else None,
        "sort_by": str(payload["sort_by"]) if payload.get("sort_by") else None,
        "limit": max(1, min(limit, 200)),
        "result_format": result_format,
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (list, dict, str, int, float, bool)) or value is None:
        return value
    return str(value)


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_filter(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _time_cutoff(filters: dict[str, Any]) -> datetime | None:
    try:
        days = int(filters.get("time_window_days") or 0)
    except (TypeError, ValueError):
        return None
    if days <= 0:
        return None
    return datetime.utcnow() - timedelta(days=days)


def _after_cutoff(value: datetime | None, cutoff: datetime | None) -> bool:
    if cutoff is None:
        return True
    if value is None:
        return False
    comparable = value.replace(tzinfo=None) if value.tzinfo else value
    return comparable >= cutoff


def _matches(row: dict[str, Any], filters: dict[str, Any], date_key: str | None) -> bool:
    agent_runtime = _string_filter(filters.get("agent_runtime"))
    if agent_runtime and str(row.get("agent_runtime") or row.get("primary_agent") or "").lower() != agent_runtime.lower():
        return False
    risk_tier = _string_filter(filters.get("risk_tier"))
    if risk_tier and str(row.get("risk_tier") or "").lower() != risk_tier.lower():
        return False
    engineer_login = _string_filter(filters.get("engineer_login"))
    if engineer_login and str(row.get("engineer_login") or row.get("author_login") or row.get("actor_login") or "").lower() != engineer_login.lower():
        return False
    skill_category = _string_filter(filters.get("skill_category"))
    if skill_category and str(row.get("skill_category") or "").lower() != skill_category.lower():
        return False
    event_type = _string_filter(filters.get("event_type"))
    if event_type and str(row.get("event_type") or "").lower() != event_type.lower():
        return False
    if date_key:
        raw = row.get(f"_{date_key}")
        if not _after_cutoff(raw if isinstance(raw, datetime) else None, _time_cutoff(filters)):
            return False
    return True


def _sort_rows(rows: list[dict[str, Any]], sort_by: str | None) -> list[dict[str, Any]]:
    if not sort_by or not rows or sort_by not in rows[0]:
        return rows
    return sorted(rows, key=lambda row: (row.get(sort_by) is None, row.get(sort_by)), reverse=True)


def _limit_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return rows[: max(1, min(limit, 200))]


def _group_rows(rows: list[dict[str, Any]], group_by: str | None, limit: int) -> tuple[list[str], list[dict[str, Any]]] | None:
    if not group_by or not rows or group_by not in rows[0]:
        return None
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(group_by)
        key = ", ".join(str(item) for item in value) if isinstance(value, list) else str(value or "unknown")
        counts[key] = counts.get(key, 0) + 1
    grouped = [{"group": key, "count": count} for key, count in counts.items()]
    grouped.sort(key=lambda row: (-int(row["count"]), str(row["group"])))
    return ["group", "count"], _limit_rows(grouped, limit)


async def _repo_ids(org_id: str, db: AsyncSession) -> list[str]:
    repos = (await db.execute(select(Repo).where(Repo.org_id == org_id))).scalars().all()
    return [repo.id for repo in repos]


async def _skill_rows(org_id: str, db: AsyncSession, filters: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    result = await db.execute(select(Skill).join(Repo).where(Repo.org_id == org_id))
    rows: list[dict[str, Any]] = []
    for skill in result.scalars().all():
        updated_at = getattr(skill, "updated_at", None) or getattr(skill, "created_at", None)
        row = {
            "domain": skill.domain,
            "skill_category": skill.skill_category,
            "score_total": skill.score_total,
            "load_count_30d": skill.load_count_30d,
            "last_loaded_at": _jsonable(skill.last_loaded_at),
            "updated_at": _jsonable(updated_at),
            "_updated_at": updated_at,
        }
        if _matches(row, filters, "updated_at"):
            rows.append(row)
    return _limit_rows(rows, limit)


async def _session_rows(repo_ids: list[str], db: AsyncSession, filters: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    if not repo_ids:
        return []
    result = await db.execute(select(AgentSession).where(AgentSession.repo_id.in_(repo_ids)))
    rows: list[dict[str, Any]] = []
    for session in result.scalars().all():
        row = {
            "engineer_login": session.engineer_login,
            "agent_runtime": session.agent_runtime,
            "session_start": _jsonable(session.session_start),
            "files_touched": _list(session.files_touched),
            "skills_loaded": _list(session.skills_loaded),
            "outcome": session.outcome,
            "_session_start": session.session_start,
        }
        if _matches(row, filters, "session_start"):
            rows.append(row)
    return _limit_rows(rows, limit)


async def _pr_rows(repo_ids: list[str], db: AsyncSession, filters: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    if not repo_ids:
        return []
    result = await db.execute(
        select(PullRequest, PRAttribution)
        .join(PRAttribution, PRAttribution.pr_id == PullRequest.id, isouter=True)
        .where(PullRequest.repo_id.in_(repo_ids))
    )
    rows: list[dict[str, Any]] = []
    for item in result.all():
        pr = item[0] if isinstance(item, tuple) else getattr(item, "PullRequest", None)
        attr = item[1] if isinstance(item, tuple) and len(item) > 1 else getattr(item, "PRAttribution", None)
        if pr is None:
            continue
        row = {
            "author_login": pr.author_login,
            "state": pr.state,
            "opened_at": _jsonable(pr.opened_at),
            "merged_at": _jsonable(pr.merged_at),
            "additions": pr.additions,
            "deletions": pr.deletions,
            "primary_agent": attr.primary_agent if attr else None,
            "agent_runtime": attr.primary_agent if attr else None,
            "confidence": attr.confidence if attr else None,
            "skills_loaded": _list(attr.skills_loaded if attr else []),
            "skills_violated": _list(attr.skills_violated if attr else []),
            "risk_score": attr.risk_score if attr else None,
            "risk_tier": attr.risk_tier if attr else None,
            "_opened_at": pr.opened_at,
        }
        if _matches(row, filters, "opened_at"):
            rows.append(row)
    return _limit_rows(rows, limit)


async def _audit_rows(org_id: str, db: AsyncSession, filters: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    result = await db.execute(select(AuditEvent).where(AuditEvent.org_id == org_id))
    rows: list[dict[str, Any]] = []
    for event in result.scalars().all():
        row = {
            "actor_login": event.actor_login,
            "event_type": event.event_type,
            "severity": event.severity,
            "description": event.summary,
            "created_at": _jsonable(event.created_at),
            "_created_at": event.created_at,
        }
        if _matches(row, filters, "created_at"):
            rows.append(row)
    return _limit_rows(rows, limit)


def _columns(rows: list[dict[str, Any]]) -> list[str]:
    ordered: list[str] = []
    for row in rows:
        for key in row:
            if key.startswith("_") or key in ordered:
                continue
            ordered.append(key)
    return ordered


def _public_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: _jsonable(value) for key, value in row.items() if not key.startswith("_")} for row in rows]


async def _suggest_followups(org_settings: dict[str, Any], query: str, rows: list[dict[str, Any]]) -> list[str]:
    sample = _public_rows(rows[:10])
    try:
        response = await call_llm(
            org_settings,
            FOLLOWUP_SYSTEM_PROMPT,
            json.dumps({"question": query, "results": sample}, default=str),
            max_tokens=256,
        )
        parsed = _extract_json(response)
        if isinstance(parsed, list):
            followups = [str(item).strip() for item in parsed if str(item).strip()]
            if followups:
                return followups[:3]
    except (LLMCallError, LLMNotConfiguredError, SkillQLParseError):
        pass
    return [
        "Which agents have the highest risk?",
        "Show me stale skills with recent usage.",
        "Which developers have the most violations?",
    ]


async def execute_skillql(query: str, org_id: str, db: AsyncSession) -> dict[str, Any]:
    org = await db.get(Org, org_id)
    org_settings = dict(org.settings or {}) if org is not None and isinstance(org.settings, dict) else {}
    plan_response = await call_llm(org_settings, SKILLQL_SYSTEM_PROMPT, query, max_tokens=768)
    plan = _parse_plan(plan_response)

    limit = int(plan["limit"])
    filters = plan["filters"]
    sources = list(dict.fromkeys(plan["data_sources"]))
    needs_repos = any(source in {"agent_sessions", "pull_requests", "pr_attributions"} for source in sources)
    repo_ids = await _repo_ids(org_id, db) if needs_repos else []

    rows: list[dict[str, Any]] = []
    pr_rows_loaded = False
    for source in sources:
        if source == "skills":
            rows.extend(await _skill_rows(org_id, db, filters, limit))
        elif source == "agent_sessions":
            rows.extend(await _session_rows(repo_ids, db, filters, limit))
        elif source in {"pull_requests", "pr_attributions"} and not pr_rows_loaded:
            rows.extend(await _pr_rows(repo_ids, db, filters, limit))
            pr_rows_loaded = True
        elif source == "audit_events":
            rows.extend(await _audit_rows(org_id, db, filters, limit))

    grouped = _group_rows(rows, plan.get("group_by"), limit)
    if grouped:
        columns, final_rows = grouped
    else:
        sorted_rows = _sort_rows(rows, plan.get("sort_by"))
        final_rows = _public_rows(_limit_rows(sorted_rows, limit))
        columns = _columns(final_rows)

    if plan["result_format"] == "number":
        columns = ["count"]
        final_rows = [{"count": len(rows)}]

    followups = await _suggest_followups(org_settings, query, final_rows)
    return {
        "query": query,
        "intent": plan["intent"],
        "result_format": plan["result_format"],
        "columns": columns,
        "rows": final_rows,
        "row_count": len(final_rows),
        "data_sources": sources,
        "suggested_followups": followups,
    }
