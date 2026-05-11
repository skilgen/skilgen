from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from statistics import median
from typing import Any, Literal

import yaml
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from apps.api.api.v8.flags import is_v8, request_flag_cache
from packages.db.database import get_db
from apps.api.api.v8.settings.connectors_registry import connector_registry
from packages.db.models import AgentSession, AuditEvent, Org, OrgPolicy, PRAttribution, PullRequest, Repo, Skill, SkillMemoryStub, SkillUsageEvent


router = APIRouter(
    prefix="/v8/orgs/{org_id}/insights",
    tags=["v8-insights"],
    dependencies=[Depends(request_flag_cache)],
)

SENSITIVITY_WEIGHTS: dict[str, float] = {
    "public": 0.25,
    "internal": 1.0,
    "sensitive": 2.0,
    "regulated": 3.0,
}
SENSITIVITY_ORDER = {"public": 0, "internal": 1, "sensitive": 2, "regulated": 3}
VIOLATION_SEVERITIES = {"critical", "error", "fatal", "high", "block", "deny", "denied"}
AGENT_COMPLIANCE_EVENT_TYPES = {
    "agent.compliance",
    "agent_compliance",
    "agent.telemetry",
    "agent_telemetry",
    "coding_agent.compliance",
    "coding_agent.telemetry",
}

CRITICAL_OPS_DEFAULT_NOTE = "critical_ops.yaml is a placeholder pending product review of critical operation taxonomy."
CRITICAL_OPS_FALLBACK_OPERATION = {
    "id": "critical-operations-placeholder",
    "label": "Product review required",
    "required_skill_categories": ["operational_knowledge", "security_compliance", "codebase_architecture"],
}


class CriticalOperationConfig(BaseModel):
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    required_skill_categories: list[str] = Field(default_factory=list)


class CriticalOpsConfig(BaseModel):
    product_review_required: bool = True
    product_review_note: str | None = None
    operations: list[CriticalOperationConfig] = Field(default_factory=list)


def _critical_ops_path() -> Path:
    return Path(__file__).with_name("critical_ops.yaml")


@lru_cache(maxsize=1)
def _load_critical_ops_config() -> CriticalOpsConfig:
    path = _critical_ops_path()
    if not path.exists():
        return CriticalOpsConfig(
            product_review_required=True,
            product_review_note=CRITICAL_OPS_DEFAULT_NOTE,
            operations=[CriticalOperationConfig.model_validate(CRITICAL_OPS_FALLBACK_OPERATION)],
        )
    try:
        source = path.read_text(encoding="utf-8")
        raw = yaml.safe_load(source) or {}
    except (OSError, yaml.YAMLError):
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    try:
        config = CriticalOpsConfig.model_validate(raw)
    except Exception:
        config = CriticalOpsConfig(product_review_required=True)
    if not config.operations:
        config.operations = [CriticalOperationConfig.model_validate(CRITICAL_OPS_FALLBACK_OPERATION)]
    if config.product_review_required and not config.product_review_note:
        config.product_review_note = CRITICAL_OPS_DEFAULT_NOTE
    return config


class TrendMetric(BaseModel):
    key: str
    label: str
    current: float | None
    previous: float | None
    delta: float | None
    delta_percent: float | None
    unit: Literal["count", "percent", "minutes", "hours"]
    source: str
    status: Literal["available", "unavailable"] = "available"


class FleetKpisResponse(BaseModel):
    period_days: int
    current_start: datetime
    current_end: datetime
    previous_start: datetime
    previous_end: datetime
    generated_at: datetime
    metrics: list[TrendMetric]


class RiskRow(BaseModel):
    id: str
    name: str
    volume: int
    denied_count: int
    deny_rate: float
    scope_sensitivity: float
    sensitivity_tier: str | None = None
    composite_risk: float
    window_days: int


class RiskRankingResponse(BaseModel):
    window_days: int
    generated_at: datetime
    formula: str = "deny_rate * scope_sensitivity * volume"
    rows: list[RiskRow]


class CoverageSkill(BaseModel):
    id: str
    domain: str
    skill_category: str | None
    score_total: int
    last_grounded_at: datetime | None
    policy_bindings: list[str]


class CriticalOperationCoverage(BaseModel):
    operation_id: str
    label: str
    required_skill_categories: list[str]
    skills: list[CoverageSkill]
    covered: bool


class CoverageRepo(BaseModel):
    repo_id: str
    repo_name: str
    sensitivity_tier: str | None
    last_grounded_at: datetime | None
    policy_bindings: list[str]
    critical_operations: list[CriticalOperationCoverage]


class CoverageSlaResponse(BaseModel):
    generated_at: datetime
    product_review_required: bool
    product_review_note: str
    repos: list[CoverageRepo]


class IntelligenceTierUsage(BaseModel):
    provider: str
    model: str | None = None
    intelligence_tier: str
    events: int
    users: int


class AccessGrantExposure(BaseModel):
    actor_login: str
    provider: str
    repo_name: str | None = None
    access_scope: str
    full_access_events: int
    autonomous_events: int
    tool_permission_events: int
    last_seen_at: datetime | None = None


class IntelligenceUsageResponse(BaseModel):
    window_days: int
    generated_at: datetime
    source: str = "audit_events.metadata"
    content_retention: Literal["metadata-only"] = "metadata-only"
    tier_usage: list[IntelligenceTierUsage]
    access_grants: list[AccessGrantExposure]


class AccessGrantsResponse(BaseModel):
    window_days: int
    generated_at: datetime
    source: str = "audit_events.metadata"
    content_retention: Literal["metadata-only"] = "metadata-only"
    grants: list[AccessGrantExposure]


class ProviderCoverageRow(BaseModel):
    connector_id: str
    label: str
    category: str
    configured: bool
    enabled: bool
    status: Literal["unconfigured", "configured", "active", "silent", "stale", "retention-risk"]
    events: int
    users: int
    models: list[str]
    intelligence_tiers: dict[str, int]
    last_event_at: datetime | None = None
    last_sync_status: str | None = None
    last_sync_requested_at: str | None = None
    last_cursor: str | None = None
    retention_days_remaining: int | None = None
    content_retention: Literal["metadata-only"] = "metadata-only"


class ProviderCoverageResponse(BaseModel):
    window_days: int
    retention_window_days: int
    generated_at: datetime
    content_retention: Literal["metadata-only"] = "metadata-only"
    rows: list[ProviderCoverageRow]


class AgentComplianceMetricSummary(BaseModel):
    events: int
    users: int
    providers: int
    sessions: int
    repos: int
    file_targets: int
    tool_permission_events: int
    mcp_tool_events: int
    full_access_events: int
    autonomous_events: int
    approvals: int
    denials: int
    warnings: int
    violations: int
    errors: int
    tokens_input: int
    tokens_output: int
    tokens_total: int
    cost_usd: float
    avg_latency_ms: float | None = None


class AgentComplianceMetricBreakdownRow(BaseModel):
    key: str
    label: str
    events: int
    users: int
    sessions: int
    full_access_events: int
    autonomous_events: int
    tool_permission_events: int
    mcp_tool_events: int
    file_targets: int
    violations: int
    warnings: int
    errors: int
    tokens_total: int
    cost_usd: float
    avg_latency_ms: float | None = None


class AgentComplianceMetricItem(BaseModel):
    key: str
    label: str
    count: int


