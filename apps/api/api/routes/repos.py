from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_user
from apps.api.api.routes.orgs import (
    _criticality_score,
    _last_30_dates,
    _repo_response,
    _score_response,
    _skill_alert,
)
from apps.api.api.routes.webhook import _queue_analysis
from packages.db.database import get_db
from packages.db.models import AnalysisRun, Dependency, Repo, ScoreHistory, Skill, SkillUsageEvent, SkillVersion
from packages.db.models.skill import skill_category_for_source_type
from packages.db.schemas import (
    AnalysisRunResponse,
    AnalyzeSourceResponse,
    DependencyReportResponse,
    DailyLoadPointResponse,
    DependencyResponse,
    RepoSkillSourceSummary,
    RepoSkillSourcesResponse,
    RepoSkillUsageStatsResponse,
    SkillCategoryCoverage,
    SkillSourceSkillSummary,
)
from skilgen.core.score import render_repo_score_badge_svg


router = APIRouter(prefix="/repos", tags=["repos"])

SKILL_CATEGORIES = [
    "codebase_architecture",
    "code_style",
    "testing_conventions",
    "internal_tools",
    "security_compliance",
    "design_system",
    "data_schema",
    "operational_knowledge",
]

SOURCE_TYPES = [
    "code",
    "openapi",
    "graphql",
    "postman",
    "terraform",
    "kubernetes",
    "helm",
    "dbt",
    "sql_schema",
    "kafka",
    "sarif",
    "sbom",
    "security_policy",
    "runbook",
    "confluence",
    "notion",
    "incident",
    "pagerduty",
]


class ManualAnalysisRequest(BaseModel):
    installation_id: int | None = None


class AnalyzeSourceRequest(BaseModel):
    """Request body for source-specific analysis jobs."""

    source_type: Literal[
        "openapi",
        "graphql",
        "postman",
        "terraform",
        "kubernetes",
        "helm",
        "dbt",
        "sql_schema",
        "kafka",
        "sarif",
        "sbom",
        "security_policy",
        "runbook",
        "confluence",
        "notion",
        "incident",
        "pagerduty",
    ]
    path: str | None = Field(default=None, max_length=512)


async def _repo_in_scope(db: AsyncSession, repo_id: str, org_id: str) -> Repo:
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return repo


def _normalized_source_type(skill: Skill) -> str:
    """Return the persisted source type or the backwards-compatible default."""
    return str(skill.source_type or "code")


def _normalized_skill_category(skill: Skill) -> str:
    """Return the persisted skill category or derive one from source type."""
    return str(skill.skill_category or skill_category_for_source_type(_normalized_source_type(skill)))


def _coverage_score(coverage_map: dict[str, SkillCategoryCoverage]) -> int:
    """Compute the 0-100 category coverage score."""
    covered = sum(1 for item in coverage_map.values() if item.covered)
    return round((covered / len(SKILL_CATEGORIES)) * 100)


async def _latest_repo_skills(db: AsyncSession, repo_id: str) -> list[Skill]:
    """Return latest skills by domain for a repository."""
    rows = (
        await db.execute(select(Skill).where(Skill.repo_id == repo_id).order_by(desc(Skill.created_at)))
    ).scalars().all()
    latest_by_domain: dict[str, Skill] = {}
    for skill in rows:
        latest_by_domain.setdefault(skill.domain, skill)
    return list(latest_by_domain.values())


def _build_coverage_map(skills: list[Skill]) -> dict[str, SkillCategoryCoverage]:
    """Build the eight-category coverage map used by API and dashboard."""
    grouped: dict[str, list[Skill]] = {category: [] for category in SKILL_CATEGORIES}
    for skill in skills:
        category = _normalized_skill_category(skill)
        if category in grouped:
            grouped[category].append(skill)
    coverage_map: dict[str, SkillCategoryCoverage] = {}
    for category, category_skills in grouped.items():
        avg = 0
        if category_skills:
            avg = round(sum(int(skill.score_total or 0) for skill in category_skills) / len(category_skills))
        coverage_map[category] = SkillCategoryCoverage(
            covered=bool(category_skills),
            skill_count=len(category_skills),
            avg_score=avg,
        )
    return coverage_map

