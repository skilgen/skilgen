from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_user
from apps.api.api.routes.orgs import _repo_response, _score_response
from packages.db.database import get_db
from packages.db.models import AnalysisRun, Repo, ScoreHistory, Skill, SkillVersion
from packages.db.schemas import AnalysisRunResponse, RepoResponse, SkillResponse


router = APIRouter(prefix="/repos", tags=["repos"])


class ManualAnalysisRequest(BaseModel):
    installation_id: int | None = None


async def _repo_in_scope(db: AsyncSession, repo_id: str, org_id: str) -> Repo:
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return repo


@router.get("/{repo_id}", response_model=RepoResponse)
async def get_repo(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> RepoResponse:
    repo = await _repo_in_scope(db, repo_id, current_org_id)
    return await _repo_response(db, repo)


@router.get("/{repo_id}/skills", response_model=list[SkillResponse])
async def get_repo_skills(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[SkillResponse]:
    await _repo_in_scope(db, repo_id, current_org_id)
    rows = (
        await db.execute(select(Skill).where(Skill.repo_id == repo_id).order_by(desc(Skill.created_at)))
    ).scalars().all()
    latest_by_domain: dict[str, Skill] = {}
    for skill in rows:
        latest_by_domain.setdefault(skill.domain, skill)
    skills = sorted(latest_by_domain.values(), key=lambda item: (-int(item.score_total or 0), item.domain))
    responses: list[SkillResponse] = []
    for skill in skills:
        version_count = (
            await db.execute(select(func.count(SkillVersion.id)).where(SkillVersion.skill_id == skill.id))
        ).scalar_one()
        latest_version = (
            await db.execute(
                select(SkillVersion)
                .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
                .order_by(desc(SkillVersion.version_number))
                .limit(1)
            )
        ).scalar_one_or_none()
        responses.append(
            SkillResponse(
            id=skill.id,
            domain=skill.domain,
            skill_path=skill.skill_path,
            score=_score_response(skill),  # type: ignore[arg-type]
            content=(skill.content[:500] if skill.content else None),
            content_hash=skill.content_hash,
            is_stale=skill.is_stale,
            load_count_30d=skill.load_count_30d,
            last_loaded_at=skill.last_loaded_at,
            version_count=int(version_count or 0),
            latest_version_number=(latest_version.version_number if latest_version else None),
        )
        )
    return responses


@router.get("/{repo_id}/score-history")
async def get_score_history(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[dict[str, object]]:
    await _repo_in_scope(db, repo_id, current_org_id)
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
async def get_runs(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[AnalysisRunResponse]:
    await _repo_in_scope(db, repo_id, current_org_id)
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
    current_org_id: str = Depends(get_current_org_id),
    _current_user: dict[str, object] = Depends(get_current_user),
) -> dict[str, str]:
    repo = await _repo_in_scope(db, repo_id, current_org_id)
    run = AnalysisRun(
        repo_id=repo_id,
        trigger="manual",
        status="queued",
        branch=repo.default_branch,
        created_at=datetime.utcnow(),
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