class AgentComplianceMetricsResponse(BaseModel):
    window_days: int
    generated_at: datetime
    source: str = "audit_events.metadata"
    content_retention: Literal["metadata-only"] = "metadata-only"
    summary: AgentComplianceMetricSummary
    by_provider: list[AgentComplianceMetricBreakdownRow]
    by_actor: list[AgentComplianceMetricBreakdownRow]
    by_model: list[AgentComplianceMetricBreakdownRow]
    by_repo: list[AgentComplianceMetricBreakdownRow]
    top_tools: list[AgentComplianceMetricItem]
    top_mcp_tools: list[AgentComplianceMetricItem]
    top_files: list[AgentComplianceMetricItem]
    policy_decisions: list[AgentComplianceMetricItem]
    approval_statuses: list[AgentComplianceMetricItem]
    source_record_types: list[AgentComplianceMetricItem]
    retention_states: list[AgentComplianceMetricItem]


class DeveloperTrackSummary(BaseModel):
    developers: int
    events: int
    sessions: int
    providers: int
    repos: int
    tool_calls: int
    file_targets: int
    violations: int
    warnings: int
    errors: int
    tokens_total: int
    cost_usd: float


class DeveloperTrackRow(BaseModel):
    actor_login: str
    rank: int
    events: int
    sessions: int
    providers: list[str]
    repos: list[str]
    models: list[str]
    tool_calls: int
    mcp_tool_calls: int
    file_targets: int
    full_access_events: int
    autonomous_events: int
    approvals: int
    denials: int
    warnings: int
    violations: int
    errors: int
    tokens_input: int
    tokens_output: int
    tokens_total: int
    cost_usd: float
    avg_latency_ms: float | None = None
    risk_score: int
    risk_band: Literal["low", "medium", "high"]
    last_active_at: datetime | None = None
    top_tools: list[AgentComplianceMetricItem]
    top_mcp_tools: list[AgentComplianceMetricItem]
    top_files: list[AgentComplianceMetricItem]
    policy_decisions: list[AgentComplianceMetricItem]
    source_record_types: list[AgentComplianceMetricItem]


class DeveloperTrackResponse(BaseModel):
    window_days: int
    generated_at: datetime
    source: str = "audit_events.metadata"
    content_retention: Literal["metadata-only"] = "metadata-only"
    summary: DeveloperTrackSummary
    developers: list[DeveloperTrackRow]


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _window(period_days: int) -> tuple[datetime, datetime, datetime, datetime]:
    current_end = _utc_now()
    current_start = current_end - timedelta(days=period_days)
    previous_end = current_start
    previous_start = previous_end - timedelta(days=period_days)
    return current_start, current_end, previous_start, previous_end


def _row_value(row: object, name: str, default: Any = None) -> Any:
    if hasattr(row, "_mapping") and name in row._mapping:
        return row._mapping[name]
    return getattr(row, name, default)


def _metric(key: str, label: str, current: float | None, previous: float | None, unit: Literal["count", "percent", "minutes", "hours"], source: str) -> TrendMetric:
    delta = None if current is None or previous is None else round(current - previous, 4)
    if current is None or previous in {None, 0}:
        delta_percent = None
    else:
        delta_percent = round(((current - previous) / previous) * 100, 2)
    return TrendMetric(key=key, label=label, current=current, previous=previous, delta=delta, delta_percent=delta_percent, unit=unit, source=source)


def _unavailable(key: str, label: str, unit: Literal["count", "percent", "minutes", "hours"], source: str) -> TrendMetric:
    return TrendMetric(key=key, label=label, current=None, previous=None, delta=None, delta_percent=None, unit=unit, source=source, status="unavailable")


def _has_violation(items: object) -> bool:
    if not isinstance(items, list):
        return False
    for item in items:
        if not isinstance(item, dict):
            continue
        severity = str(item.get("severity") or item.get("decision") or item.get("outcome") or "").lower()
        if severity in VIOLATION_SEVERITIES:
            return True
    return False


def _sensitivity_weight(tier: object) -> float:
    return SENSITIVITY_WEIGHTS.get(str(tier or "internal").lower(), 1.0)


def _sensitivity_tier(repo: object) -> str | None:
    value = getattr(repo, "sensitivity_tier", None)
    return str(value).lower() if value else None


async def _require_v8(org_id: str, db: AsyncSession, current_org_id: str) -> None:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Org access denied")
    if not await is_v8(org_id, db):
        raise HTTPException(status_code=404, detail="Insights v8 is not enabled")


async def _count_skill_usage(db: AsyncSession, org_id: str, start: datetime, end: datetime) -> int:
    return int(
        (
            await db.execute(
                select(func.count(SkillUsageEvent.id)).where(
                    SkillUsageEvent.org_id == org_id,
                    SkillUsageEvent.loaded_at >= start,
                    SkillUsageEvent.loaded_at < end,
                )
            )
        ).scalar()
        or 0
    )


async def _pull_requests_and_attributions(db: AsyncSession, org_id: str, start: datetime, end: datetime) -> tuple[list[PullRequest], dict[str, PRAttribution]]:
    repos = (await db.execute(select(Repo.id).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
    repo_ids = [str(repo_id) for repo_id in repos]
    if not repo_ids:
        return [], {}
    prs = (
        await db.execute(
            select(PullRequest).where(
                PullRequest.repo_id.in_(repo_ids),
                PullRequest.opened_at >= start,
                PullRequest.opened_at < end,
            )
        )
    ).scalars().all()
    pr_ids = [pr.id for pr in prs]
    attrs = (await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_(pr_ids)))).scalars().all() if pr_ids else []
    return list(prs), {attr.pr_id: attr for attr in attrs}


async def _deny_rate(db: AsyncSession, org_id: str, start: datetime, end: datetime) -> float | None:
    prs, attrs = await _pull_requests_and_attributions(db, org_id, start, end)
    if not prs:
        return None
    denied = sum(1 for pr in prs if _has_violation(attrs.get(pr.id).skills_violated if attrs.get(pr.id) else []))
    return round(denied / len(prs), 4)


async def _attribution_rate(db: AsyncSession, org_id: str, start: datetime, end: datetime) -> float | None:
    prs, attrs = await _pull_requests_and_attributions(db, org_id, start, end)
    if not prs:
        return None
    attributed = sum(1 for pr in prs if pr.id in attrs)
    return round(attributed / len(prs), 4)


async def _memory_approval_stats(db: AsyncSession, org_id: str, start: datetime, end: datetime) -> tuple[float | None, float | None]:
    rows = (
        await db.execute(
            select(SkillMemoryStub.status, SkillMemoryStub.created_at, SkillMemoryStub.reviewed_at).where(
                SkillMemoryStub.org_id == org_id,
                SkillMemoryStub.created_at >= start,
                SkillMemoryStub.created_at < end,
                SkillMemoryStub.status.in_(["approved", "merged", "rejected"]),
            )
        )
    ).all()
    if not rows:
        return None, None
    approved_durations: list[float] = []
    approved = 0
    for row in rows:
        status = str(_row_value(row, "status", "")).lower()
        created_at = _row_value(row, "created_at")
        reviewed_at = _row_value(row, "reviewed_at")
        if status in {"approved", "merged"}:
            approved += 1
            if isinstance(created_at, datetime) and isinstance(reviewed_at, datetime):
                approved_durations.append(max(0.0, (reviewed_at - created_at).total_seconds() / 60))
    approval_rate = round(approved / len(rows), 4)
    median_minutes = round(float(median(approved_durations)), 2) if approved_durations else None
    return approval_rate, median_minutes


async def _count_drift_events(db: AsyncSession, org_id: str, start: datetime, end: datetime) -> int:
    return int(
        (
            await db.execute(
                select(func.count(AuditEvent.id)).where(
                    AuditEvent.org_id == org_id,
                    AuditEvent.created_at >= start,
                    AuditEvent.created_at < end,
                    AuditEvent.event_type.ilike("%drift%"),
                )
            )
        ).scalar()
        or 0
    )