async def _latest_repo_score_total(db: AsyncSession, repo_id: str) -> int:
    """Return the most recent stored score total for a repository."""
    latest_run = (
        await db.execute(
            select(AnalysisRun.score_total)
            .where(AnalysisRun.repo_id == repo_id, AnalysisRun.status == "complete")
            .order_by(desc(AnalysisRun.created_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    if latest_run is not None:
        return int(latest_run or 0)
    latest_history = (
        await db.execute(
            select(ScoreHistory.score_total)
            .where(ScoreHistory.repo_id == repo_id)
            .order_by(desc(ScoreHistory.recorded_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    return int(latest_history or 0)


def _dependency_upgrade_command(dependency: Dependency) -> str | None:
    """Return the safest package-manager upgrade command for a dependency."""
    ecosystem = str(dependency.ecosystem or "").lower()
    if ecosystem == "pip":
        return f"python -m pip install --upgrade {dependency.name}"
    if ecosystem == "npm":
        return f"npm update {dependency.name}"
    if ecosystem == "cargo":
        return f"cargo update -p {dependency.name}"
    if ecosystem == "go":
        return f"go get {dependency.name}@latest"
    return None


def _dependency_response(dependency: Dependency) -> DependencyResponse:
    """Serialize a stored dependency row for API responses."""
    raw_cves = dependency.cves or []
    cves = [str(item) for item in raw_cves] if isinstance(raw_cves, list) else []
    return DependencyResponse(
        id=str(dependency.id),
        name=str(dependency.name),
        version=dependency.version,
        ecosystem=str(dependency.ecosystem),
        risk_level=str(dependency.risk_level),
        cves=cves,
        latest_version=dependency.latest_version,
        license=dependency.license,
        created_at=dependency.created_at,
        upgrade_command=_dependency_upgrade_command(dependency),
    )


def _dependency_risk_score(dependencies: list[Dependency]) -> int:
    """Compute a 0-100 dependency risk score where lower means safer."""
    weights = {"high": 30, "medium": 15, "low": 5, "healthy": 0}
    return min(100, sum(weights.get(str(item.risk_level), 0) for item in dependencies))


@router.get("/{repo_id}")
async def get_repo(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    # TODO: restore org-scoped auth before GA. Read-only repo browsing is public during dashboard bootstrap.
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    response = (await _repo_response(db, repo)).model_dump()
    response["default_branch"] = repo.default_branch
    response["installation_id"] = repo.github_installation_id
    return response

@router.get("/{repo_id}/score-badge")
async def get_repo_score_badge(
    repo_id: str,
    style: Literal["flat", "flat-square", "for-the-badge"] = Query(default="flat"),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Return an SVG Skilgen Score badge for the repository."""
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    score_total = await _latest_repo_score_total(db, repo_id)
    svg = render_repo_score_badge_svg(score_total, style=style)
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/{repo_id}/skills")
async def get_repo_skills(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, object]]:
    # TODO: restore org-scoped auth before GA. Read-only repo browsing is public during dashboard bootstrap.
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    skills = sorted(await _latest_repo_skills(db, repo_id), key=lambda item: (-int(item.score_total or 0), item.domain))
    responses: list[dict[str, object]] = []
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
        score = _score_response(skill)  # type: ignore[arg-type]
        responses.append({
            "id": skill.id,
            "repo_id": repo.id,
            "repo_name": repo.name,
            "domain": skill.domain,
            "skill_path": skill.skill_path,
            "score": score.model_dump() if score else None,
            "content": (skill.content[:500] if skill.content else None),
            "content_hash": skill.content_hash,
            "source_type": _normalized_source_type(skill),
            "skill_category": _normalized_skill_category(skill),
            "is_stale": skill.is_stale,
            "load_count_30d": skill.load_count_30d,
            "last_loaded_at": skill.last_loaded_at,
            "version_count": int(version_count or 0),
            "latest_version_number": (latest_version.version_number if latest_version else None),
            "last_updated_at": latest_version.created_at if latest_version else skill.created_at,
        })
    return responses


@router.get("/{repo_id}/skills/{skill_id}/usage-stats", response_model=RepoSkillUsageStatsResponse)
async def get_repo_skill_usage_stats(
    repo_id: str,
    skill_id: str,
    db: AsyncSession = Depends(get_db),
) -> RepoSkillUsageStatsResponse:
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Skill not found")

    now = datetime.now(UTC).replace(tzinfo=None)
    cutoff_30d = now - timedelta(days=30)
    cutoff_7d = now - timedelta(days=7)
    daily_label = func.date(SkillUsageEvent.loaded_at).label("day")

    try:
        usage = (
            await db.execute(
                select(
                    func.count(SkillUsageEvent.id).label("loads_30d"),
                    func.count(SkillUsageEvent.id).filter(SkillUsageEvent.loaded_at >= cutoff_7d).label("loads_7d"),
                    func.max(SkillUsageEvent.loaded_at).label("last_loaded_at"),
                )
                .where(SkillUsageEvent.skill_id == skill_id, SkillUsageEvent.loaded_at >= cutoff_30d)
            )
        ).one()
        daily_rows = (
            await db.execute(
                select(daily_label, func.count(SkillUsageEvent.id).label("loads"))
                .where(SkillUsageEvent.skill_id == skill_id, SkillUsageEvent.loaded_at >= cutoff_30d)
                .group_by(daily_label)
                .order_by(daily_label)
            )
        ).all()
        repo_max_loads = (
            await db.execute(select(func.max(Skill.load_count_30d)).where(Skill.repo_id == repo_id))
        ).scalar_one_or_none()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to load skill usage stats") from exc

    try:
        runtime_rows = (
            await db.execute(
                select(SkillUsageEvent.agent_runtime, func.count(SkillUsageEvent.id).label("loads"))
                .where(SkillUsageEvent.skill_id == skill_id, SkillUsageEvent.loaded_at >= cutoff_30d)
                .group_by(SkillUsageEvent.agent_runtime)
                .order_by(desc(func.count(SkillUsageEvent.id)))
            )
        ).all()
        runtime_counts = {str(row.agent_runtime or "unknown"): int(row.loads or 0) for row in runtime_rows}
    except Exception:
        await db.rollback()
        runtime_counts = {"unknown": int(usage.loads_30d or 0)}

    daily_map = {str(row.day): int(row.loads or 0) for row in daily_rows}
    loads_30d = int(usage.loads_30d or 0)
    loads_7d = int(usage.loads_7d or 0)
    last_loaded_at = usage.last_loaded_at

    return RepoSkillUsageStatsResponse(
        criticality_score=_criticality_score(loads_30d, last_loaded_at, bool(skill.is_stale), int(repo_max_loads or 1)),
        loads_30d=loads_30d,
        loads_7d=loads_7d,
        last_loaded_at=last_loaded_at,
        alert=_skill_alert(skill, loads_30d, now),
        daily_loads=[DailyLoadPointResponse(date=day, loads=daily_map.get(day, 0)) for day in _last_30_dates(now)],
        agent_runtimes=runtime_counts,
    )


@router.get("/{repo_id}/score-history")
async def get_score_history(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, object]]:
    # TODO: restore org-scoped auth before GA. Read-only repo browsing is public during dashboard bootstrap.
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    rows = (
        await db.execute(
            select(ScoreHistory)
            .where(ScoreHistory.repo_id == repo_id)
            .order_by(desc(ScoreHistory.recorded_at))
            .limit(10)
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


@router.get("/{repo_id}/skill-sources", response_model=RepoSkillSourcesResponse)
async def get_repo_skill_sources(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> RepoSkillSourcesResponse:
    """Return source-type and category coverage for a repository."""
    await _repo_in_scope(db, repo_id, current_org_id)
    try:
        skills = await _latest_repo_skills(db, repo_id)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"detail": "Unable to load skill source coverage", "code": "SKILL_SOURCES_FAILED"},
        ) from exc

    sources: list[RepoSkillSourceSummary] = []
    for source_type in SOURCE_TYPES:
        source_skills = [skill for skill in skills if _normalized_source_type(skill) == source_type]
        if not source_skills and source_type != "code":
            continue
        source_skills.sort(key=lambda skill: (-int(skill.score_total or 0), skill.domain))
        sources.append(
            RepoSkillSourceSummary(
                source_type=source_type,
                detected=bool(source_skills),
                skill_count=len(source_skills),
                last_analysed_at=max((skill.created_at for skill in source_skills), default=None),
                skills=[
                    SkillSourceSkillSummary(id=skill.id, domain=skill.domain, score=int(skill.score_total or 0))
                    for skill in source_skills
                ],
            )
        )
    coverage_map = _build_coverage_map(skills)
    return RepoSkillSourcesResponse(
        sources=sources,
        coverage_map=coverage_map,
        coverage_score=_coverage_score(coverage_map),
    )


@router.get("/{repo_id}/dependencies", response_model=DependencyReportResponse)
async def get_dependencies(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> DependencyReportResponse:
    """Return the latest dependency risk report for a repo in the current org."""
    await _repo_in_scope(db, repo_id, current_org_id)
    try:
        latest_run_result = await db.execute(
            select(AnalysisRun.id)
            .join(Dependency, Dependency.run_id == AnalysisRun.id)
            .where(AnalysisRun.repo_id == repo_id)
            .order_by(desc(AnalysisRun.created_at))
            .limit(1)
        )
        latest_run_id = latest_run_result.scalar_one_or_none()
        if latest_run_id is None:
            return DependencyReportResponse(high_risk=[], medium_risk=[], healthy=[], total_count=0, risk_score=0)

        dependencies = (
            await db.execute(
                select(Dependency)
                .where(Dependency.repo_id == repo_id, Dependency.run_id == latest_run_id)
                .order_by(Dependency.risk_level, Dependency.ecosystem, Dependency.name)
            )
        ).scalars().all()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"detail": "Unable to load dependency risk report", "code": "DEPENDENCY_REPORT_FAILED"},
        ) from exc

    high_risk = [_dependency_response(item) for item in dependencies if item.risk_level == "high"]
    medium_risk = [_dependency_response(item) for item in dependencies if item.risk_level == "medium"]
    healthy = [_dependency_response(item) for item in dependencies if item.risk_level == "healthy"]
    return DependencyReportResponse(
        high_risk=high_risk,
        medium_risk=medium_risk,
        healthy=healthy,
        total_count=len(dependencies),
        risk_score=_dependency_risk_score(list(dependencies)),
    )


@router.get("/{repo_id}/runs", response_model=list[AnalysisRunResponse])
async def get_runs(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[AnalysisRunResponse]:
    # TODO: restore org-scoped auth before GA. Read-only repo browsing is public during dashboard bootstrap.
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
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
    installation_id = (payload.installation_id if payload else None) or repo.github_installation_id
    if not installation_id:
        raise HTTPException(status_code=400, detail="Repo installation id is not available")
    run = AnalysisRun(
        repo_id=repo_id,
        trigger="manual",
        status="queued",
        branch=repo.default_branch,
        created_at=datetime.utcnow(),
    )
    db.add(run)
    await db.flush()
    await db.commit()
    await _queue_analysis(
        request,
        background_tasks,
        {
            "run_id": run.id,
            "repo_id": repo.id,
            "installation_id": int(installation_id),
            "full_name": repo.full_name,
            "ref": repo.default_branch,
        },
    )
    return {"queued": run.id}


@router.post("/{repo_id}/analyze-source", response_model=AnalyzeSourceResponse)
async def trigger_source_analysis(
    repo_id: str,
    payload: AnalyzeSourceRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
    _current_user: dict[str, object] = Depends(get_current_user),
) -> AnalyzeSourceResponse:
    """Queue a source-specific analysis run for a repository."""
    repo = await _repo_in_scope(db, repo_id, current_org_id)
    if not repo.github_installation_id:
        raise HTTPException(
            status_code=400,
            detail={"detail": "Repo installation id is not available", "code": "INSTALLATION_ID_MISSING"},
        )
    run = AnalysisRun(
        repo_id=repo_id,
        trigger=f"source:{payload.source_type}",
        status="queued",
        branch=repo.default_branch,
        created_at=datetime.utcnow(),
    )
    try:
        db.add(run)
        await db.flush()
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"detail": "Could not queue source analysis", "code": "SOURCE_ANALYSIS_QUEUE_FAILED"},
        ) from exc

    await _queue_analysis(
        request,
        background_tasks,
        {
            "run_id": run.id,
            "repo_id": repo.id,
            "installation_id": int(repo.github_installation_id),
            "full_name": repo.full_name,
            "ref": repo.default_branch,
            "source_type": payload.source_type,
            "source_path": payload.path,
        },
    )
    return AnalyzeSourceResponse(job_id=run.id, status="queued")
