from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id_optional
from apps.api.api.services.autopilot import (
    apply_autopilot_improvement,
    compute_autopilot_queue,
    deduplicate_pending_autopilot_tasks,
    generate_autopilot_improvement,
    latest_skill_content,
    reject_autopilot_improvement,
)
from apps.api.api.services.llm import LLMCallError, LLMNotConfiguredError
from packages.db.database import get_db
from packages.db.models import AutopilotTask, Org, Repo, Skill

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
    improvement_status: str | None = None
    original_content: str | None = None
    generated_content: str | None = None
    final_content: str | None = None
    generation_error: str | None = None
    pr_url: str | None = None
    pr_number: int | None = None
    generated_at: datetime | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    resolved_at: datetime | None


class AutopilotDeduplicateResponse(BaseModel):
    deduplicated: int
    tasks: list[AutopilotTaskResponse]


class AutopilotPreviewResponse(BaseModel):
    task: AutopilotTaskResponse
    title: str
    summary: str
    proposed_changes: list[str]
    risk_level: str
    generated_at: datetime


class GenerateImprovementResponse(BaseModel):
    task: AutopilotTaskResponse
    original_content: str
    generated_content: str


class ApproveAutopilotRequest(BaseModel):
    final_content: str | None = None
    create_skill_pr: bool = False


class RejectAutopilotRequest(BaseModel):
    reason: str | None = None


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
        improvement_status=task.improvement_status,
        original_content=task.original_content,
        generated_content=task.generated_content,
        final_content=task.final_content,
        generation_error=task.generation_error,
        pr_url=task.pr_url,
        pr_number=task.pr_number,
        generated_at=task.generated_at,
        reviewed_at=task.reviewed_at,
        created_at=task.created_at,
        resolved_at=task.resolved_at,
    )


async def _load_task_context(db: AsyncSession, org_id: str, task_id: str) -> tuple[AutopilotTask, Org, Repo, Skill]:
    task = await db.get(AutopilotTask, task_id)
    if task is None or task.org_id != org_id:
        raise LookupError("task_not_found")
    org = await db.get(Org, org_id)
    if org is None:
        raise LookupError("org_not_found")
    repo = await db.get(Repo, task.repo_id)
    if repo is None or repo.org_id != org_id:
        raise LookupError("repo_not_found")
    if not task.skill_id:
        raise LookupError("skill_not_found")
    skill = await db.get(Skill, task.skill_id)
    if skill is None or skill.repo_id != repo.id:
        raise LookupError("skill_not_found")
    return task, org, repo, skill


async def _load_org_repos_skills(db: AsyncSession, org_id: str) -> tuple[list[Repo], list[Skill]]:
    repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
    repo_ids = [repo.id for repo in repos]
    skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all() if repo_ids else []
    return list(repos), list(skills)


async def _load_org_tasks(db: AsyncSession, org_id: str) -> list[AutopilotTask]:
    tasks = (
        await db.execute(
            select(AutopilotTask)
            .where(AutopilotTask.org_id == org_id)
            .order_by(AutopilotTask.created_at.desc())
        )
    ).scalars().all()
    return list(tasks)


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
        await compute_autopilot_queue(db, org_id, repos, skills)
        await deduplicate_pending_autopilot_tasks(db, org_id)
        tasks = await _load_org_tasks(db, org_id)
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


