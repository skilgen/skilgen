from __future__ import annotations

import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import func, select

from packages.db.database import AsyncSessionLocal
from packages.db.models import AgentSession, AnalysisRun, LoginEvent, Org, PullRequest, Repo, Skill


router = APIRouter(tags=["metrics"])

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


async def _collect_metrics() -> dict[str, int]:
    now = datetime.utcnow()
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)
    async with AsyncSessionLocal() as db:
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
            "skillayer_orgs_total": int((await db.execute(select(func.count(Org.id)))).scalar_one() or 0),
            "skillayer_orgs_active_30d": len(active_orgs),
            "skillayer_skills_total": int((await db.execute(select(func.count(Skill.id)))).scalar_one() or 0),
            "skillayer_agent_sessions_total": int((await db.execute(select(func.count(AgentSession.id)))).scalar_one() or 0),
            "skillayer_agent_sessions_7d": int((await db.execute(select(func.count(AgentSession.id)).where(AgentSession.session_start >= cutoff_7d))).scalar_one() or 0),
            "skillayer_pull_requests_total": int((await db.execute(select(func.count(PullRequest.id)))).scalar_one() or 0),
            "skillayer_analysis_runs_total": int((await db.execute(select(func.count(AnalysisRun.id)))).scalar_one() or 0),
            "skillayer_login_events_total": int((await db.execute(select(func.count(LoginEvent.id)))).scalar_one() or 0),
            "skillayer_login_events_7d": int((await db.execute(select(func.count(LoginEvent.id)).where(LoginEvent.created_at >= cutoff_7d))).scalar_one() or 0),
            "skillayer_users_unique_total": int((await db.execute(select(func.count(func.distinct(LoginEvent.user_login))))).scalar_one() or 0),
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
    metrics = await _collect_metrics()
    accept = request.headers.get("accept", "")
    if "text/plain" in accept:
        return PlainTextResponse(_prometheus(metrics), media_type="text/plain; version=0.0.4")
    return JSONResponse(
        {
            "instance": os.getenv("SKILLAYER_INSTANCE", "cloud"),
            "version": os.getenv("SKILLAYER_VERSION", "1.0.0"),
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": metrics,
        }
    )
