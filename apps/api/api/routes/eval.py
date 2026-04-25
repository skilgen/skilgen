from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from apps.api.api.services import audit
from packages.db.database import AsyncSessionLocal, get_db
from packages.db.models import ABTest, AgentTask, EvalSession, Repo, Skill, SkillGap, SkillVersion


router = APIRouter(tags=["eval"])


TaskOutcome = Literal["success", "failure", "partial", "abandoned"]
TaskType = Literal["code_generation", "debugging", "refactoring", "documentation", "testing", "review", "other"]


class TaskPayload(BaseModel):
    repo_id: str
    session_id: str
    agent_runtime: str
    task_description: str | None = None
    task_type: TaskType | None = None
    outcome: TaskOutcome
    failure_reason: str | None = None
    skills_loaded: list[str] = Field(default_factory=list)
    duration_seconds: int | None = None
    token_count: int | None = None
    started_at: datetime
    completed_at: datetime | None = None


class BatchTaskPayload(BaseModel):
    tasks: list[TaskPayload] = Field(max_length=100)


class AgentTaskResponse(BaseModel):
    id: str
    org_id: str
    repo_id: str
    session_id: str
    agent_runtime: str
    task_type: str | None
    outcome: str
    failure_reason: str | None
    skill_domains_loaded: list[str]
    skill_score_at_task: float | None
    duration_seconds: int | None
    token_count: int | None
    started_at: datetime
    created_at: datetime


class ROIResponse(BaseModel):
    total_tasks: int
    success_rate: float | None
    multiplier: float | None
    high_skill_success_rate: float | None
    low_skill_success_rate: float | None
    by_skill_score_bucket: list[dict[str, object]]
    by_agent_runtime: list[dict[str, object]]
    skill_gaps: list[dict[str, object]]
    trend: list[dict[str, object]]
    benchmark: dict[str, object]


class ABTestCreatePayload(BaseModel):
    skill_id: str
    name: str
    control_version_id: str
    treatment_version_id: str


class ABTestResponse(BaseModel):
    id: str
    skill_id: str
    name: str
    status: str
    winner: str | None
    control_success_rate: float | None
    treatment_success_rate: float | None
    improvement_pct: float | None
    confidence: str | None
    recommendation: str | None
    created_at: datetime
    completed_at: datetime | None


class SkillGapResponse(BaseModel):
    id: str
    domain: str
    failure_count: int
    gap_type: str
    existing_skill_id: str | None
    existing_skill_score: float | None
    status: str
    suggested_action: str
    detected_at: datetime
    task_ids: list[str] = Field(default_factory=list)
    failed_tasks: list[dict[str, object]] = Field(default_factory=list)


class SkillGapPatchPayload(BaseModel):
    status: Literal["acknowledged", "resolved"]
    resolution_note: str | None = None


class EvalSessionPayload(BaseModel):
    name: str
    description: str | None = None
    eval_type: Literal["baseline", "treatment", "ab_test", "benchmark"]
    repo_id: str | None = None
    agent_runtime: str
    skill_version_snapshot: dict[str, object] = Field(default_factory=dict)


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _actual_org_id(path_org_id: str, current_org_id: str) -> str:
    if path_org_id == "current":
        return current_org_id
    if path_org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return path_org_id


async def _assert_repo_scope(db: AsyncSession, org_id: str, repo_id: str) -> Repo:
    result = await db.execute(select(Repo).where(Repo.id == repo_id, Repo.org_id == org_id, Repo.is_active.is_(True)))
    repo = result.scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    return repo


async def _resolve_skills(db: AsyncSession, repo_id: str, skill_ids: list[str]) -> tuple[list[str], float | None]:
    clean = [skill_id for skill_id in skill_ids if skill_id]
    if not clean:
        return [], None
    result = await db.execute(select(Skill).where(Skill.repo_id == repo_id, Skill.id.in_(clean)))
    skills = list(result.scalars().all())
    domains = sorted({skill.domain for skill in skills if skill.domain})
    scores = [float(skill.score_total or 0) for skill in skills]
    return domains, round(sum(scores) / len(scores), 2) if scores else None


