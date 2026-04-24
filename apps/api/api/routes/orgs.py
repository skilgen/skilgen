from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_org_id_optional
from apps.api.api.github import get_installation_token
from apps.api.api.notifications import build_test_notification_message, post_slack_message
from packages.db.database import get_db
from packages.db.models import AnalysisRun, Org, Repo, ScoreHistory, Skill, SkillUsageEvent
from packages.db.models.skill import skill_category_for_source_type
from packages.db.schemas import (
    AuditLogEventResponse,
    AuditLogResponse,
    GovernancePoliciesResponse,
    GovernancePolicyResponse,
    OrgCoverageSummaryResponse,
    OrgResponse,
    OrgSettingsResponse,
    OrgSettingsUpdate,
    RepoCoverageSummary,
    RepoResponse,
    RuntimeBreakdownEntryResponse,
    RuntimeBreakdownResponse,
    ScoreResponse,
    SkillHeatmapResponse,
    SkillHeatmapSkillResponse,
    SkillHeatmapSummaryResponse,
    TeamRepoScoreResponse,
    TeamRollupResponse,
    TeamRollupTeamResponse,
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

SKILL_CATEGORY_LANGUAGE_HINTS = {
    "codebase_architecture": "Detected from repo structure",
    "code_style": "Detected from code style patterns",
    "testing_conventions": "Detected from test patterns",
    "internal_tools": "Detected from internal tooling",
    "security_compliance": "Detected from security patterns",
    "design_system": "Detected from design system usage",
    "data_schema": "Detected from data/schema patterns",
    "operational_knowledge": "Detected from operational knowledge",
}

RUNTIME_DISPLAY_NAMES = {
    "claude_code": "Claude Code",
    "cursor": "Cursor",
    "codex": "Codex",
    "copilot": "Copilot",
    "gemini_cli": "Gemini CLI",
    "unknown": "Other",
}

DEFAULT_POLICIES = [
    {
        "name": "Minimum score gate",
        "type": "min_score",
        "threshold": 60,
        "scope": "all_repos",
        "action": "warn",
        "enabled": True,
    },
    {
        "name": "Freshness requirement",
        "type": "max_staleness_days",
        "threshold": 14,
        "scope": "all_repos",
        "action": "block_pr",
        "enabled": False,
    },
]


class ConnectRepoItem(BaseModel):
    github_repo_id: int
    full_name: str
    name: str
    language: str | None = None
    default_branch: str = "main"
    installation_id: int


class ConnectReposPayload(BaseModel):
    repos: list[ConnectRepoItem]


class OrgIntelligenceRepo(BaseModel):
    id: str
    name: str
    score: int
    score_trend: float | None
    skill_count: int
    dead_skill_count: int
    stale_skill_count: int
    last_analysed_at: datetime | None
    dormant: bool


class OrgIntelligenceCategoryMatrixEntry(BaseModel):
    repo_id: str
    repo_name: str
    covered: bool
    avg_score: int
    skill_count: int


class OrgIntelligenceStaleAlert(BaseModel):
    skill_id: str
    repo_id: str
    repo_name: str
    domain: str
    skill_path: str
    alert_type: Literal["dead", "stale_but_active", "dormant_repo"]
    last_loaded_at: datetime | None
    loads_30d: int


class OrgIntelligenceTopSkill(BaseModel):
    skill_id: str
    repo_id: str
    repo_name: str
    domain: str
    loads_30d: int
    score: int


class OrgIntelligenceResponse(BaseModel):
    org_health_score: int
    org_health_trend: float | None
    total_repos: int
    total_skills: int
    total_loads_30d: int
    repos: list[OrgIntelligenceRepo]
    category_matrix: dict[str, list[OrgIntelligenceCategoryMatrixEntry]]
    stale_alerts: list[OrgIntelligenceStaleAlert]
    top_skills: list[OrgIntelligenceTopSkill]


def _last_30_score_dates() -> list[str]:
    """Return the last 30 UTC score dates in chronological order."""
    today = datetime.now(UTC).date()
    return [(today - timedelta(days=offset)).isoformat() for offset in range(29, -1, -1)]


def _utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _runtime_display_name(runtime: str | None) -> str:
    normalized = str(runtime or "unknown")
    return RUNTIME_DISPLAY_NAMES.get(normalized, normalized.replace("_", " ").title())


def _criticality_score(loads_30d: int, last_loaded_at: datetime | None, is_stale: bool, max_loads: int) -> int:
    freq_score = min(100, (loads_30d / max(max_loads, 1)) * 100)
    recency_score = 0
    if last_loaded_at is not None:
        age = _utc_now_naive() - last_loaded_at.replace(tzinfo=None) if last_loaded_at.tzinfo else _utc_now_naive() - last_loaded_at
        if age <= timedelta(days=7):
            recency_score = 100
        elif age <= timedelta(days=30):
            recency_score = 50
    staleness_penalty = 30 if is_stale else 0
    return max(0, round(freq_score * 0.6 + recency_score * 0.4 - staleness_penalty))


def _skill_alert(skill: Skill, loads_30d: int, now: datetime) -> str:
    created_at = skill.created_at.replace(tzinfo=None) if skill.created_at.tzinfo else skill.created_at
    if skill.is_stale and loads_30d > 0:
        return "stale_but_active"
    if loads_30d == 0 and created_at < now - timedelta(days=7):
        return "dead_skill"
    return "healthy"


def _team_from_repo_name(name: str) -> str:
    parts = name.replace("_", "-").split("-")
    return parts[0] if len(parts) > 1 else name


def _event_type_for_run(run: AnalysisRun) -> str:
    trigger = str(run.trigger or "")
    if run.status == "failed":
        return "analysis_failed"
    if trigger in {"pr", "pr_trigger"}:
        return "pr_gate_triggered"
    if run.status == "complete":
        return "analysis_complete"
    return "analysis_queued"


def _actor_for_trigger(trigger: str | None) -> str:
    if trigger in {"manual", "push", "pr_trigger", "webhook", "github_push"}:
        return str(trigger)
    if trigger and trigger.startswith("source:"):
        return "webhook"
    return "manual"


def _normalize_policy(raw: object, index: int) -> GovernancePolicyResponse | None:
    if not isinstance(raw, dict):
        return None
    policy_type = str(raw.get("type") or "").strip()
    action = str(raw.get("action") or "").strip()
    if policy_type not in {"min_score", "max_staleness_days", "required_categories", "min_groundedness"}:
        return None
    if action not in {"warn", "block_pr", "notify_slack"}:
        return None
    threshold = raw.get("threshold", 0)
    if policy_type == "required_categories":
        threshold = [str(item) for item in threshold] if isinstance(threshold, list) else []
    else:
        try:
            threshold = int(threshold or 0)
        except (TypeError, ValueError):
            threshold = 0
    created_at = raw.get("created_at")
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            created_at = None
    elif not isinstance(created_at, datetime):
        created_at = None
    return GovernancePolicyResponse(
        id=str(raw.get("id") or uuid4()),
        name=str(raw.get("name") or f"Policy {index + 1}"),
        type=policy_type,
        threshold=threshold,
        scope=str(raw.get("scope") or "all_repos"),
        action=action,
        enabled=bool(raw.get("enabled", True)),
        created_at=created_at,
    )


def _get_policies(org: Org) -> list[GovernancePolicyResponse]:
    settings = org.notification_settings if isinstance(org.notification_settings, dict) else {}
    raw_policies = settings.get("policies")
    source = raw_policies if isinstance(raw_policies, list) else DEFAULT_POLICIES
    policies = [_normalize_policy(item, index) for index, item in enumerate(source)]
    return [policy for policy in policies if policy is not None]


async def _latest_repo_score(db: AsyncSession, repo_id: str) -> int:
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


async def _repo_score_before(db: AsyncSession, repo_id: str, before: datetime) -> int | None:
    previous = (
        await db.execute(
            select(ScoreHistory.score_total)
            .where(ScoreHistory.repo_id == repo_id, ScoreHistory.recorded_at <= before)
            .order_by(desc(ScoreHistory.recorded_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    return int(previous) if previous is not None else None



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
    repo_skills = (
        await db.execute(select(Skill).where(Skill.repo_id == repo.id).order_by(desc(Skill.created_at)))
    ).scalars().all()
    languages, display_language = _repo_language_metadata(list(repo_skills), repo.language)
    delta = None
    if len(latest_history) >= 2:
        delta = int(latest_history[0].score_total - latest_history[1].score_total)
    return RepoResponse(
        id=repo.id,
        full_name=repo.full_name,
        name=repo.name,
        installation_id=repo.github_installation_id,
        language=repo.language,
        languages=languages,
        display_language=display_language,
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


def _covered_categories(skills: list[Skill]) -> list[str]:
    """Return covered skill categories in the dashboard taxonomy order."""
    covered = {_skill_category(skill) for skill in skills if _skill_category(skill) in SKILL_CATEGORIES}
    return [category for category in SKILL_CATEGORIES if category in covered]


def _repo_language_metadata(skills: list[Skill], language: str | None) -> tuple[list[str], str]:
    """Return supplemental language hints and a user-facing display language."""
    covered_categories = _covered_categories(skills)
    language_hints = [SKILL_CATEGORY_LANGUAGE_HINTS.get(category, category.replace("_", " ")) for category in covered_categories]
    if language:
        return language_hints, language
    return language_hints, "Multiple" if len(covered_categories) > 2 else "Unknown"


def _repo_coverage_score(skills: list[Skill]) -> tuple[int, list[str]]:
    """Return the coverage score and missing categories for a repo skill set."""
    covered = _covered_categories(skills)
    missing = [category for category in SKILL_CATEGORIES if category not in covered]
    return round((len(covered) / len(SKILL_CATEGORIES)) * 100), missing


def _skill_debt_item(
    skill: Skill,
    repo_name: str,
    loads_30d: int,
    criticality_score: int,
    alert: str,
) -> dict[str, object]:
    """Normalize a risky or neglected skill into a debt-ledger entry."""
    score_total = int(skill.score_total or 0)
    debt_type = "stale_active" if alert == "stale_but_active" else "low_score" if score_total <= 45 else "unused"
    severity = "high" if alert == "stale_but_active" or criticality_score >= 75 else "medium" if score_total <= 60 else "low"
    suggested_action = (
        "Re-analyse or prune this skill before the next agent session."
        if alert == "stale_but_active"
        else "Improve source coverage or regenerate this skill."
        if score_total <= 45
        else "Confirm whether this skill should remain in circulation."
    )
    return {
        "skill_id": skill.id,
        "repo_id": skill.repo_id,
        "repo_name": repo_name,
        "domain": skill.domain,
        "skill_path": skill.skill_path,
        "skill_category": _skill_category(skill),
        "score_total": score_total,
        "loads_30d": loads_30d,
        "criticality_score": criticality_score,
        "alert": alert,
        "severity": severity,
        "debt_type": debt_type,
        "is_stale": bool(skill.is_stale),
        "last_loaded_at": skill.last_loaded_at,
        "suggested_action": suggested_action,
    }


def _row_value(row: object, key: str, default: object = None) -> object:
    """Read a named value from SQLAlchemy rows and simple test doubles."""
    if hasattr(row, key):
        return getattr(row, key)
    mapping = getattr(row, "_mapping", None)
    if mapping is not None and key in mapping:
        return mapping[key]
    if isinstance(row, dict):
        return row.get(key, default)
    return default


def _latest_scores_by_repo(runs: list[AnalysisRun]) -> dict[str, AnalysisRun]:
    """Pick the newest completed run per repo from rows ordered by created_at descending."""
    latest: dict[str, AnalysisRun] = {}
    for run in runs:
        if run.repo_id not in latest:
            latest[run.repo_id] = run
    return latest


def _usage_by_skill(rows: list[object]) -> dict[str, dict[str, object]]:
    """Map skill IDs to their 30-day usage aggregate."""
    usage: dict[str, dict[str, object]] = {}
    for row in rows:
        skill_id = str(_row_value(row, "skill_id", ""))
        if not skill_id:
            continue
        usage[skill_id] = {
            "loads_30d": int(_row_value(row, "loads_30d", 0) or 0),
            "loads_7d": int(_row_value(row, "loads_7d", 0) or 0),
            "last_loaded_at": _row_value(row, "last_loaded_at"),
        }
    return usage


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


@router.get("/{org_id}/skill-heatmap", response_model=SkillHeatmapResponse)
async def get_skill_heatmap(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> SkillHeatmapResponse:
    now = _utc_now_naive()
    cutoff_30 = now - timedelta(days=30)
    cutoff_7 = now - timedelta(days=7)
    try:
        skill_rows = (
            await db.execute(
                select(Skill, Repo.name.label("repo_name"))
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Repo.org_id == org_id, Repo.is_active.is_(True))
            )
        ).all()
        usage_rows = (
            await db.execute(
                select(
                    SkillUsageEvent.skill_id,
                    func.count(SkillUsageEvent.id).label("loads_30d"),
                    func.count(SkillUsageEvent.id).filter(SkillUsageEvent.loaded_at >= cutoff_7).label("loads_7d"),
                    func.max(SkillUsageEvent.loaded_at).label("last_loaded_at"),
                )
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff_30)
                .group_by(SkillUsageEvent.skill_id)
            )
        ).all()
        runtime_rows = (
            await db.execute(
                select(SkillUsageEvent.skill_id, SkillUsageEvent.agent_runtime)
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff_30)
                .distinct()
            )
        ).all()
    except SQLAlchemyError as exc:
        await _rollback(db, "skill heatmap lookup")
        raise HTTPException(status_code=400, detail="Unable to load skill heatmap") from exc

    usage_by_skill = {
        str(row.skill_id): {
            "loads_30d": int(row.loads_30d or 0),
            "loads_7d": int(row.loads_7d or 0),
            "last_loaded_at": row.last_loaded_at,
        }
        for row in usage_rows
    }
    runtimes_by_skill: dict[str, set[str]] = {}
    for row in runtime_rows:
        runtimes_by_skill.setdefault(str(row.skill_id), set()).add(str(row.agent_runtime or "unknown"))

    max_loads = max((item["loads_30d"] for item in usage_by_skill.values()), default=1)
    response_skills: list[SkillHeatmapSkillResponse] = []
    dead_skills = 0
    stale_but_active = 0
    healthy = 0
    for skill, repo_name in skill_rows:
        usage = usage_by_skill.get(skill.id, {"loads_30d": 0, "loads_7d": 0, "last_loaded_at": skill.last_loaded_at})
        last_loaded_at = usage["last_loaded_at"] or skill.last_loaded_at
        loads_30d = int(usage["loads_30d"])
        alert = _skill_alert(skill, loads_30d, now)
        criticality = _criticality_score(loads_30d, last_loaded_at, bool(skill.is_stale), max_loads)
        if alert == "dead_skill":
            dead_skills += 1
        elif alert == "stale_but_active":
            stale_but_active += 1
        else:
            healthy += 1
        response_skills.append(
            SkillHeatmapSkillResponse(
                skill_id=skill.id,
                domain=skill.domain,
                repo_id=skill.repo_id,
                repo_name=str(repo_name),
                skill_category=_skill_category(skill),
                source_type=str(skill.source_type or "code"),
                score_total=int(skill.score_total or 0),
                is_stale=bool(skill.is_stale),
                loads_30d=loads_30d,
                loads_7d=int(usage["loads_7d"]),
                criticality_score=criticality,
                last_loaded_at=last_loaded_at,
                agent_runtimes=sorted(runtimes_by_skill.get(skill.id, set())),
                alert=alert,
            )
        )
    response_skills.sort(key=lambda item: (-item.criticality_score, -item.loads_30d, item.domain))
    avg_criticality = round(
        sum(skill.criticality_score for skill in response_skills) / len(response_skills)
    ) if response_skills else 0
    return SkillHeatmapResponse(
        skills=response_skills,
        summary=SkillHeatmapSummaryResponse(
            total_skills=len(response_skills),
            dead_skills=dead_skills,
            stale_but_active=stale_but_active,
            healthy=healthy,
            avg_criticality=avg_criticality,
        ),
    )


@router.get("/{org_id}/runtime-breakdown", response_model=RuntimeBreakdownResponse)
async def get_runtime_breakdown(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> RuntimeBreakdownResponse:
    cutoff_30 = _utc_now_naive() - timedelta(days=30)
    try:
        runtime_rows = (
            await db.execute(
                select(
                    SkillUsageEvent.agent_runtime.label("runtime"),
                    func.count(SkillUsageEvent.id).label("loads_30d"),
                    func.count(func.distinct(SkillUsageEvent.skill_id)).label("unique_skills"),
                )
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff_30)
                .group_by(SkillUsageEvent.agent_runtime)
                .order_by(desc(func.count(SkillUsageEvent.id)))
            )
        ).all()
        domain_rows = (
            await db.execute(
                select(
                    SkillUsageEvent.agent_runtime.label("runtime"),
                    Skill.domain.label("domain"),
                    func.count(SkillUsageEvent.id).label("loads"),
                )
                .join(Skill, Skill.id == SkillUsageEvent.skill_id)
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff_30)
                .group_by(SkillUsageEvent.agent_runtime, Skill.domain)
            )
        ).all()
        top_domains: dict[str, tuple[str, int]] = {}
        for row in domain_rows:
            runtime = str(row.runtime or "unknown")
            loads = int(row.loads or 0)
            current = top_domains.get(runtime)
            if current is None or loads > current[1]:
                top_domains[runtime] = (str(row.domain), loads)
        runtimes = [
            RuntimeBreakdownEntryResponse(
                runtime=str(row.runtime or "unknown"),
                display_name=_runtime_display_name(row.runtime),
                loads_30d=int(row.loads_30d or 0),
                unique_skills=int(row.unique_skills or 0),
                top_skill_domain=top_domains.get(str(row.runtime or "unknown"), (None, 0))[0],
            )
            for row in runtime_rows
        ]
        return RuntimeBreakdownResponse(
            runtimes=runtimes,
            total_loads_30d=sum(item.loads_30d for item in runtimes),
        )
    except SQLAlchemyError:
        await _rollback(db, "runtime breakdown fallback")
        total_loads = (
            await db.execute(
                select(func.count(SkillUsageEvent.id)).where(
                    SkillUsageEvent.org_id == org_id,
                    SkillUsageEvent.loaded_at >= cutoff_30,
                )
            )
        ).scalar_one()
        unique_skills = (
            await db.execute(
                select(func.count(func.distinct(SkillUsageEvent.skill_id))).where(
                    SkillUsageEvent.org_id == org_id,
                    SkillUsageEvent.loaded_at >= cutoff_30,
                )
            )
        ).scalar_one()
        top_domain_row = (
            await db.execute(
                select(Skill.domain, func.count(SkillUsageEvent.id).label("loads"))
                .join(Skill, Skill.id == SkillUsageEvent.skill_id)
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff_30)
                .group_by(Skill.domain)
                .order_by(desc(func.count(SkillUsageEvent.id)))
                .limit(1)
            )
        ).first()
        return RuntimeBreakdownResponse(
            runtimes=[
                RuntimeBreakdownEntryResponse(
                    runtime="unknown",
                    display_name=_runtime_display_name("unknown"),
                    loads_30d=int(total_loads or 0),
                    unique_skills=int(unique_skills or 0),
                    top_skill_domain=(str(top_domain_row.domain) if top_domain_row else None),
                )
            ] if int(total_loads or 0) > 0 else [],
            total_loads_30d=int(total_loads or 0),
        )


@router.get("/{org_id}/intelligence", response_model=OrgIntelligenceResponse)
async def get_org_intelligence(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgIntelligenceResponse:
    """Return cross-repo skill health, coverage gaps, and agent activity."""
    _assert_org_scope(org_id, current_org_id)
    now = _utc_now_naive()
    cutoff_30 = now - timedelta(days=30)

    try:
        org = await db.get(Org, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Org not found")

        repos = (
            await db.execute(
                select(Repo)
                .where(Repo.org_id == org_id, Repo.is_active.is_(True))
                .order_by(Repo.full_name)
            )
        ).scalars().all()
        repo_ids = [repo.id for repo in repos]
        if not repo_ids:
            return OrgIntelligenceResponse(
                org_health_score=0,
                org_health_trend=None,
                total_repos=0,
                total_skills=0,
                total_loads_30d=0,
                repos=[],
                category_matrix={category: [] for category in SKILL_CATEGORIES},
                stale_alerts=[],
                top_skills=[],
            )

        skills = (
            await db.execute(
                select(Skill)
                .where(Skill.repo_id.in_(repo_ids))
            )
        ).scalars().all()
        runs = (
            await db.execute(
                select(AnalysisRun)
                .where(AnalysisRun.repo_id.in_(repo_ids), AnalysisRun.status == "complete")
                .order_by(desc(AnalysisRun.created_at))
            )
        ).scalars().all()
        last_run_rows = (
            await db.execute(
                select(AnalysisRun.repo_id, AnalysisRun.created_at)
                .where(AnalysisRun.repo_id.in_(repo_ids))
                .order_by(desc(AnalysisRun.created_at))
            )
        ).all()
        history_rows = (
            await db.execute(
                select(
                    ScoreHistory.repo_id,
                    ScoreHistory.score_total,
                    ScoreHistory.recorded_at,
                )
                .where(
                    ScoreHistory.repo_id.in_(repo_ids),
                    ScoreHistory.recorded_at >= cutoff_30,
                )
                .order_by(ScoreHistory.repo_id, ScoreHistory.recorded_at)
            )
        ).all()
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        await _rollback(db, "org intelligence lookup")
        raise HTTPException(status_code=400, detail="Unable to load org intelligence") from exc

    latest_scores = _latest_scores_by_repo(list(runs))
    repo_by_id = {repo.id: repo for repo in repos}
    skills_by_repo: dict[str, list[Skill]] = {repo.id: [] for repo in repos}
    for skill in skills:
        skills_by_repo.setdefault(skill.repo_id, []).append(skill)

    last_run_by_repo: dict[str, datetime] = {}
    for row in last_run_rows:
        repo_id = str(_row_value(row, "repo_id", ""))
        created_at = _row_value(row, "created_at")
        if repo_id and isinstance(created_at, datetime) and repo_id not in last_run_by_repo:
            last_run_by_repo[repo_id] = created_at

    history_by_repo: dict[str, list[tuple[datetime, int]]] = {repo.id: [] for repo in repos}
    for row in history_rows:
        repo_id = str(_row_value(row, "repo_id", ""))
        recorded_at = _row_value(row, "recorded_at")
        if repo_id and isinstance(recorded_at, datetime):
            history_by_repo.setdefault(repo_id, []).append((recorded_at, int(_row_value(row, "score_total", 0) or 0)))

    repo_trends: dict[str, float | None] = {}
    for repo in repos:
        points = sorted(history_by_repo.get(repo.id, []), key=lambda item: item[0])
        repo_trends[repo.id] = float(points[-1][1] - points[0][1]) if len(points) >= 2 else None

    total_loads_30d = sum(int(skill.load_count_30d or 0) for skill in skills)

    response_repos: list[OrgIntelligenceRepo] = []
    for repo in repos:
        repo_skills = skills_by_repo.get(repo.id, [])
        current_score = int(latest_scores[repo.id].score_total or 0) if repo.id in latest_scores else 0
        last_analysed_at = last_run_by_repo.get(repo.id) or repo.last_analysed_at
        dormant = last_analysed_at is None or (last_analysed_at.replace(tzinfo=None) if last_analysed_at.tzinfo else last_analysed_at) < cutoff_30
        response_repos.append(
            OrgIntelligenceRepo(
                id=repo.id,
                name=repo.name,
                score=current_score,
                score_trend=repo_trends.get(repo.id),
                skill_count=len(repo_skills),
                dead_skill_count=sum(
                    1
                    for skill in repo_skills
                    if int(skill.load_count_30d or 0) == 0
                    and (skill.last_loaded_at is None or (skill.last_loaded_at.replace(tzinfo=None) if skill.last_loaded_at.tzinfo else skill.last_loaded_at) < cutoff_30)
                ),
                stale_skill_count=sum(1 for skill in repo_skills if bool(skill.is_stale)),
                last_analysed_at=last_analysed_at,
                dormant=dormant,
            )
        )
    response_repos.sort(key=lambda item: (item.score, item.name))

    category_matrix: dict[str, list[OrgIntelligenceCategoryMatrixEntry]] = {}
    for category in SKILL_CATEGORIES:
        entries: list[OrgIntelligenceCategoryMatrixEntry] = []
        for repo in repos:
            category_skills = [skill for skill in skills_by_repo.get(repo.id, []) if _skill_category(skill) == category]
            entries.append(
                OrgIntelligenceCategoryMatrixEntry(
                    repo_id=repo.id,
                    repo_name=repo.name,
                    covered=bool(category_skills),
                    avg_score=round(sum(int(skill.score_total or 0) for skill in category_skills) / len(category_skills)) if category_skills else 0,
                    skill_count=len(category_skills),
                )
            )
        category_matrix[category] = entries

    stale_alerts: list[OrgIntelligenceStaleAlert] = []
    dormant_by_repo = {repo.id: repo.dormant for repo in response_repos}
    for skill in skills:
        repo = repo_by_id.get(skill.repo_id)
        if repo is None:
            continue
        loads_30d = int(skill.load_count_30d or 0)
        last_loaded_at = skill.last_loaded_at
        is_dead = loads_30d == 0 and (last_loaded_at is None or (last_loaded_at.replace(tzinfo=None) if last_loaded_at.tzinfo else last_loaded_at) < cutoff_30)
        helper_alert = _skill_alert(skill, loads_30d, now)
        alert_type: Literal["dead", "stale_but_active", "dormant_repo"] | None = None
        if is_dead or helper_alert == "dead_skill":
            alert_type = "dead"
        elif bool(skill.is_stale):
            alert_type = "stale_but_active"
        elif dormant_by_repo.get(skill.repo_id):
            alert_type = "dormant_repo"
        if alert_type is None:
            continue
        stale_alerts.append(
            OrgIntelligenceStaleAlert(
                skill_id=skill.id,
                repo_id=skill.repo_id,
                repo_name=repo.name,
                domain=skill.domain,
                skill_path=skill.skill_path,
                alert_type=alert_type,
                last_loaded_at=last_loaded_at,
                loads_30d=loads_30d,
            )
        )
    stale_alerts.sort(
        key=lambda alert: (
            0 if alert.alert_type == "dead" else 1,
            alert.last_loaded_at is not None,
            alert.last_loaded_at or datetime.min,
        )
    )

    top_skills = [
        OrgIntelligenceTopSkill(
            skill_id=skill.id,
            repo_id=skill.repo_id,
            repo_name=repo_by_id[skill.repo_id].name if skill.repo_id in repo_by_id else "unknown",
            domain=skill.domain,
            loads_30d=int(skill.load_count_30d or 0),
            score=int(skill.score_total or 0),
        )
        for skill in sorted(skills, key=lambda item: (-int(item.load_count_30d or 0), item.domain))[:10]
    ]

    repo_scores = [repo.score for repo in response_repos]
    repo_trend_values = [trend for trend in repo_trends.values() if trend is not None]
    max_loads = max((int(skill.load_count_30d or 0) for skill in skills), default=1)
    for skill in skills:
        _criticality_score(int(skill.load_count_30d or 0), skill.last_loaded_at, bool(skill.is_stale), max_loads)

    return OrgIntelligenceResponse(
        org_health_score=round(sum(repo_scores) / len(repo_scores)) if repo_scores else 0,
        org_health_trend=(sum(repo_trend_values) / len(repo_trend_values)) if repo_trend_values else None,
        total_repos=len(repos),
        total_skills=len(skills),
        total_loads_30d=total_loads_30d,
        repos=response_repos,
        category_matrix=category_matrix,
        stale_alerts=stale_alerts[:20],
        top_skills=top_skills,
    )


@router.get("/{org_id}/skill-debt")
async def get_skill_debt(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    """Return skill debt summary: stale, never-loaded, low-score, and uncovered domains."""
    _assert_org_scope(org_id, current_org_id)

    repos = (
        await db.execute(
            select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True))
        )
    ).scalars().all()

    all_skills = (
        await db.execute(
            select(Skill)
            .join(Repo, Repo.id == Skill.repo_id)
            .where(Repo.org_id == org_id, Repo.is_active.is_(True))
        )
    ).scalars().all()

    stale_skills = [skill for skill in all_skills if skill.is_stale]
    low_score_skills = [skill for skill in all_skills if int(skill.score_total or 0) < 40]
    never_loaded_skills = [skill for skill in all_skills if int(skill.load_count_30d or 0) == 0]
    zero_subscore_skills = [
        skill
        for skill in all_skills
        if int(skill.score_groundedness or 0) == 0 and int(skill.score_coverage or 0) == 0
    ]

    repo_gaps: list[dict[str, object]] = []
    for repo in repos:
        repo_skills = [skill for skill in all_skills if skill.repo_id == repo.id]
        covered = _covered_categories(repo_skills)
        missing = [category for category in SKILL_CATEGORIES if category not in covered]
        if missing:
            repo_gaps.append(
                {
                    "repo_id": repo.id,
                    "repo_name": repo.name,
                    "covered_categories": covered,
                    "missing_categories": missing,
                    "coverage_score": round((len(covered) / len(SKILL_CATEGORIES)) * 100),
                }
            )

    debt_score = min(
        100,
        len(stale_skills) * 3
        + len(low_score_skills) * 2
        + len(never_loaded_skills) * 1
        + sum(len(gap["missing_categories"]) for gap in repo_gaps) * 2,
    )

    def _skill_dict(skill: Skill) -> dict[str, object]:
        return {
            "id": skill.id,
            "domain": skill.domain,
            "repo_id": skill.repo_id,
            "score_total": int(skill.score_total or 0),
            "is_stale": bool(skill.is_stale),
            "load_count_30d": int(skill.load_count_30d or 0),
        }

    return {
        "debt_score": debt_score,
        "total_skills": len(all_skills),
        "stale_skills": [_skill_dict(skill) for skill in stale_skills[:20]],
        "low_score_skills": [_skill_dict(skill) for skill in sorted(low_score_skills, key=lambda item: item.score_total or 0)[:20]],
        "never_loaded_skills": [_skill_dict(skill) for skill in never_loaded_skills[:20]],
        "zero_subscore_skills": [_skill_dict(skill) for skill in zero_subscore_skills[:20]],
        "repo_coverage_gaps": repo_gaps,
        "summary": {
            "stale_count": len(stale_skills),
            "low_score_count": len(low_score_skills),
            "never_loaded_count": len(never_loaded_skills),
            "zero_subscore_count": len(zero_subscore_skills),
            "repos_with_gaps": len(repo_gaps),
        },
    }


@router.get("/{org_id}/team-rollup", response_model=TeamRollupResponse)
async def get_team_rollup(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> TeamRollupResponse:
    now = _utc_now_naive()
    seven_days_ago = now - timedelta(days=7)
    try:
        repos = (
            await db.execute(
                select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)).order_by(Repo.full_name)
            )
        ).scalars().all()
        skills = (
            await db.execute(
                select(Skill).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == org_id, Repo.is_active.is_(True))
            )
        ).scalars().all()
    except SQLAlchemyError as exc:
        await _rollback(db, "team rollup lookup")
        raise HTTPException(status_code=400, detail="Unable to load team rollup") from exc

    repo_name_by_id = {repo.id: repo.name for repo in repos}
    team_map: dict[str, dict[str, object]] = {}
    for repo in repos:
        team = _team_from_repo_name(repo.name)
        current_score = await _latest_repo_score(db, repo.id)
        previous_score = await _repo_score_before(db, repo.id, seven_days_ago)
        team_entry = team_map.setdefault(team, {"repos": [], "scores_7d": [], "skills": []})
        team_entry["repos"].append({
            "id": repo.id,
            "name": repo.name,
            "score": current_score,
        })
        if previous_score is not None:
            team_entry["scores_7d"].append(previous_score)
    for skill in skills:
        team = _team_from_repo_name(repo_name_by_id.get(skill.repo_id, "unknown"))
        team_map.setdefault(team, {"repos": [], "scores_7d": [], "skills": []})["skills"].append(skill)

    teams: list[TeamRollupTeamResponse] = []
    for team_name, payload in team_map.items():
        repos_payload = [TeamRepoScoreResponse(**repo_payload) for repo_payload in payload["repos"]]
        repos_payload.sort(key=lambda item: item.score, reverse=True)
        team_skills = list(payload["skills"])
        covered = {_skill_category(skill) for skill in team_skills if _skill_category(skill) in SKILL_CATEGORIES}
        avg_score = round(sum(repo.score for repo in repos_payload) / len(repos_payload)) if repos_payload else 0
        previous_avg = (
            round(sum(payload["scores_7d"]) / len(payload["scores_7d"]))
            if payload["scores_7d"] else None
        )
        teams.append(
            TeamRollupTeamResponse(
                team_name=team_name,
                repo_count=len(repos_payload),
                avg_score=avg_score,
                worst_repo=min(repos_payload, key=lambda item: item.score, default=None),
                best_repo=max(repos_payload, key=lambda item: item.score, default=None),
                score_delta_7d=(avg_score - previous_avg) if previous_avg is not None else None,
                skill_count=len(team_skills),
                coverage_score=round((len(covered) / len(SKILL_CATEGORIES)) * 100) if SKILL_CATEGORIES else 0,
                repos=repos_payload,
            )
        )
    teams.sort(key=lambda item: (-item.avg_score, item.team_name))
    org_avg_score = round(sum(team.avg_score for team in teams) / len(teams)) if teams else 0
    needs_attention = min(teams, key=lambda item: item.avg_score).team_name if teams else None
    top_team = max(teams, key=lambda item: item.avg_score).team_name if teams else None
    return TeamRollupResponse(
        teams=teams,
        org_avg_score=org_avg_score,
        top_team=top_team,
        needs_attention=needs_attention,
    )


@router.get("/{org_id}/audit-log", response_model=AuditLogResponse)
async def get_audit_log(
    org_id: str,
    event_type: str | None = Query(default=None),
    repo_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> AuditLogResponse:
    try:
        query = (
            select(AnalysisRun, Repo.name.label("repo_name"))
            .join(Repo, Repo.id == AnalysisRun.repo_id)
            .where(Repo.org_id == org_id)
            .order_by(desc(AnalysisRun.created_at))
        )
        if repo_id:
            query = query.where(Repo.id == repo_id)
        rows = (await db.execute(query.limit(max(limit + offset + 100, 200)))).all()
    except SQLAlchemyError as exc:
        await _rollback(db, "audit log lookup")
        raise HTTPException(status_code=400, detail="Unable to load audit log") from exc

    events: list[AuditLogEventResponse] = []
    for run, repo_name in rows:
        derived_event_type = _event_type_for_run(run)
        if event_type and derived_event_type != event_type:
            continue
        anchor = (run.created_at or _utc_now_naive()) - timedelta(seconds=1)
        score_before = await _repo_score_before(db, run.repo_id, anchor)
        score_after = int(run.score_total) if run.score_total is not None else None
        events.append(
            AuditLogEventResponse(
                id=run.id,
                event_type=derived_event_type,
                repo_name=str(repo_name),
                repo_id=run.repo_id,
                actor=_actor_for_trigger(run.trigger),
                status=run.status,
                score_before=score_before,
                score_after=score_after,
                skill_count=int(run.skill_count) if run.skill_count is not None else None,
                created_at=run.created_at,
            )
        )
    return AuditLogResponse(events=events[offset:offset + limit], limit=limit, offset=offset)


@router.get("/{org_id}/policies", response_model=GovernancePoliciesResponse)
async def get_org_policies(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> GovernancePoliciesResponse:
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    return GovernancePoliciesResponse(policies=_get_policies(org))


@router.post("/{org_id}/policies", response_model=GovernancePoliciesResponse)
async def upsert_org_policies(
    org_id: str,
    payload: GovernancePoliciesResponse,
    db: AsyncSession = Depends(get_db),
) -> GovernancePoliciesResponse:
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    settings = dict(org.notification_settings or {})
    normalized = [_normalize_policy(item.model_dump(), index) for index, item in enumerate(payload.policies)]
    policies = [policy for policy in normalized if policy is not None]
    settings["policies"] = [
        {
            **policy.model_dump(),
            "created_at": policy.created_at.isoformat() if policy.created_at else datetime.now(UTC).isoformat(),
        }
        for policy in policies
    ]
    org.notification_settings = settings
    try:
        await db.flush()
        await db.commit()
    except SQLAlchemyError as exc:
        await _rollback(db, "policy update")
        raise HTTPException(status_code=400, detail="Unable to update policies") from exc
    return GovernancePoliciesResponse(policies=policies)


@router.get("/{org_id}/available-repos")
async def list_available_repos(
    org_id: str,
    installation_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> list[dict[str, object]]:
    """Return GitHub repos from the installation not yet connected to this org."""
    if current_org_id is not None:
        _assert_org_scope(org_id, current_org_id)
    resolved_installation_id: int | None = installation_id

    if resolved_installation_id is None:
        org = await db.get(Org, org_id)
        if org is not None and org.github_installation_id:
            resolved_installation_id = org.github_installation_id

    if resolved_installation_id is None:
        resolved_installation_id = (
            await db.execute(
                select(Repo.github_installation_id)
                .where(Repo.org_id == org_id, Repo.github_installation_id.is_not(None))
                .limit(1)
            )
        ).scalar_one_or_none()

    if not resolved_installation_id:
        raise HTTPException(
            status_code=404,
            detail="No GitHub installation found for this org. Provide installation_id as a query param.",
        )

    existing_ids = set(
        (
            await db.execute(
                select(Repo.github_repo_id).where(Repo.org_id == org_id)
            )
        ).scalars().all()
    )

    token = get_installation_token(int(resolved_installation_id))

    all_repos: list[dict[str, object]] = []
    page = 1
    async with httpx.AsyncClient(timeout=15.0) as client:
        while True:
            resp = await client.get(
                "https://api.github.com/installation/repositories",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                params={"per_page": 100, "page": page},
            )
            if not resp.is_success:
                break
            data = resp.json()
            batch = data.get("repositories", [])
            if not batch:
                break
            for repo in batch:
                if repo["id"] not in existing_ids:
                    all_repos.append(
                        {
                            "github_repo_id": repo["id"],
                            "full_name": repo["full_name"],
                            "name": repo["name"],
                            "language": repo.get("language"),
                            "default_branch": repo.get("default_branch", "main"),
                            "private": repo.get("private", False),
                            "installation_id": resolved_installation_id,
                        }
                    )
            if len(batch) < 100:
                break
            page += 1

    return all_repos


@router.post("/{org_id}/refresh-repo-languages")
async def refresh_repo_languages(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> dict[str, int]:
    """Fetch the primary language from GitHub for connected repos that have language=null.

    Uses the GitHub App installation token so private repos are covered too.
    Safe to call repeatedly — only touches repos with a null language column.
    """
    if current_org_id is not None:
        _assert_org_scope(org_id, current_org_id)

    repos_to_update = list(
        (
            await db.execute(
                select(Repo).where(
                    Repo.org_id == org_id,
                    Repo.language.is_(None),
                    Repo.github_installation_id.is_not(None),
                    Repo.is_active.is_(True),
                )
            )
        ).scalars().all()
    )

    if not repos_to_update:
        return {"updated": 0}

    installation_id = repos_to_update[0].github_installation_id
    token = get_installation_token(int(installation_id))

    updated = 0
    async with httpx.AsyncClient(timeout=10.0) as client:
        for repo in repos_to_update:
            try:
                resp = await client.get(
                    f"https://api.github.com/repos/{repo.full_name}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                )
                if resp.is_success:
                    language = resp.json().get("language")
                    if language:
                        repo.language = language
                        updated += 1
            except Exception:
                continue

    if updated:
        try:
            await db.commit()
        except SQLAlchemyError:
            await _rollback(db, "refresh repo languages")

    return {"updated": updated}


@router.post("/{org_id}/connect-repos")
async def connect_repos(
    org_id: str,
    payload: ConnectReposPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> list[dict[str, str]]:
    """Idempotently create Repo rows for user-selected repos."""
    if current_org_id is not None:
        _assert_org_scope(org_id, current_org_id)
    created: list[dict[str, str]] = []
    for item in payload.repos:
        existing = (
            await db.execute(select(Repo).where(Repo.github_repo_id == item.github_repo_id))
        ).scalar_one_or_none()
        if existing:
            continue
        repo = Repo(
            org_id=org_id,
            github_repo_id=item.github_repo_id,
            github_installation_id=item.installation_id,
            full_name=item.full_name,
            name=item.name,
            language=item.language,
            default_branch=item.default_branch,
            is_active=True,
        )
        db.add(repo)
        created.append({"full_name": item.full_name, "name": item.name})
    try:
        await db.flush()
        await db.commit()
    except SQLAlchemyError as exc:
        await _rollback(db, "connect repos")
        raise HTTPException(status_code=400, detail="Failed to connect repos") from exc
    return created


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


class LocalUsageEvent(BaseModel):
    """A single skill-load event exported from the local .skilgen/analytics/usage.jsonl file."""

    skill_path: str
    """Relative path to the SKILL.md file, e.g. '.skilgen/skills/backend/testing/SKILL.md'."""
    agent_runtime: str = "unknown"
    session_id: str = ""
    timestamp: str = ""


class SyncAnalyticsPayload(BaseModel):
    """Payload for the sync-analytics endpoint — a batch of local usage events."""

    repo_id: str
    events: list[LocalUsageEvent]


class SyncAnalyticsResponse(BaseModel):
    synced: int
    skipped: int


@router.post("/{org_id}/sync-analytics", response_model=SyncAnalyticsResponse)
async def sync_local_analytics(
    org_id: str,
    payload: SyncAnalyticsPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SyncAnalyticsResponse:
    """Sync skill-load events from the local analytics file to the API database.

    The skilgen CLI writes skill loads to ``.skilgen/analytics/usage.jsonl``
    during local sessions.  This endpoint maps those events to DB skill records
    (by ``skill_path``) and increments their ``load_count_30d`` counters,
    creating the ``SkillUsageEvent`` rows that power the dashboard heatmap.
    """
    _assert_org_scope(org_id, current_org_id)
    if not payload.events:
        return SyncAnalyticsResponse(synced=0, skipped=0)

    # Verify the repo belongs to this org.
    repo = await db.get(Repo, payload.repo_id)
    if repo is None or repo.org_id != org_id:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Load all skills for this repo so we can match by skill_path.
    skills_result = await db.execute(select(Skill).where(Skill.repo_id == payload.repo_id))
    skills_by_path: dict[str, Skill] = {
        str(skill.skill_path or "").strip("/"): skill
        for skill in skills_result.scalars().all()
    }

    now = datetime.now(UTC).replace(tzinfo=None)
    synced = 0
    skipped = 0

    for event in payload.events:
        normalized = event.skill_path.strip("/").removeprefix(".skilgen/").removeprefix("skilgen/")
        # Try the raw path first, then a normalized version.
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
                org_id=org_id,
                repo_id=payload.repo_id,
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

    return SyncAnalyticsResponse(synced=synced, skipped=skipped)
