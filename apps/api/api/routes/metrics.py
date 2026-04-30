from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.database import AsyncSessionLocal
from packages.db.models import AgentSession, AnalysisRun, LoginEvent, Org, PullRequest, Repo, Skill


router = APIRouter(tags=["metrics"])

_CACHE_TTL_SECONDS = 60.0
_started_at = time.monotonic()
_cached_metrics: tuple[float, dict[str, object]] | None = None

METRIC_HELP = {
    "skillayer_orgs_total": "Total number of orgs",
    "skillayer_orgs_active_30d": "Number of orgs with activity in the last 30 days",
    "skillayer_skills_total": "Total number of skills",
    "skillayer_agent_sessions_total": "Total number of agent sessions",
    "skillayer_agent_sessions_7d": "Agent sessions in the last 7 days",
    "skillayer_pull_requests_total": "Total number of pull requests",
    "skillayer_analysis_runs_total": "Total number of analysis runs",
    "skillayer_login_events_total": "Total login events",
    "skillayer_login_events_7d": "Login events in the last 7 days",
    "skillayer_users_unique_total": "Total unique users seen in login events",
}


def _iso_z(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


def _cached_response(now: float) -> dict[str, object] | None:
    if _cached_metrics is None:
        return None
    cached_at, payload = _cached_metrics
    if now - cached_at > _CACHE_TTL_SECONDS:
        return None
    updated = dict(payload)
    updated["uptime_seconds"] = int(now - _started_at)
    return updated


async def _collect_legacy_metrics(db: object, now: float) -> dict[str, object]:
    total_analysis_runs = (await db.execute(select(func.count(AnalysisRun.id)))).scalar_one()
    total_skills = (await db.execute(select(func.count(Skill.id)))).scalar_one()
    total_orgs = (await db.execute(select(func.count(Org.id)))).scalar_one()
    total_repos = (await db.execute(select(func.count(Repo.id)))).scalar_one()
    avg_score = (
        await db.execute(
            select(func.avg(AnalysisRun.score_total)).where(
                AnalysisRun.status == "complete",
                AnalysisRun.score_total.is_not(None),
            )
        )
    ).scalar_one()
    last_run_at = (
        await db.execute(select(AnalysisRun.created_at).order_by(desc(AnalysisRun.created_at)).limit(1))
    ).scalar_one_or_none()
    return {
        "uptime_seconds": int(now - _started_at),
        "total_analysis_runs": int(total_analysis_runs or 0),
        "total_skills": int(total_skills or 0),
        "total_orgs": int(total_orgs or 0),
        "total_repos": int(total_repos or 0),
        "avg_score": float(avg_score) if avg_score is not None else None,
        "last_run_at": _iso_z(last_run_at),
    }


async def _collect_self_hosted_metrics(db: AsyncSession, legacy: dict[str, object]) -> dict[str, int]:
    now = datetime.utcnow()
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)
    repo_org_rows = (await db.execute(select(Repo.id, Repo.org_id))).all()
    repo_to_org = {repo_id: org_id for repo_id, org_id in repo_org_rows}
    active_orgs = set(
        (await db.execute(select(AgentSession.org_id).where(AgentSession.session_start >= cutoff_30d))).scalars().all()
    )
    active_run_repo_ids = (
        await db.execute(select(AnalysisRun.repo_id).where(AnalysisRun.created_at >= cutoff_30d))
    ).scalars().all()
    active_orgs.update(repo_to_org.get(repo_id) for repo_id in active_run_repo_ids if repo_to_org.get(repo_id))
    return {
        "skillayer_orgs_total": int(legacy["total_orgs"] or 0),
        "skillayer_orgs_active_30d": len(active_orgs),
        "skillayer_skills_total": int(legacy["total_skills"] or 0),
        "skillayer_agent_sessions_total": int((await db.execute(select(func.count(AgentSession.id)))).scalar_one() or 0),
        "skillayer_agent_sessions_7d": int(
            (await db.execute(select(func.count(AgentSession.id)).where(AgentSession.session_start >= cutoff_7d))).scalar_one() or 0
        ),
        "skillayer_pull_requests_total": int((await db.execute(select(func.count(PullRequest.id)))).scalar_one() or 0),
        "skillayer_analysis_runs_total": int(legacy["total_analysis_runs"] or 0),
        "skillayer_login_events_total": int((await db.execute(select(func.count(LoginEvent.id)))).scalar_one() or 0),
        "skillayer_login_events_7d": int(
            (await db.execute(select(func.count(LoginEvent.id)).where(LoginEvent.created_at >= cutoff_7d))).scalar_one() or 0
        ),
        "skillayer_users_unique_total": int(
            (await db.execute(select(func.count(func.distinct(LoginEvent.user_login))))).scalar_one() or 0
        ),
    }


async def _collect_metrics(now: float) -> dict[str, object]:
    async with AsyncSessionLocal() as db:
        legacy = await _collect_legacy_metrics(db, now)
        if isinstance(db, AsyncSession):
            metrics = await _collect_self_hosted_metrics(db, legacy)
        else:
            metrics = {
                "skillayer_orgs_total": int(legacy["total_orgs"] or 0),
                "skillayer_orgs_active_30d": 0,
                "skillayer_skills_total": int(legacy["total_skills"] or 0),
                "skillayer_agent_sessions_total": 0,
                "skillayer_agent_sessions_7d": 0,
                "skillayer_pull_requests_total": 0,
                "skillayer_analysis_runs_total": int(legacy["total_analysis_runs"] or 0),
                "skillayer_login_events_total": 0,
                "skillayer_login_events_7d": 0,
                "skillayer_users_unique_total": 0,
            }
        return {
            **legacy,
            "instance": os.getenv("SKILLAYER_INSTANCE", "cloud"),
            "version": os.getenv("SKILLAYER_VERSION", "1.0.0"),
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": metrics,
        }


def _prometheus(metrics: dict[str, int]) -> str:
    lines: list[str] = []
    for key, value in metrics.items():
        lines.append(f"# HELP {key} {METRIC_HELP[key]}")
        lines.append(f"# TYPE {key} gauge")
        lines.append(f"{key} {value}")
    return "\n".join(lines) + "\n"


@router.get("/metrics", response_model=None)
async def get_metrics(request: Request) -> JSONResponse | PlainTextResponse:
    global _cached_metrics

    now = time.monotonic()
    payload = _cached_response(now)
    if payload is None:
        try:
            payload = await _collect_metrics(now)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail={"detail": "Unable to load metrics", "code": "METRICS_UNAVAILABLE"},
            ) from exc
        _cached_metrics = (now, payload)

    accept = request.headers.get("accept", "")
    if "text/plain" in accept:
        return PlainTextResponse(_prometheus(payload["metrics"]), media_type="text/plain; version=0.0.4")
    return JSONResponse(payload)
