from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from apps.api.api.auth import get_current_org_id, get_current_user
from apps.api.api.routes.orgs import (
    _criticality_score,
    _last_30_dates,
    _repo_language_metadata,
    _repo_response,
    _score_response,
    _skill_alert,
)

from apps.api.api.analysis import _skill_category_for_domain
from apps.api.api.routes.webhook import _queue_analysis
from apps.api.api.services.memory import run_session_knowledge_extraction
from packages.db.database import get_db
from packages.db.models import AgentSession, AnalysisRun, Dependency, Repo, ScoreHistory, Skill, SkillMemoryStub, SkillUsageEvent, SkillVersion
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


class SkillContentUpdate(BaseModel):
    """Request body for manual skill content updates."""

    content: str = Field(min_length=1, max_length=200_000)


class SessionMessage(BaseModel):
    role: Literal["user", "assistant", "tool"]
    content: str


class SessionIngestionPayload(BaseModel):
    session_id: str = Field(max_length=128)
    agent_runtime: Literal["claude_code", "codex", "cursor", "copilot", "gemini", "other"]
    task_description: str | None = Field(default=None, max_length=1000)
    engineer_login: str | None = Field(default=None, max_length=128)
    duration_minutes: int | None = None
    files_touched: list[str] = Field(default_factory=list, max_length=500)
    skill_paths_loaded: list[str] = Field(default_factory=list, max_length=200)
    messages: list[SessionMessage] = Field(default_factory=list, max_length=500)


class SessionIngestionResponse(BaseModel):
    session_db_id: str
    status: Literal["created", "duplicate"]
    extraction_queued: bool


class AgentSessionResponse(BaseModel):
    id: str
    session_id: str
    agent_runtime: str
    task_description: str | None
    engineer_login: str | None
    duration_minutes: int | None
    files_touched: list[str]
    skill_paths_loaded: list[str]
    extraction_status: str
    discoveries_found: int
    created_at: datetime


class KnowledgeVelocityPoint(BaseModel):
    week_start: str
    discoveries: int


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


