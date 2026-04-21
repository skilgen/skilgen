from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_user
from apps.api.api.routes.orgs import _repo_response, _score_response
from packages.db.database import get_db
from packages.db.models import AnalysisRun, Repo, ScoreHistory, Skill
from packages.db.schemas import AnalysisRunResponse, RepoResponse, SkillResponse


router = APIRouter(prefix="/repos", tags=["repos"], dependencies=[Depends(get_current_user)])


class ManualAnalysisRequest(BaseModel):
    installation_id: int | None = None


@router.get("/{repo_id}", response_model=RepoResponse)
async def get_repo(repo_id: str, db: AsyncSession = Depends(get_db)) -> RepoResponse:
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    return await _repo_response(db, repo)


@router.get("/{repo_id}/skills", response_model=list[SkillResponse])
async def get_repo_skills(repo_id: str, db: AsyncSession = Depends(get_db)) -> list[SkillResponse]:
    skills = (
        await db.execute(select(Skill).where(Skill.repo_id == repo_id).order_by(desc(Skill.score_total)))
    ).scalars().all()
    return [
        SkillResponse(
            id=skill.id,
            domain=skill.domain,
            skill_path=skill.skill_path,
            score=_score_response(skill),  # type: ignore[arg-type]
            is_stale=skill.is_stale,
            load_count_30d=skill.load_count_30d,
            last_loaded_at=skill.last_loaded_at,
        )
        for skill in skills
    ]


@router.get("/{repo_id}/score-history")
async def get_score_history(repo_id: str, db: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    rows = (
        await db.execute(
            select(ScoreHistory)
            .where(ScoreHistory.repo_id == repo_id)
            .order_by(desc(ScoreHistory.recorded_at))
            .limit(90)
        )
    ).scalars().all()
    return [
        {
            "date": row.recorded_at.date().isoformat(),
            "score_total": row.score_total,
            "groundedness": row.score_groundedness,
            "coverage": row.score_coverage,
            "freshness": row.score_freshness,
            "structure": row.score_structure,
        }
        for row in reversed(rows)
    ]


@router.get("/{repo_id}/runs", response_model=list[AnalysisRunResponse])
async def get_runs(repo_id: str, db: AsyncSession = Depends(get_db)) -> list[AnalysisRunResponse]:
    runs = (
        await db.execute(
            select(AnalysisRun)
            .where(AnalysisRun.repo_id == repo_id)
            .order_by(desc(AnalysisRun.created_at))
            .limit(10)
        )
    ).scalars().all()
    return [
        AnalysisRunResponse(
            id=run.id,
            status=run.status,
            trigger=run.trigger,
            commit_sha=run.commit_sha,
            score=_score_response(run),
            domain_count=run.domain_count,
            skill_count=run.skill_count,
            started_at=run.started_at,
            completed_at=run.completed_at,
        )
        for run in runs
    ]


@router.post("/{repo_id}/analyse")
async def trigger_analysis(
    repo_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    payload: ManualAnalysisRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    run = AnalysisRun(
        repo_id=repo_id,
        trigger="manual",
        status="queued",
        branch=repo.default_branch,
        created_at=datetime.now(timezone.utc),
    )
    db.add(run)
    await db.flush()
    installation_id = (payload.installation_id if payload else None) or repo.github_installation_id
    if not installation_id:
        raise HTTPException(status_code=400, detail="Repo installation id is not available")
    await _queue_analysis(
        request,
        background_tasks,
        {
            "run_id": run.id,
            "repo_id": repo.id,
            "installation_id": int(installation_id),
            "full_name": repo.full_name,
        },
    )
    return {"queued": run.id}
from apps.api.api.routes.webhook import _queue_analysis