async def _weekly_active_humans(db: AsyncSession, org_id: str, end: datetime) -> int:
    start = end - timedelta(days=7)
    rows = (
        await db.execute(
            select(AgentSession.engineer_login).where(
                AgentSession.org_id == org_id,
                AgentSession.created_at >= start,
                AgentSession.created_at < end,
                AgentSession.engineer_login.is_not(None),
            )
        )
    ).scalars().all()
    return len({str(row) for row in rows if row})


@router.get("", response_model=FleetKpisResponse)
async def insights_default(
    org_id: str,
    period_days: int = Query(default=30, ge=1, le=180),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> FleetKpisResponse:
    return await get_fleet_kpis(org_id, period_days, db, current_org_id)


@router.get("/fleet-kpis", response_model=FleetKpisResponse)
async def get_fleet_kpis(
    org_id: str,
    period_days: int = Query(default=30, ge=1, le=180),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> FleetKpisResponse:
    await _require_v8(org_id, db, current_org_id)
    current_start, current_end, previous_start, previous_end = _window(period_days)
    current_approvals, current_median = await _memory_approval_stats(db, org_id, current_start, current_end)
    previous_approvals, previous_median = await _memory_approval_stats(db, org_id, previous_start, previous_end)
    metrics = [
        _metric("total_agent_actions", "Total agent actions", await _count_skill_usage(db, org_id, current_start, current_end), await _count_skill_usage(db, org_id, previous_start, previous_end), "count", "skill_usage_events"),
        _metric("deny_rate", "Deny rate", await _deny_rate(db, org_id, current_start, current_end), await _deny_rate(db, org_id, previous_start, previous_end), "percent", "pr_attributions.skills_violated"),
        _metric("approval_rate", "Approval rate", current_approvals, previous_approvals, "percent", "skill_memory_stubs"),
        _metric("median_time_to_approve", "Median time to approve", current_median, previous_median, "minutes", "skill_memory_stubs"),
        _metric("drift_events", "Drift events", await _count_drift_events(db, org_id, current_start, current_end), await _count_drift_events(db, org_id, previous_start, previous_end), "count", "audit_events"),
        _unavailable("quarantined_skills", "Quarantined skills", "count", "quarantine_state_not_present"),
        _unavailable("mttr_violations", "MTTR for violations", "hours", "violation_resolution_state_not_present"),
        _metric("attributed_agent_commits", "Agent commits with full attribution", await _attribution_rate(db, org_id, current_start, current_end), await _attribution_rate(db, org_id, previous_start, previous_end), "percent", "pr_attributions"),
        _metric("weekly_active_human_users", "Weekly active human users", await _weekly_active_humans(db, org_id, current_end), await _weekly_active_humans(db, org_id, previous_end), "count", "agent_sessions"),
    ]
    return FleetKpisResponse(
        period_days=period_days,
        current_start=current_start,
        current_end=current_end,
        previous_start=previous_start,
        previous_end=previous_end,
        generated_at=_utc_now(),
        metrics=metrics,
    )


async def _risk_rows_from_view(db: AsyncSession, org_id: str, view_name: str, id_field: str, name_field: str, limit: int) -> list[RiskRow]:
    rows = (
        await db.execute(
            text(
                f"""
                SELECT *
                FROM {view_name}
                WHERE org_id = :org_id
                ORDER BY composite_risk DESC, volume DESC, {name_field} ASC
                LIMIT :limit
                """
            ),
            {"org_id": org_id, "limit": limit},
        )
    ).mappings().all()
    return [
        RiskRow(
            id=str(row[id_field]),
            name=str(row[name_field]),
            volume=int(row["volume"] or 0),
            denied_count=int(row["denied_count"] or 0),
            deny_rate=round(float(row["deny_rate"] or 0), 4),
            scope_sensitivity=round(float(row["scope_sensitivity"] or 0), 4),
            sensitivity_tier=str(row["sensitivity_tier"]) if row.get("sensitivity_tier") else None,
            composite_risk=round(float(row["composite_risk"] or 0), 4),
            window_days=int(row["window_days"] or 30),
        )
        for row in rows
    ]


async def _risk_fallback(db: AsyncSession, org_id: str, group: Literal["agent", "repo"], limit: int) -> list[RiskRow]:
    generated_at = _utc_now()
    cutoff = generated_at - timedelta(days=30)
    repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
    repo_by_id = {repo.id: repo for repo in repos}
    if not repo_by_id:
        return []
    prs = (await db.execute(select(PullRequest).where(PullRequest.repo_id.in_(repo_by_id.keys()), PullRequest.opened_at >= cutoff))).scalars().all()
    attrs = (await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_([pr.id for pr in prs])))).scalars().all() if prs else []
    attr_by_pr = {attr.pr_id: attr for attr in attrs}
    buckets: dict[str, dict[str, Any]] = defaultdict(lambda: {"volume": 0, "denied_count": 0, "scope_sum": 0.0, "name": "", "tier": None})
    for pr in prs:
        repo = repo_by_id.get(pr.repo_id)
        if repo is None:
            continue
        attr = attr_by_pr.get(pr.id)
        key = str(attr.primary_agent if group == "agent" and attr else repo.id)
        row = buckets[key]
        row["name"] = key if group == "agent" else repo.full_name
        row["volume"] += 1
        row["denied_count"] += 1 if _has_violation(attr.skills_violated if attr else []) else 0
        tier = _sensitivity_tier(repo)
        row["tier"] = tier
        row["scope_sum"] += _sensitivity_weight(tier)
    ranked = []
    for key, row in buckets.items():
        volume = int(row["volume"])
        deny_rate = round((int(row["denied_count"]) / volume) if volume else 0.0, 4)
        scope = round(float(row["scope_sum"]) / volume, 4) if volume else 0.0
        ranked.append(
            RiskRow(
                id=key,
                name=str(row["name"]),
                volume=volume,
                denied_count=int(row["denied_count"]),
                deny_rate=deny_rate,
                scope_sensitivity=scope,
                sensitivity_tier=row["tier"],
                composite_risk=round(deny_rate * scope * volume, 4),
                window_days=30,
            )
        )
    return sorted(ranked, key=lambda item: (-item.composite_risk, -item.volume, item.name))[:limit]