def _compute_skill_score(content: str) -> dict[str, int]:
    """Compute the lightweight 0-100 score used for manual content edits."""
    word_count = len(content.split())
    has_headings = bool(re.search(r"^#{1,3}\s", content, re.MULTILINE))
    heading_count = len(re.findall(r"^#{1,3}\s", content, re.MULTILINE))
    has_code_blocks = "```" in content
    file_ref_count = len(re.findall(r"`[^`]+\.(py|ts|tsx|js|go|rs|java|cs|rb|php)`", content))
    has_patterns_section = bool(re.search(r"pattern|example|usage|how.to", content, re.IGNORECASE))
    has_version_hint = bool(re.search(r"v\d+\.\d+|version|last.verified|updated", content, re.IGNORECASE))
    bullet_count = len(re.findall(r"^\s*[-*]\s", content, re.MULTILINE))

    groundedness = min(25, file_ref_count * 4 + (8 if has_code_blocks else 0) + (5 if has_patterns_section else 0))
    coverage = min(25, max(0, (word_count // 20)) + (heading_count * 3) + (bullet_count // 2))
    freshness = min(25, 10 + (15 if has_version_hint else 0))
    structure = min(25, (10 if has_headings else 0) + (heading_count * 3) + (5 if bullet_count >= 3 else 0))

    return {
        "total": groundedness + coverage + freshness + structure,
        "groundedness": groundedness,
        "coverage": coverage,
        "freshness": freshness,
        "structure": structure,
    }


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


async def _repo_score_history_rows(db: AsyncSession, repo_id: str, limit: int = 30) -> list[ScoreHistory]:
    """Load recent score history in ascending order for charting and projections."""
    rows = (
        await db.execute(
            select(ScoreHistory)
            .where(ScoreHistory.repo_id == repo_id)
            .order_by(desc(ScoreHistory.recorded_at))
            .limit(limit)
        )
    ).scalars().all()
    return list(reversed(rows))


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
    latest_skills = await _latest_repo_skills(db, repo.id)
    languages, derived_display_language = _repo_language_metadata(latest_skills, repo.language)
    response["default_branch"] = repo.default_branch
    response["installation_id"] = repo.github_installation_id
    response["languages"] = languages
    response["display_language"] = repo.language or derived_display_language
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


@router.patch("/{repo_id}/skills/{skill_id}/content")
async def update_repo_skill_content(
    repo_id: str,
    skill_id: str,
    payload: SkillContentUpdate,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    """Update stored skill content and create a new version for the edit."""
    await _repo_in_scope(db, repo_id, current_org_id)
    skill = await db.get(Skill, skill_id)
    if skill is None or skill.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Skill not found")

    content_hash = hashlib.sha256(payload.content.encode()).hexdigest()
    score = _compute_skill_score(payload.content)

    latest_version_number = (
        await db.execute(
            select(SkillVersion.version_number)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .order_by(desc(SkillVersion.version_number))
            .limit(1)
        )
    ).scalar_one_or_none()

    if content_hash == skill.content_hash:
        return {
            "updated": False,
            "version_number": int(latest_version_number or 1),
            "score": _score_response(skill).model_dump(),
        }

    try:
        await db.execute(
            update(SkillVersion)
            .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
            .values(is_latest=False)
        )
        count_result = await db.execute(
            select(func.count(SkillVersion.id)).where(SkillVersion.skill_id == skill.id)
        )
        version_number = int(count_result.scalar() or 0) + 1

        skill.content = payload.content
        skill.content_hash = content_hash
        skill.score_total = score["total"]
        skill.score_groundedness = score["groundedness"]
        skill.score_coverage = score["coverage"]
        skill.score_freshness = score["freshness"]
        skill.score_structure = score["structure"]
        skill.is_stale = False

        db.add(
            SkillVersion(
                skill_id=skill.id,
                run_id=skill.run_id or str(uuid4()),
                repo_id=repo_id,
                domain=skill.domain,
                content=payload.content,
                content_hash=content_hash,
                version_number=version_number,
                is_latest=True,
            )
        )
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to update skill content") from exc

    return {
        "updated": True,
        "version_number": version_number,
        "score": _score_response(skill).model_dump(),
    }


def _week_start(value: datetime) -> datetime:
    return (value - timedelta(days=value.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


@router.post("/{repo_id}/sessions", response_model=SessionIngestionResponse, status_code=201)
async def ingest_agent_session(
    repo_id: str,
    payload: SessionIngestionPayload,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SessionIngestionResponse:
    """Capture a coding-agent session for asynchronous knowledge extraction."""
    repo = await _repo_in_scope(db, repo_id, current_org_id)
    existing = (
        await db.execute(
            select(AgentSession).where(
                AgentSession.repo_id == repo_id,
                AgentSession.session_id == payload.session_id,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return SessionIngestionResponse(session_db_id=existing.id, status="duplicate", extraction_queued=False)

    session = AgentSession(
        repo_id=repo_id,
        org_id=repo.org_id,
        session_id=payload.session_id,
        agent_runtime=payload.agent_runtime,
        task_description=payload.task_description,
        engineer_login=payload.engineer_login,
        duration_minutes=payload.duration_minutes,
        files_touched=list(payload.files_touched),
        skill_paths_loaded=list(payload.skill_paths_loaded),
        raw_message_count=len(payload.messages),
        extraction_status="pending",
        discoveries_found=0,
    )
    db.add(session)
    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to capture session") from exc

    background_tasks.add_task(run_session_knowledge_extraction, session.id, payload.messages, repo_id)
    return SessionIngestionResponse(session_db_id=session.id, status="created", extraction_queued=True)


@router.get("/{repo_id}/sessions", response_model=list[AgentSessionResponse])
async def list_agent_sessions(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[AgentSessionResponse]:
    await _repo_in_scope(db, repo_id, current_org_id)
    sessions = (
        await db.execute(
            select(AgentSession)
            .where(AgentSession.repo_id == repo_id)
            .order_by(desc(AgentSession.created_at))
            .limit(20)
        )
    ).scalars().all()
    return [
        AgentSessionResponse(
            id=session.id,
            session_id=session.session_id,
            agent_runtime=session.agent_runtime,
            task_description=session.task_description,
            engineer_login=session.engineer_login,
            duration_minutes=session.duration_minutes,
            files_touched=list(session.files_touched or []),
            skill_paths_loaded=list(session.skill_paths_loaded or []),
            extraction_status=session.extraction_status,
            discoveries_found=int(session.discoveries_found or 0),
            created_at=session.created_at,
        )
        for session in sessions
    ]


@router.get("/{repo_id}/knowledge-velocity", response_model=list[KnowledgeVelocityPoint])
async def repo_knowledge_velocity(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[KnowledgeVelocityPoint]:
    await _repo_in_scope(db, repo_id, current_org_id)
    now = datetime.now(UTC).replace(tzinfo=None)
    this_week = _week_start(now)
    week_starts = [this_week - timedelta(weeks=offset) for offset in range(8)]
    oldest = week_starts[-1]
    rows = (
        await db.execute(
            select(SkillMemoryStub.created_at)
            .where(
                SkillMemoryStub.repo_id == repo_id,
                SkillMemoryStub.status != "rejected",
                SkillMemoryStub.created_at >= oldest,
            )
        )
    ).all()
    counts = {week.date().isoformat(): 0 for week in week_starts}
    for row in rows:
        created_at = getattr(row, "created_at", None) or row[0]
        if isinstance(created_at, datetime):
            key = _week_start(created_at).date().isoformat()
            if key in counts:
                counts[key] += 1
    return [KnowledgeVelocityPoint(week_start=week.date().isoformat(), discoveries=counts[week.date().isoformat()]) for week in week_starts]


@router.get("/{repo_id}/score-history")
async def get_score_history(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, object]]:
    # TODO: restore org-scoped auth before GA. Read-only repo browsing is public during dashboard bootstrap.
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    rows = await _repo_score_history_rows(db, repo_id, limit=10)
    return [
        {
            "date": row.recorded_at.date().isoformat(),
            "score_total": row.score_total,
            "groundedness": row.score_groundedness,
            "coverage": row.score_coverage,
            "freshness": row.score_freshness,
            "structure": row.score_structure,
        }
        for row in rows
    ]


@router.get("/{repo_id}/score-forecast")
async def get_score_forecast(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Return a simple linear forecast for 30/90-day score based on score history."""
    import statistics

    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")

    history = await _repo_score_history_rows(db, repo_id, limit=30)
    if len(history) < 2:
        return {
            "has_forecast": False,
            "reason": "Not enough history — analyse more frequently to enable forecasting.",
            "current_score": int(history[-1].score_total) if history else None,
            "forecast_30d": None,
            "forecast_90d": None,
            "trend": "stable",
        }

    scores = [int(point.score_total or 0) for point in history]
    n = len(scores)
    x_vals = list(range(n))
    x_mean = statistics.mean(x_vals)
    y_mean = statistics.mean(scores)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, scores))
    denominator = sum((x - x_mean) ** 2 for x in x_vals)
    slope = numerator / denominator if denominator != 0 else 0

    total_days = max(1, (history[-1].recorded_at - history[0].recorded_at).days)
    days_per_point = total_days / (n - 1) if n > 1 else 7

    slope_per_day = slope / max(days_per_point, 1)
    current = scores[-1]
    forecast_30 = max(0, min(100, round(current + slope_per_day * 30)))
    forecast_90 = max(0, min(100, round(current + slope_per_day * 90)))
    trend = "improving" if slope_per_day > 0.1 else "declining" if slope_per_day < -0.1 else "stable"

    return {
        "has_forecast": True,
        "current_score": current,
        "forecast_30d": forecast_30,
        "forecast_90d": forecast_90,
        "trend": trend,
        "slope_per_day": round(slope_per_day, 3),
        "data_points": n,
        "reason": None,
    }


@router.get("/{repo_id}/skills/{skill_id}/versions/{version_id}/diff")
async def get_skill_version_diff(
    repo_id: str,
    skill_id: str,
    version_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Return line-level diff between a skill version and its predecessor."""
    from difflib import unified_diff

    skill = await db.get(Skill, skill_id)
    if skill is None or skill.repo_id != repo_id:
        raise HTTPException(status_code=404, detail="Skill not found")

    version = await db.get(SkillVersion, version_id)
    if version is None or version.skill_id != skill_id:
        raise HTTPException(status_code=404, detail="Skill version not found")

    previous_version = (
        await db.execute(
            select(SkillVersion)
            .where(
                SkillVersion.skill_id == skill_id,
                SkillVersion.version_number < version.version_number,
            )
            .order_by(desc(SkillVersion.version_number))
            .limit(1)
        )
    ).scalar_one_or_none()

    old_content = previous_version.content if previous_version else ""
    new_content = version.content or ""
    old_lines = (old_content or "").splitlines(keepends=True)
    new_lines = (new_content or "").splitlines(keepends=True)
    diff = list(
        unified_diff(
            old_lines,
            new_lines,
            fromfile=f"v{previous_version.version_number if previous_version else 0}",
            tofile=f"v{version.version_number}",
            lineterm="",
        )
    )

    lines: list[dict[str, str]] = []
    if previous_version is None:
        for line in (version.content or "").splitlines():
            lines.append({"type": "added", "text": line})
    else:
        for line in diff:
            if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
                lines.append({"type": "meta", "text": line})
            elif line.startswith("+"):
                lines.append({"type": "added", "text": line[1:]})
            elif line.startswith("-"):
                lines.append({"type": "removed", "text": line[1:]})
            else:
                lines.append({"type": "context", "text": line[1:] if line.startswith(" ") else line})

    return {
        "skill_id": skill_id,
        "repo_id": repo_id,
        "domain": skill.domain,
        "version_id": version_id,
        "version_number": version.version_number,
        "prev_version_number": previous_version.version_number if previous_version else None,
        "is_first_version": previous_version is None,
        "lines": lines,
        "added_count": sum(1 for line in lines if line["type"] == "added"),
        "removed_count": sum(1 for line in lines if line["type"] == "removed"),
    }


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


@router.post("/{repo_id}/backfill-categories")
async def backfill_skill_categories(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, int]:
    """Re-infer skill_category for all existing skills in a repo without re-running analysis.

    Uses the same domain/path keyword mapping as analysis.py so the categories
    are consistent with future analysis runs.
    """
    repo = await db.get(Repo, repo_id)
    if repo is None or repo.org_id != current_org_id:
        raise HTTPException(status_code=404, detail="Repo not found")

    skills_result = await db.execute(select(Skill).where(Skill.repo_id == repo_id))
    skills = skills_result.scalars().all()

    updated = 0
    for skill in skills:
        source_type = str(skill.source_type or "code")
        if source_type != "code":
            new_category = skill_category_for_source_type(source_type)
        else:
            new_category = _skill_category_for_domain(
                str(skill.domain or ""),
                str(skill.skill_path or ""),
            )
        if skill.skill_category != new_category:
            skill.skill_category = new_category
            updated += 1

    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to backfill categories") from exc

    return {"updated": updated, "total": len(skills)}


class _LocalUsageEvent(BaseModel):
    skill_path: str
    agent_runtime: str = "unknown"
    session_id: str = ""
    timestamp: str = ""


class _SyncAnalyticsPayload(BaseModel):
    repo_id: str
    events: list[_LocalUsageEvent]


@router.post("/{repo_id}/sync-analytics")
async def sync_repo_analytics(
    repo_id: str,
    payload: _SyncAnalyticsPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, int]:
    """Sync local ``.skilgen/analytics/usage.jsonl`` events to the API database.

    Maps skill paths to DB skill records and increments ``load_count_30d``
    so the dashboard heatmap reflects real agent usage data.
    """
    repo = await db.get(Repo, repo_id)
    if repo is None or repo.org_id != current_org_id:
        raise HTTPException(status_code=404, detail="Repo not found")

    skills_result = await db.execute(select(Skill).where(Skill.repo_id == repo_id))
    skills_by_path: dict[str, Skill] = {
        str(skill.skill_path or "").strip("/"): skill
        for skill in skills_result.scalars().all()
    }

    now = datetime.now(UTC).replace(tzinfo=None)
    synced = 0
    skipped = 0

    for event in payload.events:
        normalized = event.skill_path.strip("/").removeprefix(".skilgen/").removeprefix("skilgen/")
        skill = skills_by_path.get(event.skill_path.strip("/")) or skills_by_path.get(normalized)
        if skill is None:
            skipped += 1
            continue

        try:
            loaded_at = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00")).replace(tzinfo=None)
        except (ValueError, AttributeError):
            loaded_at = now

        skill.load_count_30d = int(skill.load_count_30d or 0) + 1
        if skill.last_loaded_at is None or loaded_at > skill.last_loaded_at:
            skill.last_loaded_at = loaded_at

        db.add(
            SkillUsageEvent(
                org_id=current_org_id,
                repo_id=repo_id,
                skill_id=skill.id,
                agent_runtime=event.agent_runtime[:100] or "unknown",
                session_id=event.session_id[:255] or str(uuid4()),
                loaded_at=loaded_at,
            )
        )
        synced += 1

    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to sync analytics") from exc

    return {"synced": synced, "skipped": skipped}
