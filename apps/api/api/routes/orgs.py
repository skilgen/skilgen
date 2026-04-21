from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_user
from packages.db.database import get_db
from packages.db.models import Org, Repo, ScoreHistory, Skill
from packages.db.schemas import OrgResponse, RepoResponse, ScoreResponse


router = APIRouter(prefix="/orgs", tags=["orgs"], dependencies=[Depends(get_current_user)])


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
        language=repo.language,
        is_monorepo=repo.is_monorepo,
        last_analysed_at=repo.last_analysed_at,
        score=_score_response(latest_history[0] if latest_history else None),
        score_delta=delta,
        skill_count=int(skill_count or 0),
    )


@router.get("/{org_id}", response_model=OrgResponse)
async def get_org(org_id: str, db: AsyncSession = Depends(get_db)) -> OrgResponse:
    org = await db.get(Org, org_id)
    if org is None:
        from fastapi import HTTPException

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
    responses = [await _repo_response(db, repo) for repo in repos]
    return sorted(responses, key=lambda repo: repo.score.total if repo.score else -1, reverse=True)


@router.get("/{org_id}/stats")
async def get_org_stats(org_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    repo_count = (await db.execute(select(func.count(Repo.id)).where(Repo.org_id == org_id))).scalar_one()
    skill_count = (
        await db.execute(select(func.count(Skill.id)).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == org_id))
    ).scalar_one()
    avg_score = (
        await db.execute(
            select(func.avg(ScoreHistory.score_total))
            .join(Repo, Repo.id == ScoreHistory.repo_id)
            .where(Repo.org_id == org_id)
        )
    ).scalar_one()
    since = datetime.now(timezone.utc) - timedelta(days=30)
    history_rows = (
        await db.execute(
            select(ScoreHistory.recorded_at, ScoreHistory.score_total)
            .join(Repo, Repo.id == ScoreHistory.repo_id)
            .where(Repo.org_id == org_id, ScoreHistory.recorded_at >= since)
            .order_by(ScoreHistory.recorded_at)
        )
    ).all()
    buckets: dict[str, list[int]] = {}
    for recorded_at, score in history_rows:
        buckets.setdefault(recorded_at.date().isoformat(), []).append(int(score))
    score_trend = [
        {"date": date, "avg_score": round(sum(scores) / len(scores), 2)}
        for date, scores in sorted(buckets.items())
    ]
    repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
    repo_responses = [await _repo_response(db, repo) for repo in repos]
    scored = [repo for repo in repo_responses if repo.score is not None]
    top_repo = max(scored, key=lambda repo: repo.score.total) if scored else None
    worst_repo = min(scored, key=lambda repo: repo.score.total) if scored else None
    return {
        "repo_count": int(repo_count or 0),
        "avg_score": float(avg_score) if avg_score is not None else None,
        "skill_count": int(skill_count or 0),
        "score_trend": score_trend,
        "top_repo": top_repo.model_dump(mode="json") if top_repo else None,
        "worst_repo": worst_repo.model_dump(mode="json") if worst_repo else None,
    }
