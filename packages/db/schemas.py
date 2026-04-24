from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ScoreResponse(BaseModel):
    total: int
    groundedness: int
    coverage: int
    freshness: int
    structure: int


class OrgResponse(BaseModel):
    id: str
    login: str
    name: str
    plan: str
    repo_count: int
    avg_score: float | None


class OrgSettingsResponse(BaseModel):
    """Response body for organization settings."""

    id: str
    login: str
    name: str
    plan: str
    score_threshold: int
    slack_webhook_url: str | None
    notify_on_pr: bool
    notify_on_stale: bool
    github_app_installed: bool
    github_installation_id: int | None
    webhook_url: str
    recent_deliveries: list[dict[str, object]]


class OrgSettingsUpdate(BaseModel):
    """Partial update body for organization settings."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=255)
    score_threshold: int | None = Field(default=None, ge=0, le=100)
    slack_webhook_url: AnyHttpUrl | None = None
    notify_on_pr: bool | None = None
    notify_on_stale: bool | None = None


class RepoResponse(BaseModel):
    id: str
    full_name: str
    name: str
    installation_id: int | None = None
    language: str | None
    is_monorepo: bool
    last_analysed_at: datetime | None
    score: ScoreResponse | None
    score_delta: int | None
    skill_count: int


class SkillResponse(BaseModel):
    id: str
    repo_id: str
    repo_name: str
    domain: str
    skill_path: str
    score: ScoreResponse
    content: str | None = None
    content_hash: str | None = None
    source_type: str | None = "code"
    skill_category: str | None = "codebase_architecture"
    is_stale: bool
    load_count_30d: int
    last_loaded_at: datetime | None
    version_count: int = 0
    latest_version_number: int | None = None


class SkillVersionSummaryResponse(BaseModel):
    id: str
    version_number: int
    is_latest: bool
    content_hash: str
    created_at: datetime
    run_id: str


class SkillVersionResponse(BaseModel):
    id: str
    version_number: int
    content: str
    content_hash: str
    created_at: datetime
    is_latest: bool


class DependencyResponse(BaseModel):
    id: str
    name: str
    version: str | None
    ecosystem: str
    risk_level: str
    cves: list[str]
    latest_version: str | None
    license: str | None
    created_at: datetime
    upgrade_command: str | None = None


class DependencyReportResponse(BaseModel):
    high_risk: list[DependencyResponse]
    medium_risk: list[DependencyResponse]
    healthy: list[DependencyResponse]
    total_count: int
    risk_score: int


class SkillSourceSkillSummary(BaseModel):
    id: str
    domain: str
    score: int


class RepoSkillSourceSummary(BaseModel):
    source_type: str
    detected: bool
    skill_count: int
    last_analysed_at: datetime | None
    skills: list[SkillSourceSkillSummary]


class SkillCategoryCoverage(BaseModel):
    covered: bool
    skill_count: int
    avg_score: int


class RepoSkillSourcesResponse(BaseModel):
    sources: list[RepoSkillSourceSummary]
    coverage_map: dict[str, SkillCategoryCoverage]
    coverage_score: int


class AnalyzeSourceResponse(BaseModel):
    job_id: str
    status: str


class RepoCoverageSummary(BaseModel):
    repo_id: str
    name: str
    coverage_score: int
    missing_categories: list[str]


class OrgCoverageSummaryResponse(BaseModel):
    repos: list[RepoCoverageSummary]
    org_coverage_score: int
    most_missing_category: str | None


class SkillHeatmapSkillResponse(BaseModel):
    skill_id: str
    domain: str
    repo_id: str
    repo_name: str
    skill_category: str
    source_type: str
    score_total: int
    is_stale: bool
    loads_30d: int
    loads_7d: int
    criticality_score: int
    last_loaded_at: datetime | None
    agent_runtimes: list[str]
    alert: str


class SkillHeatmapSummaryResponse(BaseModel):
    total_skills: int
    dead_skills: int
    stale_but_active: int
    healthy: int
    avg_criticality: int


class SkillHeatmapResponse(BaseModel):
    skills: list[SkillHeatmapSkillResponse]
    summary: SkillHeatmapSummaryResponse


class RuntimeBreakdownEntryResponse(BaseModel):
    runtime: str
    display_name: str
    loads_30d: int
    unique_skills: int
    top_skill_domain: str | None


class RuntimeBreakdownResponse(BaseModel):
    runtimes: list[RuntimeBreakdownEntryResponse]
    total_loads_30d: int


class DailyLoadPointResponse(BaseModel):
    date: str
    loads: int


class RepoSkillUsageStatsResponse(BaseModel):
    criticality_score: int
    loads_30d: int
    loads_7d: int
    last_loaded_at: datetime | None
    alert: str
    daily_loads: list[DailyLoadPointResponse]
    agent_runtimes: dict[str, int]


class TeamRepoScoreResponse(BaseModel):
    id: str
    name: str
    score: int


class TeamRollupTeamResponse(BaseModel):
    team_name: str
    repo_count: int
    avg_score: int
    worst_repo: TeamRepoScoreResponse | None
    best_repo: TeamRepoScoreResponse | None
    score_delta_7d: int | None
    skill_count: int
    coverage_score: int
    repos: list[TeamRepoScoreResponse]


class TeamRollupResponse(BaseModel):
    teams: list[TeamRollupTeamResponse]
    org_avg_score: int
    top_team: str | None
    needs_attention: str | None


class AuditLogEventResponse(BaseModel):
    id: str
    event_type: str
    repo_name: str
    repo_id: str
    actor: str
    status: str
    score_before: int | None
    score_after: int | None
    skill_count: int | None
    created_at: datetime | None


class AuditLogResponse(BaseModel):
    events: list[AuditLogEventResponse]
    limit: int
    offset: int


class GovernancePolicyResponse(BaseModel):
    id: str
    name: str
    type: str
    threshold: int | list[str]
    scope: str
    action: str
    enabled: bool = True
    created_at: datetime | None = None


class GovernancePoliciesResponse(BaseModel):
    policies: list[GovernancePolicyResponse]


class RegistrySkillSummaryResponse(BaseModel):
    id: str
    org_id: str
    repo_id: str
    skill_id: str
    domain: str
    name: str
    description: str
    is_public: bool
    is_official: bool
    import_count: int
    tags: list[str]
    created_at: datetime
    score_total: int


class RegistryListResponse(BaseModel):
    skills: list[RegistrySkillSummaryResponse]
    total: int
    limit: int
    offset: int


class RegistrySkillDetailResponse(RegistrySkillSummaryResponse):
    content: str
    content_hash: str | None
    skill_path: str
    repo_name: str
    repo_full_name: str


class AnalysisRunResponse(BaseModel):
    id: str
    status: str
    trigger: str
    commit_sha: str | None
    score: ScoreResponse | None
    domain_count: int | None
    skill_count: int | None
    started_at: datetime | None
    completed_at: datetime | None


class WebhookPayload(BaseModel):
    action: str | None = None
    ref: str | None = None
    repository: dict[str, Any]
    installation: dict[str, Any] | None = None
    sender: dict[str, Any]
