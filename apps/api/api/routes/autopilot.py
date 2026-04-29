from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id_optional
from apps.api.api.services.autopilot import compute_autopilot_queue
from packages.db.database import get_db
from packages.db.models import AutopilotTask, Repo, Skill

router = APIRouter(prefix="/orgs", tags=["autopilot"])


class AutopilotTaskResponse(BaseModel):
    id: str
    org_id: str
    repo_id: str
    repo_name: str | None = None
    skill_id: str | None
    skill_domain: str | None = None
    skill_path: str | None = None
    task_type: str
    trigger_reason: str
    freshness_at_trigger: int
    status: str
    created_at: datetime
    resolved_at: datetime | None


def _error(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def _task_response(task: AutopilotTask, repo_lookup: dict[str, Repo], skill_lookup: dict[str, Skill]) -> AutopilotTaskResponse:
    repo = repo_lookup.get(task.repo_id)
    skill = skill_lookup.get(task.skill_id or "")
    return AutopilotTaskResponse(
        id=task.id,
        org_id=task.org_id,
        repo_id=task.repo_id,
        repo_name=repo.name if repo else None,
        skill_id=task.skill_id,
        skill_domain=skill.domain if skill else None,
        skill_path=skill.skill_path if skill else None,
        task_type=task.task_type,
        trigger_reason=task.trigger_reason,
        freshness_at_trigger=int(task.freshness_at_trigger or 0),
        status=task.status,
        created_at=task.created_at,
        resolved_at=task.resolved_at,
    )


async def _load_org_repos_skills(db: AsyncSession, org_id: str) -> tuple[list[Repo], list[Skill]]:
    repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
    repo_ids = [repo.id for repo in repos]
    skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all() if repo_ids else []
    return list(repos), list(skills)


@router.get("/{org_id}/autopilot/queue", response_model=list[AutopilotTaskResponse])
async def get_autopilot_queue(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> list[AutopilotTaskResponse] | JSONResponse:
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden")
    try:
        repos, skills = await _load_org_repos_skills(db, org_id)
        tasks = await compute_autopilot_queue(db, org_id, repos, skills)
        await db.commit()
        return [_task_response(task, {repo.id: repo for repo in repos}, {skill.id: skill for skill in skills}) for task in tasks]
    except Exception:
        await db.rollback()
        return _error(400, "Could not load autopilot queue")


@router.post("/{org_id}/autopilot/trigger", response_model=list[AutopilotTaskResponse])
async def trigger_autopilot(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> list[AutopilotTaskResponse] | JSONResponse:
    return await get_autopilot_queue(org_id, db, current_org_id)


@router.post("/{org_id}/autopilot/tasks/{task_id}/skip", response_model=AutopilotTaskResponse)
async def skip_autopilot_task(
    org_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> AutopilotTaskResponse | JSONResponse:
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden")
    try:
        task = await db.get(AutopilotTask, task_id)
        if task is None or task.org_id != org_id:
            return _error(404, "Task not found")
        task.status = "skipped"
        task.resolved_at = datetime.utcnow()
        await db.commit()
        repos, skills = await _load_org_repos_skills(db, org_id)
        return _task_response(task, {repo.id: repo for repo in repos}, {skill.id: skill for skill in skills})
    except Exception:
        await db.rollback()
        return _error(400, "Could not skip task")


@router.post("/{org_id}/autopilot/tasks/{task_id}/approve", response_model=AutopilotTaskResponse)
async def approve_autopilot_task(
    org_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> AutopilotTaskResponse | JSONResponse:
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden")
    try:
        task = await db.get(AutopilotTask, task_id)
        if task is None or task.org_id != org_id:
            return _error(404, "Task not found")
        task.status = "approved"
        task.resolved_at = datetime.utcnow()
        await db.commit()
        repos, skills = await _load_org_repos_skills(db, org_id)
        return _task_response(task, {repo.id: repo for repo in repos}, {skill.id: skill for skill in skills})
    except Exception:
        await db.rollback()
        return _error(400, "Could not approve task")
