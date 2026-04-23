from __future__ import annotations

from datetime import datetime, timezone
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.database import AsyncSessionLocal
from packages.db.models import AnalysisRun, Org, Repo, Skill


router = APIRouter(tags=["metrics"])

_CACHE_TTL_SECONDS = 60.0
_started_at = time.monotonic()
_cached_metrics: tuple[float, "MetricsResponse"] | None = None


class MetricsResponse(BaseModel):
    """Unauthenticated platform metrics payload for uptime and data volume checks."""

    uptime_seconds: int
    total_analysis_runs: int
    total_skills: int
    total_orgs: int
    total_repos: int
    avg_score: float | None
    last_run_at: datetime | None


def _cached_response(now: float) -> MetricsResponse | None:
    """Return the cached metrics response while it remains inside the TTL."""
    if _cached_metrics is None:
        return None
    cached_at, payload = _cached_metrics
    if now - cached_at <= _CACHE_TTL_SECONDS:
        return payload.model_copy(update={"uptime_seconds": int(now - _started_at)})
    return None


async def _collect_metrics(db: AsyncSession, now: float) -> MetricsResponse:
    """Collect metrics from the database and normalize values for the API response."""
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
    payload = MetricsResponse(
        uptime_seconds=int(now - _started_at),
        total_analysis_runs=int(total_analysis_runs or 0),
        total_skills=int(total_skills or 0),
        total_orgs=int(total_orgs or 0),
        total_repos=int(total_repos or 0),
        avg_score=float(avg_score) if avg_score is not None else None,
        last_run_at=last_run_at.replace(tzinfo=timezone.utc) if last_run_at and last_run_at.tzinfo is None else last_run_at,
    )
    return payload


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """Return public service metrics with a short TTL to avoid repeated COUNT queries."""
    global _cached_metrics

    now = time.monotonic()
    cached = _cached_response(now)
    if cached is not None:
        return cached

    try:
        async with AsyncSessionLocal() as db:
            payload = await _collect_metrics(db, now)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={"detail": "Unable to load metrics", "code": "METRICS_UNAVAILABLE"},
        ) from exc

    _cached_metrics = (now, payload)
    return payload
