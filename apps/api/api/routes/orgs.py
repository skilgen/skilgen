from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import desc, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from apps.api.api.notifications import build_test_notification_message, post_slack_message
from packages.db.database import get_db
from packages.db.models import AnalysisRun, Org, Repo, ScoreHistory, Skill, SkillUsageEvent
from packages.db.models.skill import skill_category_for_source_type
from packages.db.schemas import (
    OrgCoverageSummaryResponse,
    OrgResponse,
    OrgSettingsResponse,
    OrgSettingsUpdate,
    RepoCoverageSummary,
    RepoResponse,
    ScoreResponse,
)


router = APIRouter(prefix="/orgs", tags=["orgs"])
logger = logging.getLogger(__name__)

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


def _error(status_code: int, detail: str, code: str) -> JSONResponse:
    """Build a structured JSON error response for organization routes."""
    return JSONResponse(status_code=status_code, content={"detail": detail, "code": code})


def _skill_category(skill: Skill) -> str:
    """Return the skill category persisted in DB or derive it from source type."""
    return str(skill.skill_category or skill_category_for_source_type(skill.source_type))


def _repo_coverage_score(skills: list[Skill]) -> tuple[int, list[str]]:
    """Return the coverage score and missing categories for a repo skill set."""
    covered = {_skill_category(skill) for skill in skills if _skill_category(skill) in SKILL_CATEGORIES}
    missing = [category for category in SKILL_CATEGORIES if category not in covered]
    return round((len(covered) / len(SKILL_CATEGORIES)) * 100), missing


async def _rollback(db: AsyncSession, context: str) -> None:
    """Rollback an org route transaction and log rollback failures."""
    try:
        await db.rollback()
    except Exception:
        logger.exception("Org route rollback failed during %s", context)


def _org_settings_response(org: Org, installation_id: int | None, recent_runs: list[AnalysisRun]) -> OrgSettingsResponse:
    """Convert an org and its GitHub state into a settings response."""
    return OrgSettingsResponse(
        id=org.id,
        login=org.login,
        name=org.name,
        plan=org.plan,
        score_threshold=int(org.score_threshold or 60),
        slack_webhook_url=org.slack_webhook_url,
        notify_on_pr=bool(org.notify_on_pr),
        notify_on_stale=bool(org.notify_on_stale),
        github_app_installed=installation_id is not None,
        github_installation_id=installation_id,
        webhook_url="/webhook/github",
        recent_deliveries=[
            {
                "id": run.id,
                "status": run.status,
                "trigger": run.trigger,
                "created_at": run.created_at.isoformat() if run.created_at else None,
            }
            for run in recent_runs
        ],
    )