@router.get("/risky-agents", response_model=RiskRankingResponse)
async def get_risky_agents(
    org_id: str,
    limit: int = Query(default=25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> RiskRankingResponse:
    await _require_v8(org_id, db, current_org_id)
    try:
        rows = await _risk_rows_from_view(db, org_id, "v8_insights_risky_agents", "agent_runtime", "agent_runtime", limit)
    except SQLAlchemyError:
        await db.rollback()
        rows = await _risk_fallback(db, org_id, "agent", limit)
    return RiskRankingResponse(window_days=30, generated_at=_utc_now(), rows=rows)


@router.get("/risky-repos", response_model=RiskRankingResponse)
async def get_risky_repos(
    org_id: str,
    limit: int = Query(default=25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> RiskRankingResponse:
    await _require_v8(org_id, db, current_org_id)
    try:
        rows = await _risk_rows_from_view(db, org_id, "v8_insights_risky_repos", "repo_id", "repo_name", limit)
    except SQLAlchemyError:
        await db.rollback()
        rows = await _risk_fallback(db, org_id, "repo", limit)
    return RiskRankingResponse(window_days=30, generated_at=_utc_now(), rows=rows)


def _policy_bindings(policy_rows: list[OrgPolicy], repo_id: str) -> list[str]:
    bindings: list[str] = []
    for policy in policy_rows:
        cfg = policy.rule_config or {}
        applies = not cfg.get("repo_id") and not cfg.get("repo_ids")
        if str(cfg.get("repo_id") or "") == repo_id:
            applies = True
        if isinstance(cfg.get("repo_ids"), list) and repo_id in {str(item) for item in cfg.get("repo_ids", [])}:
            applies = True
        if applies:
            bindings.append(policy.name)
    return bindings


def _repo_in_scope(repo: Repo) -> bool:
    tier = _sensitivity_tier(repo)
    if tier is None:
        return True
    return SENSITIVITY_ORDER.get(tier, 1) >= SENSITIVITY_ORDER["internal"]


def _metadata_value(metadata: object, *keys: str) -> str | None:
    if not isinstance(metadata, dict):
        return None
    for key in keys:
        value = metadata.get(key)
        if value not in {None, ""}:
            return str(value)
    return None


def _metadata_bool(metadata: object, *keys: str) -> bool:
    if not isinstance(metadata, dict):
        return False
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.lower() in {"1", "true", "yes", "full", "autonomous"}:
            return True
    return False


def _tool_permission_count(metadata: object) -> int:
    if not isinstance(metadata, dict):
        return 0
    for key in ("tool_permissions", "tools", "tool_calls", "mcp_tools"):
        value = metadata.get(key)
        if isinstance(value, list):
            return len(value)
        if isinstance(value, dict):
            return len(value)
        if isinstance(value, int):
            return max(0, value)
    return 0


def _metadata_int(metadata: object, *keys: str) -> int:
    if not isinstance(metadata, dict):
        return 0
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return max(0, value)
        if isinstance(value, float):
            return max(0, int(value))
        if isinstance(value, str):
            try:
                return max(0, int(float(value)))
            except ValueError:
                continue
    return 0


def _metadata_float(metadata: object, *keys: str) -> float:
    if not isinstance(metadata, dict):
        return 0.0
    for key in keys:
        value = metadata.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            return max(0.0, float(value))
        if isinstance(value, str):
            try:
                return max(0.0, float(value))
            except ValueError:
                continue
    return 0.0


def _metadata_list(metadata: object, key: str) -> list[str]:
    if not isinstance(metadata, dict):
        return []
    value = metadata.get(key)
    if isinstance(value, list):
        return [str(item) for item in value if item not in {None, ""}]
    if isinstance(value, dict):
        return [str(item) for item in value.keys()]
    if isinstance(value, str) and value:
        return [value]
    return []


def _counter_rows(counter: dict[str, int], *, limit: int = 12) -> list[AgentComplianceMetricItem]:
    rows = sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]
    return [AgentComplianceMetricItem(key=key, label=key, count=count) for key, count in rows]


def _is_agent_compliance_event(event: object) -> bool:
    return str(getattr(event, "event_type", "") or "").lower() in AGENT_COMPLIANCE_EVENT_TYPES


def _risk_band(score: int) -> Literal["low", "medium", "high"]:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def _empty_breakdown(key: str, label: str) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "events": 0,
        "users": set(),
        "sessions": set(),
        "full_access_events": 0,
        "autonomous_events": 0,
        "tool_permission_events": 0,
        "mcp_tool_events": 0,
        "file_targets": 0,
        "violations": 0,
        "warnings": 0,
        "errors": 0,
        "tokens_total": 0,
        "cost_usd": 0.0,
        "latencies": [],
    }


def _add_breakdown_metric(bucket: dict[str, Any], event_metrics: dict[str, Any], actor: str, session_id: str | None) -> None:
    bucket["events"] = int(bucket["events"]) + 1
    users = bucket["users"]
    if isinstance(users, set):
        users.add(actor)
    sessions = bucket["sessions"]
    if session_id and isinstance(sessions, set):
        sessions.add(session_id)
    for key in (
        "full_access_events",
        "autonomous_events",
        "tool_permission_events",
        "mcp_tool_events",
        "file_targets",
        "violations",
        "warnings",
        "errors",
        "tokens_total",
    ):
        bucket[key] = int(bucket[key]) + int(event_metrics[key])
    bucket["cost_usd"] = float(bucket["cost_usd"]) + float(event_metrics["cost_usd"])
    if event_metrics["latency_ms"]:
        latencies = bucket["latencies"]
        if isinstance(latencies, list):
            latencies.append(float(event_metrics["latency_ms"]))


def _breakdown_rows(buckets: dict[str, dict[str, Any]], *, limit: int = 12) -> list[AgentComplianceMetricBreakdownRow]:
    rows: list[AgentComplianceMetricBreakdownRow] = []
    for bucket in buckets.values():
        latencies = bucket.get("latencies")
        avg_latency = round(sum(latencies) / len(latencies), 2) if isinstance(latencies, list) and latencies else None
        users = bucket.get("users")
        sessions = bucket.get("sessions")
        rows.append(
            AgentComplianceMetricBreakdownRow(
                key=str(bucket["key"]),
                label=str(bucket["label"]),
                events=int(bucket["events"]),
                users=len(users) if isinstance(users, set) else 0,
                sessions=len(sessions) if isinstance(sessions, set) else 0,
                full_access_events=int(bucket["full_access_events"]),
                autonomous_events=int(bucket["autonomous_events"]),
                tool_permission_events=int(bucket["tool_permission_events"]),
                mcp_tool_events=int(bucket["mcp_tool_events"]),
                file_targets=int(bucket["file_targets"]),
                violations=int(bucket["violations"]),
                warnings=int(bucket["warnings"]),
                errors=int(bucket["errors"]),
                tokens_total=int(bucket["tokens_total"]),
                cost_usd=round(float(bucket["cost_usd"]), 6),
                avg_latency_ms=avg_latency,
            )
        )
    rows.sort(key=lambda item: (-item.events, item.label))
    return rows[:limit]


def _agent_compliance_metrics_from_events(events: list[AuditEvent], window_days: int) -> AgentComplianceMetricsResponse:
    actors: set[str] = set()
    providers: set[str] = set()
    sessions: set[str] = set()
    repos: set[str] = set()
    latency_values: list[float] = []
    summary_totals = {
        "events": 0,
        "file_targets": 0,
        "tool_permission_events": 0,
        "mcp_tool_events": 0,
        "full_access_events": 0,
        "autonomous_events": 0,
        "approvals": 0,
        "denials": 0,
        "warnings": 0,
        "violations": 0,
        "errors": 0,
        "tokens_input": 0,
        "tokens_output": 0,
        "tokens_total": 0,
    }
    cost_usd = 0.0
    by_provider: dict[str, dict[str, Any]] = {}
    by_actor: dict[str, dict[str, Any]] = {}
    by_model: dict[str, dict[str, Any]] = {}
    by_repo: dict[str, dict[str, Any]] = {}
    top_tools: dict[str, int] = {}
    top_mcp_tools: dict[str, int] = {}
    top_files: dict[str, int] = {}
    policy_decisions: dict[str, int] = {}
    approval_statuses: dict[str, int] = {}
    source_record_types: dict[str, int] = {}
    retention_states: dict[str, int] = {}

    for event in events:
        if not _is_agent_compliance_event(event):
            continue
        metadata = getattr(event, "metadata_json", {}) or {}
        actor = str(getattr(event, "actor_login", None) or _metadata_value(metadata, "actor_login", "user") or "unknown")
        provider = _metadata_value(metadata, "provider", "agent_provider", "source_provider") or str(getattr(event, "resource_type", None) or "unknown")
        model = _metadata_value(metadata, "model", "model_name", "model_id") or "unknown model"
        tier = _metadata_value(metadata, "intelligence_tier", "model_tier", "reasoning_tier")
        model_label = f"{model} · {tier}" if tier else model
        repo_name = str(getattr(event, "repo_name", None) or _metadata_value(metadata, "repo_name", "repo") or "unknown repo")
        session_id = _metadata_value(metadata, "session_id", "agent_session_id", "thread_id")
        tool_count = _tool_permission_count(metadata)
        mcp_tools = _metadata_list(metadata, "mcp_tools")
        file_targets = _metadata_list(metadata, "file_targets")
        violation_count = len(_metadata_list(metadata, "violations"))
        warning_count = _metadata_int(metadata, "warnings", "warning_count")
        error_count = _metadata_int(metadata, "error_count", "errors")
        input_tokens = _metadata_int(metadata, "tokens_input", "input_tokens", "prompt_tokens")
        output_tokens = _metadata_int(metadata, "tokens_output", "output_tokens", "completion_tokens")
        total_tokens = _metadata_int(metadata, "tokens_total", "total_tokens") or input_tokens + output_tokens
        event_cost = _metadata_float(metadata, "cost_usd", "estimated_cost_usd")
        latency_ms = _metadata_float(metadata, "latency_ms", "duration_ms")
        is_full_access = _metadata_bool(metadata, "full_access", "full_access_granted") or _metadata_value(metadata, "access_scope") == "full-access"
        is_autonomous = _metadata_bool(metadata, "autonomous_access", "autonomous")

        actors.add(actor)
        providers.add(provider)
        repos.add(repo_name)
        if session_id:
            sessions.add(session_id)
        if latency_ms:
            latency_values.append(latency_ms)
        summary_totals["events"] += 1
        summary_totals["file_targets"] += len(file_targets)
        summary_totals["tool_permission_events"] += tool_count
        summary_totals["mcp_tool_events"] += len(mcp_tools)
        summary_totals["full_access_events"] += 1 if is_full_access else 0
        summary_totals["autonomous_events"] += 1 if is_autonomous else 0
        summary_totals["warnings"] += warning_count
        summary_totals["violations"] += violation_count
        summary_totals["errors"] += error_count
        summary_totals["tokens_input"] += input_tokens
        summary_totals["tokens_output"] += output_tokens
        summary_totals["tokens_total"] += total_tokens
        cost_usd += event_cost

        decision = _metadata_value(metadata, "policy_decision")
        if decision:
            policy_decisions[decision] = policy_decisions.get(decision, 0) + 1
            if decision.lower() in {"deny", "denied", "block", "blocked", "reject", "rejected"}:
                summary_totals["denials"] += 1
        approval = _metadata_value(metadata, "approval_status")
        if approval:
            approval_statuses[approval] = approval_statuses.get(approval, 0) + 1
            if approval.lower() in {"approved", "approve", "allowed", "allow"}:
                summary_totals["approvals"] += 1
            elif approval.lower() in {"denied", "deny", "rejected", "reject", "blocked", "block"}:
                summary_totals["denials"] += 1
        source_record_type = _metadata_value(metadata, "source_record_type") or "unknown"
        source_record_types[source_record_type] = source_record_types.get(source_record_type, 0) + 1
        retention_state = _metadata_value(metadata, "content_retention", "redaction_state") or "metadata-only"
        retention_states[retention_state] = retention_states.get(retention_state, 0) + 1
        for tool in _metadata_list(metadata, "tool_permissions"):
            top_tools[tool] = top_tools.get(tool, 0) + 1
        if isinstance(metadata, dict) and isinstance(metadata.get("tool_calls"), str):
            top_tools[str(metadata["tool_calls"])] = top_tools.get(str(metadata["tool_calls"]), 0) + 1
        for tool in mcp_tools:
            top_mcp_tools[tool] = top_mcp_tools.get(tool, 0) + 1
        for file_target in file_targets:
            top_files[file_target] = top_files.get(file_target, 0) + 1

        event_metrics = {
            "full_access_events": 1 if is_full_access else 0,
            "autonomous_events": 1 if is_autonomous else 0,
            "tool_permission_events": tool_count,
            "mcp_tool_events": len(mcp_tools),
            "file_targets": len(file_targets),
            "violations": violation_count,
            "warnings": warning_count,
            "errors": error_count,
            "tokens_total": total_tokens,
            "cost_usd": event_cost,
            "latency_ms": latency_ms,
        }
        for buckets, key, label in (
            (by_provider, provider, provider),
            (by_actor, actor, actor),
            (by_model, model_label, model_label),
            (by_repo, repo_name, repo_name),
        ):
            bucket = buckets.setdefault(key, _empty_breakdown(key, label))
            _add_breakdown_metric(bucket, event_metrics, actor, session_id)

    avg_latency = round(sum(latency_values) / len(latency_values), 2) if latency_values else None
    return AgentComplianceMetricsResponse(
        window_days=window_days,
        generated_at=_utc_now(),
        summary=AgentComplianceMetricSummary(
            events=summary_totals["events"],
            users=len(actors),
            providers=len(providers),
            sessions=len(sessions),
            repos=len(repos),
            file_targets=summary_totals["file_targets"],
            tool_permission_events=summary_totals["tool_permission_events"],
            mcp_tool_events=summary_totals["mcp_tool_events"],
            full_access_events=summary_totals["full_access_events"],
            autonomous_events=summary_totals["autonomous_events"],
            approvals=summary_totals["approvals"],
            denials=summary_totals["denials"],
            warnings=summary_totals["warnings"],
            violations=summary_totals["violations"],
            errors=summary_totals["errors"],
            tokens_input=summary_totals["tokens_input"],
            tokens_output=summary_totals["tokens_output"],
            tokens_total=summary_totals["tokens_total"],
            cost_usd=round(cost_usd, 6),
            avg_latency_ms=avg_latency,
        ),
        by_provider=_breakdown_rows(by_provider),
        by_actor=_breakdown_rows(by_actor),
        by_model=_breakdown_rows(by_model),
        by_repo=_breakdown_rows(by_repo),
        top_tools=_counter_rows(top_tools),
        top_mcp_tools=_counter_rows(top_mcp_tools),
        top_files=_counter_rows(top_files),
        policy_decisions=_counter_rows(policy_decisions),
        approval_statuses=_counter_rows(approval_statuses),
        source_record_types=_counter_rows(source_record_types),
        retention_states=_counter_rows(retention_states),
    )


def _empty_developer_bucket(actor: str) -> dict[str, Any]:
    return {
        "actor_login": actor,
        "events": 0,
        "sessions": set(),
        "providers": set(),
        "repos": set(),
        "models": set(),
        "tool_calls": 0,
        "mcp_tool_calls": 0,
        "file_targets": set(),
        "full_access_events": 0,
        "autonomous_events": 0,
        "approvals": 0,
        "denials": 0,
        "warnings": 0,
        "violations": 0,
        "errors": 0,
        "tokens_input": 0,
        "tokens_output": 0,
        "tokens_total": 0,
        "cost_usd": 0.0,
        "latencies": [],
        "risk_score": 0,
        "last_active_at": None,
        "top_tools": {},
        "top_mcp_tools": {},
        "top_files": {},
        "policy_decisions": {},
        "source_record_types": {},
    }


def _developer_track_from_events(events: list[AuditEvent], window_days: int, *, limit: int) -> DeveloperTrackResponse:
    buckets: dict[str, dict[str, Any]] = {}
    provider_set: set[str] = set()
    repo_set: set[str] = set()
    total_sessions: set[str] = set()
    totals = {
        "events": 0,
        "tool_calls": 0,
        "file_targets": 0,
        "violations": 0,
        "warnings": 0,
        "errors": 0,
        "tokens_total": 0,
    }
    total_cost = 0.0

    for event in events:
        if not _is_agent_compliance_event(event):
            continue
        metadata = getattr(event, "metadata_json", {}) or {}
        actor = str(getattr(event, "actor_login", None) or _metadata_value(metadata, "actor_login", "user") or "unknown")
        provider = _metadata_value(metadata, "provider", "agent_provider", "source_provider") or str(getattr(event, "resource_type", None) or "unknown")
        repo_name = str(getattr(event, "repo_name", None) or _metadata_value(metadata, "repo_name", "repo") or "unknown repo")
        model = _metadata_value(metadata, "model", "model_name", "model_id")
        tier = _metadata_value(metadata, "intelligence_tier", "model_tier", "reasoning_tier")
        model_label = f"{model} · {tier}" if model and tier else model or tier
        session_id = _metadata_value(metadata, "session_id", "agent_session_id", "conversation_id", "thread_id")
        tools = _metadata_list(metadata, "tool_permissions") or _metadata_list(metadata, "tools")
        tool_count = _tool_permission_count(metadata)
        mcp_tools = _metadata_list(metadata, "mcp_tools")
        file_targets = _metadata_list(metadata, "file_targets")
        warning_count = _metadata_int(metadata, "warnings", "warning_count")
        violation_count = len(_metadata_list(metadata, "violations")) + _metadata_int(metadata, "violation_count")
        error_count = _metadata_int(metadata, "error_count", "errors")
        input_tokens = _metadata_int(metadata, "tokens_input", "input_tokens", "prompt_tokens")
        output_tokens = _metadata_int(metadata, "tokens_output", "output_tokens", "completion_tokens")
        total_tokens = _metadata_int(metadata, "tokens_total", "total_tokens") or input_tokens + output_tokens
        event_cost = _metadata_float(metadata, "cost_usd", "estimated_cost_usd")
        latency_ms = _metadata_float(metadata, "latency_ms", "duration_ms")
        decision = _metadata_value(metadata, "policy_decision", "decision", "outcome")
        approval = _metadata_value(metadata, "approval_status")
        source_record_type = _metadata_value(metadata, "source_record_type") or "unknown"
        risk_score = max(
            _metadata_int(metadata, "risk_score"),
            85 if decision and decision.lower() in {"deny", "denied", "block", "blocked", "reject", "rejected"} else 0,
            80 if _metadata_value(metadata, "access_scope") == "full-access" else 0,
            70 if violation_count else 0,
            45 if warning_count else 0,
            25,
        )
        is_full_access = _metadata_bool(metadata, "full_access", "full_access_granted") or _metadata_value(metadata, "access_scope") == "full-access"
        is_autonomous = _metadata_bool(metadata, "autonomous_access", "autonomous")

        bucket = buckets.setdefault(actor, _empty_developer_bucket(actor))
        bucket["events"] = int(bucket["events"]) + 1
        bucket["tool_calls"] = int(bucket["tool_calls"]) + tool_count
        bucket["mcp_tool_calls"] = int(bucket["mcp_tool_calls"]) + len(mcp_tools)
        bucket["full_access_events"] = int(bucket["full_access_events"]) + (1 if is_full_access else 0)
        bucket["autonomous_events"] = int(bucket["autonomous_events"]) + (1 if is_autonomous else 0)
        bucket["warnings"] = int(bucket["warnings"]) + warning_count
        bucket["violations"] = int(bucket["violations"]) + violation_count
        bucket["errors"] = int(bucket["errors"]) + error_count
        bucket["tokens_input"] = int(bucket["tokens_input"]) + input_tokens
        bucket["tokens_output"] = int(bucket["tokens_output"]) + output_tokens
        bucket["tokens_total"] = int(bucket["tokens_total"]) + total_tokens
        bucket["cost_usd"] = float(bucket["cost_usd"]) + event_cost
        bucket["risk_score"] = max(int(bucket["risk_score"]), risk_score)
        if latency_ms:
            bucket["latencies"].append(latency_ms)
        created_at = getattr(event, "created_at", None)
        if isinstance(created_at, datetime):
            last_active = bucket["last_active_at"]
            if not isinstance(last_active, datetime) or created_at > last_active:
                bucket["last_active_at"] = created_at
        bucket["providers"].add(provider)
        bucket["repos"].add(repo_name)
        if model_label:
            bucket["models"].add(model_label)
        if session_id:
            bucket["sessions"].add(session_id)
            total_sessions.add(session_id)
        bucket["file_targets"].update(file_targets)
        for key, items in (("top_tools", tools), ("top_mcp_tools", mcp_tools), ("top_files", file_targets)):
            counter = bucket[key]
            for item in items:
                counter[item] = int(counter.get(item, 0)) + 1
        for key, value in (("policy_decisions", decision), ("source_record_types", source_record_type)):
            counter = bucket[key]
            if value:
                counter[value] = int(counter.get(value, 0)) + 1
        if decision and decision.lower() in {"allow", "allowed", "approve", "approved"}:
            bucket["approvals"] = int(bucket["approvals"]) + 1
        elif decision and decision.lower() in {"deny", "denied", "block", "blocked", "reject", "rejected"}:
            bucket["denials"] = int(bucket["denials"]) + 1
        if approval and approval.lower() in {"approved", "approve", "allowed", "allow"}:
            bucket["approvals"] = int(bucket["approvals"]) + 1
        elif approval and approval.lower() in {"denied", "deny", "rejected", "reject", "blocked", "block"}:
            bucket["denials"] = int(bucket["denials"]) + 1

        provider_set.add(provider)
        repo_set.add(repo_name)
        totals["events"] += 1
        totals["tool_calls"] += tool_count
        totals["file_targets"] += len(file_targets)
        totals["violations"] += violation_count
        totals["warnings"] += warning_count
        totals["errors"] += error_count
        totals["tokens_total"] += total_tokens
        total_cost += event_cost

    rows: list[DeveloperTrackRow] = []
    sorted_buckets = sorted(
        buckets.values(),
        key=lambda item: (-int(item["violations"]), -int(item["risk_score"]), -int(item["events"]), str(item["actor_login"])),
    )
    for rank, bucket in enumerate(sorted_buckets[:limit], start=1):
        latencies = bucket["latencies"]
        rows.append(
            DeveloperTrackRow(
                actor_login=str(bucket["actor_login"]),
                rank=rank,
                events=int(bucket["events"]),
                sessions=len(bucket["sessions"]),
                providers=sorted(bucket["providers"]),
                repos=sorted(bucket["repos"]),
                models=sorted(bucket["models"]),
                tool_calls=int(bucket["tool_calls"]),
                mcp_tool_calls=int(bucket["mcp_tool_calls"]),
                file_targets=len(bucket["file_targets"]),
                full_access_events=int(bucket["full_access_events"]),
                autonomous_events=int(bucket["autonomous_events"]),
                approvals=int(bucket["approvals"]),
                denials=int(bucket["denials"]),
                warnings=int(bucket["warnings"]),
                violations=int(bucket["violations"]),
                errors=int(bucket["errors"]),
                tokens_input=int(bucket["tokens_input"]),
                tokens_output=int(bucket["tokens_output"]),
                tokens_total=int(bucket["tokens_total"]),
                cost_usd=round(float(bucket["cost_usd"]), 6),
                avg_latency_ms=round(sum(latencies) / len(latencies), 2) if latencies else None,
                risk_score=int(bucket["risk_score"]),
                risk_band=_risk_band(int(bucket["risk_score"])),
                last_active_at=bucket["last_active_at"] if isinstance(bucket["last_active_at"], datetime) else None,
                top_tools=_counter_rows(bucket["top_tools"], limit=6),
                top_mcp_tools=_counter_rows(bucket["top_mcp_tools"], limit=6),
                top_files=_counter_rows(bucket["top_files"], limit=6),
                policy_decisions=_counter_rows(bucket["policy_decisions"], limit=6),
                source_record_types=_counter_rows(bucket["source_record_types"], limit=6),
            )
        )

    return DeveloperTrackResponse(
        window_days=window_days,
        generated_at=_utc_now(),
        summary=DeveloperTrackSummary(
            developers=len(buckets),
            events=totals["events"],
            sessions=len(total_sessions),
            providers=len(provider_set),
            repos=len(repo_set),
            tool_calls=totals["tool_calls"],
            file_targets=totals["file_targets"],
            violations=totals["violations"],
            warnings=totals["warnings"],
            errors=totals["errors"],
            tokens_total=totals["tokens_total"],
            cost_usd=round(total_cost, 6),
        ),
        developers=rows,
    )


def _intelligence_usage_from_events(events: list[AuditEvent], window_days: int) -> IntelligenceUsageResponse:
    tier_buckets: dict[tuple[str, str | None, str], dict[str, object]] = {}
    access_buckets: dict[tuple[str, str, str | None, str], dict[str, object]] = {}
    for event in events:
        if not _is_agent_compliance_event(event):
            continue
        metadata = getattr(event, "metadata_json", {}) or {}
        provider = _metadata_value(metadata, "provider", "agent_provider", "source_provider") or str(getattr(event, "resource_type", None) or getattr(event, "event_type", "unknown")).split(".")[0]
        model = _metadata_value(metadata, "model", "model_name", "model_id")
        tier = _metadata_value(metadata, "intelligence_tier", "model_tier", "reasoning_tier")
        actor = str(getattr(event, "actor_login", None) or _metadata_value(metadata, "actor_login", "user") or "unknown")
        if tier:
            key = (provider, model, tier)
            bucket = tier_buckets.setdefault(key, {"events": 0, "users": set()})
            bucket["events"] = int(bucket["events"]) + 1
            users = bucket["users"]
            if isinstance(users, set):
                users.add(actor)

        access_scope = _metadata_value(metadata, "access_scope", "permission_scope", "grant_scope")
        is_full_access = _metadata_bool(metadata, "full_access", "full_access_granted")
        is_autonomous = _metadata_bool(metadata, "autonomous_access", "autonomous")
        tool_events = _tool_permission_count(metadata)
        if access_scope or is_full_access or is_autonomous or tool_events:
            scope = access_scope or ("full-access" if is_full_access else "tool-permission")
            repo_name = str(getattr(event, "repo_name", None) or _metadata_value(metadata, "repo_name", "repo") or "") or None
            key = (actor, provider, repo_name, scope)
            bucket = access_buckets.setdefault(
                key,
                {
                    "full_access_events": 0,
                    "autonomous_events": 0,
                    "tool_permission_events": 0,
                    "last_seen_at": None,
                },
            )
            if is_full_access or scope == "full-access":
                bucket["full_access_events"] = int(bucket["full_access_events"]) + 1
            if is_autonomous:
                bucket["autonomous_events"] = int(bucket["autonomous_events"]) + 1
            bucket["tool_permission_events"] = int(bucket["tool_permission_events"]) + tool_events
            created_at = getattr(event, "created_at", None)
            if isinstance(created_at, datetime):
                last_seen_at = bucket["last_seen_at"]
                if not isinstance(last_seen_at, datetime) or created_at > last_seen_at:
                    bucket["last_seen_at"] = created_at

    tier_usage = [
        IntelligenceTierUsage(provider=provider, model=model, intelligence_tier=tier, events=int(values["events"]), users=len(values["users"]) if isinstance(values["users"], set) else 0)
        for (provider, model, tier), values in tier_buckets.items()
    ]
    access_grants = [
        AccessGrantExposure(
            actor_login=actor,
            provider=provider,
            repo_name=repo_name,
            access_scope=scope,
            full_access_events=int(values["full_access_events"]),
            autonomous_events=int(values["autonomous_events"]),
            tool_permission_events=int(values["tool_permission_events"]),
            last_seen_at=values["last_seen_at"] if isinstance(values["last_seen_at"], datetime) else None,
        )
        for (actor, provider, repo_name, scope), values in access_buckets.items()
    ]
    tier_usage.sort(key=lambda item: (-item.events, item.provider, item.intelligence_tier))
    access_grants.sort(key=lambda item: (-(item.full_access_events + item.autonomous_events + item.tool_permission_events), item.actor_login, item.provider))
    return IntelligenceUsageResponse(window_days=window_days, generated_at=_utc_now(), tier_usage=tier_usage, access_grants=access_grants)


def _agent_connector_registry() -> list[dict[str, Any]]:
    return [
        item
        for item in connector_registry()
        if item.get("category") in {"compliance-telemetry", "coding-agent"}
    ]


def _agent_connector_settings(org: Org | None) -> dict[str, dict[str, Any]]:
    settings = dict(getattr(org, "settings", None) or {}) if org else {}
    raw = settings.get("v8_agent_compliance_connectors")
    if not isinstance(raw, dict):
        return {}
    return {str(key): dict(value) for key, value in raw.items() if isinstance(value, dict)}


def _connector_event_matches(event: AuditEvent, connector: dict[str, Any]) -> bool:
    metadata = getattr(event, "metadata_json", {}) or {}
    connector_id = str(connector.get("id") or "")
    label = str(connector.get("label") or "")
    source_type = str(connector.get("source_type") or "")
    candidates = {
        _metadata_value(metadata, "connector_id"),
        _metadata_value(metadata, "provider", "agent_provider", "source_provider"),
        str(getattr(event, "resource_type", "") or ""),
    }
    normalized = {str(item).lower() for item in candidates if item}
    return any(value and value.lower() in normalized for value in (connector_id, label, source_type))


def _provider_coverage_rows(
    org: Org | None,
    events: list[AuditEvent],
    *,
    window_days: int,
    retention_window_days: int,
) -> list[ProviderCoverageRow]:
    now = _utc_now()
    configured = _agent_connector_settings(org)
    rows: list[ProviderCoverageRow] = []
    for connector in _agent_connector_registry():
        connector_id = str(connector.get("id") or "")
        settings = configured.get(connector_id) or {}
        matched = [event for event in events if _connector_event_matches(event, connector)]
        users = {
            str(getattr(event, "actor_login", None) or _metadata_value(getattr(event, "metadata_json", {}) or {}, "actor_login", "user"))
            for event in matched
            if getattr(event, "actor_login", None) or _metadata_value(getattr(event, "metadata_json", {}) or {}, "actor_login", "user")
        }
        models = sorted(
            {
                model
                for event in matched
                if (model := _metadata_value(getattr(event, "metadata_json", {}) or {}, "model", "model_name", "model_id"))
            }
        )
        tiers: dict[str, int] = {}
        for event in matched:
            tier = _metadata_value(getattr(event, "metadata_json", {}) or {}, "intelligence_tier", "model_tier", "reasoning_tier")
            if tier:
                tiers[tier] = tiers.get(tier, 0) + 1
        last_event_at = max([event.created_at for event in matched if isinstance(event.created_at, datetime)], default=None)
        configured_flag = connector_id in configured
        enabled = bool(settings.get("enabled"))
        if not configured_flag:
            status: Literal["unconfigured", "configured", "active", "silent", "stale", "retention-risk"] = "unconfigured"
        elif not enabled:
            status = "configured"
        elif not matched:
            status = "silent"
        elif last_event_at and (now - last_event_at) > timedelta(days=max(1, retention_window_days - 3)):
            status = "retention-risk"
        elif last_event_at and (now - last_event_at) > timedelta(hours=24):
            status = "stale"
        else:
            status = "active"
        retention_days_remaining = None
        if last_event_at:
            retention_days_remaining = max(0, retention_window_days - int((now - last_event_at).total_seconds() // 86400))
        rows.append(
            ProviderCoverageRow(
                connector_id=connector_id,
                label=str(connector.get("label") or connector_id),
                category=str(connector.get("category") or "coding-agent"),
                configured=configured_flag,
                enabled=enabled,
                status=status,
                events=len(matched),
                users=len(users),
                models=models,
                intelligence_tiers=tiers,
                last_event_at=last_event_at,
                last_sync_status=str(settings.get("last_sync_status")) if settings.get("last_sync_status") else None,
                last_sync_requested_at=str(settings.get("last_sync_requested_at")) if settings.get("last_sync_requested_at") else None,
                last_cursor=str(settings.get("cursor")) if settings.get("cursor") else None,
                retention_days_remaining=retention_days_remaining,
            )
        )
    return sorted(rows, key=lambda row: (row.status == "unconfigured", row.status == "configured", -row.events, row.label))


@router.get("/coverage-sla", response_model=CoverageSlaResponse)
async def get_coverage_sla(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> CoverageSlaResponse:
    await _require_v8(org_id, db, current_org_id)
    critical_ops = _load_critical_ops_config()
    repos = (
        await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)).order_by(Repo.full_name))
    ).scalars().all()
    scoped_repos = [repo for repo in repos if _repo_in_scope(repo)]
    skills = (
        await db.execute(select(Skill).where(Skill.repo_id.in_([repo.id for repo in scoped_repos])).order_by(desc(Skill.updated_at)))
    ).scalars().all() if scoped_repos else []
    policies = (
        await db.execute(select(OrgPolicy).where(OrgPolicy.org_id == org_id, OrgPolicy.enabled.is_(True)).order_by(OrgPolicy.name))
    ).scalars().all()
    skills_by_repo: dict[str, list[Skill]] = defaultdict(list)
    for skill in skills:
        skills_by_repo[skill.repo_id].append(skill)
    response_repos: list[CoverageRepo] = []
    for repo in scoped_repos:
        repo_policy_bindings = _policy_bindings(list(policies), repo.id)
        repo_skills = skills_by_repo.get(repo.id, [])
        operations: list[CriticalOperationCoverage] = []
        for operation in critical_ops.operations:
            categories = [str(item) for item in operation.required_skill_categories]
            matched = [skill for skill in repo_skills if (skill.skill_category or "") in categories]
            operations.append(
                CriticalOperationCoverage(
                    operation_id=operation.id,
                    label=operation.label,
                    required_skill_categories=categories,
                    covered=bool(matched) and bool(repo_policy_bindings),
                    skills=[
                        CoverageSkill(
                            id=skill.id,
                            domain=skill.domain,
                            skill_category=skill.skill_category,
                            score_total=int(skill.score_total or 0),
                            last_grounded_at=skill.updated_at or skill.created_at,
                            policy_bindings=repo_policy_bindings,
                        )
                        for skill in matched
                    ],
                )
            )
        response_repos.append(
            CoverageRepo(
                repo_id=repo.id,
                repo_name=repo.full_name,
                sensitivity_tier=_sensitivity_tier(repo),
                last_grounded_at=repo.last_analysed_at,
                policy_bindings=repo_policy_bindings,
                critical_operations=operations,
            )
        )
    return CoverageSlaResponse(
        generated_at=_utc_now(),
        product_review_required=critical_ops.product_review_required,
        product_review_note=critical_ops.product_review_note or "",
        repos=response_repos,
    )


@router.get("/intelligence-usage", response_model=IntelligenceUsageResponse)
async def get_intelligence_usage(
    org_id: str,
    window_days: int = Query(default=30, ge=1, le=180),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> IntelligenceUsageResponse:
    await _require_v8(org_id, db, current_org_id)
    cutoff = _utc_now() - timedelta(days=window_days)
    events = (
        await db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.org_id == org_id,
                AuditEvent.created_at >= cutoff,
                AuditEvent.event_type.in_(sorted(AGENT_COMPLIANCE_EVENT_TYPES)),
            )
            .order_by(desc(AuditEvent.created_at))
            .limit(5000)
        )
    ).scalars().all()
    return _intelligence_usage_from_events(list(events), window_days)


@router.get("/access-grants", response_model=AccessGrantsResponse)
async def get_access_grants(
    org_id: str,
    window_days: int = Query(default=30, ge=1, le=180),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AccessGrantsResponse:
    await _require_v8(org_id, db, current_org_id)
    cutoff = _utc_now() - timedelta(days=window_days)
    events = (
        await db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.org_id == org_id,
                AuditEvent.created_at >= cutoff,
                AuditEvent.event_type.in_(sorted(AGENT_COMPLIANCE_EVENT_TYPES)),
            )
            .order_by(desc(AuditEvent.created_at))
            .limit(5000)
        )
    ).scalars().all()
    usage = _intelligence_usage_from_events(list(events), window_days)
    return AccessGrantsResponse(
        window_days=window_days,
        generated_at=usage.generated_at,
        grants=usage.access_grants,
    )