def _task_response(task: AgentTask) -> AgentTaskResponse:
    return AgentTaskResponse(
        id=task.id,
        org_id=task.org_id,
        repo_id=task.repo_id,
        session_id=task.session_id,
        agent_runtime=task.agent_runtime,
        task_type=task.task_type,
        outcome=task.outcome,
        failure_reason=task.failure_reason,
        skill_domains_loaded=list(task.skill_domains_loaded or []),
        skill_score_at_task=task.skill_score_at_task,
        duration_seconds=task.duration_seconds,
        token_count=task.token_count,
        started_at=task.started_at,
        created_at=task.created_at,
    )


def _success_rate(tasks: list[AgentTask]) -> float | None:
    if not tasks:
        return None
    return round(sum(1 for task in tasks if task.outcome == "success") / len(tasks), 4)


def _avg(values: list[float | int | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    return round(sum(clean) / len(clean), 2) if clean else None


def _suggested_action(gap: SkillGap, freshness: int | None = None) -> str:
    if gap.gap_type == "missing_skill":
        return f"Generate a new skill: `skilgen deliver --project-root . --focus {gap.domain}`"
    if gap.gap_type == "stale_skill":
        return f"Regenerate skill — freshness score: {freshness if freshness is not None else 'low'}/25"
    return f"Improve skill quality — current score: {int(gap.existing_skill_score or 0)}/100"


async def _audit_task_recorded(org_id: str, repo_id: str, task_id: str, outcome: str) -> None:
    async with AsyncSessionLocal() as db:
        await audit.emit(
            db,
            org_id,
            "agent_task_recorded",
            "agent_task_recorded",
            f"Agent task recorded with outcome {outcome}",
            repo_id=repo_id,
            resource_type="agent_task",
            resource_id=task_id,
            metadata={"outcome": outcome},
        )
        await db.commit()


async def _detect_skill_gaps(org_id: str, repo_id: str, db: AsyncSession) -> int:
    cutoff = _now() - timedelta(days=7)
    failed_result = await db.execute(
        select(AgentTask).where(
            AgentTask.org_id == org_id,
            AgentTask.repo_id == repo_id,
            AgentTask.outcome == "failure",
            AgentTask.started_at >= cutoff,
        )
    )
    failed_tasks = list(failed_result.scalars().all())
    counts: Counter[str] = Counter()
    task_ids_by_domain: dict[str, list[str]] = defaultdict(list)
    for task in failed_tasks:
        for domain in task.skill_domains_loaded or ["unknown"]:
            counts[str(domain)] += 1
            task_ids_by_domain[str(domain)].append(task.id)

    open_result = await db.execute(select(SkillGap).where(SkillGap.org_id == org_id, SkillGap.repo_id == repo_id, SkillGap.status == "open"))
    open_gaps = {gap.domain: gap for gap in open_result.scalars().all()}
    changed = 0

    for domain, failure_count in counts.items():
        if failure_count < 3:
            continue
        skill_result = await db.execute(select(Skill).where(Skill.repo_id == repo_id, Skill.domain == domain).order_by(desc(Skill.created_at)).limit(1))
        skill = skill_result.scalar_one_or_none()
        gap_type = "missing_skill"
        if skill is not None and int(skill.score_total or 0) < 40:
            gap_type = "weak_skill"
        elif skill is not None and int(skill.score_freshness or 0) < 15:
            gap_type = "stale_skill"
        elif skill is not None:
            gap_type = "weak_skill"

        existing = open_gaps.get(domain)
        if existing is None:
            db.add(
                SkillGap(
                    id=str(uuid4()),
                    org_id=org_id,
                    repo_id=repo_id,
                    domain=domain,
                    detected_at=_now(),
                    failure_count=failure_count,
                    task_ids=task_ids_by_domain[domain],
                    existing_skill_id=skill.id if skill else None,
                    existing_skill_score=float(skill.score_total) if skill else None,
                    gap_type=gap_type,
                    status="open",
                )
            )
        else:
            existing.failure_count = failure_count
            existing.task_ids = task_ids_by_domain[domain]
            existing.existing_skill_id = skill.id if skill else None
            existing.existing_skill_score = float(skill.score_total) if skill else None
            existing.gap_type = gap_type
        changed += 1

    for domain, gap in open_gaps.items():
        if counts.get(domain, 0) == 0:
            gap.status = "resolved"
            gap.resolved_at = _now()
            gap.resolution_note = "Auto-resolved after recent failures cleared."
            changed += 1
    await db.commit()
    return changed


async def _detect_skill_gaps_background(org_id: str, repo_id: str) -> None:
    async with AsyncSessionLocal() as db:
        await _detect_skill_gaps(org_id, repo_id, db)


async def _gap_count_after_insert(db: AsyncSession, org_id: str, repo_id: str) -> int:
    cutoff = _now() - timedelta(days=7)
    result = await db.execute(
        select(AgentTask).where(
            AgentTask.org_id == org_id,
            AgentTask.repo_id == repo_id,
            AgentTask.outcome == "failure",
            AgentTask.started_at >= cutoff,
        )
    )
    counts: Counter[str] = Counter()
    for task in result.scalars().all():
        for domain in task.skill_domains_loaded or ["unknown"]:
            counts[str(domain)] += 1
    return sum(1 for count in counts.values() if count >= 3)


@router.post("/orgs/{org_id}/tasks")
async def record_task(
    org_id: str,
    payload: TaskPayload,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    await _assert_repo_scope(db, actual_org_id, payload.repo_id)
    domains, avg_score = await _resolve_skills(db, payload.repo_id, payload.skills_loaded)
    task = AgentTask(
        id=str(uuid4()),
        org_id=actual_org_id,
        repo_id=payload.repo_id,
        session_id=payload.session_id,
        agent_runtime=payload.agent_runtime,
        task_description=payload.task_description,
        task_type=payload.task_type,
        outcome=payload.outcome,
        failure_reason=payload.failure_reason,
        skills_loaded=payload.skills_loaded,
        skill_domains_loaded=domains,
        duration_seconds=payload.duration_seconds,
        token_count=payload.token_count,
        skill_score_at_task=avg_score,
        started_at=payload.started_at.replace(tzinfo=None),
        completed_at=payload.completed_at.replace(tzinfo=None) if payload.completed_at else None,
    )
    db.add(task)
    await db.flush()
    gaps_detected = await _gap_count_after_insert(db, actual_org_id, payload.repo_id) > 0
    await db.commit()
    background_tasks.add_task(_detect_skill_gaps_background, actual_org_id, payload.repo_id)
    background_tasks.add_task(_audit_task_recorded, actual_org_id, payload.repo_id, task.id, payload.outcome)
    return {"task_id": task.id, "gaps_detected": gaps_detected}


@router.post("/orgs/{org_id}/tasks/batch")
async def record_tasks_batch(
    org_id: str,
    payload: BatchTaskPayload,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, int]:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    inserted = 0
    repo_ids: set[str] = set()
    for item in payload.tasks:
        await _assert_repo_scope(db, actual_org_id, item.repo_id)
        domains, avg_score = await _resolve_skills(db, item.repo_id, item.skills_loaded)
        db.add(
            AgentTask(
                id=str(uuid4()),
                org_id=actual_org_id,
                repo_id=item.repo_id,
                session_id=item.session_id,
                agent_runtime=item.agent_runtime,
                task_description=item.task_description,
                task_type=item.task_type,
                outcome=item.outcome,
                failure_reason=item.failure_reason,
                skills_loaded=item.skills_loaded,
                skill_domains_loaded=domains,
                duration_seconds=item.duration_seconds,
                token_count=item.token_count,
                skill_score_at_task=avg_score,
                started_at=item.started_at.replace(tzinfo=None),
                completed_at=item.completed_at.replace(tzinfo=None) if item.completed_at else None,
            )
        )
        inserted += 1
        repo_ids.add(item.repo_id)
    await db.flush()
    gaps_detected = 0
    for repo_id in repo_ids:
        gaps_detected += await _gap_count_after_insert(db, actual_org_id, repo_id)
    await db.commit()
    for repo_id in repo_ids:
        background_tasks.add_task(_detect_skill_gaps_background, actual_org_id, repo_id)
    return {"inserted": inserted, "gaps_detected": gaps_detected}


@router.get("/orgs/{org_id}/roi", response_model=ROIResponse)
async def get_roi(
    org_id: str,
    repo_id: str | None = None,
    agent_runtime: str | None = None,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> ROIResponse:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    cutoff = _now() - timedelta(days=days)
    filters = [AgentTask.org_id == actual_org_id, AgentTask.started_at >= cutoff]
    if repo_id:
        filters.append(AgentTask.repo_id == repo_id)
    if agent_runtime:
        filters.append(AgentTask.agent_runtime == agent_runtime)
    task_result = await db.execute(select(AgentTask).where(*filters).order_by(AgentTask.started_at))
    tasks = list(task_result.scalars().all())
    high = [task for task in tasks if task.skill_score_at_task is not None and task.skill_score_at_task >= 70]
    low = [task for task in tasks if task.skill_score_at_task is not None and task.skill_score_at_task < 40]
    high_rate = _success_rate(high)
    low_rate = _success_rate(low)
    multiplier = None
    if high_rate is not None and low_rate is not None and len(high) >= 5 and len(low) >= 5:
        multiplier = 10 if low_rate == 0 and high_rate > 0 else round(min(10, high_rate / low_rate), 2) if low_rate else None

    buckets = [
        ("0-39", lambda task: task.skill_score_at_task is not None and task.skill_score_at_task < 40),
        ("40-69", lambda task: task.skill_score_at_task is not None and 40 <= task.skill_score_at_task < 70),
        ("70-100", lambda task: task.skill_score_at_task is not None and task.skill_score_at_task >= 70),
    ]
    by_bucket = []
    for label, predicate in buckets:
        bucket_tasks = [task for task in tasks if predicate(task)]
        by_bucket.append({"bucket": label, "task_count": len(bucket_tasks), "success_rate": _success_rate(bucket_tasks)})

    runtime_rows = []
    for runtime in sorted({task.agent_runtime for task in tasks}):
        runtime_tasks = [task for task in tasks if task.agent_runtime == runtime]
        domain_counts = Counter(domain for task in runtime_tasks for domain in (task.skill_domains_loaded or []))
        runtime_rows.append(
            {
                "runtime": runtime,
                "task_count": len(runtime_tasks),
                "success_rate": _success_rate(runtime_tasks),
                "avg_token_count": _avg([task.token_count for task in runtime_tasks]),
                "best_domain": domain_counts.most_common(1)[0][0] if domain_counts else None,
            }
        )

    gaps_result = await db.execute(select(SkillGap).where(SkillGap.org_id == actual_org_id, SkillGap.status == "open").order_by(desc(SkillGap.failure_count)))
    skill_gaps = [
        {"domain": gap.domain, "failure_count": gap.failure_count, "gap_type": gap.gap_type, "existing_score": gap.existing_skill_score}
        for gap in gaps_result.scalars().all()
        if not repo_id or gap.repo_id == repo_id
    ]

    trend = []
    for week_index in range(7, -1, -1):
        start = _now() - timedelta(weeks=week_index + 1)
        end = _now() - timedelta(weeks=week_index)
        week_tasks = [task for task in tasks if start <= task.started_at < end]
        trend.append(
            {
                "week": start.date().isoformat(),
                "success_rate": _success_rate(week_tasks),
                "avg_skill_score": _avg([task.skill_score_at_task for task in week_tasks]),
            }
        )

    with_skills = [task for task in tasks if task.skills_loaded]
    without_skills = [task for task in tasks if not task.skills_loaded]
    with_rate = _success_rate(with_skills)
    without_rate = _success_rate(without_skills)
    benchmark = {
        "with_skills_success_rate": with_rate,
        "without_skills_success_rate": without_rate,
        "skill_advantage_pct": round(((with_rate - without_rate) / without_rate) * 100, 2) if with_rate is not None and without_rate else None,
        "note": "Insufficient data" if len(high) < 5 or len(low) < 5 else None,
    }
    return ROIResponse(
        total_tasks=len(tasks),
        success_rate=_success_rate(tasks),
        multiplier=multiplier,
        high_skill_success_rate=high_rate,
        low_skill_success_rate=low_rate,
        by_skill_score_bucket=by_bucket,
        by_agent_runtime=runtime_rows,
        skill_gaps=skill_gaps,
        trend=trend,
        benchmark=benchmark,
    )


@router.post("/orgs/{org_id}/ab-tests", response_model=ABTestResponse)
async def create_ab_test(
    org_id: str,
    payload: ABTestCreatePayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> ABTestResponse:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    skill_result = await db.execute(select(Skill).where(Skill.id == payload.skill_id).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == actual_org_id))
    skill = skill_result.scalar_one_or_none()
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    await _assert_repo_scope(db, actual_org_id, skill.repo_id)
    control_session = EvalSession(id=str(uuid4()), org_id=actual_org_id, repo_id=skill.repo_id, name=f"{payload.name} — Control", eval_type="ab_test", skill_version_snapshot={payload.skill_id: payload.control_version_id}, agent_runtime="mixed")
    treatment_session = EvalSession(id=str(uuid4()), org_id=actual_org_id, repo_id=skill.repo_id, name=f"{payload.name} — Treatment", eval_type="ab_test", skill_version_snapshot={payload.skill_id: payload.treatment_version_id}, agent_runtime="mixed")
    db.add_all([control_session, treatment_session])
    await db.flush()
    test = ABTest(
        id=str(uuid4()),
        org_id=actual_org_id,
        repo_id=skill.repo_id,
        skill_id=payload.skill_id,
        name=payload.name,
        status="running",
        control_version_id=payload.control_version_id,
        treatment_version_id=payload.treatment_version_id,
        control_session_id=control_session.id,
        treatment_session_id=treatment_session.id,
        created_at=_now(),
    )
    db.add(test)
    await db.commit()
    return _ab_response(test)


def _ab_response(test: ABTest) -> ABTestResponse:
    return ABTestResponse(
        id=test.id,
        skill_id=test.skill_id,
        name=test.name,
        status=test.status,
        winner=test.winner,
        control_success_rate=test.control_success_rate,
        treatment_success_rate=test.treatment_success_rate,
        improvement_pct=test.improvement_pct,
        confidence=test.confidence,
        recommendation=test.recommendation,
        created_at=test.created_at,
        completed_at=test.completed_at,
    )


@router.get("/orgs/{org_id}/ab-tests")
async def list_ab_tests(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[dict[str, object]]:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    result = await db.execute(
        select(ABTest, Skill, Repo).join(Skill, Skill.id == ABTest.skill_id).join(Repo, Repo.id == ABTest.repo_id).where(ABTest.org_id == actual_org_id).order_by(desc(ABTest.created_at))
    )
    return [
        {
            **_ab_response(test).model_dump(),
            "skill_name": skill.domain,
            "repo_name": repo.name,
            "control_session_id": test.control_session_id,
            "treatment_session_id": test.treatment_session_id,
        }
        for test, skill, repo in result.all()
    ]


async def _session_rates(db: AsyncSession, session_id: str | None) -> tuple[int, float | None]:
    if not session_id:
        return 0, None
    result = await db.execute(select(AgentTask).where(AgentTask.session_id == session_id))
    tasks = list(result.scalars().all())
    return len(tasks), _success_rate(tasks)


@router.get("/orgs/{org_id}/ab-tests/{test_id}")
async def get_ab_test(
    org_id: str,
    test_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    result = await db.execute(select(ABTest).where(ABTest.id == test_id, ABTest.org_id == actual_org_id))
    test = result.scalar_one_or_none()
    if test is None:
        raise HTTPException(status_code=404, detail="A/B test not found")
    control_count, control_rate = await _session_rates(db, test.control_session_id)
    treatment_count, treatment_rate = await _session_rates(db, test.treatment_session_id)
    return {
        **_ab_response(test).model_dump(),
        "control_session_id": test.control_session_id,
        "treatment_session_id": test.treatment_session_id,
        "control_task_count": control_count,
        "treatment_task_count": treatment_count,
        "current_control_success_rate": control_rate,
        "current_treatment_success_rate": treatment_rate,
    }


@router.post("/orgs/{org_id}/ab-tests/{test_id}/conclude", response_model=ABTestResponse)
async def conclude_ab_test(
    org_id: str,
    test_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> ABTestResponse:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    result = await db.execute(select(ABTest).where(ABTest.id == test_id, ABTest.org_id == actual_org_id))
    test = result.scalar_one_or_none()
    if test is None:
        raise HTTPException(status_code=404, detail="A/B test not found")
    control_count, control_rate = await _session_rates(db, test.control_session_id)
    treatment_count, treatment_rate = await _session_rates(db, test.treatment_session_id)
    control = control_rate or 0
    treatment = treatment_rate or 0
    confidence = "high" if control_count >= 20 and treatment_count >= 20 else "medium" if control_count >= 10 and treatment_count >= 10 else "low"
    if treatment > control + 0.05:
        winner = "treatment"
    elif control > treatment + 0.05:
        winner = "control"
    else:
        winner = "inconclusive"
    improvement = round(((treatment - control) / control) * 100, 2) if control else None
    if winner == "treatment" and improvement is not None:
        recommendation = f"Skill treatment improved task success rate by {int(round(improvement))}% ({confidence} confidence). Ship it."
    elif winner == "control":
        recommendation = f"Control performed better ({confidence} confidence). Keep the current skill version."
    else:
        recommendation = "Results are inconclusive — collect more task data before deciding."
    test.status = "completed"
    test.winner = winner
    test.control_success_rate = control_rate
    test.treatment_success_rate = treatment_rate
    test.improvement_pct = improvement
    test.confidence = confidence
    test.recommendation = recommendation
    test.completed_at = _now()
    await db.commit()
    return _ab_response(test)


@router.get("/orgs/{org_id}/skill-gaps", response_model=list[SkillGapResponse])
async def list_skill_gaps(
    org_id: str,
    status: str = "open",
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[SkillGapResponse]:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    result = await db.execute(select(SkillGap).where(SkillGap.org_id == actual_org_id, SkillGap.status == status).order_by(desc(SkillGap.failure_count)))
    gaps = list(result.scalars().all())
    responses: list[SkillGapResponse] = []
    for gap in gaps:
        freshness = None
        failed_tasks: list[dict[str, object]] = []
        if gap.existing_skill_id:
            skill_result = await db.execute(select(Skill).where(Skill.id == gap.existing_skill_id))
            skill = skill_result.scalar_one_or_none()
            freshness = skill.score_freshness if skill else None
        if gap.task_ids:
            task_result = await db.execute(select(AgentTask).where(AgentTask.id.in_(gap.task_ids)).order_by(desc(AgentTask.started_at)).limit(10))
            failed_tasks = [
                {
                    "id": task.id,
                    "description": task.task_description,
                    "outcome": task.outcome,
                    "failure_reason": task.failure_reason,
                    "started_at": task.started_at.isoformat(),
                }
                for task in task_result.scalars().all()
            ]
        responses.append(
            SkillGapResponse(
                id=gap.id,
                domain=gap.domain,
                failure_count=gap.failure_count,
                gap_type=gap.gap_type,
                existing_skill_id=gap.existing_skill_id,
                existing_skill_score=gap.existing_skill_score,
                status=gap.status,
                suggested_action=_suggested_action(gap, freshness),
                detected_at=gap.detected_at,
                task_ids=list(gap.task_ids or []),
                failed_tasks=failed_tasks,
            )
        )
    return responses


@router.patch("/orgs/{org_id}/skill-gaps/{gap_id}", response_model=SkillGapResponse)
async def patch_skill_gap(
    org_id: str,
    gap_id: str,
    payload: SkillGapPatchPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SkillGapResponse:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    result = await db.execute(select(SkillGap).where(SkillGap.id == gap_id, SkillGap.org_id == actual_org_id))
    gap = result.scalar_one_or_none()
    if gap is None:
        raise HTTPException(status_code=404, detail="Skill gap not found")
    gap.status = payload.status
    gap.resolution_note = payload.resolution_note
    if payload.status == "resolved":
        gap.resolved_at = _now()
    await db.commit()
    return SkillGapResponse(
        id=gap.id,
        domain=gap.domain,
        failure_count=gap.failure_count,
        gap_type=gap.gap_type,
        existing_skill_id=gap.existing_skill_id,
        existing_skill_score=gap.existing_skill_score,
        status=gap.status,
        suggested_action=_suggested_action(gap),
        detected_at=gap.detected_at,
        task_ids=list(gap.task_ids or []),
    )


@router.get("/orgs/{org_id}/benchmark")
async def get_benchmark(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    tasks_result = await db.execute(select(AgentTask).where(AgentTask.org_id == actual_org_id))
    tasks = list(tasks_result.scalars().all())
    with_skills = [task for task in tasks if task.skills_loaded]
    baseline_result = await db.execute(select(EvalSession).where(EvalSession.org_id == actual_org_id, EvalSession.eval_type == "baseline").order_by(desc(EvalSession.created_at)).limit(1))
    baseline = baseline_result.scalar_one_or_none()
    return {
        "with_skilgen": {"success_rate": _success_rate(with_skills), "avg_tokens": _avg([task.token_count for task in with_skills]), "sample_size": len(with_skills)},
        "without_skilgen": {
            "success_rate": baseline.success_rate if baseline else None,
            "avg_tokens": baseline.avg_token_count if baseline else None,
            "sample_size": baseline.task_count if baseline else 0,
            "note": None if baseline else "Baseline not recorded",
        },
        "has_baseline": baseline is not None,
        "setup_instructions": "Run a baseline eval session before loading skills, then record outcomes with `skilgen eval record`.",
    }


@router.post("/orgs/{org_id}/eval-sessions")
async def create_eval_session(
    org_id: str,
    payload: EvalSessionPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    actual_org_id = _actual_org_id(org_id, current_org_id)
    if payload.repo_id:
        await _assert_repo_scope(db, actual_org_id, payload.repo_id)
    session = EvalSession(
        id=str(uuid4()),
        org_id=actual_org_id,
        repo_id=payload.repo_id,
        name=payload.name,
        description=payload.description,
        eval_type=payload.eval_type,
        skill_version_snapshot=payload.skill_version_snapshot,
        agent_runtime=payload.agent_runtime,
    )
    db.add(session)
    await db.commit()
    return {"id": session.id, "name": session.name, "eval_type": session.eval_type}