@router.post("/{id}/autopilot/deduplicate", response_model=AutopilotDeduplicateResponse)
async def deduplicate_autopilot_queue(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> AutopilotDeduplicateResponse | JSONResponse:
    if current_org_id and current_org_id != id:
        return _error(403, "Forbidden")
    try:
        repos, skills = await _load_org_repos_skills(db, id)
        deduplicated = await deduplicate_pending_autopilot_tasks(db, id)
        tasks = await _load_org_tasks(db, id)
        await db.commit()
        return AutopilotDeduplicateResponse(
            deduplicated=deduplicated,
            tasks=[_task_response(task, {repo.id: repo for repo in repos}, {skill.id: skill for skill in skills}) for task in tasks],
        )
    except Exception:
        await db.rollback()
        return _error(400, "Could not deduplicate autopilot queue")


@router.get("/{org_id}/autopilot/tasks/{task_id}/preview", response_model=AutopilotPreviewResponse)
async def preview_autopilot_task(
    org_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> AutopilotPreviewResponse | JSONResponse:
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden")
    try:
        task = await db.get(AutopilotTask, task_id)
        if task is None or task.org_id != org_id:
            return _error(404, "Task not found")
        repos, skills = await _load_org_repos_skills(db, org_id)
        repo_lookup = {repo.id: repo for repo in repos}
        skill_lookup = {skill.id: skill for skill in skills}
        task_response = _task_response(task, repo_lookup, skill_lookup)
        skill_label = task_response.skill_path or task_response.skill_domain or task_response.skill_id or "repository skill"
        repo_label = task_response.repo_name or task_response.repo_id
        freshness = int(task.freshness_at_trigger or 0)
        return AutopilotPreviewResponse(
            task=task_response,
            title=f"Regenerate {skill_label}",
            summary=f"Autopilot will refresh {skill_label} in {repo_label} because freshness is {freshness}/25.",
            proposed_changes=[
                "Re-run skill generation for the affected repository context.",
                "Preserve the existing skill path and domain when updated evidence is available.",
                "Leave the task pending until it is approved or skipped.",
            ],
            risk_level="low" if freshness >= 10 else "medium",
            generated_at=datetime.utcnow(),
        )
    except Exception:
        await db.rollback()
        return _error(400, "Could not preview task")


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


@router.post("/{org_id}/autopilot/{task_id}/generate-improvement", response_model=GenerateImprovementResponse)
async def generate_autopilot_task_improvement(
    org_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> GenerateImprovementResponse | JSONResponse:
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden")
    try:
        task, org, repo, skill = await _load_task_context(db, org_id, task_id)
        task = await generate_autopilot_improvement(db, task, org, repo, skill)
        await db.commit()
        response = _task_response(task, {repo.id: repo}, {skill.id: skill})
        return GenerateImprovementResponse(
            task=response,
            original_content=task.original_content or await latest_skill_content(db, skill),
            generated_content=task.generated_content or "",
        )
    except LookupError:
        await db.rollback()
        return _error(404, "Task not found")
    except LLMNotConfiguredError as exc:
        await db.rollback()
        return _error(402, str(exc))
    except LLMCallError as exc:
        await db.rollback()
        return _error(502, str(exc))
    except Exception:
        await db.rollback()
        return _error(400, "Could not generate improvement")


@router.post("/{org_id}/autopilot/{task_id}/approve", response_model=AutopilotTaskResponse)
@router.post("/{org_id}/autopilot/tasks/{task_id}/approve", response_model=AutopilotTaskResponse)
async def approve_autopilot_task(
    org_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
    payload: ApproveAutopilotRequest | None = None,
) -> AutopilotTaskResponse | JSONResponse:
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden")
    try:
        task = await db.get(AutopilotTask, task_id)
        if task is None or task.org_id != org_id:
            return _error(404, "Task not found")
        if payload and (payload.final_content or task.generated_content):
            _task, _org, repo, skill = await _load_task_context(db, org_id, task_id)
            final_content = payload.final_content or task.generated_content or ""
            if not final_content.strip():
                return _error(400, "final_content is required")
            await apply_autopilot_improvement(db, task, repo, skill, final_content, create_pr=payload.create_skill_pr)
            await db.commit()
            return _task_response(task, {repo.id: repo}, {skill.id: skill})
        task.status = "approved"
        task.improvement_status = task.improvement_status or "approved"
        task.reviewed_at = datetime.utcnow()
        task.resolved_at = datetime.utcnow()
        await db.commit()
        repos, skills = await _load_org_repos_skills(db, org_id)
        return _task_response(task, {repo.id: repo for repo in repos}, {skill.id: skill for skill in skills})
    except Exception:
        await db.rollback()
        return _error(400, "Could not approve task")


@router.post("/{org_id}/autopilot/{task_id}/reject", response_model=AutopilotTaskResponse)
async def reject_autopilot_task(
    org_id: str,
    task_id: str,
    payload: RejectAutopilotRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> AutopilotTaskResponse | JSONResponse:
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden")
    try:
        task = await db.get(AutopilotTask, task_id)
        if task is None or task.org_id != org_id:
            return _error(404, "Task not found")
        await reject_autopilot_improvement(db, task, payload.reason if payload else None)
        await db.commit()
        repos, skills = await _load_org_repos_skills(db, org_id)
        return _task_response(task, {repo.id: repo for repo in repos}, {skill.id: skill for skill in skills})
    except Exception:
        await db.rollback()
        return _error(400, "Could not reject task")