async def _load_org_settings(db: AsyncSession, org: Org) -> OrgSettingsResponse:
    """Load org settings plus lightweight GitHub installation state."""
    installation_id = (
        await db.execute(
            select(Repo.github_installation_id)
            .where(Repo.org_id == org.id, Repo.github_installation_id.is_not(None), Repo.is_active.is_(True))
            .order_by(desc(Repo.created_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    recent_runs = (
        await db.execute(
            select(AnalysisRun)
            .join(Repo, Repo.id == AnalysisRun.repo_id)
            .where(Repo.org_id == org.id)
            .order_by(desc(AnalysisRun.created_at))
            .limit(5)
        )
    ).scalars().all()
    return _org_settings_response(org, installation_id, list(recent_runs))


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


@router.get("/{org_id}/coverage-summary", response_model=OrgCoverageSummaryResponse)
async def get_org_coverage_summary(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgCoverageSummaryResponse:
    """Return per-repo knowledge coverage for the authenticated organization."""
    _assert_org_scope(org_id, current_org_id)
    try:
        repos = (
            await db.execute(
                select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)).order_by(Repo.full_name)
            )
        ).scalars().all()
        summaries: list[RepoCoverageSummary] = []
        missing_counts = {category: 0 for category in SKILL_CATEGORIES}
        for repo in repos:
            skills = (
                await db.execute(select(Skill).where(Skill.repo_id == repo.id).order_by(desc(Skill.created_at)))
            ).scalars().all()
            latest_by_domain: dict[str, Skill] = {}
            for skill in skills:
                latest_by_domain.setdefault(skill.domain, skill)
            score, missing = _repo_coverage_score(list(latest_by_domain.values()))
            for category in missing:
                missing_counts[category] += 1
            summaries.append(
                RepoCoverageSummary(
                    repo_id=repo.id,
                    name=repo.name,
                    coverage_score=score,
                    missing_categories=missing,
                )
            )
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"detail": "Unable to load org coverage summary", "code": "COVERAGE_SUMMARY_FAILED"},
        ) from exc

    org_score = round(sum(repo.coverage_score for repo in summaries) / len(summaries)) if summaries else 0
    most_missing = None
    if summaries:
        most_missing = max(missing_counts.items(), key=lambda item: item[1])[0]
    return OrgCoverageSummaryResponse(
        repos=summaries,
        org_coverage_score=org_score,
        most_missing_category=most_missing,
    )


@router.get("/{org_id}/settings", response_model=OrgSettingsResponse)
async def get_org_settings(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgSettingsResponse | JSONResponse:
    """Return organization settings for the authenticated organization."""
    _assert_org_scope(org_id, current_org_id)
    try:
        org = await db.get(Org, org_id)
        if org is None:
            return _error(404, "Org not found", "ORG_NOT_FOUND")
        return await _load_org_settings(db, org)
    except SQLAlchemyError:
        await _rollback(db, "org settings lookup")
        return _error(400, "Could not load org settings", "ORG_SETTINGS_LOOKUP_FAILED")


@router.patch("/{org_id}/settings", response_model=OrgSettingsResponse)
async def update_org_settings(
    org_id: str,
    payload: OrgSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgSettingsResponse | JSONResponse:
    """Update organization settings for the authenticated organization."""
    _assert_org_scope(org_id, current_org_id)
    try:
        org = await db.get(Org, org_id)
        if org is None:
            return _error(404, "Org not found", "ORG_NOT_FOUND")

        fields = payload.model_fields_set
        if "name" in fields and payload.name is not None:
            org.name = payload.name
        if "score_threshold" in fields and payload.score_threshold is not None:
            org.score_threshold = payload.score_threshold
        if "slack_webhook_url" in fields:
            org.slack_webhook_url = str(payload.slack_webhook_url) if payload.slack_webhook_url else None
        if "notify_on_pr" in fields and payload.notify_on_pr is not None:
            org.notify_on_pr = payload.notify_on_pr
        if "notify_on_stale" in fields and payload.notify_on_stale is not None:
            org.notify_on_stale = payload.notify_on_stale

        await db.flush()
        await db.commit()
        return await _load_org_settings(db, org)
    except SQLAlchemyError:
        await _rollback(db, "org settings update")
        return _error(400, "Could not update org settings", "ORG_SETTINGS_UPDATE_FAILED")


@router.post("/{org_id}/test-notification", response_model=None)
async def test_org_notification(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, bool] | JSONResponse:
    """Send a test Slack notification for the authenticated organization."""
    _assert_org_scope(org_id, current_org_id)
    try:
        org = await db.get(Org, org_id)
    except SQLAlchemyError:
        await _rollback(db, "org test notification lookup")
        return _error(400, "Could not load org settings", "ORG_SETTINGS_LOOKUP_FAILED")
    if org is None:
        return _error(404, "Org not found", "ORG_NOT_FOUND")
    if not org.slack_webhook_url:
        return _error(400, "Slack webhook URL is not configured", "SLACK_WEBHOOK_NOT_CONFIGURED")
    try:
        await post_slack_message(org.slack_webhook_url, build_test_notification_message(org))
    except Exception:
        return _error(502, "Could not send Slack test notification", "SLACK_TEST_FAILED")
    return {"ok": True}


def _last_30_dates(now: datetime) -> list[str]:
    """Return the inclusive UTC date labels for the current 30-day window."""
    start = now.date() - timedelta(days=29)
    return [(start + timedelta(days=offset)).isoformat() for offset in range(30)]


@router.get("/{org_id}/analytics")
async def get_org_analytics(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    """Return org-scoped skill usage analytics for the dashboard."""
    _assert_org_scope(org_id, current_org_id)
    now = datetime.now(UTC).replace(tzinfo=None)
    cutoff = now - timedelta(days=30)
    try:
        total_skills = (
            await db.execute(
                select(func.count(Skill.id))
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Repo.org_id == org_id, Repo.is_active.is_(True))
            )
        ).scalar_one()
        usage_totals = (
            await db.execute(
                select(
                    func.coalesce(func.sum(Skill.load_count_30d), 0).label("total_loads"),
                    func.count(Skill.id).filter(Skill.load_count_30d > 0).label("unique_loaded"),
                )
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Repo.org_id == org_id, Repo.is_active.is_(True))
            )
        ).one()
        top_rows = (
            await db.execute(
                select(Skill, Repo.name.label("repo_name"), Repo.full_name.label("repo_full_name"))
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Repo.org_id == org_id, Repo.is_active.is_(True), Skill.load_count_30d > 0)
                .order_by(desc(Skill.load_count_30d), Skill.domain)
                .limit(10)
            )
        ).all()
        never_rows = (
            await db.execute(
                select(Skill, Repo.name.label("repo_name"), Repo.full_name.label("repo_full_name"))
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Repo.org_id == org_id, Repo.is_active.is_(True), Skill.load_count_30d == 0)
                .order_by(Repo.full_name, Skill.domain)
                .limit(25)
            )
        ).all()
        agent_rows = (
            await db.execute(
                select(SkillUsageEvent.agent_runtime, func.count(SkillUsageEvent.id))
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff)
                .group_by(SkillUsageEvent.agent_runtime)
                .order_by(desc(func.count(SkillUsageEvent.id)))
            )
        ).all()
        daily_label = func.date(SkillUsageEvent.loaded_at).label("day")
        daily_rows = (
            await db.execute(
                select(daily_label, func.count(SkillUsageEvent.id))
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff)
                .group_by(daily_label)
                .order_by(daily_label)
            )
        ).all()
        repo_loads = func.coalesce(func.sum(Skill.load_count_30d), 0).label("loads")
        repo_rows = (
            await db.execute(
                select(Repo.id, Repo.name, Repo.full_name, repo_loads)
                .join(Skill, Skill.repo_id == Repo.id)
                .where(Repo.org_id == org_id, Repo.is_active.is_(True))
                .group_by(Repo.id, Repo.name, Repo.full_name)
                .order_by(desc(repo_loads), Repo.full_name)
                .limit(1)
            )
        ).first()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to load org analytics") from exc

    daily_counts = {str(row[0]): int(row[1] or 0) for row in daily_rows}
    daily_loads = [{"date": day, "loads": daily_counts.get(day, 0)} for day in _last_30_dates(now)]
    top_skills = [
        {
            "id": skill.id,
            "domain": skill.domain,
            "skill_path": skill.skill_path,
            "repo_id": skill.repo_id,
            "repo_name": repo_name,
            "repo_full_name": repo_full_name,
            "loads": int(skill.load_count_30d or 0),
            "last_loaded_at": skill.last_loaded_at,
        }
        for skill, repo_name, repo_full_name in top_rows
    ]
    never_loaded = [
        {
            "id": skill.id,
            "domain": skill.domain,
            "skill_path": skill.skill_path,
            "repo_id": skill.repo_id,
            "repo_name": repo_name,
            "repo_full_name": repo_full_name,
        }
        for skill, repo_name, repo_full_name in never_rows
    ]
    most_active_repo = None
    if repo_rows is not None:
        most_active_repo = {
            "id": repo_rows.id,
            "name": repo_rows.name,
            "full_name": repo_rows.full_name,
            "loads": int(repo_rows.loads or 0),
        }
    return {
        "total_loads_30d": int(usage_totals.total_loads or 0),
        "unique_skills_loaded": int(usage_totals.unique_loaded or 0),
        "total_skills": int(total_skills or 0),
        "top_skills": top_skills,
        "never_loaded": never_loaded,
        "agent_breakdown": {str(agent): int(count or 0) for agent, count in agent_rows},
        "daily_loads": daily_loads,
        "most_active_repo": most_active_repo,
        "most_loaded_skill": top_skills[0] if top_skills else None,
    }