@router.get("/agent-compliance-metrics", response_model=AgentComplianceMetricsResponse)
async def get_agent_compliance_metrics(
    org_id: str,
    window_days: int = Query(default=30, ge=1, le=180),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AgentComplianceMetricsResponse:
    await _require_v8(org_id, db, current_org_id)
    cutoff = _utc_now() - timedelta(days=window_days)
    events = (
        await db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.org_id == org_id,
                AuditEvent.created_at >= cutoff,
                AuditEvent.event_type.in_(sorted(AGENT_COMPLIANCE_EVENT_TYPES)),
            )
            .order_by(desc(AuditEvent.created_at))
            .limit(5000)
        )
    ).scalars().all()
    return _agent_compliance_metrics_from_events(list(events), window_days)


@router.get("/developer-track", response_model=DeveloperTrackResponse)
async def get_developer_track(
    org_id: str,
    window_days: int = Query(default=30, ge=1, le=180),
    limit: int = Query(default=25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> DeveloperTrackResponse:
    await _require_v8(org_id, db, current_org_id)
    cutoff = _utc_now() - timedelta(days=window_days)
    events = (
        await db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.org_id == org_id,
                AuditEvent.created_at >= cutoff,
                AuditEvent.event_type.in_(sorted(AGENT_COMPLIANCE_EVENT_TYPES)),
            )
            .order_by(desc(AuditEvent.created_at))
            .limit(5000)
        )
    ).scalars().all()
    return _developer_track_from_events(list(events), window_days, limit=limit)


@router.get("/provider-coverage", response_model=ProviderCoverageResponse)
async def get_provider_coverage(
    org_id: str,
    window_days: int = Query(default=30, ge=1, le=180),
    retention_window_days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> ProviderCoverageResponse:
    await _require_v8(org_id, db, current_org_id)
    org = await db.get(Org, org_id)
    cutoff = _utc_now() - timedelta(days=window_days)
    events = (
        await db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.org_id == org_id,
                AuditEvent.created_at >= cutoff,
                AuditEvent.event_type.in_(sorted(AGENT_COMPLIANCE_EVENT_TYPES)),
            )
            .order_by(desc(AuditEvent.created_at))
            .limit(5000)
        )
    ).scalars().all()
    return ProviderCoverageResponse(
        window_days=window_days,
        retention_window_days=retention_window_days,
        generated_at=_utc_now(),
        rows=_provider_coverage_rows(org, list(events), window_days=window_days, retention_window_days=retention_window_days),
    )
