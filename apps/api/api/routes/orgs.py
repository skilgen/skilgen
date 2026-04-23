from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import AnalysisRun, Org, Repo, ScoreHistory, Skill
from packages.db.schemas import OrgResponse, RepoResponse, ScoreResponse


router = APIRouter(prefix="/orgs", tags=["orgs"])


def _last_30_score_dates() -> list[str]:
    """Return the last 30 UTC score dates in chronological order."""
    today = datetime.now(UTC).date()
    return [(today - timedelta(days=offset)).isoformat() for offset in range(29, -1, -1)]



def _score_response(row: object) -> ScoreResponse | None:
    if row is None:
        return None
    total = getattr(row, "score_total", None)
    if total is None:
        return None
    return ScoreResponse(
        total=int(total or 0),
        groundedness=int(getattr(row, "score_groundedness", 0) or 0),
        coverage=int(getattr(row, "score_coverage", 0) or 0),
        freshness=int(getattr(row, "score_freshness", 0) or 0),
        structure=int(getattr(row, "score_structure", 0) or 0),
    )


async def _repo_response(db: AsyncSession, repo: Repo) -> RepoResponse:
    latest_run = (
        await db.execute(
            select(AnalysisRun)
            .where(AnalysisRun.repo_id == repo.id, AnalysisRun.status == "complete")
            .order_by(desc(AnalysisRun.created_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    latest_history = (
        await db.execute(
            select(ScoreHistory)
            .where(ScoreHistory.repo_id == repo.id)
            .order_by(desc(ScoreHistory.recorded_at))
            .limit(2)
        )
    ).scalars().all()
    skill_count = (
        await db.execute(select(func.count(Skill.id)).where(Skill.repo_id == repo.id))
    ).scalar_one()
    delta = None
    if len(latest_history) >= 2:
        delta = int(latest_history[0].score_total - latest_history[1].score_total)
    return RepoResponse(
        id=repo.id,
        full_name=repo.full_name,
        name=repo.name,
        installation_id=repo.github_installation_id,
        language=repo.language,
        is_monorepo=repo.is_monorepo,
        last_analysed_at=repo.last_analysed_at,
        score=_score_response(latest_run or (latest_history[0] if latest_history else None)),
        score_delta=delta,
        skill_count=int(latest_run.skill_count or 0) if latest_run else int(skill_count or 0),
    )


def _assert_org_scope(requested_org_id: str, current_org_id: str) -> None:
    if requested_org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/bootstrap")
async def bootstrap_org(
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    # TODO: remove before GA. This bootstraps the dashboard while WorkOS org-token mapping is verified.
    result = await db.execute(select(Org).limit(1))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="No org")
    return {
        "id": org.id,
        "login": org.login,
        "name": org.name,
        "plan": org.plan,
    }


@router.get("/{org_id}", response_model=OrgResponse)
async def get_org(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgResponse:
    _assert_org_scope(org_id, current_org_id)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    repo_count = (await db.execute(select(func.count(Repo.id)).where(Repo.org_id == org_id))).scalar_one()
    avg_score = (
        await db.execute(
            select(func.avg(ScoreHistory.score_total))
            .join(Repo, Repo.id == ScoreHistory.repo_id)
            .where(Repo.org_id == org_id)
        )
    ).scalar_one()
    return OrgResponse(
        id=org.id,
        login=org.login,
        name=org.name,
        plan=org.plan,
        repo_count=int(repo_count or 0),
        avg_score=float(avg_score) if avg_score is not None else None,
    )


@router.get("/{org_id}/repos", response_model=list[RepoResponse])
async def list_org_repos(
    org_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: str = "",
    db: AsyncSession = Depends(get_db),
) -> list[RepoResponse]:
    query = select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True))
    if search:
        query = query.where(Repo.full_name.ilike(f"%{search}%"))
    repos = (await db.execute(query.order_by(Repo.full_name).offset(offset).limit(limit))).scalars().all()
    repo_list = [await _repo_response(db, repo) for repo in repos]
    return sorted(repo_list, key=lambda repo: repo.score.total if repo.score else -1, reverse=True)


@router.get("/{org_id}/stats")
async def get_org_stats(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    repo_count_result = await db.execute(
        select(func.count(Repo.id)).where(Repo.org_id == org_id, Repo.is_active.is_(True))
    )
    repo_count = repo_count_result.scalar() or 0

    avg_score_result = await db.execute(
        select(func.avg(AnalysisRun.score_total))
        .join(Repo, AnalysisRun.repo_id == Repo.id)
        .where(Repo.org_id == org_id, AnalysisRun.status == "complete")
    )
    avg_score = avg_score_result.scalar()

    active_repos = (
        await db.execute(select(Repo.id).where(Repo.org_id == org_id, Repo.is_active.is_(True)))
    ).scalars().all()
    skill_count = 0
    for repo_id in active_repos:
        latest_run = (
            await db.execute(
                select(AnalysisRun)
                .where(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "complete")
                .order_by(desc(AnalysisRun.created_at))
                .limit(1)
            )
        ).scalar_one_or_none()
        if latest_run is not None:
            skill_count += int(latest_run.skill_count or 0)

    trend_date = func.date(ScoreHistory.recorded_at).label("date")
    start_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=29)
    trend_result = await db.execute(
        select(trend_date, func.avg(ScoreHistory.score_total).label("avg_score"))
        .join(Repo, ScoreHistory.repo_id == Repo.id)
        .where(Repo.org_id == org_id, ScoreHistory.recorded_at >= start_at)
        .group_by(trend_date)
        .order_by(trend_date)
    )
    daily_scores = {str(row.date): round(row.avg_score or 0) for row in trend_result.fetchall()}
    trend = [{"date": date, "score": daily_scores.get(date, 0)} for date in _last_30_score_dates()]

    return {
        "repo_count": int(repo_count or 0),
        "avg_score": round(avg_score or 0),
        "skill_count": int(skill_count or 0),
        "active_agents": 0,
        "score_trend": trend,
    }
