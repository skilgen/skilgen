from __future__ import annotations

import asyncio
import base64
from collections import defaultdict
from itertools import combinations
import json
import socket
import urllib.error
import urllib.request
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
import hashlib
import logging
import secrets
from typing import Any, Literal
from uuid import NAMESPACE_URL, uuid4, uuid5

import csv
from io import StringIO
import time
import httpx

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_org_id_optional
from apps.api.api.github import get_installation_token
from apps.api.api.notifications import build_test_notification_message, post_slack_message
from apps.api.api.services import audit
from apps.api.api.services.audit import get_actor_login
from apps.api.api.services.agent_connection import get_agent_connection_status, normalize_runtime, runtime_display_name
from apps.api.api.services.commit_check import _severity_bucket
from apps.api.api.services.github_pr import create_skill_pr
from apps.api.api.services.dependency_analyzer import compute_cross_repo_dependencies, compute_repo_dependencies
from apps.api.api.services.half_life import compute_skill_decay_timeline, predict_half_life_days
from apps.api.api.services.knowledge_concentration import concentration_response
from apps.api.api.services.llm import LLMCallError, LLMNotConfiguredError, call_llm
from apps.api.api.services.manifest import verify_manifest
from apps.api.api.services.skill_generator import generate_skill_with_ai
from packages.db.llm_key import decrypt_key, encrypt_key, key_hint
from apps.api.api.services.policy import POLICY_RULE_TYPES, PolicyViolation, evaluate_policies
from apps.api.api.services.policy_engine import PR_POLICY_RULE_TYPES, validate_pr_policy_config
from apps.api.api.services.redflags import compute_repo_red_flags
from apps.api.api.services.standup import collect_standup_summary, parse_standup_date, send_standup
from packages.db.database import get_db
from packages.db.models import AgentSession, AnalysisRun, AuditEvent, CoverageGap, DependencyGraphCache, FlagDismissal, Org, OrgLLMConfig, OrgPolicy, PRAttribution, PullRequest, Repo, ScoreHistory, Skill, SkillHalfLife, SkillMemoryStub, SkillUsageEvent, SkillVersion
from packages.db.models import SourceConnection as SourceConnectionModel
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
ALL_POLICY_RULE_TYPES = POLICY_RULE_TYPES | PR_POLICY_RULE_TYPES

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

SKILL_CATEGORY_LABELS = {
    "codebase_architecture": "Architecture",
    "code_style": "Code Style",
    "testing_conventions": "Testing",
    "internal_tools": "Internal Tools",
    "security_compliance": "Security",
    "design_system": "Design System",
    "data_schema": "Data Schema",
    "operational_knowledge": "Operational",
}


class DebtGapGenerateRequest(BaseModel):
    mode: Literal["preview", "push"] = "preview"


class DebtGenerateAllRequest(BaseModel):
    domains: list[str] | None = None
    repo_ids: list[str] | None = None


class ManifestVerifyRequest(BaseModel):
    manifest: dict[str, Any]

SOURCE_TYPE_DISPLAY_NAMES = {
    "code": "Codebase",
    "github": "GitHub",
    "openapi": "OpenAPI",
    "graphql": "GraphQL",
    "postman": "Postman",
    "terraform": "Terraform",
    "kubernetes": "Kubernetes",
    "helm": "Helm",
    "dbt": "dbt",
    "sql_schema": "SQL Schema",
    "kafka": "Kafka",
    "sarif": "SARIF",
    "sbom": "SBOM",
    "security_policy": "Security Policy",
    "runbook": "Runbook",
    "confluence": "Confluence",
    "notion": "Notion",
    "incident": "Incidents",
    "pagerduty": "PagerDuty",
}

SOURCE_REFRESH_COMMANDS = {
    "code": "skilgen deliver --project-root .",
    "github": "skilgen deliver --project-root .",
    "openapi": "skilgen analyze --source openapi",
    "graphql": "skilgen analyze --source graphql",
    "postman": "skilgen analyze --source postman",
    "terraform": "skilgen analyze --source terraform",
    "kubernetes": "skilgen analyze --source kubernetes",
    "helm": "skilgen analyze --source helm",
    "dbt": "skilgen analyze --source dbt",
    "sql_schema": "skilgen analyze --source sql_schema",
    "kafka": "skilgen analyze --source kafka",
    "sarif": "skilgen analyze --source sarif",
    "sbom": "skilgen analyze --source sbom",
    "security_policy": "skilgen analyze --source security_policy",
    "runbook": "skilgen analyze --source runbook",
    "confluence": "skilgen analyze --source confluence",
    "notion": "skilgen analyze --source notion",
    "incident": "skilgen analyze --source incident",
    "pagerduty": "skilgen analyze --source pagerduty",
}

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

COMMON_SOURCE_TYPES: dict[str, dict[str, str]] = {
    "github": {"label": "GitHub", "command": "skilgen deliver --project-root ."},
    "openapi": {"label": "OpenAPI", "command": "skilgen analyse --source openapi --file openapi.yaml"},
    "database": {"label": "PostgreSQL", "command": "skilgen analyse --source sql-schema --file schema.sql"},
    "confluence": {"label": "Confluence", "command": "skilgen analyse --source confluence --space TEAM"},
    "terraform": {"label": "Terraform", "command": "skilgen analyse --source terraform --dir infra/"},
    "kubernetes": {"label": "Kubernetes", "command": "skilgen analyse --source kubernetes --dir k8s/"},
    "kafka": {"label": "Kafka", "command": "skilgen analyse --source kafka --bootstrap-server localhost:9092"},
    "dbt": {"label": "dbt", "command": "skilgen analyse --source dbt --dir models/"},
    "sarif": {"label": "SARIF", "command": "skilgen analyse --source sarif --file results.sarif"},
    "pagerduty": {"label": "PagerDuty", "command": "skilgen analyse --source pagerduty"},
    "notion": {"label": "Notion", "command": "skilgen analyse --source notion --workspace TEAM"},
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


class MemoryStubResponse(BaseModel):
    id: str
    repo_id: str
    repo_name: str
    domain: str
    skill_id: str | None
    discovery_type: str
    title: str
    proposed_content: str
    evidence: str | None
    confidence: float
    agent_runtime: str
    engineer_login: str | None
    task_description: str | None
    status: str
    reviewer_note: str | None
    merged_version_number: int | None
    created_at: datetime
    reviewed_at: datetime | None
    session_created_at: datetime
    existing_skill_content: str | None


class MemoryQueueResponse(BaseModel):
    total: int
    pending_count: int
    items: list[MemoryStubResponse]


class MemoryStubAction(BaseModel):
    action: Literal["approve", "reject"]
    edited_content: str | None = None
    reviewer_note: str | None = None


class KnowledgeVelocityWeek(BaseModel):
    week_start: str
    discovered: int
    approved: int


class KnowledgeVelocityResponse(BaseModel):
    weekly: list[KnowledgeVelocityWeek]
    total_discoveries_all_time: int
    approval_rate: float | None


class RedFlagResponse(BaseModel):
    flag_type: str
    severity: Literal["critical", "high", "medium"]
    repo_id: str
    repo_name: str
    skill_id: str | None
    domain: str | None
    title: str
    description: str
    loads_30d: int
    action: str
    action_url: str | None


class RedFlagsResponse(BaseModel):
    critical_count: int
    high_count: int
    medium_count: int
    flags: list[RedFlagResponse]


class AnthropicKeyPayload(BaseModel):
    api_key: str = Field(min_length=1, max_length=4096)


class OrgIntegrationSettingsResponse(BaseModel):
    anthropic_api_key_set: bool
    anthropic_api_key_hint: str | None = None
    other: dict[str, object] = Field(default_factory=dict)


class SlackSettingsPayload(BaseModel):
    webhook_url: str | None = Field(default=None, max_length=4096)
    standup_enabled: bool = False
    standup_hour: int = Field(default=9, ge=0, le=23)


class MyCodeTodayPR(BaseModel):
    id: str
    github_pr_number: int
    title: str
    state: str | None
    risk_tier: str


class MyCodeTodaySession(BaseModel):
    session_id: str
    agent_runtime: str
    started_at: str
    ended_at: str | None
    files_touched: list[str]
    skills_loaded: list[str]
    outcome: str | None
    pr: MyCodeTodayPR | None = None


class MyCodeTodaySummary(BaseModel):
    total_sessions: int
    total_files: int
    skills_used: list[str]
    prs_opened: int
    prs_merged: int
    violations: int
    warnings: int


class MyCodeTodayResponse(BaseModel):
    date: str
    login: str
    sessions: list[MyCodeTodaySession]
    summary: MyCodeTodaySummary


class RedFlagDismissPayload(BaseModel):
    flag_type: str = Field(min_length=1, max_length=100)
    repo_id: str = Field(min_length=1)
    skill_id: str | None = None
    reason: str = Field(default="not_a_risk", max_length=255)


class RedFlagRestorePayload(BaseModel):
    flag_type: str = Field(min_length=1, max_length=100)
    repo_id: str = Field(min_length=1)
    skill_id: str | None = None


class FlagDismissalResponse(BaseModel):
    id: str
    org_id: str
    flag_type: str
    repo_id: str
    skill_id: str | None
    dismissed_by: str
    reason: str
    dismissed_at: datetime


class MemoryScoreBreakdown(BaseModel):
    coverage: float
    load_frequency: float
    compliance: float
    freshness: float
    quality: float | None = None


class MemoryScoreResponse(BaseModel):
    score: int
    breakdown: MemoryScoreBreakdown
    trend_7d: int
    trend_30d: int
    computed_at: datetime
    trend: str | None = None
    grade: Literal["A", "B", "C", "D", "F"]


class AuditEventResponse(BaseModel):
    id: str
    event_type: str
    action: str
    actor_login: str | None
    repo_id: str | None
    repo_name: str | None
    skill_id: str | None
    skill_domain: str | None
    resource_type: str | None
    resource_id: str | None
    summary: str
    severity: Literal["info", "warning", "critical"]
    metadata: dict[str, object]
    created_at: datetime


class AuditEventsResponse(BaseModel):
    total: int
    events: list[AuditEventResponse]
    has_more: bool


class AuditStatsResponse(BaseModel):
    total_events: int
    by_severity: dict[str, int]
    by_resource_type: dict[str, int]
    most_active_actor: str | None
    critical_events_7d: int
    analysis_runs_30d: int
    gate_failures_30d: int
    gate_pass_rate: float | None


class AuditWebhookConfig(BaseModel):
    webhook_url: str
    secret: str | None = None
    enabled: bool
    event_filter: Literal["critical", "warnings", "all"] = "warnings"


class PolicyResponse(BaseModel):
    id: str
    name: str
    description: str | None
    rule_type: str
    rule_config: dict[str, object]
    severity: Literal["error", "warning"]
    enabled: bool
    created_at: datetime
    violation_count: int = 0


class PolicyMutation(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=512)
    rule_type: str | None = None
    rule_config: dict[str, object] | None = None
    severity: Literal["error", "warning"] | None = None
    enabled: bool | None = None


class PolicyViolationResponse(BaseModel):
    policy_id: str
    policy_name: str
    rule_type: str
    severity: Literal["error", "warning"]
    repo_id: str | None
    repo_name: str | None
    skill_id: str | None
    skill_domain: str | None
    description: str
    fix_url: str | None


class PolicyCheckResponse(BaseModel):
    passed: bool
    error_count: int
    warning_count: int
    violations: list[PolicyViolationResponse]
    checked_at: datetime


class OrgLLMConfigResponse(BaseModel):
    provider: str | None
    model: str | None
    base_url: str | None = None
    api_key_hint: str | None
    is_configured: bool


class LLMConfigUpdate(BaseModel):
    provider: Literal["anthropic", "openai", "gemini", "custom"]
    model: str = Field(min_length=1, max_length=200)
    api_key: str = Field(min_length=1, max_length=4096)
    base_url: str | None = Field(default=None, max_length=1024)


class LLMConfigTestResponse(BaseModel):
    success: bool
    response: str | None = None
    error: str | None = None


class SkillSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    mode: Literal["natural", "skillql"] = "natural"
    limit: int = Field(default=20, ge=1, le=50)


class SkillSearchResult(BaseModel):
    skill_id: str
    repo_id: str
    repo_name: str
    domain: str
    skill_category: str | None
    score_total: int
    load_count_30d: int
    is_stale: bool
    content_preview: str
    relevance_score: int


class SkillSearchResponse(BaseModel):
    query: str
    mode: Literal["natural", "skillql"]
    result_count: int
    results: list[SkillSearchResult]


class SkillColoadTreeNode(BaseModel):
    name: str
    value: float = 0
    display: str | None = None
    always_together: bool | None = None
    score: int | None = None
    status: str | None = None
    skill_id: str | None = None
    runtime: str | None = None
    cluster_id: str | None = None
    repo_name: str | None = None
    loads_30d: int | None = None
    sessions: int | None = None
    children: list["SkillColoadTreeNode"] = Field(default_factory=list)


class SkillColoadTreeResponse(SkillColoadTreeNode):
    uniform_loads: bool
    generated_at: datetime


class AnalyticsSuggestionRequest(BaseModel):
    skill_id: str = Field(min_length=1)
    risk_reason: str = Field(min_length=1, max_length=2000)


class AnalyticsSuggestionResponse(BaseModel):
    skill_id: str
    suggestions: list[str]
    summary: str


class AnalyticsRiskHighlightResponse(BaseModel):
    summary: str
    highlights: list[str]


class SkillAIActionPreviewRequest(BaseModel):
    repo_id: str
    domain: str = Field(min_length=1, max_length=120)
    reason: str = Field(min_length=1, max_length=2000)
    affected_files: list[str] = Field(default_factory=list, max_length=20)
    source: Literal["knowledge_risk", "red_flag"] = "knowledge_risk"


class SkillAIActionPreviewResponse(BaseModel):
    repo_id: str
    repo_name: str
    domain: str
    skill_path: str
    branch_name: str
    pr_title: str
    pr_body: str
    content: str
    file_references: list[str] = []
    anti_patterns: list[str] = []


class SkillAIActionPushRequest(BaseModel):
    repo_id: str
    domain: str = Field(min_length=1, max_length=120)
    skill_path: str = Field(min_length=1, max_length=512)
    content: str = Field(min_length=1, max_length=60000)
    branch_name: str = Field(min_length=1, max_length=255)
    pr_title: str = Field(min_length=1, max_length=255)
    pr_body: str = Field(min_length=1, max_length=4000)


class SkillAIActionPushResponse(BaseModel):
    pr_url: str
    pr_number: int
    branch: str


class SourceRefreshRequest(BaseModel):
    repo_id: str = Field(min_length=1)
    source_type: str = Field(min_length=1, max_length=80)


class SourceConnectionRequest(BaseModel):
    source_type: str = Field(min_length=1, max_length=80)
    params: dict[str, Any] = Field(default_factory=dict)
    display_name: str | None = Field(default=None, max_length=255)
    timeout_seconds: float = Field(default=3.0, ge=0.1, le=10.0)


class SourceTestResponse(BaseModel):
    source_type: str
    success: bool
    status: str
    message: str
    details: dict[str, object] = Field(default_factory=dict)
    tested_at: datetime


class SourceConnectResponse(BaseModel):
    id: str
    source_type: str
    display_name: str
    connected: bool
    status: str
    message: str
    last_tested_at: datetime | None


class SourceConnection(BaseModel):
    id: str
    source_type: str
    display_name: str
    repo_id: str | None = None
    connected: bool
    skill_count: int
    last_skill_generated_at: str | None
    can_generate_skills: bool
    generate_command: str | None
    coverage_domains: list[str]
    connection_id: str | None = None
    connection_status: str | None = None
    last_tested_at: datetime | None = None
    last_connected_at: datetime | None = None
    last_error: str | None = None


class EnterpriseSkillRequest(BaseModel):
    skill_id: str | None = Field(default=None, min_length=1)
    skill_ids: list[str] = Field(default_factory=list)
    is_enterprise: bool = True
    name: str | None = None
    domain: str | None = None
    content: str | None = None
    applies_to: Literal["all"] | list[str] = "all"


class EnterpriseSkillResponse(BaseModel):
    id: str
    repo_id: str
    repo_name: str
    domain: str
    skill_path: str
    source_type: str | None
    skill_category: str | None
    score_total: int
    is_enterprise: bool
    last_updated_at: datetime | None


class InsightItem(BaseModel):
    type: Literal["anomaly", "opportunity", "trend", "gap"]
    title: str
    description: str
    cta_label: str | None = None
    cta_url: str | None = None
    severity: Literal["high", "medium", "low"]


class KnowledgeRiskGenerateRequest(BaseModel):
    mode: Literal["preview", "push"] = "preview"
    custom_intent: str | None = Field(default=None, max_length=2000)


class KnowledgeRiskDismissResponse(BaseModel):
    dismissed: bool


class ConnectRuntimeStatus(BaseModel):
    connected: bool
    last_seen_at: str | None = None
    load_count_30d: int = 0


class ConnectStatusResponse(BaseModel):
    org_id: str
    repos_connected: int
    skills_generated: int
    github_app_installed: bool
    agent_runtimes: dict[str, ConnectRuntimeStatus]
    next_step: str | None = None


class HalfLifeBufferRequest(BaseModel):
    hours_before_decay: int = Field(default=24, ge=1, le=168)


class OrgHalfLifeSkillResponse(BaseModel):
    skill_id: str
    repo_id: str
    repo_name: str
    domain: str
    skill_path: str
    predicted_decay_days: float
    predicted_decay_date: datetime | None
    decay_confidence: float
    regeneration_buffer_hours: int
    regen_queued: bool
    urgency: Literal["now", "soon", "ok"]


class OrgHalfLifeResponse(BaseModel):
    summary: dict[str, int]
    skills: list[OrgHalfLifeSkillResponse]


class HalfLifeRefreshResponse(BaseModel):
    refreshed: bool
    skill_count: int
    regen_queued_count: int


class HalfLifeBufferPayload(BaseModel):
    buffer_hours: int = Field(default=24, ge=1, le=168)
    skill_id: str | None = None


class HalfLifeBufferResponse(BaseModel):
    updated: bool
    buffer_hours: int
    skill_count: int
    queued: list[dict[str, object]] = Field(default_factory=list)


class TeamSummaryResponse(BaseModel):
    team_count: int
    repo_count: int
    avg_score: int
    top_team: str | None = None
    needs_attention: str | None = None


class CriticalityItem(BaseModel):
    skill_id: str
    domain: str
    repo_id: str
    repo_name: str
    load_count_30d: int
    score_total: int
    risk_level: Literal["critical", "high", "medium", "low"]
    risk_reason: str
    dependency_rank: int
    is_every_session: bool
    last_loaded_at: str | None = None


class SessionSkillItem(BaseModel):
    domain: str
    score: int
    loaded_at: str


class OrgSessionItem(BaseModel):
    session_id: str
    agent_runtime: str
    agent_display_name: str = ""
    repo_id: str
    repo_name: str
    started_at: str
    ended_at: str
    duration_minutes: float
    skills_loaded: list[SessionSkillItem]
    skill_count: int
    session_context: str
    quality_signal: Literal["strong", "mixed", "weak"]
    avg_skill_score: int
    outcome: str = "unknown"


class SessionTagPayload(BaseModel):
    outcome: Literal["success", "needs_rework", "unknown"] = "unknown"
    notes: str | None = Field(default=None, max_length=1000)


class OrgSessionsResponse(BaseModel):
    sessions: list[OrgSessionItem]
    total: int


class SetupStatusStep(BaseModel):
    id: str
    title: str
    done: bool
    action_url: str | None = None
    description: str | None = None
    cli_command: str | None = None


class SetupStatusResponse(BaseModel):
    has_repos: bool
    has_skills: bool
    has_agent_loads: bool
    has_high_score_skills: bool
    setup_steps: list[SetupStatusStep]
    completion_percent: int


class OrgApiKeyResponse(BaseModel):
    api_key: str


class OrgActionItemResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    action_url: str
    priority: Literal["urgent", "recommended", "suggested"]


class OrgActionItemsResponse(BaseModel):
    items: list[OrgActionItemResponse]


class SkillPushPayload(BaseModel):
    skill_id: str | None = None
    branch_name: str | None = Field(default=None, max_length=255)
    pr_title: str | None = Field(default=None, max_length=255)
    pr_body: str | None = Field(default=None, max_length=4000)
    content: str | None = Field(default=None, max_length=200_000)
    generate_if_missing: bool = False


class SkillPushResponse(BaseModel):
    pushed: bool
    repo_id: str
    skill_id: str
    pr_url: str
    pr_number: int
    branch: str


def _last_30_score_dates() -> list[str]:
    """Return the last 30 UTC score dates in chronological order."""
    today = datetime.now(UTC).date()
    return [(today - timedelta(days=offset)).isoformat() for offset in range(29, -1, -1)]


def _utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _runtime_display_name(runtime: str | None) -> str:
    return runtime_display_name(runtime)


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


def _skill_age_days(skill: Skill, now: datetime) -> int:
    created_at = skill.created_at.replace(tzinfo=None) if skill.created_at and skill.created_at.tzinfo else skill.created_at
    if not created_at:
        return 0
    return max(0, (now - created_at).days)


def _criticality_risk(skill: Skill, loads: int, is_every_session: bool, now: datetime) -> tuple[str, str]:
    score = int(skill.score_total or 0)
    freshness = int(skill.score_freshness or 0)
    coverage = int(getattr(skill, "score_coverage", 0) or 0)
    age_days = _skill_age_days(skill, now)
    stale = bool(skill.is_stale) or age_days > 30
    load_label = "Loaded in nearly every recorded session" if is_every_session else f"Loaded {loads} times in 30 days"
    if loads >= 5 and score < 60:
        return "critical", f"{load_label}, but quality is only {score}/100; agents are repeatedly receiving weak guidance."
    if loads >= 3 and freshness < 8:
        return "critical", f"{load_label}, while freshness is {freshness}/25; this is high-use stale context."
    if loads >= 3 and stale:
        return "critical", f"{load_label}, and the skill appears stale for {age_days} days; refresh before more sessions rely on it."
    if loads >= 3 and score < 75:
        return "high", f"{load_label} with quality {score}/100; improve it before this pattern spreads further."
    if loads >= 2 and coverage < 10:
        return "high", f"{load_label}, but coverage is {coverage}/25; agents may be missing key cases."
    if loads >= 1 and score < 80:
        return "medium", f"{load_label} with score {score}/100; review before it becomes a stronger dependency."
    if loads == 0 and str(skill.skill_category or "") == "codebase_architecture":
        return "medium", "Core architectural skill but never loaded; agents may be coding without architecture context."
    return "low", "Usage and quality are in a reasonable range."


def _session_context_from_domains(domains: list[str]) -> str:
    normalized = {domain.lower() for domain in domains}
    if any("security" in domain for domain in normalized):
        return "Security-sensitive work"
    if "data_schema" in normalized or any("schema" in domain for domain in normalized):
        return "Database or data model changes"
    if "testing_conventions" in normalized or any("test" in domain for domain in normalized):
        return "Writing or fixing tests"
    if "codebase_architecture" in normalized and len(domains) >= 4:
        return "Major architectural change"
    if len(domains) >= 6:
        return "Broad feature development"
    if len(domains) == 1:
        return f"Focused {domains[0]} work"
    return "General development session"


def _session_quality_from_scores(scores: list[int]) -> tuple[Literal["strong", "mixed", "weak"], int]:
    avg = round(sum(scores) / len(scores)) if scores else 0
    if avg >= 75:
        return "strong", avg
    if avg >= 50:
        return "mixed", avg
    return "weak", avg


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


def _audit_event_response(event: AuditEvent) -> AuditEventResponse:
    return AuditEventResponse(
        id=event.id,
        event_type=event.event_type,
        action=event.action,
        actor_login=event.actor_login,
        repo_id=event.repo_id,
        repo_name=event.repo_name,
        skill_id=event.skill_id,
        skill_domain=event.skill_domain,
        resource_type=event.resource_type,
        resource_id=event.resource_id,
        summary=event.summary,
        severity=event.severity if event.severity in {"info", "warning", "critical"} else "info",
        metadata=event.metadata_json or {},
        created_at=event.created_at,
    )


def _policy_response(policy: OrgPolicy, violation_count: int = 0) -> PolicyResponse:
    return PolicyResponse(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        rule_type=policy.rule_type,
        rule_config=policy.rule_config or {},
        severity=policy.severity if policy.severity in {"error", "warning"} else "error",
        enabled=bool(policy.enabled),
        created_at=policy.created_at,
        violation_count=violation_count,
    )


def _policy_violation_response(violation: PolicyViolation) -> PolicyViolationResponse:
    return PolicyViolationResponse(**violation.__dict__)


def _policy_check_response(violations: list[PolicyViolation]) -> PolicyCheckResponse:
    error_count = sum(1 for item in violations if item.severity == "error")
    warning_count = sum(1 for item in violations if item.severity == "warning")
    return PolicyCheckResponse(
        passed=error_count == 0,
        error_count=error_count,
        warning_count=warning_count,
        violations=[_policy_violation_response(item) for item in violations],
        checked_at=_utc_now_naive(),
    )


def _llm_config_response(org: Org | None) -> OrgLLMConfigResponse:
    settings_payload = dict(org.settings or {}) if org is not None and isinstance(org.settings, dict) else {}
    return OrgLLMConfigResponse(
        provider=str(settings_payload["llm_provider"]) if settings_payload.get("llm_provider") else None,
        model=str(settings_payload["llm_model"]) if settings_payload.get("llm_model") else None,
        api_key_hint=str(settings_payload["llm_api_key_hint"]) if settings_payload.get("llm_api_key_hint") else None,
        base_url=str(settings_payload["llm_base_url"]) if settings_payload.get("llm_base_url") else None,
        is_configured=bool(settings_payload.get("llm_api_key_enc")),
    )


def _clear_org_llm_settings(org: Org) -> None:
    settings_payload = dict(org.settings or {}) if isinstance(org.settings, dict) else {}
    for key in ("llm_provider", "llm_model", "llm_api_key_enc", "llm_base_url", "llm_api_key_hint", "llm_config"):
        settings_payload.pop(key, None)
    org.settings = settings_payload


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


def _org_settings_dict(org: Org) -> dict[str, object]:
    return dict(org.settings or {}) if isinstance(org.settings, dict) else {}


def _anthropic_settings_response(org: Org) -> OrgIntegrationSettingsResponse:
    settings = _org_settings_dict(org)
    encrypted_key = settings.get("anthropic_api_key_encrypted")
    hint = settings.get("anthropic_api_key_hint")
    other = {key: value for key, value in settings.items() if not str(key).startswith("anthropic_api_key")}
    return OrgIntegrationSettingsResponse(
        anthropic_api_key_set=bool(encrypted_key),
        anthropic_api_key_hint=str(hint) if hint else None,
        other=other,
    )


def _memory_grade(score: int) -> Literal["A", "B", "C", "D", "F"]:
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"


def build_memory_score_response(
    repos: list[Repo],
    skills: list[Skill],
    total_loads_30d: int,
    previous_score: int | None = None,
) -> MemoryScoreResponse:
    """Compute the board-level organizational memory score."""
    if not skills:
        return MemoryScoreResponse(
            score=0,
            breakdown=MemoryScoreBreakdown(coverage=0, load_frequency=0, compliance=0, quality=0, freshness=0),
            trend_7d=0,
            trend_30d=0,
            computed_at=datetime.utcnow(),
            trend="Stable",
            grade="F",
        )

    skills_by_repo: dict[str, list[Skill]] = {repo.id: [] for repo in repos}
    for skill in skills:
        skills_by_repo.setdefault(skill.repo_id, []).append(skill)

    repo_coverage_rates = []
    for repo in repos:
        repo_skills = skills_by_repo.get(repo.id, [])
        covered = {_skill_category(skill) for skill in repo_skills if _skill_category(skill) in SKILL_CATEGORIES}
        repo_coverage_rates.append(min(1.0, len(covered) / len(SKILL_CATEGORIES)))
    coverage_rate = sum(repo_coverage_rates) / len(repo_coverage_rates) if repo_coverage_rates else 0
    load_frequency_score = min(1.0, total_loads_30d / 1000)
    avg_skill_quality = min(1.0, sum(int(skill.score_total or 0) for skill in skills) / (len(skills) * 100))
    freshness_rate = sum(1 for skill in skills if int(skill.score_freshness or 0) >= 15) / len(skills)

    raw_score = (
        coverage_rate * 30
        + load_frequency_score * 25
        + avg_skill_quality * 30
        + freshness_rate * 15
    )
    score = round(raw_score)
    trend_7d = 0 if previous_score is None else score - previous_score
    trend_30d = trend_7d
    if previous_score is None or previous_score == score:
        trend = "Stable"
    else:
        trend = f"{trend_7d:+d} this week"
    return MemoryScoreResponse(
        score=score,
        breakdown=MemoryScoreBreakdown(
            coverage=round(coverage_rate, 4),
            load_frequency=round(load_frequency_score, 4),
            compliance=round(avg_skill_quality, 4),
            quality=round(avg_skill_quality, 4),
            freshness=round(freshness_rate, 4),
        ),
        trend_7d=trend_7d,
        trend_30d=trend_30d,
        computed_at=datetime.utcnow(),
        trend=trend,
        grade=_memory_grade(score),
    )


def _encode_cursor(offset: int) -> str:
    return base64.urlsafe_b64encode(str(offset).encode("utf-8")).decode("ascii").rstrip("=")


def _decode_cursor(cursor: str | None) -> int:
    if not cursor:
        return 0
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        return max(0, int(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")))
    except (ValueError, UnicodeDecodeError):
        return 0


def _normalise_agent_filter(agent: str | None) -> set[str]:
    if not agent:
        return set()
    return {part.strip() for part in agent.split(",") if part.strip()}


def _pr_html_url(pr: PullRequest, repo: Repo) -> str | None:
    raw = pr.raw if isinstance(pr.raw, dict) else {}
    url = raw.get("html_url")
    if isinstance(url, str) and url:
        return url
    if repo.full_name and pr.github_pr_number:
        return f"https://github.com/{repo.full_name}/pull/{pr.github_pr_number}"
    return None


def _check_runs(pr: PullRequest) -> list[dict[str, object]]:
    raw = pr.raw if isinstance(pr.raw, dict) else {}
    runs = raw.get("check_runs")
    if not isinstance(runs, list):
        return []
    normalized: list[dict[str, object]] = []
    for item in runs:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "name": item.get("name") or "Check",
                "status": item.get("status") or "unknown",
                "conclusion": item.get("conclusion"),
                "details_url": item.get("details_url") or item.get("html_url"),
            }
        )
    return normalized


def _ci_status(pr: PullRequest) -> str:
    runs = _check_runs(pr)
    if not runs:
        return "unknown"
    if any(run.get("status") != "completed" for run in runs):
        return "pending"
    conclusions = {str(run.get("conclusion") or "").lower() for run in runs}
    if "failure" in conclusions or "timed_out" in conclusions or "cancelled" in conclusions:
        return "failure"
    if conclusions and conclusions.issubset({"success", "skipped", "neutral"}):
        return "success"
    return "neutral"


def _finding_counts(attribution: PRAttribution | None) -> tuple[int, int]:
    findings = attribution.skills_violated if attribution and isinstance(attribution.skills_violated, list) else []
    violations = 0
    warnings = 0
    for item in findings:
        if not isinstance(item, dict):
            continue
        if _severity_bucket(item) == "violation":
            violations += 1
        else:
            warnings += 1
    return violations, warnings


def _scorecard_top_counts(counts: dict[str, int], limit: int) -> list[str]:
    return [name for name, _count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def _scorecard_risk_tier(attribution: PRAttribution | None) -> str:
    tier = str(attribution.risk_tier or "").lower() if attribution else ""
    if tier in {"green", "yellow", "red"}:
        return tier
    risk_score = int(attribution.risk_score or 0) if attribution else 0
    if risk_score >= 70:
        return "red"
    if risk_score >= 40:
        return "yellow"
    return "green"


def _scorecard_skill_name(item: object) -> str | None:
    if isinstance(item, str):
        value = item.strip()
        return value or None
    if isinstance(item, dict):
        for key in ("skill_name", "name", "title", "skill_id", "domain"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _dt_naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=None) if value.tzinfo else value


def _json_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _pr_card(pr: PullRequest, repo: Repo, attribution: PRAttribution | None) -> dict[str, object]:
    violation_count, warning_count = _finding_counts(attribution)
    sessions = attribution.sessions if attribution and isinstance(attribution.sessions, list) else []
    return {
        "pr_id": pr.id,
        "repo_id": repo.id,
        "repo_name": repo.name,
        "github_pr_number": pr.github_pr_number,
        "title": pr.title or f"PR #{pr.github_pr_number}",
        "url": _pr_html_url(pr, repo),
        "author_login": pr.author_login,
        "primary_agent": attribution.primary_agent if attribution else "human",
        "confidence": attribution.confidence if attribution else 1.0,
        "lines_by_agent": attribution.lines_by_agent if attribution else {"human": int((pr.additions or 0) + (pr.deletions or 0))},
        "additions": pr.additions or 0,
        "deletions": pr.deletions or 0,
        "changed_files": pr.changed_files or 0,
        "skills_loaded": attribution.skills_loaded if attribution and isinstance(attribution.skills_loaded, list) else [],
        "violation_count": violation_count,
        "warning_count": warning_count,
        "risk_score": attribution.risk_score if attribution else 0,
        "risk_tier": attribution.risk_tier if attribution else "green",
        "ci_status": _ci_status(pr),
        "opened_at": pr.opened_at.isoformat() if pr.opened_at else None,
        "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
        "session_ids": sessions,
    }


def _list_or_empty(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _finding_counts_from_items(items: object) -> tuple[int, int]:
    violations = 0
    warnings = 0
    for item in _list_or_empty(items):
        if not isinstance(item, dict):
            continue
        severity = str(item.get("severity") or "warning").lower()
        if severity in {"critical", "error", "fatal", "failure"}:
            violations += 1
        else:
            warnings += 1
    return violations, warnings


def _dismissal_response(dismissal: FlagDismissal) -> FlagDismissalResponse:
    return FlagDismissalResponse(
        id=str(dismissal.id),
        org_id=str(dismissal.org_id),
        flag_type=str(dismissal.flag_type),
        repo_id=str(dismissal.repo_id),
        skill_id=str(dismissal.skill_id) if dismissal.skill_id else None,
        dismissed_by=str(dismissal.dismissed_by),
        reason=str(dismissal.reason),
        dismissed_at=dismissal.dismissed_at,
    )


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


def _week_start(value: datetime) -> datetime:
    return (value - timedelta(days=value.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


def _memory_stub_response(stub: SkillMemoryStub, repo_name: str, session_created_at: datetime, existing_skill_content: str | None) -> MemoryStubResponse:
    return MemoryStubResponse(
        id=stub.id,
        repo_id=stub.repo_id,
        repo_name=repo_name,
        domain=stub.domain,
        skill_id=stub.skill_id,
        discovery_type=stub.discovery_type,
        title=stub.title,
        proposed_content=stub.proposed_content,
        evidence=stub.evidence,
        confidence=float(stub.confidence or 0),
        agent_runtime=stub.agent_runtime,
        engineer_login=stub.engineer_login,
        task_description=stub.task_description,
        status=stub.status,
        reviewer_note=stub.reviewer_note,
        merged_version_number=stub.merged_version_number,
        created_at=stub.created_at,
        reviewed_at=stub.reviewed_at,
        session_created_at=session_created_at,
        existing_skill_content=existing_skill_content,
    )


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


def _source_display_name(source_type: str) -> str:
    """Return a stable dashboard label for a skill source type."""
    return SOURCE_TYPE_DISPLAY_NAMES.get(source_type, source_type.replace("_", " ").title())


def _source_generate_command(source_type: str, has_repos: bool) -> str | None:
    """Return the suggested CLI command only when there is a repo to run it against."""
    if not has_repos:
        return None
    return SOURCE_REFRESH_COMMANDS.get(source_type, f"skilgen analyze --source {source_type}")


def _source_params_hint(params: dict[str, Any]) -> dict[str, object]:
    """Return non-secret connection metadata safe to persist and display."""
    secret_words = ("token", "secret", "password", "key", "credential", "private")
    hints: dict[str, object] = {}
    for key, value in params.items():
        lowered = key.lower()
        if any(word in lowered for word in secret_words):
            if isinstance(value, str) and value:
                hints[f"{key}_hint"] = key_hint(value)
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            hints[key] = value
    return hints


def _encrypted_source_params(params: dict[str, Any]) -> str:
    """Encrypt params JSON with the shared key helper used for stored LLM secrets."""
    return encrypt_key(json.dumps(params, sort_keys=True))


def _decrypted_source_params(connection: SourceConnectionModel) -> dict[str, Any]:
    try:
        payload = decrypt_key(connection.encrypted_params)
        decoded = json.loads(payload)
        return decoded if isinstance(decoded, dict) else {}
    except Exception:
        return {}


def _http_probe(url: str, timeout_seconds: float) -> tuple[bool, str, dict[str, object]]:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "skilgen-source-test/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status_code = int(getattr(response, "status", 200) or 200)
            ok = 200 <= status_code < 500
            return ok, f"HTTP endpoint responded with {status_code}.", {"status_code": status_code}
    except urllib.error.HTTPError as exc:
        status_code = int(exc.code)
        return status_code < 500, f"HTTP endpoint responded with {status_code}.", {"status_code": status_code}


async def _probe_source_connection(source_type: str, params: dict[str, Any], timeout_seconds: float) -> SourceTestResponse:
    tested_at = datetime.utcnow()
    if params.get("mock_success") is True:
        return SourceTestResponse(source_type=source_type, success=True, status="connected", message="Mock source connection succeeded.", details={"mocked": True}, tested_at=tested_at)
    if params.get("mock_failure") is True:
        return SourceTestResponse(source_type=source_type, success=False, status="failed", message="Mock source connection failed.", details={"mocked": True}, tested_at=tested_at)

    url = str(params.get("url") or params.get("base_url") or params.get("endpoint") or "").strip()
    try:
        if url.startswith(("http://", "https://")):
            success, message, details = await asyncio.wait_for(
                asyncio.to_thread(_http_probe, url, timeout_seconds),
                timeout=timeout_seconds + 0.5,
            )
            return SourceTestResponse(source_type=source_type, success=success, status="connected" if success else "failed", message=message, details=details, tested_at=tested_at)

        host = str(params.get("host") or "").strip()
        port = params.get("port")
        if host and port:
            sock = await asyncio.wait_for(
                asyncio.to_thread(socket.create_connection, (host, int(port)), timeout_seconds),
                timeout=timeout_seconds + 0.5,
            )
            sock.close()
            return SourceTestResponse(source_type=source_type, success=True, status="connected", message=f"TCP connection to {host}:{port} succeeded.", details={"host": host, "port": int(port)}, tested_at=tested_at)

        if source_type in {"github", "confluence", "notion", "pagerduty"} and any(params.get(key) for key in ("token", "api_key", "access_token")):
            return SourceTestResponse(source_type=source_type, success=True, status="configured", message="Credentials are present; live driver is not required for this source test.", details={"driver_required": False}, tested_at=tested_at)

        return SourceTestResponse(source_type=source_type, success=True, status="configured", message="Connection parameters were accepted without requiring optional source drivers.", details={"driver_required": False}, tested_at=tested_at)
    except Exception as exc:
        return SourceTestResponse(source_type=source_type, success=False, status="failed", message=str(exc), details={"error_type": exc.__class__.__name__}, tested_at=tested_at)


def _source_connection(source_type: str, source_skills: list[Skill], has_repos: bool, repo_id: str | None = None, connection: SourceConnectionModel | None = None) -> SourceConnection:
    """Normalize source coverage into the org source connection contract."""
    generated_dates = [skill.created_at for skill in source_skills if isinstance(skill.created_at, datetime)]
    last_generated_at = max(generated_dates).isoformat() if generated_dates else None
    connection_status = str(connection.status) if connection is not None else None
    db_connected = connection_status in {"connected", "configured"}
    return SourceConnection(
        id=connection.id if connection is not None else f"source-{source_type}",
        source_type=source_type,
        display_name=(connection.display_name or _source_display_name(source_type)) if connection is not None else _source_display_name(source_type),
        repo_id=repo_id,
        connected=db_connected or bool(source_skills),
        skill_count=len(source_skills),
        last_skill_generated_at=last_generated_at,
        can_generate_skills=has_repos,
        generate_command=_source_generate_command(source_type, has_repos),
        coverage_domains=sorted({str(skill.domain) for skill in source_skills if getattr(skill, "domain", None)}),
        connection_id=connection.id if connection is not None else None,
        connection_status=connection_status,
        last_tested_at=connection.last_tested_at if connection is not None else None,
        last_connected_at=connection.last_connected_at if connection is not None else None,
        last_error=connection.last_error if connection is not None else None,
    )


def _insight(
    insight_type: Literal["anomaly", "opportunity", "trend", "gap"],
    title: str,
    description: str,
    severity: Literal["high", "medium", "low"],
    cta_label: str | None = None,
    cta_url: str | None = None,
) -> InsightItem:
    return InsightItem(
        type=insight_type,
        title=title,
        description=description,
        severity=severity,
        cta_label=cta_label,
        cta_url=cta_url,
    )


def _generate_org_api_key() -> str:
    """Return a new Skillayer org API key."""
    return f"sk-{secrets.token_urlsafe(32)}"


def _org_settings_response(org: Org, installation_id: int | None, recent_runs: list[AnalysisRun]) -> OrgSettingsResponse:
    """Convert an org and its GitHub state into a settings response."""
    settings_payload = org.settings if isinstance(org.settings, dict) else {}
    return OrgSettingsResponse(
        id=org.id,
        login=org.login,
        name=org.name,
        plan=org.plan,
        score_threshold=int(org.score_threshold or 60),
        slack_webhook_url=org.slack_webhook_url,
        slack_standup_enabled=bool(org.slack_standup_enabled),
        slack_standup_hour=int(org.slack_standup_hour or 9),
        notify_on_pr=bool(org.notify_on_pr),
        notify_on_stale=bool(org.notify_on_stale),
        anthropic_api_key_set=bool(settings_payload.get("anthropic_api_key_encrypted")),
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


@router.get("/{org_id}/setup-status", response_model=SetupStatusResponse)
async def get_org_setup_status(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SetupStatusResponse:
    """Return onboarding setup progress for the product loop."""
    _assert_org_scope(org_id, current_org_id)
    repo_count = int(
        (
            await db.execute(select(func.count(Repo.id)).where(Repo.org_id == org_id, Repo.is_active.is_(True)))
        ).scalar()
        or 0
    )
    skill_count = int(
        (
            await db.execute(
                select(func.count(Skill.id)).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == org_id, Repo.is_active.is_(True))
            )
        ).scalar()
        or 0
    )
    high_score_count = int(
        (
            await db.execute(
                select(func.count(Skill.id)).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == org_id, Repo.is_active.is_(True), Skill.score_total >= 70)
            )
        ).scalar()
        or 0
    )
    cutoff = _utc_now_naive() - timedelta(days=30)
    load_count = int(
        (
            await db.execute(select(func.count(SkillUsageEvent.id)).where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff))
        ).scalar()
        or 0
    )

    has_repos = repo_count > 0
    has_skills = skill_count > 0
    has_agent_loads = load_count > 0
    has_high_score_skills = high_score_count > 0

    steps = [
        SetupStatusStep(
            id="connect_repo",
            title="Connect a repository",
            done=has_repos,
            action_url="/dashboard/repos",
        ),
        SetupStatusStep(
            id="generate_skills",
            title="Generate your first skills",
            done=has_skills,
            action_url="/dashboard/repos",
            description="Open Repos and run Analyse now from the dashboard",
        ),
        SetupStatusStep(
            id="connect_agent",
            title="Connect your AI agent",
            done=has_agent_loads,
            action_url="/dashboard/connect",
            description="Configure Claude Code, Cursor, or Codex to load your skills",
        ),
        SetupStatusStep(
            id="improve_skills",
            title="Improve skill quality to 70+",
            done=has_high_score_skills,
            description="Use the improvement plan to boost your lowest-scoring skills",
        ),
    ]
    completed = sum(1 for step in steps if step.done)
    return SetupStatusResponse(
        has_repos=has_repos,
        has_skills=has_skills,
        has_agent_loads=has_agent_loads,
        has_high_score_skills=has_high_score_skills,
        setup_steps=steps,
        completion_percent=completed * 25,
    )


@router.get("/{org_id}/connect/status", response_model=ConnectStatusResponse)
async def get_org_connect_status(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> ConnectStatusResponse:
    """Return connection status for GitHub, generated skills, and agent runtimes."""
    _assert_org_scope(org_id, current_org_id)
    try:
        repos = (
            await db.execute(
                select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)).order_by(Repo.name)
            )
        ).scalars().all()
        repo_ids = [repo.id for repo in repos]
        skill_count = int(
            (
                await db.execute(
                    select(func.count(Skill.id)).where(Skill.repo_id.in_(repo_ids))
                    if repo_ids
                    else select(func.count(Skill.id)).where(False)
                )
            ).scalar()
            or 0
        )
        runtime_status = await get_agent_connection_status(org_id, db)
    except Exception as exc:
        await _rollback(db, "connect status lookup")
        raise HTTPException(status_code=400, detail="Unable to load connection status") from exc

    github_connected = any(repo.github_installation_id for repo in repos)
    has_agent_loads = any(bool(item.get("connected")) or int(item.get("load_count_30d") or 0) > 0 for item in runtime_status.values())
    next_step = None
    if not repos:
        next_step = "Connect a GitHub repository"
    elif skill_count == 0:
        next_step = "Generate skills for connected repositories"
    elif not has_agent_loads:
        next_step = "Connect an AI coding agent"
    return ConnectStatusResponse(
        org_id=org_id,
        repos_connected=len(repos),
        skills_generated=skill_count,
        github_app_installed=github_connected,
        agent_runtimes={key: ConnectRuntimeStatus(**value) for key, value in runtime_status.items()},
        next_step=next_step,
    )


@router.get("/{org_id}/api-key", response_model=OrgApiKeyResponse)
async def get_org_api_key(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgApiKeyResponse | JSONResponse:
    """Return the org API key used by local agents."""
    _assert_org_scope(org_id, current_org_id)
    try:
        result = await db.execute(select(Org).where(Org.id == org_id))
        org = result.scalar_one_or_none()
        if org is None:
            return _error(404, "Org not found", "ORG_NOT_FOUND")
        if not org.api_key:
            org.api_key = _generate_org_api_key()
            await db.flush()
            await db.commit()
        return OrgApiKeyResponse(api_key=org.api_key)
    except SQLAlchemyError:
        await _rollback(db, "org api key lookup")
        return _error(400, "Could not load org API key", "ORG_API_KEY_LOOKUP_FAILED")


@router.post("/{org_id}/api-key/rotate", response_model=OrgApiKeyResponse)
async def rotate_org_api_key(
    org_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgApiKeyResponse | JSONResponse:
    """Rotate the org API key used by local agents."""
    _assert_org_scope(org_id, current_org_id)
    try:
        result = await db.execute(select(Org).where(Org.id == org_id))
        org = result.scalar_one_or_none()
        if org is None:
            return _error(404, "Org not found", "ORG_NOT_FOUND")
        org.api_key = _generate_org_api_key()
        await db.flush()
        await audit.emit(
            db,
            org_id,
            "api_key_rotated",
            "rotated",
            "Rotated org API key",
            actor_login=get_actor_login(request),
            resource_type="org",
            resource_id=org_id,
        )
        await db.commit()
        return OrgApiKeyResponse(api_key=org.api_key)
    except SQLAlchemyError:
        await _rollback(db, "org api key rotation")
        return _error(400, "Could not rotate org API key", "ORG_API_KEY_ROTATE_FAILED")


@router.get("/{org_id}/action-items", response_model=OrgActionItemsResponse)
async def get_org_action_items(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgActionItemsResponse:
    """Return prioritized setup and skill-health actions for an org."""
    _assert_org_scope(org_id, current_org_id)
    repos = (
        await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)).order_by(Repo.full_name))
    ).scalars().all()
    repo_ids = [repo.id for repo in repos]
    skills = (
        await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)).order_by(Skill.repo_id, Skill.domain))
    ).scalars().all() if repo_ids else []
    items: list[OrgActionItemResponse] = []
    if not repos:
        items.append(
            OrgActionItemResponse(
                id="connect-repo",
                type="generate",
                title="Connect a repository",
                description="Connect at least one repository so Skillayer can generate skills.",
                action_url="/dashboard/repos",
                priority="urgent",
            )
        )
        return OrgActionItemsResponse(items=items)

    repo_by_id = {repo.id: repo for repo in repos}
    cutoff = _utc_now_naive() - timedelta(days=30)
    load_rows = (
        await db.execute(
            select(SkillUsageEvent.skill_id, func.count(SkillUsageEvent.id).label("loads"), func.max(SkillUsageEvent.loaded_at).label("last_loaded_at"))
            .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff)
            .group_by(SkillUsageEvent.skill_id)
        )
    ).all()
    loads_by_skill = {str(row.skill_id): int(row.loads or 0) for row in load_rows}
    loaded_low_scores = [skill for skill in skills if loads_by_skill.get(skill.id, 0) > 0]
    if loaded_low_scores:
        skill = sorted(loaded_low_scores, key=lambda item: (int(item.score_total or 0), -loads_by_skill.get(item.id, 0)))[0]
        repo = repo_by_id.get(skill.repo_id)
        items.append(
            OrgActionItemResponse(
                id=f"improve-{skill.id}",
                type="improve",
                title=f"Improve {skill.domain} in {repo.name if repo else 'repo'}",
                description=f"Agents are loading it but it only scores {int(skill.score_total or 0)}/100.",
                action_url=f"/dashboard/repos/{skill.repo_id}/skills/{skill.id}",
                priority="urgent" if int(skill.score_total or 0) < 40 else "recommended",
            )
        )

    categories_by_repo: dict[str, set[str]] = {repo.id: set() for repo in repos}
    for skill in skills:
        categories_by_repo.setdefault(skill.repo_id, set()).add(_skill_category(skill))
    missing_counts: dict[str, int] = {}
    for category in SKILL_CATEGORIES:
        missing_counts[category] = sum(1 for repo in repos if category not in categories_by_repo.get(repo.id, set()))
    missing_category, missing_count = max(missing_counts.items(), key=lambda item: item[1]) if missing_counts else ("codebase_architecture", 0)
    if missing_count > 0:
        label = missing_category.replace("_", " ")
        items.append(
            OrgActionItemResponse(
                id=f"generate-{missing_category}",
                type="generate",
                title=f"Generate {label} skills",
                description=f"Missing from {missing_count} repos.",
                action_url=f"/dashboard/debt?tab=gaps&domain={missing_category}",
                priority="recommended",
            )
        )

    decay_rows = (
        await db.execute(
            select(SkillHalfLife, Skill, Repo)
            .join(Skill, Skill.id == SkillHalfLife.skill_id)
            .join(Repo, Repo.id == SkillHalfLife.repo_id)
            .where(SkillHalfLife.org_id == org_id, SkillHalfLife.predicted_decay_date.is_not(None))
            .order_by(SkillHalfLife.predicted_decay_date)
        )
    ).all()
    threshold = _utc_now_naive() + timedelta(days=3)
    for half_life, skill, repo in decay_rows:
        if half_life.predicted_decay_date and half_life.predicted_decay_date <= threshold:
            items.append(
                OrgActionItemResponse(
                    id=f"refresh-{skill.id}",
                    type="refresh",
                    title=f"Regenerate {skill.domain} before it goes stale",
                    description=f"{repo.name} is predicted to decay within 3 days.",
                    action_url=f"/dashboard/repos/{skill.repo_id}/skills/{skill.id}",
                    priority="urgent",
                )
            )
            break

    if not items:
        low_score_count = sum(1 for skill in skills if int(skill.score_total or 0) < 40)
        if low_score_count > 0:
            items.append(
                OrgActionItemResponse(
                    id="review-low-score",
                    type="review",
                    title=f"Review {low_score_count} skills with score under 40",
                    description="Start with the lowest scoring skills and use their improvement plans.",
                    action_url="/dashboard/skills",
                    priority="recommended",
                )
            )
        else:
            items.append(
                OrgActionItemResponse(
                    id="review-healthy-skills",
                    type="review",
                    title="Review your healthiest skills",
                    description="No urgent score or decay risks found. Spot-check your strongest skills for drift.",
                    action_url="/dashboard/skills",
                    priority="suggested",
                )
            )

    priority_order = {"urgent": 0, "recommended": 1, "suggested": 2}
    items.sort(key=lambda item: priority_order[item.priority])
    return OrgActionItemsResponse(items=items[:3])


@router.get("/{org_id}/sources", response_model=list[SourceConnection])
async def get_org_sources(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[SourceConnection]:
    """Return org-level source connections from generated skills plus common disconnected source types."""
    _assert_org_scope(org_id, current_org_id)
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
        skills = (
            await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))
        ).scalars().all() if repo_ids else []
        connections = (
            await db.execute(select(SourceConnectionModel).where(SourceConnectionModel.org_id == org_id))
        ).scalars().all()
    except HTTPException:
        raise
    except Exception as exc:
        await _rollback(db, "org sources lookup")
        raise HTTPException(status_code=400, detail="Unable to load org sources") from exc

    skills_by_source: dict[str, list[Skill]] = {}
    for skill in skills:
        source_type = str(skill.source_type or "code")
        skills_by_source.setdefault(source_type, []).append(skill)

    connections_by_source = {str(connection.source_type): connection for connection in connections}
    source_types = [source_type for source_type in COMMON_SOURCE_TYPES]
    for source_type in sorted(skills_by_source):
        if source_type not in source_types:
            source_types.append(source_type)
    for source_type in sorted(connections_by_source):
        if source_type not in source_types:
            source_types.append(source_type)

    return [
        _source_connection(
            source_type,
            skills_by_source.get(source_type, []),
            bool(repo_ids),
            repo_ids[0] if repo_ids else None,
            connections_by_source.get(source_type),
        )
        for source_type in source_types
    ]


@router.post("/{org_id}/sources/test", response_model=SourceTestResponse)
async def test_org_source(
    org_id: str,
    payload: SourceConnectionRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SourceTestResponse:
    """Test source connection params without requiring optional source drivers."""
    _assert_org_scope(org_id, current_org_id)
    source_type = payload.source_type.strip()
    try:
        org = await db.get(Org, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Org not found")
        return await _probe_source_connection(source_type, payload.params, payload.timeout_seconds)
    except HTTPException:
        raise
    except Exception as exc:
        await _rollback(db, "org source test")
        return SourceTestResponse(
            source_type=source_type,
            success=False,
            status="failed",
            message=str(exc),
            details={"error_type": exc.__class__.__name__},
            tested_at=datetime.utcnow(),
        )


@router.post("/{org_id}/sources/connect", response_model=SourceConnectResponse)
async def connect_org_source(
    org_id: str,
    payload: SourceConnectionRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SourceConnectResponse:
    """Persist an org source connection after a safe connection test."""
    _assert_org_scope(org_id, current_org_id)
    source_type = payload.source_type.strip()
    try:
        org = await db.get(Org, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Org not found")

        existing = (
            await db.execute(
                select(SourceConnectionModel).where(
                    SourceConnectionModel.org_id == org_id,
                    SourceConnectionModel.source_type == source_type,
                )
            )
        ).scalar_one_or_none()
        params = payload.params or (_decrypted_source_params(existing) if existing is not None else {})
        test_result = await _probe_source_connection(source_type, params, payload.timeout_seconds)

        now = datetime.utcnow()
        connection = existing or SourceConnectionModel(org_id=org_id, source_type=source_type, created_at=now)
        connection.display_name = payload.display_name or _source_display_name(source_type)
        connection.status = test_result.status
        connection.encrypted_params = _encrypted_source_params(params)
        connection.params_hint = _source_params_hint(params)
        connection.last_tested_at = test_result.tested_at
        connection.last_connected_at = now if test_result.success else connection.last_connected_at
        connection.last_error = None if test_result.success else test_result.message
        connection.updated_at = now
        db.add(connection)
        await db.flush()
        await db.commit()

        return SourceConnectResponse(
            id=connection.id,
            source_type=source_type,
            display_name=connection.display_name or _source_display_name(source_type),
            connected=test_result.success,
            status=connection.status,
            message=test_result.message,
            last_tested_at=connection.last_tested_at,
        )
    except HTTPException:
        await _rollback(db, "org source connect")
        raise
    except Exception as exc:
        await _rollback(db, "org source connect")
        raise HTTPException(status_code=400, detail="Could not connect source") from exc


@router.post("/{org_id}/sources/refresh")
async def refresh_org_source(
    org_id: str,
    payload: SourceRefreshRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    """Queue a source-specific analysis run for a repo in the org."""
    _assert_org_scope(org_id, current_org_id)
    source_type = payload.source_type.strip()
    if source_type not in COMMON_SOURCE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported source type")
    try:
        repo = await db.get(Repo, payload.repo_id)
        if repo is None:
            raise HTTPException(status_code=404, detail="Repo not found")
        if repo.org_id != org_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        run = AnalysisRun(
            repo_id=repo.id,
            trigger=f"source:{source_type}",
            status="queued",
            branch=repo.default_branch,
            created_at=datetime.utcnow(),
        )
        db.add(run)
        await db.flush()
        await db.commit()
        return {
            "queued": True,
            "message": f"Refresh queued for {repo.name} {source_type} source.",
        }
    except HTTPException:
        raise
    except Exception as exc:
        await _rollback(db, "org source refresh")
        raise HTTPException(status_code=400, detail="Could not queue source refresh") from exc


def _enterprise_skill_response(skill: Skill, repo: Repo) -> EnterpriseSkillResponse:
    return EnterpriseSkillResponse(
        id=skill.id,
        repo_id=repo.id,
        repo_name=repo.name,
        domain=skill.domain,
        skill_path=skill.skill_path,
        source_type=skill.source_type,
        skill_category=skill.skill_category,
        score_total=int(skill.score_total or 0),
        is_enterprise=bool(getattr(skill, "is_enterprise", False)),
        last_updated_at=skill.last_loaded_at or skill.created_at,
    )


@router.get("/{org_id}/enterprise-skills", response_model=list[EnterpriseSkillResponse])
async def get_enterprise_skills(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[EnterpriseSkillResponse]:
    """Return org skills promoted for enterprise reuse."""
    _assert_org_scope(org_id, current_org_id)
    try:
        org = await db.get(Org, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Org not found")
        rows = (
            await db.execute(
                select(Skill, Repo)
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Repo.org_id == org_id, Skill.is_enterprise.is_(True))
                .order_by(desc(Skill.created_at), Skill.domain)
            )
        ).all()
        return [_enterprise_skill_response(skill, repo) for skill, repo in rows]
    except HTTPException:
        raise
    except Exception as exc:
        await _rollback(db, "enterprise skills lookup")
        raise HTTPException(status_code=400, detail="Unable to load enterprise skills") from exc


@router.post("/{org_id}/enterprise-skills", response_model=list[EnterpriseSkillResponse])
async def save_enterprise_skills(
    org_id: str,
    payload: EnterpriseSkillRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[EnterpriseSkillResponse]:
    """Mark one or more org skills as enterprise reusable guidance."""
    _assert_org_scope(org_id, current_org_id)
    skill_ids = [skill_id for skill_id in ([payload.skill_id] if payload.skill_id else []) + payload.skill_ids if skill_id]
    try:
        org = await db.get(Org, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Org not found")
        if not skill_ids and payload.content and payload.domain:
            repo_filter = [Repo.org_id == org_id, Repo.is_active.is_(True)]
            if isinstance(payload.applies_to, list):
                repo_filter.append(Repo.id.in_(payload.applies_to))
            repos = (await db.execute(select(Repo).where(*repo_filter).order_by(Repo.name))).scalars().all()
            if not repos:
                raise HTTPException(status_code=404, detail="No repos found for enterprise skill")
            responses: list[EnterpriseSkillResponse] = []
            now = datetime.utcnow()
            for repo in repos:
                run = AnalysisRun(repo_id=repo.id, trigger="enterprise_skill", status="complete", branch=repo.default_branch, created_at=now, completed_at=now)
                db.add(run)
                await db.flush()
                skill = Skill(
                    repo_id=repo.id,
                    run_id=run.id,
                    domain=payload.domain,
                    skill_path=f".skillayer/enterprise/{payload.domain}.md",
                    content=payload.content,
                    content_hash=hashlib.sha256(payload.content.encode()).hexdigest(),
                    source_type="enterprise",
                    skill_category=payload.domain if payload.domain in SKILL_CATEGORIES else "operational_knowledge",
                    score_total=80,
                    score_groundedness=20,
                    score_coverage=20,
                    score_freshness=20,
                    score_structure=20,
                    is_enterprise=True,
                    created_at=now,
                )
                db.add(skill)
                await db.flush()
                responses.append(_enterprise_skill_response(skill, repo))
            await db.commit()
            return responses
        if not skill_ids:
            raise HTTPException(status_code=422, detail="At least one skill_id or content/domain is required")
        rows = (
            await db.execute(
                select(Skill, Repo)
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Repo.org_id == org_id, Skill.id.in_(skill_ids))
                .order_by(Skill.domain)
            )
        ).all()
        found_ids = {skill.id for skill, _repo in rows}
        missing_ids = [skill_id for skill_id in skill_ids if skill_id not in found_ids]
        if missing_ids:
            raise HTTPException(status_code=404, detail=f"Skills not found in org: {', '.join(missing_ids)}")
        responses: list[EnterpriseSkillResponse] = []
        for skill, repo in rows:
            skill.is_enterprise = payload.is_enterprise
            responses.append(_enterprise_skill_response(skill, repo))
        await db.commit()
        return responses
    except HTTPException:
        await _rollback(db, "enterprise skills update")
        raise
    except Exception as exc:
        await _rollback(db, "enterprise skills update")
        raise HTTPException(status_code=400, detail="Unable to update enterprise skills") from exc


@router.post("/{org_id}/skills/{skill_id}/push", response_model=SkillPushResponse)
async def push_skill_to_repo(
    org_id: str,
    skill_id: str,
    payload: SkillPushPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SkillPushResponse:
    """Open or update a GitHub PR that pushes skill content back into the repo."""
    _assert_org_scope(org_id, current_org_id)
    if payload.skill_id and payload.skill_id != skill_id:
        raise HTTPException(status_code=422, detail="Payload skill_id does not match path skill_id")
    try:
        row = (
            await db.execute(
                select(Skill, Repo, Org)
                .join(Repo, Repo.id == Skill.repo_id)
                .join(Org, Org.id == Repo.org_id)
                .where(Skill.id == skill_id, Repo.org_id == org_id, Repo.is_active.is_(True))
            )
        ).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Skill not found")
        skill, repo, org = row
        content = payload.content or skill.content
        if not content and payload.generate_if_missing:
            generated = await generate_skill_with_ai(
                _org_settings_dict(org),
                domain=skill.domain,
                repo_name=repo.name,
                context_files=[skill.skill_path],
                enterprise_skills=[],
                user_intent=f"Regenerate {skill.domain} skill for repository push.",
            )
            content = str(generated.get("content") or "")
        if not content:
            raise HTTPException(status_code=422, detail="Skill has no content to push")
        safe_domain = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in skill.domain.lower()).strip("-") or "skill"
        branch_name = payload.branch_name or f"skillayer/push-{safe_domain}"
        pr_title = payload.pr_title or f"Update Skillayer skill: {skill.domain}"
        pr_body = payload.pr_body or (
            "This PR was opened by Skillayer to push the latest skill guidance back into the repository.\n\n"
            f"- Skill: `{skill.domain}`\n"
            f"- Path: `{skill.skill_path}`\n"
            f"- Generated at: `{datetime.utcnow().isoformat()}Z`"
        )
    except HTTPException:
        await _rollback(db, "skill push lookup")
        raise
    except Exception as exc:
        await _rollback(db, "skill push lookup")
        raise HTTPException(status_code=400, detail="Unable to prepare skill push") from exc

    try:
        pr = await create_skill_pr(
            repo=repo,
            skill_path=skill.skill_path,
            skill_content=content,
            branch_name=branch_name,
            pr_title=pr_title,
            pr_body=pr_body,
        )
        await audit.emit(
            db,
            org_id,
            "skill.push_pr_opened",
            "pushed",
            f"Opened skill push PR for {skill.domain}",
            actor_login=get_actor_login(request),
            repo_id=repo.id,
            repo_name=repo.name,
            skill_id=skill.id,
            skill_domain=skill.domain,
            resource_type="skill",
            resource_id=skill.id,
            metadata={"pr_url": pr.get("pr_url"), "branch": pr.get("branch")},
        )
        await db.commit()
        return SkillPushResponse(
            pushed=True,
            repo_id=repo.id,
            skill_id=skill.id,
            pr_url=str(pr["pr_url"]),
            pr_number=int(pr["pr_number"]),
            branch=str(pr["branch"]),
        )
    except Exception as exc:
        await _rollback(db, "skill push audit")
        raise HTTPException(status_code=400, detail="Unable to push skill to repository") from exc


@router.get("/{org_id}/intelligence/insights", response_model=list[InsightItem])
async def get_org_intelligence_insights(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[InsightItem]:
    """Return heuristic org insights for gaps, anomalies, opportunities, and trends."""
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
        skills = (
            await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))
        ).scalars().all() if repo_ids else []
        usage_rows = (
            await db.execute(
                select(
                    SkillUsageEvent.skill_id,
                    func.count(SkillUsageEvent.id).label("loads_30d"),
                )
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff_30)
                .group_by(SkillUsageEvent.skill_id)
            )
        ).all()
        history_rows = (
            await db.execute(
                select(ScoreHistory.repo_id, ScoreHistory.score_total, ScoreHistory.recorded_at)
                .where(ScoreHistory.repo_id.in_(repo_ids), ScoreHistory.recorded_at >= cutoff_30)
                .order_by(ScoreHistory.repo_id, ScoreHistory.recorded_at)
            )
        ).all() if repo_ids else []
    except HTTPException:
        raise
    except Exception as exc:
        await _rollback(db, "org intelligence insights lookup")
        raise HTTPException(status_code=400, detail="Unable to load org intelligence insights") from exc

    if not repos:
        return [
            _insight(
                "gap",
                "Connect your first repository",
                "No active repositories are available, so Skillayer cannot generate organization intelligence yet.",
                "high",
                "Connect repos",
                "/dashboard/repos",
            )
        ]

    usage_by_skill = {str(_row_value(row, "skill_id", "")): int(_row_value(row, "loads_30d", 0) or 0) for row in usage_rows}
    repo_by_id = {repo.id: repo for repo in repos}
    insights: list[InsightItem] = []

    covered_categories = {_skill_category(skill) for skill in skills}
    missing_categories = [category for category in SKILL_CATEGORIES if category not in covered_categories]
    if missing_categories:
        label = missing_categories[0].replace("_", " ")
        insights.append(
            _insight(
                "gap",
                f"{len(missing_categories)} knowledge categories need coverage",
                f"Start with {label}; it is missing from the generated skill set.",
                "high" if len(missing_categories) >= 4 else "medium",
                "View sources",
                "/dashboard/sources",
            )
        )

    stale_active = [
        skill
        for skill in skills
        if bool(skill.is_stale) and (usage_by_skill.get(skill.id, 0) or int(skill.load_count_30d or 0)) > 0
    ]
    if stale_active:
        skill = sorted(stale_active, key=lambda item: -(usage_by_skill.get(item.id, 0) or int(item.load_count_30d or 0)))[0]
        repo = repo_by_id.get(skill.repo_id)
        insights.append(
            _insight(
                "anomaly",
                f"Agents are loading stale {skill.domain} guidance",
                f"{repo.name if repo else 'A repo'} has stale guidance with recent agent usage.",
                "high",
                "Review skill",
                f"/dashboard/repos/{skill.repo_id}/skills/{skill.id}",
            )
        )

    low_scoring_loaded = [
        skill
        for skill in skills
        if int(skill.score_total or 0) < 60 and (usage_by_skill.get(skill.id, 0) or int(skill.load_count_30d or 0)) > 0
    ]
    if low_scoring_loaded:
        skill = sorted(low_scoring_loaded, key=lambda item: (int(item.score_total or 0), -(usage_by_skill.get(item.id, 0) or int(item.load_count_30d or 0))))[0]
        insights.append(
            _insight(
                "opportunity",
                f"Improve a frequently used low-score skill",
                f"{skill.domain} scores {int(skill.score_total or 0)}/100 while still being loaded by agents.",
                "medium",
                "Improve skill",
                f"/dashboard/repos/{skill.repo_id}/skills/{skill.id}",
            )
        )

    dormant_repos = [
        repo
        for repo in repos
        if repo.last_analysed_at is None
        or (repo.last_analysed_at.replace(tzinfo=None) if repo.last_analysed_at.tzinfo else repo.last_analysed_at) < cutoff_30
    ]
    if dormant_repos:
        repo = sorted(dormant_repos, key=lambda item: item.last_analysed_at or datetime.min)[0]
        insights.append(
            _insight(
                "trend",
                f"{repo.name} has not been analysed recently",
                "Refresh dormant repositories so the org intelligence view reflects current code.",
                "medium",
                "Refresh repo",
                f"/dashboard/repos/{repo.id}",
            )
        )

    history_by_repo: dict[str, list[tuple[datetime, int]]] = {}
    for row in history_rows:
        repo_id = str(_row_value(row, "repo_id", ""))
        recorded_at = _row_value(row, "recorded_at")
        if repo_id and isinstance(recorded_at, datetime):
            history_by_repo.setdefault(repo_id, []).append((recorded_at, int(_row_value(row, "score_total", 0) or 0)))
    declining: list[tuple[int, Repo]] = []
    for repo_id, points in history_by_repo.items():
        ordered = sorted(points, key=lambda item: item[0])
        if len(ordered) >= 2:
            delta = ordered[-1][1] - ordered[0][1]
            if delta <= -10 and repo_id in repo_by_id:
                declining.append((delta, repo_by_id[repo_id]))
    if declining:
        delta, repo = sorted(declining, key=lambda item: item[0])[0]
        insights.append(
            _insight(
                "trend",
                f"{repo.name} score dropped {abs(delta)} points",
                "The 30-day score trend is moving down; review recent analysis runs and stale skills.",
                "high",
                "Open repo",
                f"/dashboard/repos/{repo.id}",
            )
        )

    if not insights:
        insights.append(
            _insight(
                "trend",
                "Org intelligence looks stable",
                "No major stale, low-score, or coverage-gap signals were detected across active repositories.",
                "low",
                "Review skills",
                "/dashboard/skills",
            )
        )
    return insights[:6]


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


@router.get("/{org_id}/overview/score-trend")
async def get_overview_score_trend(
    org_id: str,
    weeks: int = Query(default=30, ge=4, le=52),
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> list[dict[str, object]]:
    if current_org_id:
        _assert_org_scope(org_id, current_org_id)
    try:
        repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
        repo_ids = [repo.id for repo in repos]
        now = datetime.utcnow()
        start = now - timedelta(weeks=weeks)
        if not repo_ids:
            return []
        history = (
            await db.execute(
                select(ScoreHistory, Repo.name.label("repo_name"))
                .join(Repo, Repo.id == ScoreHistory.repo_id)
                .where(ScoreHistory.repo_id.in_(repo_ids), ScoreHistory.recorded_at >= start)
                .order_by(ScoreHistory.recorded_at)
            )
        ).all()
        latest_scores = (
            await db.execute(
                select(Skill.repo_id, func.avg(Skill.score_total).label("score"))
                .where(Skill.repo_id.in_(repo_ids))
                .group_by(Skill.repo_id)
            )
        ).all()
        current_by_repo = {str(repo_id): int(score or 0) for repo_id, score in latest_scores}
        if not current_by_repo:
            current_by_repo = {repo.id: 0 for repo in repos}

        points: list[dict[str, object]] = []
        previous_score: int | None = None
        for offset in range(weeks - 1, -1, -1):
            week_end = now - timedelta(weeks=offset)
            week_start = week_end - timedelta(days=7)
            week_label = f"{week_end.isocalendar().year}-W{week_end.isocalendar().week:02d}"
            scores_by_repo: dict[str, int] = {}
            events: list[dict[str, object]] = []
            for row, repo_name in history:
                if row.recorded_at <= week_end:
                    scores_by_repo[row.repo_id] = int(row.score_total or 0)
                if week_start <= row.recorded_at <= week_end:
                    events.append({"repo_id": row.repo_id, "repo_name": repo_name, "score": int(row.score_total or 0), "date": row.recorded_at.isoformat()})
            if not scores_by_repo:
                scores_by_repo = dict(current_by_repo)
            score = int(sum(scores_by_repo.values()) / max(1, len(scores_by_repo)))
            delta = 0 if previous_score is None else score - previous_score
            previous_score = score
            points.append(
                {
                    "week": week_label,
                    "date": week_end.date().isoformat(),
                    "score": score,
                    "delta": delta,
                    "repos_changed": len({str(event["repo_id"]) for event in events}),
                    "events": events[:12],
                }
            )
        if not any(point["events"] for point in points):
            current_score = int(sum(current_by_repo.values()) / max(1, len(current_by_repo)))
            points = [
                {
                    "week": f"{(now - timedelta(weeks=offset)).isocalendar().year}-W{(now - timedelta(weeks=offset)).isocalendar().week:02d}",
                    "date": (now - timedelta(weeks=offset)).date().isoformat(),
                    "score": current_score,
                    "delta": 0,
                    "repos_changed": len(repos),
                    "events": [{"repo_id": repo.id, "repo_name": repo.name, "score": current_score, "date": now.isoformat()} for repo in repos[:5]],
                }
                for offset in range(3, -1, -1)
            ]
        return points
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not load overview score trend") from exc


@router.post("/{org_id}/repos/{repo_id}/analyse")
async def trigger_org_repo_analysis(
    org_id: str,
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    try:
        repo = await db.get(Repo, repo_id)
        if repo is None or repo.org_id != org_id:
            raise HTTPException(status_code=404, detail="Repo not found")
        now = datetime.utcnow()
        avg_skill_score = (
            await db.execute(select(func.avg(Skill.score_total)).where(Skill.repo_id == repo_id))
        ).scalar_one_or_none()
        score = int(avg_skill_score or 0)
        run = AnalysisRun(
            repo_id=repo_id,
            trigger="manual",
            status="queued",
            branch=repo.default_branch,
            score_total=score,
            created_at=now,
            started_at=now,
        )
        repo.last_analysed_at = now
        db.add(run)
        await db.flush()
        await db.commit()
        return {"queued": True, "run_id": run.id, "repo_id": repo_id, "score": score, "last_analysed_at": now.isoformat()}
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not queue analysis") from exc


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


@router.get("/{org_id}/analytics/criticality", response_model=list[CriticalityItem])
async def get_analytics_criticality(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[CriticalityItem]:
    _assert_org_scope(org_id, current_org_id)
    now = datetime.utcnow()
    cutoff_30 = now - timedelta(days=30)
    try:
        rows = (
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
                    func.count(SkillUsageEvent.id).label("loads"),
                    func.count(func.distinct(SkillUsageEvent.session_id)).label("sessions"),
                    func.max(SkillUsageEvent.loaded_at).label("last_loaded_at"),
                )
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff_30)
                .group_by(SkillUsageEvent.skill_id)
            )
        ).all()
        total_sessions = int(
            (
                await db.execute(
                    select(func.count(func.distinct(SkillUsageEvent.session_id))).where(
                        SkillUsageEvent.org_id == org_id,
                        SkillUsageEvent.loaded_at >= cutoff_30,
                    )
                )
            ).scalar_one()
            or 0
        )
    except Exception as exc:
        await _rollback(db, "analytics criticality")
        raise HTTPException(status_code=400, detail="Unable to load skill criticality") from exc

    usage = {
        str(row.skill_id): {
            "loads": int(row.loads or 0),
            "sessions": int(row.sessions or 0),
            "last_loaded_at": row.last_loaded_at,
        }
        for row in usage_rows
    }
    ranked = sorted(rows, key=lambda row: (-(usage.get(row[0].id, {}).get("loads", 0)), str(row[0].domain)))
    rank_by_skill = {skill.id: index + 1 for index, (skill, _repo_name) in enumerate(ranked)}
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    items: list[CriticalityItem] = []
    for skill, repo_name in rows:
        skill_usage = usage.get(skill.id, {"loads": int(skill.load_count_30d or 0), "sessions": 0, "last_loaded_at": skill.last_loaded_at})
        loads = int(skill_usage.get("loads", 0) or 0)
        session_count = int(skill_usage.get("sessions", 0) or 0)
        is_every_session = total_sessions > 0 and session_count > total_sessions * 0.8
        risk_level, risk_reason = _criticality_risk(skill, loads, is_every_session, now)
        last_loaded = skill_usage.get("last_loaded_at") or skill.last_loaded_at
        items.append(
            CriticalityItem(
                skill_id=skill.id,
                domain=skill.domain,
                repo_id=skill.repo_id,
                repo_name=str(repo_name),
                load_count_30d=loads,
                score_total=int(skill.score_total or 0),
                risk_level=risk_level,
                risk_reason=risk_reason,
                dependency_rank=rank_by_skill.get(skill.id, len(rank_by_skill) + 1),
                is_every_session=is_every_session,
                last_loaded_at=last_loaded.isoformat() if isinstance(last_loaded, datetime) else None,
            )
        )
    return sorted(items, key=lambda item: (severity_order[item.risk_level], item.dependency_rank, item.domain))


@router.get("/{org_id}/analytics/skill-coload-tree", response_model=SkillColoadTreeResponse)
async def get_skill_coload_tree(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SkillColoadTreeResponse:
    _assert_org_scope(org_id, current_org_id)
    now = datetime.utcnow()
    cutoff_30 = now - timedelta(days=30)
    try:
        event_rows = (
            await db.execute(
                select(
                    SkillUsageEvent.session_id,
                    SkillUsageEvent.agent_runtime,
                    SkillUsageEvent.skill_id,
                    Skill.domain,
                    Repo.name.label("repo_name"),
                    Skill.score_total,
                    Skill.load_count_30d,
                    Skill.score_freshness,
                    Skill.is_stale,
                )
                .join(Skill, Skill.id == SkillUsageEvent.skill_id)
                .join(Repo, Repo.id == Skill.repo_id)
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff_30)
                .order_by(SkillUsageEvent.agent_runtime, SkillUsageEvent.session_id)
            )
        ).all()
    except Exception as exc:
        await _rollback(db, "analytics coload tree")
        raise HTTPException(status_code=400, detail="Unable to load skill coload tree") from exc

    skill_meta: dict[str, dict[str, object]] = {}
    sessions_by_runtime: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    load_counts_by_runtime: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for session_id, runtime, skill_id, domain, repo_name, score_total, load_count_30d, score_freshness, is_stale in event_rows:
        runtime_key = normalize_runtime(runtime)
        skill_key = str(skill_id)
        sessions_by_runtime[runtime_key][str(session_id)].add(skill_key)
        load_counts_by_runtime[runtime_key][skill_key] += 1
        skill_meta[skill_key] = {
            "domain": str(domain or "unknown"),
            "repo_name": str(repo_name or ""),
            "score": int(score_total or 0),
            "load_count_30d": int(load_count_30d or 0),
            "score_freshness": int(score_freshness or 0),
            "is_stale": bool(is_stale),
        }

    def status_for(meta: dict[str, object], loads: int) -> str:
        if loads <= 0:
            return "never_loaded"
        if bool(meta.get("is_stale")) or int(meta.get("score_freshness") or 0) < 10:
            return "stale"
        score = int(meta.get("score") or 0)
        if score < 75:
            return "low_score"
        return "healthy"

    loaded_counts = [int(loads) for runtime_counts in load_counts_by_runtime.values() for loads in runtime_counts.values()]
    uniform_loads = len(loaded_counts) > 1 and len(set(loaded_counts)) == 1

    def sized_value(loads: int, score: int) -> float:
        if uniform_loads:
            return max(1.0, float(loads or 1) * ((float(score or 0) / 100.0) + 0.1))
        return float(max(1, loads))

    runtime_nodes: list[SkillColoadTreeNode] = []
    for runtime, sessions in sorted(sessions_by_runtime.items(), key=lambda item: _runtime_display_name(item[0])):
        session_count = max(1, len(sessions))
        skill_session_counts: dict[str, int] = defaultdict(int)
        pair_counts: dict[tuple[str, str], int] = defaultdict(int)
        for skill_ids in sessions.values():
            ordered = sorted(skill_ids)
            for skill_id in ordered:
                skill_session_counts[skill_id] += 1
            for left, right in combinations(ordered, 2):
                pair_counts[(left, right)] += 1

        def leaf(skill_id: str) -> SkillColoadTreeNode:
            meta = skill_meta.get(skill_id, {})
            loads = int(load_counts_by_runtime[runtime].get(skill_id, 0))
            score = int(meta.get("score") or 0)
            return SkillColoadTreeNode(
                name=str(meta.get("domain") or "unknown"),
                value=sized_value(loads, score),
                score=score,
                status=status_for(meta, loads),
                skill_id=skill_id,
                runtime=runtime,
                repo_name=str(meta.get("repo_name") or ""),
                loads_30d=loads,
                sessions=int(skill_session_counts.get(skill_id, 0)),
            )

        linked: dict[str, set[str]] = {skill_id: set() for skill_id in skill_session_counts}
        for (left, right), count in pair_counts.items():
            denominator = max(1, min(skill_session_counts[left], skill_session_counts[right]))
            if count / denominator >= 0.70:
                linked[left].add(right)
                linked[right].add(left)

        cluster_ids: list[set[str]] = []
        seen: set[str] = set()
        for skill_id in sorted(skill_session_counts):
            if skill_id in seen:
                continue
            stack = [skill_id]
            component: set[str] = set()
            while stack:
                current = stack.pop()
                if current in component:
                    continue
                component.add(current)
                stack.extend(sorted(linked.get(current, set()) - component))
            seen.update(component)
            cluster_ids.append(component)

        def skill_sort_key(skill_id: str) -> tuple[int, int, str]:
            meta = skill_meta.get(skill_id, {})
            loads = int(load_counts_by_runtime[runtime].get(skill_id, 0))
            return (-loads, -int(meta.get("score") or 0), str(meta.get("domain") or "unknown"))

        clusters: list[SkillColoadTreeNode] = []
        for index, component in enumerate(cluster_ids, start=1):
            ordered_skill_ids = sorted(component, key=skill_sort_key)
            children = [leaf(skill_id) for skill_id in ordered_skill_ids]
            if not children:
                continue
            cluster_status = min(
                (child.status or "healthy" for child in children),
                key=lambda status: {"stale": 0, "low_score": 1, "healthy": 2, "never_loaded": 3}.get(status, 4),
            )
            cluster_value = sum(float(child.value or 0) for child in children)
            cluster_name = "Core cluster" if len(children) > 1 else f"{children[0].name} cluster"
            clusters.append(
                SkillColoadTreeNode(
                    name=cluster_name,
                    value=cluster_value,
                    status=cluster_status,
                    runtime=runtime,
                    cluster_id=f"{runtime}-{index}",
                    always_together=all(
                        pair_counts.get(tuple(sorted((left, right))), 0) / session_count >= 0.70
                        for left, right in combinations(ordered_skill_ids, 2)
                    )
                    if len(ordered_skill_ids) > 1
                    else False,
                    children=children,
                )
            )

        runtime_uniform = len({int(load_counts_by_runtime[runtime].get(skill_id, 0)) for skill_id in skill_session_counts}) == 1
        clusters.sort(
            key=lambda node: (
                -int(sum((child.score or 0) for child in node.children) / max(len(node.children), 1)) if runtime_uniform else -float(node.value or 0),
                str(node.name),
            )
        )

        runtime_nodes.append(
            SkillColoadTreeNode(
                name=_runtime_display_name(runtime),
                display=_runtime_display_name(runtime),
                value=len(sessions),
                runtime=runtime,
                children=clusters,
            )
        )

    root_value = sum(node.value for node in runtime_nodes) or 0
    return SkillColoadTreeResponse(name="All sessions", value=root_value, children=runtime_nodes, uniform_loads=uniform_loads, generated_at=now)


@router.post("/{org_id}/analytics/improvement-suggestions", response_model=AnalyticsSuggestionResponse)
async def get_skill_improvement_suggestions(
    org_id: str,
    payload: AnalyticsSuggestionRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AnalyticsSuggestionResponse | JSONResponse:
    _assert_org_scope(org_id, current_org_id)
    skill = await db.get(Skill, payload.skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    repo = await db.get(Repo, skill.repo_id)
    if repo is None or repo.org_id != org_id:
        raise HTTPException(status_code=404, detail="Skill not found")
    org = await db.get(Org, org_id)
    try:
        response = await call_llm(
            _org_settings_dict(org) if org else {},
            "You are a concise Skillayer analytics advisor. Return exactly 3 short bullet suggestions.",
            f"Skill: {skill.domain}\nRepo: {repo.full_name}\nScore: {skill.score_total}/100\nLoads 30d: {skill.load_count_30d}\nRisk reason: {payload.risk_reason}\nContent excerpt:\n{str(skill.content or '')[:1400]}",
            max_tokens=320,
        )
    except LLMNotConfiguredError as exc:
        return _error(402, str(exc), "llm_not_configured")
    except LLMCallError as exc:
        return _error(502, str(exc), "llm_call_failed")
    suggestions = [line.strip(" -•\t") for line in response.splitlines() if line.strip()]
    suggestions = suggestions[:3] or [response.strip()]
    return AnalyticsSuggestionResponse(skill_id=skill.id, suggestions=suggestions, summary=f"{skill.domain} improvement plan")


@router.get("/{org_id}/analytics/highlight-risks", response_model=AnalyticsRiskHighlightResponse)
async def highlight_analytics_risks(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AnalyticsRiskHighlightResponse | JSONResponse:
    _assert_org_scope(org_id, current_org_id)
    org = await db.get(Org, org_id)
    criticality = await get_analytics_criticality(org_id, db, current_org_id)
    top = [item for item in criticality if item.risk_level in {"critical", "high"}][:8]
    if not top:
        return AnalyticsRiskHighlightResponse(summary="No critical analytics risks detected.", highlights=["Keep collecting agent sessions to improve confidence."])
    try:
        response = await call_llm(
            _org_settings_dict(org) if org else {},
            "You are a concise Skillayer risk analyst. Summarize analytics risk in 1 sentence, then 3 bullets.",
            "\n".join([f"- {item.domain} in {item.repo_name}: {item.risk_level}, {item.load_count_30d} loads, {item.risk_reason}" for item in top]),
            max_tokens=360,
        )
    except LLMNotConfiguredError as exc:
        return _error(402, str(exc), "llm_not_configured")
    except LLMCallError as exc:
        return _error(502, str(exc), "llm_call_failed")
    lines = [line.strip(" -•\t") for line in response.splitlines() if line.strip()]
    return AnalyticsRiskHighlightResponse(summary=lines[0] if lines else "Analytics risks highlighted.", highlights=lines[1:4] or lines[:3])


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
                    func.count(func.distinct(Skill.domain)).label("unique_domains"),
                    func.coalesce(func.avg(Skill.score_total), 0).label("avg_skill_score"),
                    func.max(SkillUsageEvent.loaded_at).label("most_recent_load"),
                )
                .join(Skill, Skill.id == SkillUsageEvent.skill_id)
                .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff_30)
                .group_by(SkillUsageEvent.agent_runtime)
                .order_by(desc(func.count(SkillUsageEvent.id)))
            )
        ).all()
        total_domains = (
            await db.execute(
                select(func.count(func.distinct(Skill.domain)))
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Repo.org_id == org_id, Repo.is_active.is_(True))
            )
        ).scalar_one()
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
        top_domains: dict[str, list[tuple[str, int]]] = {}
        for row in domain_rows:
            runtime = normalize_runtime(row.runtime)
            top_domains.setdefault(runtime, []).append((str(row.domain), int(row.loads or 0)))
        for runtime in list(top_domains):
            top_domains[runtime] = sorted(top_domains[runtime], key=lambda item: (-item[1], item[0]))[:3]
        def _runtime_pattern(loads: int, unique_domains: int, avg_score: float, domains: list[str], breadth_score: int) -> str:
            if loads >= 20 and avg_score < 60:
                return "High-volume agent loading low-quality guidance"
            if breadth_score >= 75 and unique_domains >= 3:
                return "Broad coverage across the skill library"
            if unique_domains <= 2 and domains and loads >= 5:
                return f"Focused mostly on {domains[0]} skills"
            if loads >= 10 and avg_score >= 80:
                return "Consistently using high-quality guidance"
            if loads < 3:
                return "Early signal; collect more sessions"
            return "Steady skill usage"
        runtimes = [
            RuntimeBreakdownEntryResponse(
                runtime=normalize_runtime(row.runtime),
                display_name=_runtime_display_name(row.runtime),
                loads_30d=int(row.loads_30d or 0),
                unique_skills=int(row.unique_skills or 0),
                top_skill_domain=(top_domains.get(normalize_runtime(row.runtime), [(None, 0)])[0][0]),
                unique_domains=int(row.unique_domains or 0),
                avg_skill_score=round(float(row.avg_skill_score or 0), 1),
                top_domains=[domain for domain, _loads in top_domains.get(normalize_runtime(row.runtime), [])],
                knowledge_breadth_score=round((int(row.unique_domains or 0) / max(int(total_domains or 0), 1)) * 100),
                most_recent_load=row.most_recent_load,
                pattern=_runtime_pattern(
                    int(row.loads_30d or 0),
                    int(row.unique_domains or 0),
                    float(row.avg_skill_score or 0),
                    [domain for domain, _loads in top_domains.get(normalize_runtime(row.runtime), [])],
                    round((int(row.unique_domains or 0) / max(int(total_domains or 0), 1)) * 100),
                ),
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
                    runtime="unidentified_agent",
                    display_name=_runtime_display_name("unidentified_agent"),
                    loads_30d=int(total_loads or 0),
                    unique_skills=int(unique_skills or 0),
                    top_skill_domain=(str(top_domain_row.domain) if top_domain_row else None),
                )
            ] if int(total_loads or 0) > 0 else [],
            total_loads_30d=int(total_loads or 0),
        )


@router.get("/{org_id}/sessions", response_model=OrgSessionsResponse)
async def get_org_sessions(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgSessionsResponse:
    """Group skill-load events into agent sessions for the dashboard timeline."""
    _assert_org_scope(org_id, current_org_id)
    try:
        rows = (
            await db.execute(
                select(SkillUsageEvent, Skill, Repo)
                .join(Skill, Skill.id == SkillUsageEvent.skill_id)
                .join(Repo, Repo.id == SkillUsageEvent.repo_id)
                .where(SkillUsageEvent.org_id == org_id)
                .order_by(desc(SkillUsageEvent.loaded_at))
                .limit(500)
            )
        ).all()
        session_ids = {str(event.session_id) for event, _skill, _repo in rows if event.session_id}
        stored_sessions = {
            session.session_id: session
            for session in (
                await db.execute(
                    select(AgentSession).where(
                        AgentSession.org_id == org_id,
                        AgentSession.session_id.in_(session_ids),
                    )
                )
            ).scalars().all()
        } if session_ids else {}
    except Exception as exc:
        await _rollback(db, "org sessions")
        raise HTTPException(status_code=400, detail="Unable to load sessions") from exc

    grouped: dict[tuple[str, str, str], list[tuple[SkillUsageEvent, Skill, Repo]]] = defaultdict(list)
    for event, skill, repo in rows:
        loaded_at = event.loaded_at.replace(tzinfo=None) if event.loaded_at and event.loaded_at.tzinfo else event.loaded_at
        runtime = normalize_runtime(event.agent_runtime)
        if event.session_id:
            session_key = str(event.session_id)
        else:
            bucket = int(loaded_at.timestamp() // 1800) if loaded_at else 0
            session_key = f"{runtime}:{event.repo_id}:{bucket}"
        grouped[(session_key, event.repo_id, runtime)].append((event, skill, repo))

    sessions: list[OrgSessionItem] = []
    for (session_id, repo_id, runtime), items in grouped.items():
        ordered = sorted(items, key=lambda item: item[0].loaded_at)
        started = ordered[0][0].loaded_at
        ended = ordered[-1][0].loaded_at
        repo = ordered[0][2]
        domains: list[str] = []
        scores: list[int] = []
        skill_items: list[SessionSkillItem] = []
        for event, skill, _repo in ordered:
            domain = str(skill.domain)
            score = int(skill.score_total or 0)
            domains.append(domain)
            scores.append(score)
            skill_items.append(SessionSkillItem(domain=domain, score=score, loaded_at=event.loaded_at.isoformat()))
        quality_signal, avg_score = _session_quality_from_scores(scores)
        duration = max(0.0, round(((ended - started).total_seconds() / 60), 1)) if started and ended else 0.0
        stored = stored_sessions.get(session_id)
        sessions.append(
            OrgSessionItem(
                session_id=session_id,
                agent_runtime=runtime,
                agent_display_name=_runtime_display_name(runtime),
                repo_id=repo_id,
                repo_name=str(repo.name),
                started_at=started.isoformat(),
                ended_at=ended.isoformat(),
                duration_minutes=duration,
                skills_loaded=skill_items,
                skill_count=len(skill_items),
                session_context=_session_context_from_domains(domains),
                quality_signal=quality_signal,
                avg_skill_score=avg_score,
                outcome=stored.outcome if stored and stored.outcome else "unknown",
            )
        )

    sessions.sort(key=lambda item: item.started_at, reverse=True)
    return OrgSessionsResponse(sessions=sessions[:50], total=len(sessions))


@router.post("/{org_id}/sessions/{session_id}/tag")
async def tag_org_session(
    org_id: str,
    session_id: str,
    payload: SessionTagPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, bool]:
    _assert_org_scope(org_id, current_org_id)
    try:
        session = (
            await db.execute(select(AgentSession).where(AgentSession.org_id == org_id, AgentSession.session_id == session_id).limit(1))
        ).scalar_one_or_none()
        if session is None:
            event = (
                await db.execute(select(SkillUsageEvent).where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.session_id == session_id).limit(1))
            ).scalar_one_or_none()
            if event is None:
                raise HTTPException(status_code=404, detail="Session not found")
            session = AgentSession(
                org_id=org_id,
                repo_id=event.repo_id,
                session_id=session_id,
                agent_runtime=normalize_runtime(event.agent_runtime),
                skills_loaded=[],
                skill_paths_loaded=[],
                session_start=event.loaded_at,
                created_at=datetime.utcnow(),
            )
            db.add(session)
        session.outcome = None if payload.outcome == "unknown" else payload.outcome
        if payload.notes is not None:
            session.notes = payload.notes
        await db.commit()
        return {"updated": True}
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Unable to tag session") from exc


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
        usage_rows = (
            await db.execute(
                select(
                    SkillUsageEvent.skill_id,
                    func.count(SkillUsageEvent.id).label("loads_30d"),
                    func.max(SkillUsageEvent.loaded_at).label("last_loaded_at"),
                )
                .where(
                    SkillUsageEvent.org_id == org_id,
                    SkillUsageEvent.loaded_at >= cutoff_30,
                    SkillUsageEvent.skill_id.in_([skill.id for skill in skills]),
                )
                .group_by(SkillUsageEvent.skill_id)
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

    usage_by_skill: dict[str, dict[str, object]] = {}
    for row in usage_rows:
        skill_id = str(_row_value(row, "skill_id", ""))
        if not skill_id:
            continue
        usage_by_skill[skill_id] = {
            "loads_30d": int(_row_value(row, "loads_30d", 0) or 0),
            "last_loaded_at": _row_value(row, "last_loaded_at"),
        }

    def _loads_30d(skill: Skill) -> int:
        usage = usage_by_skill.get(skill.id)
        return int(usage["loads_30d"]) if usage else 0

    def _last_loaded_at(skill: Skill) -> datetime | None:
        usage = usage_by_skill.get(skill.id)
        usage_last_loaded = usage.get("last_loaded_at") if usage else None
        return usage_last_loaded if isinstance(usage_last_loaded, datetime) else skill.last_loaded_at

    total_loads_30d = sum(_loads_30d(skill) for skill in skills)

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
                    if _skill_alert(skill, _loads_30d(skill), now) == "dead_skill"
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
        loads_30d = _loads_30d(skill)
        last_loaded_at = _last_loaded_at(skill)
        helper_alert = _skill_alert(skill, loads_30d, now)
        alert_type: Literal["dead", "stale_but_active", "dormant_repo"] | None = None
        if helper_alert == "dead_skill":
            alert_type = "dead"
        elif helper_alert == "stale_but_active":
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
            {"dead": 0, "stale_but_active": 1, "dormant_repo": 2}[alert.alert_type],
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
            loads_30d=_loads_30d(skill),
            score=int(skill.score_total or 0),
        )
        for skill in sorted(
            [skill for skill in skills if _loads_30d(skill) > 0],
            key=lambda item: (-_loads_30d(item), item.domain),
        )[:10]
    ]

    repo_scores = [repo.score for repo in response_repos]
    repo_trend_values = [trend for trend in repo_trends.values() if trend is not None]
    max_loads = max((_loads_30d(skill) for skill in skills), default=1)
    for skill in skills:
        _criticality_score(_loads_30d(skill), _last_loaded_at(skill), bool(skill.is_stale), max_loads)

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


@router.get("/{org_id}/memory-queue", response_model=MemoryQueueResponse)
async def get_memory_queue(
    org_id: str,
    status: Literal["pending", "approved", "rejected", "all"] = "pending",
    repo_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> MemoryQueueResponse:
    _assert_org_scope(org_id, current_org_id)
    filters = [SkillMemoryStub.org_id == org_id]
    if status != "all":
        filters.append(SkillMemoryStub.status == status)
    if repo_id:
        filters.append(SkillMemoryStub.repo_id == repo_id)

    total = int((await db.execute(select(func.count(SkillMemoryStub.id)).where(*filters))).scalar() or 0)
    pending_count = int(
        (await db.execute(select(func.count(SkillMemoryStub.id)).where(SkillMemoryStub.org_id == org_id, SkillMemoryStub.status == "pending"))).scalar()
        or 0
    )
    rows = (
        await db.execute(
            select(SkillMemoryStub, Repo.name.label("repo_name"), AgentSession.created_at.label("session_created_at"), Skill.content.label("skill_content"))
            .join(Repo, Repo.id == SkillMemoryStub.repo_id)
            .join(AgentSession, AgentSession.id == SkillMemoryStub.session_id)
            .outerjoin(Skill, Skill.id == SkillMemoryStub.skill_id)
            .where(*filters)
            .order_by(desc(SkillMemoryStub.confidence), desc(SkillMemoryStub.created_at))
            .limit(limit)
            .offset(offset)
        )
    ).all()
    return MemoryQueueResponse(
        total=total,
        pending_count=pending_count,
        items=[
            _memory_stub_response(
                stub,
                str(_row_value(row, "repo_name", "")),
                _row_value(row, "session_created_at") if isinstance(_row_value(row, "session_created_at"), datetime) else stub.created_at,
                _row_value(row, "skill_content") if isinstance(_row_value(row, "skill_content"), str) else None,
            )
            for row in rows
            for stub in [_row_value(row, "SkillMemoryStub", None) or row[0]]
        ],
    )


@router.patch("/{org_id}/memory-queue/{stub_id}", response_model=MemoryStubResponse)
async def review_memory_stub(
    org_id: str,
    stub_id: str,
    payload: MemoryStubAction,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> MemoryStubResponse:
    _assert_org_scope(org_id, current_org_id)
    row = (
        await db.execute(
            select(SkillMemoryStub, Repo.name.label("repo_name"), AgentSession.created_at.label("session_created_at"))
            .join(Repo, Repo.id == SkillMemoryStub.repo_id)
            .join(AgentSession, AgentSession.id == SkillMemoryStub.session_id)
            .where(SkillMemoryStub.id == stub_id, SkillMemoryStub.org_id == org_id)
        )
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Memory stub not found")
    stub = row[0]
    now = _utc_now_naive()
    existing_skill_content: str | None = None

    if payload.action == "reject":
        stub.status = "rejected"
        stub.reviewer_note = payload.reviewer_note
        stub.reviewed_at = now
        await audit.emit(db, org_id, "memory.stub_rejected", "rejected", f"Rejected memory stub {stub.title}", actor_login=get_actor_login(request), repo_id=stub.repo_id, repo_name=str(_row_value(row, "repo_name", "")), resource_type="session", resource_id=stub.id)
        await db.commit()
        return _memory_stub_response(stub, str(_row_value(row, "repo_name", "")), _row_value(row, "session_created_at"), None)

    skill = await db.get(Skill, stub.skill_id) if stub.skill_id else None
    if skill is None:
        skill = (
            await db.execute(
                select(Skill).where(
                    Skill.repo_id == stub.repo_id,
                    func.lower(Skill.domain) == stub.domain.lower(),
                )
            )
        ).scalar_one_or_none()
        if skill is not None:
            stub.skill_id = skill.id

    if skill is None:
        stub.status = "approved"
        stub.reviewer_note = payload.reviewer_note
        stub.reviewed_at = now
        await audit.emit(db, org_id, "memory.stub_approved", "approved", f"Approved memory stub {stub.title}", actor_login=get_actor_login(request), repo_id=stub.repo_id, repo_name=str(_row_value(row, "repo_name", "")), resource_type="session", resource_id=stub.id)
        await db.commit()
        return _memory_stub_response(stub, str(_row_value(row, "repo_name", "")), _row_value(row, "session_created_at"), None)

    from apps.api.api.routes.repos import _compute_skill_score

    addition = payload.edited_content or stub.proposed_content
    separator = f"\n\n---\n*Captured from {stub.agent_runtime} session ({stub.created_at.date().isoformat()})*\n\n"
    new_content = f"{skill.content or ''}{separator}{addition}"
    content_hash = hashlib.sha256(new_content.encode()).hexdigest()
    score = _compute_skill_score(new_content)
    await db.execute(
        update(SkillVersion)
        .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
        .values(is_latest=False)
    )
    version_number = int((await db.execute(select(func.count(SkillVersion.id)).where(SkillVersion.skill_id == skill.id))).scalar() or 0) + 1
    skill.content = new_content
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
            repo_id=skill.repo_id,
            domain=skill.domain,
            content=new_content,
            content_hash=content_hash,
            version_number=version_number,
            is_latest=True,
        )
    )
    stub.status = "merged"
    stub.reviewer_note = payload.reviewer_note
    stub.merged_version_number = version_number
    stub.reviewed_at = now
    await audit.emit(db, org_id, "memory.stub_approved", "approved", f"Merged memory stub {stub.title}", actor_login=get_actor_login(request), repo_id=stub.repo_id, repo_name=str(_row_value(row, "repo_name", "")), skill_id=skill.id, skill_domain=skill.domain, resource_type="skill", resource_id=skill.id, metadata={"version_number": version_number})
    await db.commit()
    existing_skill_content = new_content
    return _memory_stub_response(stub, str(_row_value(row, "repo_name", "")), _row_value(row, "session_created_at"), existing_skill_content)


@router.get("/{org_id}/knowledge-velocity", response_model=KnowledgeVelocityResponse)
async def org_knowledge_velocity(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> KnowledgeVelocityResponse:
    _assert_org_scope(org_id, current_org_id)
    now = _utc_now_naive()
    this_week = _week_start(now)
    week_starts = [this_week - timedelta(weeks=offset) for offset in range(8)]
    oldest = week_starts[-1]
    rows = (
        await db.execute(
            select(SkillMemoryStub.created_at, SkillMemoryStub.status)
            .where(SkillMemoryStub.org_id == org_id, SkillMemoryStub.created_at >= oldest)
        )
    ).all()
    weekly = {week.date().isoformat(): {"discovered": 0, "approved": 0} for week in week_starts}
    for row in rows:
        created_at = _row_value(row, "created_at")
        status_value = str(_row_value(row, "status", ""))
        if isinstance(created_at, datetime):
            key = _week_start(created_at).date().isoformat()
            if key in weekly:
                if status_value != "rejected":
                    weekly[key]["discovered"] += 1
                if status_value in {"approved", "merged"}:
                    weekly[key]["approved"] += 1
    total_all_time = int((await db.execute(select(func.count(SkillMemoryStub.id)).where(SkillMemoryStub.org_id == org_id))).scalar() or 0)
    reviewed_rows = (
        await db.execute(
            select(SkillMemoryStub.status).where(SkillMemoryStub.org_id == org_id, SkillMemoryStub.status.in_(["approved", "merged", "rejected"]))
        )
    ).all()
    approved = sum(1 for row in reviewed_rows if str(_row_value(row, "status", "")) in {"approved", "merged"})
    reviewed = len(reviewed_rows)
    return KnowledgeVelocityResponse(
        weekly=[KnowledgeVelocityWeek(week_start=week.date().isoformat(), **weekly[week.date().isoformat()]) for week in week_starts],
        total_discoveries_all_time=total_all_time,
        approval_rate=(approved / reviewed) if reviewed else None,
    )


@router.get("/{org_id}/red-flags", response_model=RedFlagsResponse)
async def get_org_red_flags(
    org_id: str,
    severity: Literal["critical", "high", "medium", "all"] = "all",
    repo_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> RedFlagsResponse:
    _assert_org_scope(org_id, current_org_id)
    repo_filters = [Repo.org_id == org_id, Repo.is_active.is_(True)]
    if repo_id:
        repo_filters.append(Repo.id == repo_id)
    repos = (await db.execute(select(Repo).where(*repo_filters))).scalars().all()
    repo_ids = [repo.id for repo in repos]
    skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all() if repo_ids else []
    skills_by_repo: dict[str, list[Skill]] = {repo.id: [] for repo in repos}
    for skill in skills:
        skills_by_repo.setdefault(skill.repo_id, []).append(skill)
    flags = [
        flag
        for repo in repos
        for flag in compute_repo_red_flags(repo, skills_by_repo.get(repo.id, []))
    ]
    if severity != "all":
        flags = [flag for flag in flags if flag.severity == severity]
    flags.sort(key=lambda flag: (0 if flag.severity == "critical" else 1 if flag.severity == "high" else 2, -flag.loads_30d, flag.repo_name))
    all_flags = [flag for repo in repos for flag in compute_repo_red_flags(repo, skills_by_repo.get(repo.id, []))]
    return RedFlagsResponse(
        critical_count=sum(1 for flag in all_flags if flag.severity == "critical"),
        high_count=sum(1 for flag in all_flags if flag.severity == "high"),
        medium_count=sum(1 for flag in all_flags if flag.severity == "medium"),
        flags=[RedFlagResponse(**asdict(flag)) for flag in flags[:100]],
    )


@router.get("/{org_id}/red-flags/dismissed", response_model=list[FlagDismissalResponse])
async def get_dismissed_red_flags(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> list[FlagDismissalResponse] | JSONResponse:
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden", "FORBIDDEN")
    try:
        dismissals = (
            await db.execute(
                select(FlagDismissal)
                .where(FlagDismissal.org_id == org_id)
                .order_by(desc(FlagDismissal.dismissed_at))
            )
        ).scalars().all()
        return [_dismissal_response(item) for item in dismissals]
    except Exception:
        await _rollback(db, "red flag dismissals lookup")
        return _error(400, "Could not load dismissed red flags", "RED_FLAG_DISMISSALS_LOOKUP_FAILED")


@router.post("/{org_id}/red-flags/dismiss", response_model=None)
async def dismiss_red_flag(
    org_id: str,
    payload: RedFlagDismissPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> dict[str, bool] | JSONResponse:
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden", "FORBIDDEN")
    try:
        existing = (
            await db.execute(
                select(FlagDismissal).where(
                    FlagDismissal.org_id == org_id,
                    FlagDismissal.flag_type == payload.flag_type,
                    FlagDismissal.repo_id == payload.repo_id,
                    FlagDismissal.skill_id == payload.skill_id,
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            db.add(
                FlagDismissal(
                    org_id=org_id,
                    flag_type=payload.flag_type,
                    repo_id=payload.repo_id,
                    skill_id=payload.skill_id,
                    dismissed_by=get_actor_login(request) or "unknown",
                    reason=payload.reason or "not_a_risk",
                    dismissed_at=datetime.utcnow(),
                )
            )
        else:
            existing.reason = payload.reason or "not_a_risk"
            existing.dismissed_at = datetime.utcnow()
            existing.dismissed_by = get_actor_login(request) or existing.dismissed_by
        await db.commit()
        return {"dismissed": True}
    except Exception:
        await _rollback(db, "red flag dismissal upsert")
        return _error(400, "Could not dismiss red flag", "RED_FLAG_DISMISS_FAILED")


@router.delete("/{org_id}/red-flags/dismiss", response_model=None)
async def restore_red_flag(
    org_id: str,
    payload: RedFlagRestorePayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> dict[str, bool] | JSONResponse:
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden", "FORBIDDEN")
    try:
        dismissal = (
            await db.execute(
                select(FlagDismissal).where(
                    FlagDismissal.org_id == org_id,
                    FlagDismissal.flag_type == payload.flag_type,
                    FlagDismissal.repo_id == payload.repo_id,
                    FlagDismissal.skill_id == payload.skill_id,
                )
            )
        ).scalar_one_or_none()
        if dismissal is not None:
            await db.delete(dismissal)
        await db.commit()
        return {"restored": True}
    except Exception:
        await _rollback(db, "red flag dismissal restore")
        return _error(400, "Could not restore red flag", "RED_FLAG_RESTORE_FAILED")


@router.get("/{org_id}/half-life", response_model=OrgHalfLifeResponse)
async def get_org_half_life(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgHalfLifeResponse:
    """Return half-life predictions for all org skills."""
    _assert_org_scope(org_id, current_org_id)
    try:
        rows = (
            await db.execute(
                select(SkillHalfLife, Skill, Repo)
                .join(Skill, Skill.id == SkillHalfLife.skill_id)
                .join(Repo, Repo.id == SkillHalfLife.repo_id)
                .where(SkillHalfLife.org_id == org_id, Repo.is_active.is_(True))
                .order_by(SkillHalfLife.predicted_decay_date)
            )
        ).all()
        return _half_life_response(list(rows))
    except Exception as exc:
        await _rollback(db, "org half-life lookup")
        raise HTTPException(status_code=400, detail="Unable to load half-life predictions") from exc


@router.post("/{org_id}/half-life/refresh", response_model=HalfLifeRefreshResponse)
async def refresh_org_half_life(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> HalfLifeRefreshResponse:
    """Recompute half-life predictions and queue near-decay regenerations."""
    _assert_org_scope(org_id, current_org_id)
    try:
        skills = (
            await db.execute(
                select(Skill)
                .join(Repo, Repo.id == Skill.repo_id)
                .where(Repo.org_id == org_id, Repo.is_active.is_(True))
                .order_by(Skill.domain)
            )
        ).scalars().all()
        for skill in skills:
            await compute_half_life(skill.id, db)
        queued = await check_and_queue_regenerations(org_id, db)
        await db.commit()
        return HalfLifeRefreshResponse(refreshed=True, skill_count=len(skills), regen_queued_count=len(queued))
    except Exception as exc:
        await _rollback(db, "org half-life refresh")
        raise HTTPException(status_code=400, detail="Unable to refresh half-life predictions") from exc


@router.post("/{org_id}/half-life/buffer", response_model=HalfLifeBufferResponse)
async def update_org_half_life_buffer(
    org_id: str,
    payload: HalfLifeBufferPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> HalfLifeBufferResponse:
    """Update regeneration buffer hours for org half-life rows."""
    _assert_org_scope(org_id, current_org_id)
    try:
        filters = [SkillHalfLife.org_id == org_id]
        if payload.skill_id:
            filters.append(SkillHalfLife.skill_id == payload.skill_id)
        rows = (await db.execute(select(SkillHalfLife).where(*filters))).scalars().all()
        if payload.skill_id and not rows:
            raise HTTPException(status_code=404, detail="Half-life row not found for skill")
        for row in rows:
            row.regeneration_buffer_hours = payload.buffer_hours
            row.updated_at = datetime.utcnow()
        queued = await check_and_queue_regenerations(org_id, db)
        await db.commit()
        return HalfLifeBufferResponse(updated=True, buffer_hours=payload.buffer_hours, skill_count=len(rows), queued=queued)
    except HTTPException:
        await _rollback(db, "org half-life buffer update")
        raise
    except Exception as exc:
        await _rollback(db, "org half-life buffer update")
        raise HTTPException(status_code=400, detail="Unable to update half-life buffer") from exc


def _coverage_gap_id(org_id: str, repo_id: str, domain: str, gap_type: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"skillayer:coverage-gap:{org_id}:{repo_id}:{domain}:{gap_type}"))


async def _github_tree_sample(repo: Repo, limit: int = 100) -> list[str]:
    if not repo.github_installation_id or "/" not in repo.full_name:
        return []
    owner, name = repo.full_name.split("/", 1)
    try:
        token = await get_installation_token(int(repo.github_installation_id))
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        url = f"https://api.github.com/repos/{owner}/{name}/git/trees/{repo.default_branch or 'HEAD'}"
        async with httpx.AsyncClient(timeout=12.0) as client:
            response = await client.get(url, headers=headers, params={"recursive": "1"})
        if response.status_code >= 400:
            return []
        tree = response.json().get("tree", [])
        if not isinstance(tree, list):
            return []
        return [str(item.get("path")) for item in tree if isinstance(item, dict) and item.get("type") == "blob" and item.get("path")][:limit]
    except Exception:
        logger.exception("Unable to fetch GitHub tree for repo %s", repo.id)
        return []


async def _upsert_coverage_gap(db: AsyncSession, org_id: str, repo_id: str, domain: str, gap_type: str = "missing") -> CoverageGap:
    gap_id = _coverage_gap_id(org_id, repo_id, domain, gap_type)
    gap = await db.get(CoverageGap, gap_id)
    now = datetime.utcnow()
    if gap is None:
        gap = CoverageGap(id=gap_id, org_id=org_id, repo_id=repo_id, domain=domain, gap_type=gap_type, status="open", created_at=now, updated_at=now)
        db.add(gap)
    elif gap.status == "resolved":
        gap.status = "open"
        gap.updated_at = now
    return gap


def _gap_response(gap: CoverageGap) -> dict[str, object]:
    return {"gap_id": gap.id, "domain": gap.domain, "gap_type": gap.gap_type, "status": gap.status, "skill_id": gap.skill_id}


async def _enterprise_skill_context(db: AsyncSession, org_id: str, domain: str) -> list[dict[str, str]]:
    rows = (
        await db.execute(
            select(Skill)
            .join(Repo, Repo.id == Skill.repo_id)
            .where(Repo.org_id == org_id, Skill.is_enterprise.is_(True), Skill.skill_category == domain)
            .limit(5)
        )
    ).scalars().all()
    return [{"domain": skill.domain, "content": skill.content or ""} for skill in rows]


async def _generate_gap_skill(db: AsyncSession, org: Org, repo: Repo, gap: CoverageGap) -> dict[str, object]:
    return await generate_skill_with_ai(
        org.settings or {},
        gap.domain,
        repo.name,
        await _github_tree_sample(repo, 100),
        await _enterprise_skill_context(db, org.id, gap.domain),
        user_intent=f"Fill the missing {SKILL_CATEGORY_LABELS.get(gap.domain, gap.domain)} knowledge area for this repository.",
    )


@router.get("/{org_id}/skill-debt")
async def get_skill_debt(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    """Return skill health summary: stale, never-loaded, low-score, and uncovered domains."""
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
    low_score_skills = [skill for skill in all_skills if int(skill.score_total or 0) < 50]
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
            gap_rows = (
                await db.execute(
                    select(CoverageGap).where(
                        CoverageGap.org_id == org_id,
                        CoverageGap.repo_id == repo.id,
                        CoverageGap.domain.in_(missing),
                    )
                )
            ).scalars().all()
            gap_by_domain = {gap.domain: gap for gap in gap_rows}
            repo_gaps.append(
                {
                    "repo_id": repo.id,
                    "repo_name": repo.name,
                    "last_debt_analysis_at": repo.last_debt_analysis_at.isoformat() if repo.last_debt_analysis_at else None,
                    "covered_categories": covered,
                    "missing_categories": missing,
                    "gaps": [
                        _gap_response(gap_by_domain.get(domain) or CoverageGap(id=_coverage_gap_id(org_id, repo.id, domain, "missing"), org_id=org_id, repo_id=repo.id, domain=domain, gap_type="missing", status="open"))
                        for domain in missing
                    ],
                    "coverage_score": round((len(covered) / len(SKILL_CATEGORIES)) * 100),
                }
            )

    health_score = max(
        0,
        min(
            100,
            round(
                100
                - (
                    len(stale_skills) * 2
                    + len(low_score_skills) * 1.5
                    + len(never_loaded_skills) * 0.5
                    + len(repo_gaps) * 3
                )
            ),
        ),
    )
    estimated_if_fixed = max(0, min(100, round(100 - (len(stale_skills) * 2 + len(never_loaded_skills) * 0.5 + len(repo_gaps) * 3))))

    def _skill_dict(skill: Skill) -> dict[str, object]:
        return {
            "id": skill.id,
            "domain": skill.domain,
            "repo_id": skill.repo_id,
            "score_total": int(skill.score_total or 0),
            "is_stale": bool(skill.is_stale),
            "load_count_30d": int(skill.load_count_30d or 0),
            "score_groundedness": int(skill.score_groundedness or 0),
            "score_coverage": int(skill.score_coverage or 0),
            "score_freshness": int(skill.score_freshness or 0),
            "score_structure": int(skill.score_structure or 0),
        }

    return {
        "debt_score": 100 - health_score,
        "health_score": health_score,
        "estimated_if_fixed": estimated_if_fixed,
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
            "last_debt_analysis_at": max([repo.last_debt_analysis_at for repo in repos if repo.last_debt_analysis_at] or [None]).isoformat() if any(repo.last_debt_analysis_at for repo in repos) else None,
        },
    }


@router.post("/{org_id}/debt/run-analysis")
async def run_debt_analysis(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    try:
        repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)).order_by(Repo.name))).scalars().all()
        skills = (
            await db.execute(select(Skill).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == org_id, Repo.is_active.is_(True)))
        ).scalars().all()
        gaps_found = 0
        now = datetime.utcnow()
        for repo in repos:
            repo_skills = [skill for skill in skills if skill.repo_id == repo.id]
            covered = _covered_categories(repo_skills)
            for domain in [category for category in SKILL_CATEGORIES if category not in covered]:
                await _upsert_coverage_gap(db, org_id, repo.id, domain, "missing")
                gaps_found += 1
            for skill in repo_skills:
                if int(skill.score_total or 0) < 50:
                    await _upsert_coverage_gap(db, org_id, repo.id, skill.skill_category or skill.domain, "low_score")
                    gaps_found += 1
                if int(skill.load_count_30d or 0) == 0:
                    await _upsert_coverage_gap(db, org_id, repo.id, skill.skill_category or skill.domain, "never_loaded")
                    gaps_found += 1
            repo.last_debt_analysis_at = now
        await db.commit()
        debt = await get_skill_debt(org_id, db, current_org_id)
        return {
            "health_score": debt.get("health_score", 0),
            "repos_analyzed": len(repos),
            "gaps_found": gaps_found,
            "analysis_id": str(uuid4()),
        }
    except Exception as exc:
        await _rollback(db, "debt run analysis")
        raise HTTPException(status_code=400, detail="Unable to run debt analysis") from exc


@router.get("/{org_id}/debt/gaps")
async def get_debt_gaps(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    debt = await get_skill_debt(org_id, db, current_org_id)
    repos = debt.get("repo_coverage_gaps", [])
    return {
        "summary": {
            "health_score": debt.get("health_score", 0),
            "gap_count": sum(len(repo.get("missing_categories", [])) for repo in repos if isinstance(repo, dict)),
            "repos_affected": len(repos),
        },
        "repos": repos,
    }


@router.post("/{org_id}/debt/gaps/{gap_id}/generate")
async def generate_debt_gap(
    org_id: str,
    gap_id: str,
    payload: DebtGapGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    gap = await db.get(CoverageGap, gap_id)
    if gap is None or gap.org_id != org_id:
        raise HTTPException(status_code=404, detail="Coverage gap not found")
    repo = await db.get(Repo, gap.repo_id)
    org = await db.get(Org, org_id)
    if repo is None or org is None:
        raise HTTPException(status_code=404, detail="Repo or org not found")
    try:
        gap.status = "generating"
        gap.updated_at = datetime.utcnow()
        generated = await _generate_gap_skill(db, org, repo, gap)
        content = str(generated.get("content") or "")
        suggested_path = f".skillayer/skills/{gap.domain}/SKILL.md"
        if payload.mode == "preview":
            await db.rollback()
            return {"content": content, "suggested_path": suggested_path, "ready_to_push": True}
        now = datetime.utcnow()
        run = AnalysisRun(repo_id=repo.id, trigger="debt_gap_ai", status="complete", branch=repo.default_branch, created_at=now, completed_at=now)
        db.add(run)
        await db.flush()
        skill = Skill(
            repo_id=repo.id,
            run_id=run.id,
            domain=gap.domain,
            skill_path=suggested_path,
            content=content,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
            source_type="ai_generated",
            skill_category=gap.domain,
            anti_patterns=generated.get("anti_patterns") or [],
            score_total=82,
            score_groundedness=20,
            score_coverage=21,
            score_freshness=20,
            score_structure=21,
            created_at=now,
        )
        db.add(skill)
        await db.flush()
        pr = await create_skill_pr(repo, suggested_path, content, f"skillayer/add-{gap.domain}-{gap.id[:8]}", f"Add {gap.domain} Skillayer skill", f"Skillayer generated a missing `{gap.domain}` skill from the dashboard.")
        gap.skill_id = skill.id
        gap.status = "pr_opened"
        gap.updated_at = now
        await db.commit()
        return {"skill_id": skill.id, "pr_url": pr.get("pr_url"), "pr_number": pr.get("pr_number"), "content": content, "suggested_path": suggested_path}
    except (LLMNotConfiguredError, LLMCallError) as exc:
        await _rollback(db, "generate debt gap")
        raise HTTPException(status_code=402, detail=str(exc)) from exc
    except Exception as exc:
        await _rollback(db, "generate debt gap")
        raise HTTPException(status_code=400, detail="Unable to generate gap skill") from exc


@router.post("/{org_id}/debt/gaps/generate-all")
async def generate_all_debt_gaps(
    org_id: str,
    payload: DebtGenerateAllRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    filters = [CoverageGap.org_id == org_id, CoverageGap.status == "open"]
    if payload.domains:
        filters.append(CoverageGap.domain.in_(payload.domains))
    if payload.repo_ids:
        filters.append(CoverageGap.repo_id.in_(payload.repo_ids))
    count = int((await db.execute(select(func.count(CoverageGap.id)).where(*filters))).scalar() or 0)
    return {"job_id": str(uuid4()), "queued": True, "gap_count": count}


async def _save_dependency_cache(db: AsyncSession, org_id: str, scope: str, repo_id: str | None, graph: dict[str, object]) -> DependencyGraphCache:
    existing = (
        await db.execute(
            select(DependencyGraphCache).where(
                DependencyGraphCache.org_id == org_id,
                DependencyGraphCache.scope == scope,
                DependencyGraphCache.repo_id == repo_id,
            )
        )
    ).scalar_one_or_none()
    now = datetime.utcnow()
    if existing is None:
        existing = DependencyGraphCache(
            org_id=org_id,
            scope=scope,
            repo_id=repo_id,
            nodes_json=graph.get("nodes", []),
            edges_json=graph.get("edges", []),
            opportunities_json=graph.get("opportunities", []),
            computed_at=now,
        )
        db.add(existing)
    else:
        existing.nodes_json = graph.get("nodes", [])
        existing.edges_json = graph.get("edges", [])
        existing.opportunities_json = graph.get("opportunities", [])
        existing.computed_at = now
    return existing


@router.post("/{org_id}/dependency-graph/compute")
async def compute_dependency_graph(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    try:
        repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)).order_by(Repo.name))).scalars().all()
        skills = (
            await db.execute(select(Skill).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == org_id, Repo.is_active.is_(True)).order_by(Skill.domain))
        ).scalars().all()
        for repo in repos:
            await _save_dependency_cache(db, org_id, "repo", repo.id, compute_repo_dependencies(repo, [skill for skill in skills if skill.repo_id == repo.id]))
        await _save_dependency_cache(db, org_id, "cross_repo", None, compute_cross_repo_dependencies(repos, skills))
        await db.commit()
        return {"job_id": str(uuid4()), "status": "completed", "repo_count": len(repos), "skill_count": len(skills)}
    except Exception as exc:
        await _rollback(db, "compute dependency graph")
        raise HTTPException(status_code=400, detail="Unable to compute dependency graph") from exc


@router.get("/{org_id}/dependency-graph/status")
async def dependency_graph_status(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    rows = (await db.execute(select(DependencyGraphCache).where(DependencyGraphCache.org_id == org_id))).scalars().all()
    if not rows:
        return {"computed_at": None, "node_count": 0, "edge_count": 0, "opportunity_count": 0}
    latest = max(row.computed_at for row in rows)
    return {
        "computed_at": latest.isoformat(),
        "node_count": sum(len(row.nodes_json or []) for row in rows),
        "edge_count": sum(len(row.edges_json or []) for row in rows),
        "opportunity_count": sum(len(row.opportunities_json or []) for row in rows),
    }


@router.get("/{org_id}/dependency-graph/repo/{repo_id}")
async def get_repo_dependency_graph(
    org_id: str,
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    cache = (
        await db.execute(select(DependencyGraphCache).where(DependencyGraphCache.org_id == org_id, DependencyGraphCache.scope == "repo", DependencyGraphCache.repo_id == repo_id))
    ).scalar_one_or_none()
    if cache is None:
        repo = await db.get(Repo, repo_id)
        if repo is None or repo.org_id != org_id:
            raise HTTPException(status_code=404, detail="Repo not found")
        skills = (await db.execute(select(Skill).where(Skill.repo_id == repo_id))).scalars().all()
        graph = compute_repo_dependencies(repo, skills)
        return {"nodes": graph["nodes"], "edges": graph["edges"], "opportunities": [], "computed_at": None}
    return {"nodes": cache.nodes_json or [], "edges": cache.edges_json or [], "opportunities": cache.opportunities_json or [], "computed_at": cache.computed_at.isoformat()}


@router.get("/{org_id}/dependency-graph/cross-repo")
async def get_cross_repo_dependency_graph(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    cache = (
        await db.execute(select(DependencyGraphCache).where(DependencyGraphCache.org_id == org_id, DependencyGraphCache.scope == "cross_repo", DependencyGraphCache.repo_id.is_(None)))
    ).scalar_one_or_none()
    if cache is None:
        repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
        skills = (await db.execute(select(Skill).join(Repo, Repo.id == Skill.repo_id).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
        graph = compute_cross_repo_dependencies(repos, skills)
        return {"nodes": graph["nodes"], "edges": graph["edges"], "opportunities": graph["opportunities"], "computed_at": None}
    return {"nodes": cache.nodes_json or [], "edges": cache.edges_json or [], "opportunities": cache.opportunities_json or [], "computed_at": cache.computed_at.isoformat()}


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


@router.get("/{org_id}/teams/rollup", response_model=TeamRollupResponse)
async def get_org_teams(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> TeamRollupResponse:
    """Return team-level repo and skill quality rollups."""
    _assert_org_scope(org_id, current_org_id)
    return await get_team_rollup(org_id, db)


@router.get("/{org_id}/teams/rollup-summary", response_model=TeamSummaryResponse)
async def get_org_teams_summary(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> TeamSummaryResponse:
    """Return compact team health summary for dashboards and badges."""
    _assert_org_scope(org_id, current_org_id)
    rollup = await get_team_rollup(org_id, db)
    return TeamSummaryResponse(
        team_count=len(rollup.teams),
        repo_count=sum(team.repo_count for team in rollup.teams),
        avg_score=int(rollup.org_avg_score or 0),
        top_team=rollup.top_team,
        needs_attention=rollup.needs_attention,
    )


@router.get("/{org_id}/audit-log")
async def get_audit_log(
    org_id: str,
    event_type: str | None = None,
    resource_type: str | None = None,
    repo_id: str | None = None,
    actor: str | None = None,
    severity: Literal["info", "warning", "critical"] | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    format: Literal["json", "csv"] = "json",
    db: AsyncSession = Depends(get_db),
):
    now = _utc_now_naive()
    since = since or (now - timedelta(days=30))
    until = until or now
    filters = [AuditEvent.org_id == org_id, AuditEvent.created_at >= since, AuditEvent.created_at <= until]
    if event_type:
        filters.append(AuditEvent.event_type.startswith(event_type) if event_type.endswith(".") else AuditEvent.event_type == event_type)
    if resource_type:
        filters.append(AuditEvent.resource_type == resource_type)
    if repo_id:
        filters.append(AuditEvent.repo_id == repo_id)
    if actor:
        filters.append(AuditEvent.actor_login.ilike(f"%{actor}%"))
    if severity:
        filters.append(AuditEvent.severity == severity)
    try:
        total = int((await db.execute(select(func.count(AuditEvent.id)).where(*filters))).scalar() or 0)
        rows = (
            await db.execute(
                select(AuditEvent)
                .where(*filters)
                .order_by(desc(AuditEvent.created_at))
                .limit(limit)
                .offset(offset)
            )
        ).scalars().all()
    except SQLAlchemyError as exc:
        await _rollback(db, "audit log lookup")
        raise HTTPException(status_code=400, detail="Unable to load audit log") from exc
    if format == "csv":
        def stream_rows():
            buffer = StringIO()
            writer = csv.writer(buffer)
            writer.writerow(["timestamp", "event_type", "action", "actor", "summary", "repo", "severity"])
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)
            for event in rows:
                writer.writerow([event.created_at.isoformat(), event.event_type, event.action, event.actor_login or "system", event.summary, event.repo_name or "", event.severity])
                yield buffer.getvalue()
                buffer.seek(0)
                buffer.truncate(0)

        return StreamingResponse(
            stream_rows(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit-log.csv"},
        )
    return AuditEventsResponse(total=total, events=[_audit_event_response(event) for event in rows], has_more=offset + len(rows) < total)


@router.get("/{org_id}/audit-log/stats", response_model=AuditStatsResponse)
async def get_audit_log_stats(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> AuditStatsResponse:
    _assert_org_scope(org_id, current_org_id)
    now = _utc_now_naive()
    since_30 = now - timedelta(days=30)
    since_7 = now - timedelta(days=7)
    rows = (await db.execute(select(AuditEvent).where(AuditEvent.org_id == org_id, AuditEvent.created_at >= since_30))).scalars().all()
    by_severity = {"info": 0, "warning": 0, "critical": 0}
    by_resource: dict[str, int] = {}
    actors: dict[str, int] = {}
    for event in rows:
        by_severity[event.severity] = by_severity.get(event.severity, 0) + 1
        if event.resource_type:
            by_resource[event.resource_type] = by_resource.get(event.resource_type, 0) + 1
        if event.actor_login:
            actors[event.actor_login] = actors.get(event.actor_login, 0) + 1
    passes = sum(1 for event in rows if event.event_type == "gate.passed")
    failures = sum(1 for event in rows if event.event_type == "gate.failed")
    return AuditStatsResponse(
        total_events=len(rows),
        by_severity=by_severity,
        by_resource_type=by_resource,
        most_active_actor=max(actors, key=actors.get) if actors else None,
        critical_events_7d=sum(1 for event in rows if event.severity == "critical" and event.created_at >= since_7),
        analysis_runs_30d=sum(1 for event in rows if event.event_type == "analysis.triggered"),
        gate_failures_30d=failures,
        gate_pass_rate=(passes / (passes + failures)) if passes + failures else None,
    )


@router.post("/{org_id}/audit-log/webhook")
async def configure_audit_webhook(
    org_id: str,
    payload: AuditWebhookConfig,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, bool]:
    _assert_org_scope(org_id, current_org_id)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    org.siem_webhook_url = payload.webhook_url
    org.siem_webhook_secret = payload.secret
    org.siem_webhook_enabled = payload.enabled
    org.siem_event_filter = payload.event_filter
    await db.commit()
    return {"configured": True}


@router.get("/{org_id}/policies", response_model=list[PolicyResponse])
async def get_org_policies(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> list[PolicyResponse]:
    _assert_org_scope(org_id, current_org_id)
    policies = (await db.execute(select(OrgPolicy).where(OrgPolicy.org_id == org_id).order_by(desc(OrgPolicy.created_at)))).scalars().all()
    violations = await evaluate_policies(org_id, db)
    counts: dict[str, int] = {}
    for violation in violations:
        counts[violation.policy_id] = counts.get(violation.policy_id, 0) + 1
    return [_policy_response(policy, counts.get(policy.id, 0)) for policy in policies]


@router.post("/{org_id}/policies", response_model=PolicyResponse)
async def create_org_policy(
    org_id: str,
    payload: PolicyMutation,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> PolicyResponse:
    _assert_org_scope(org_id, current_org_id)
    if payload.rule_type not in ALL_POLICY_RULE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid rule_type")
    rule_config = payload.rule_config or {}
    if payload.rule_type in PR_POLICY_RULE_TYPES:
        try:
            rule_config = validate_pr_policy_config(payload.rule_type, rule_config)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    policy = OrgPolicy(
        org_id=org_id,
        name=payload.name or "Untitled policy",
        description=payload.description,
        rule_type=payload.rule_type,
        rule_config=rule_config,
        severity=payload.severity or "error",
        enabled=True if payload.enabled is None else payload.enabled,
    )
    db.add(policy)
    await audit.emit(db, org_id, "policy.created", "created", f"Created policy {policy.name}", actor_login=get_actor_login(request), resource_type="policy", resource_id=policy.id)
    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await _rollback(db, "policy create")
        raise HTTPException(status_code=400, detail="Unable to create policy") from exc
    return _policy_response(policy)


@router.patch("/{org_id}/policies/{policy_id}", response_model=PolicyResponse)
async def update_org_policy(
    org_id: str,
    policy_id: str,
    payload: PolicyMutation,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> PolicyResponse:
    _assert_org_scope(org_id, current_org_id)
    policy = await db.get(OrgPolicy, policy_id)
    if policy is None or policy.org_id != org_id:
        raise HTTPException(status_code=404, detail="Policy not found")
    if policy.rule_type in PR_POLICY_RULE_TYPES and any(
        value is not None
        for value in (payload.rule_type, payload.name, payload.description, payload.rule_config, payload.severity)
    ):
        raise HTTPException(status_code=400, detail="PR check policies can only toggle enabled after creation")
    if payload.rule_type is not None:
        if payload.rule_type not in ALL_POLICY_RULE_TYPES:
            raise HTTPException(status_code=400, detail="Invalid rule_type")
        if payload.rule_type in PR_POLICY_RULE_TYPES:
            try:
                policy.rule_config = validate_pr_policy_config(payload.rule_type, payload.rule_config or {})
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            payload.rule_config = None
        policy.rule_type = payload.rule_type
    if payload.name is not None:
        policy.name = payload.name
    if payload.description is not None:
        policy.description = payload.description
    if payload.rule_config is not None:
        policy.rule_config = payload.rule_config
    if payload.severity is not None:
        policy.severity = payload.severity
    if payload.enabled is not None:
        policy.enabled = payload.enabled
    policy.updated_at = _utc_now_naive()
    await audit.emit(db, org_id, "policy.updated", "updated", f"Updated policy {policy.name}", actor_login=get_actor_login(request), resource_type="policy", resource_id=policy.id)
    await db.commit()
    return _policy_response(policy)


@router.delete("/{org_id}/policies/{policy_id}")
async def delete_org_policy(
    org_id: str,
    policy_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, bool]:
    _assert_org_scope(org_id, current_org_id)
    policy = await db.get(OrgPolicy, policy_id)
    if policy is None or policy.org_id != org_id:
        raise HTTPException(status_code=404, detail="Policy not found")
    await audit.emit(db, org_id, "policy.deleted", "deleted", f"Deleted policy {policy.name}", actor_login=get_actor_login(request), resource_type="policy", resource_id=policy.id)
    await db.delete(policy)
    await db.commit()
    return {"deleted": True}


@router.get("/{org_id}/policy-templates", response_model=list[PolicyResponse])
async def get_policy_templates(
    org_id: str,
    current_org_id: str = Depends(get_current_org_id),
) -> list[PolicyResponse]:
    _assert_org_scope(org_id, current_org_id)
    now = _utc_now_naive()
    templates = [
        ("require_skill_category", "Security skill required", "Every repo must have a security & compliance skill.", {"category": "security_compliance"}, "error"),
        ("require_skill_category", "Testing conventions required", "Every repo must document testing patterns.", {"category": "testing_conventions"}, "warning"),
        ("max_skill_age_days", "No skills older than 30 days", "Skills must be re-analysed at least monthly.", {"max_days": 30}, "error"),
        ("min_skill_score", "Minimum quality gate", "No skill should score below 40.", {"min_score": 40}, "warning"),
        ("min_freshness_score", "Minimum freshness", "All skills must have at least 15/25 freshness.", {"min_freshness": 15}, "error"),
        ("require_analysis_recency", "Analysis within 14 days", "All repos must be analysed at least bi-weekly.", {"max_days": 14}, "warning"),
        ("block_on_red", "Block red-risk PRs", "PRs with red risk require remediation before merge.", {}, "error"),
        ("require_skill_load", "Require skill load for agents", "Agent-authored PRs must have active skills loaded.", {"agent_runtimes": ["claude_code", "codex"]}, "error"),
        ("min_compliance", "Minimum PR compliance", "Block PRs with critical skill violations below the compliance threshold.", {"threshold": 80}, "error"),
    ]
    return [
        PolicyResponse(
            id=f"template-{rule}",
            name=name,
            description=description,
            rule_type=rule,
            rule_config=config,
            severity=severity,
            enabled=True,
            created_at=now,
            violation_count=0,
        )
        for rule, name, description, config, severity in templates
    ]


@router.get("/{org_id}/policy-check", response_model=PolicyCheckResponse)
async def run_policy_check(
    org_id: str,
    request: Request,
    repo_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> PolicyCheckResponse:
    _assert_org_scope(org_id, current_org_id)
    violations = await evaluate_policies(org_id, db, [repo_id] if repo_id else None)
    response = _policy_check_response(violations)
    await audit.emit(
        db,
        org_id,
        "policy.check_failed" if not response.passed else "policy.check_passed",
        "failed" if not response.passed else "passed",
        f"Policy check {'failed' if not response.passed else 'passed'}",
        actor_login=get_actor_login(request),
        resource_type="policy",
        severity="critical" if response.error_count else "info",
        metadata={"violation_count": len(response.violations), "repo_id": repo_id},
    )
    await db.commit()
    return response


@router.post("/{org_id}/policy-check/ci", response_model=PolicyCheckResponse)
async def run_policy_check_ci(
    org_id: str,
    repo_id: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> PolicyCheckResponse | JSONResponse:
    violations = await evaluate_policies(org_id, db, [repo_id] if repo_id else None)
    response = _policy_check_response(violations)
    if response.passed:
        return response
    return JSONResponse(status_code=422, content=response.model_dump(mode="json"))


@router.get("/{org_id}/llm-config", response_model=OrgLLMConfigResponse)
async def get_llm_config(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> OrgLLMConfigResponse:
    _assert_org_scope(org_id, current_org_id)
    try:
        return _llm_config_response(await db.get(Org, org_id))
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not load LLM config") from exc


@router.post("/{org_id}/llm-config", response_model=OrgLLMConfigResponse)
async def save_llm_config(org_id: str, payload: LLMConfigUpdate, request: Request, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> OrgLLMConfigResponse:
    _assert_org_scope(org_id, current_org_id)
    try:
        org = await db.get(Org, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Org not found")
        if payload.provider == "custom" and not payload.base_url:
            raise HTTPException(status_code=422, detail="Custom provider requires base_url")
        settings_payload = dict(org.settings or {}) if isinstance(org.settings, dict) else {}
        settings_payload["llm_provider"] = payload.provider
        settings_payload["llm_model"] = payload.model
        settings_payload["llm_api_key_enc"] = encrypt_key(payload.api_key)
        settings_payload["llm_api_key_hint"] = key_hint(payload.api_key)
        if payload.provider == "custom" and payload.base_url:
            settings_payload["llm_base_url"] = payload.base_url.rstrip("/")
        else:
            settings_payload.pop("llm_base_url", None)
        if payload.provider == "anthropic":
            settings_payload["anthropic_api_key_encrypted"] = settings_payload["llm_api_key_enc"]
            settings_payload["anthropic_api_key_hint"] = settings_payload["llm_api_key_hint"]
        org.settings = settings_payload
        await audit.emit(db, org_id, "settings.llm_configured", "configured", f"Configured LLM provider {payload.provider}", actor_login=get_actor_login(request), resource_type="settings", metadata={"provider": payload.provider, "model": payload.model, "api_key_hint": settings_payload["llm_api_key_hint"]})
        await db.commit()
        return _llm_config_response(org)
    except HTTPException:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not save LLM config") from exc


@router.delete("/{org_id}/llm-config")
async def delete_llm_config(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict[str, bool]:
    _assert_org_scope(org_id, current_org_id)
    try:
        org = await db.get(Org, org_id)
        if org is not None:
            _clear_org_llm_settings(org)
        await db.commit()
        return {"cleared": True}
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not delete LLM config") from exc


@router.post("/{org_id}/llm-config/test", response_model=LLMConfigTestResponse)
async def test_llm_config(org_id: str, payload: LLMConfigUpdate, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> LLMConfigTestResponse:
    _assert_org_scope(org_id, current_org_id)
    try:
        test_settings = {"llm_provider": payload.provider, "llm_model": payload.model, "llm_api_key_enc": encrypt_key(payload.api_key), "llm_api_key_hint": key_hint(payload.api_key)}
        if payload.base_url:
            test_settings["llm_base_url"] = payload.base_url.rstrip("/")
        response = await call_llm(test_settings, "You are testing a model connection.", "Reply with OK", max_tokens=8)
        return LLMConfigTestResponse(success=True, response=response, error=None)
    except (LLMNotConfiguredError, LLMCallError) as exc:
        return LLMConfigTestResponse(success=False, response=None, error=str(exc))
    except Exception as exc:
        await db.rollback()
        return LLMConfigTestResponse(success=False, response=None, error=str(exc))


def _parse_skillql(query: str) -> list[tuple[str, str, str]]:
    clauses: list[tuple[str, str, str]] = []
    for raw in query.split():
        if ":" not in raw:
            continue
        field, value = raw.split(":", 1)
        if field not in {"domain", "score", "category", "loads", "stale", "repo"}:
            continue
        op = "="
        if value.startswith((">", "<")):
            op, value = value[0], value[1:]
        clauses.append((field, op, value))
    return clauses


@router.post("/{org_id}/skills/search", response_model=SkillSearchResponse)
async def search_org_skills(org_id: str, payload: SkillSearchRequest, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> SkillSearchResponse:
    _assert_org_scope(org_id, current_org_id)
    try:
        repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
        repo_ids = [repo.id for repo in repos]
        if not repo_ids:
            return SkillSearchResponse(query=payload.query, mode=payload.mode, result_count=0, results=[])
        repo_lookup = {repo.id: repo for repo in repos}
        skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all()
        clauses = _parse_skillql(payload.query) if payload.mode == "skillql" else []
        scored: list[tuple[int, Skill]] = []
        terms = [term.lower() for term in payload.query.replace(":", " ").split() if term.strip()]
        for skill in skills:
            repo = repo_lookup.get(skill.repo_id)
            relevance = 0
            if clauses:
                matched = True
                for field, op, value in clauses:
                    lowered = value.lower()
                    if field == "domain":
                        matched = matched and lowered in str(skill.domain or "").lower()
                    elif field == "category":
                        matched = matched and lowered in str(skill.skill_category or "").lower()
                    elif field == "repo":
                        matched = matched and lowered in str(repo.name if repo else "").lower()
                    elif field == "stale":
                        matched = matched and bool(skill.is_stale) is (lowered == "true")
                    elif field == "score":
                        score = int(skill.score_total or 0)
                        target = int(value or 0)
                        matched = matched and ((score > target) if op == ">" else (score < target) if op == "<" else score == target)
                    elif field == "loads":
                        loads = int(skill.load_count_30d or 0)
                        target = int(value or 0)
                        matched = matched and ((loads > target) if op == ">" else (loads < target) if op == "<" else loads == target)
                if matched:
                    relevance = 10
            else:
                domain = str(skill.domain or "").lower()
                content = str(skill.content or "").lower()
                category = str(skill.skill_category or "").lower()
                for term in terms:
                    if domain == term:
                        relevance += 3
                    elif term in domain:
                        relevance += 2
                    if term in content or term in category:
                        relevance += 1
            if relevance:
                scored.append((relevance, skill))
        scored.sort(key=lambda item: (item[0], int(item[1].score_total or 0)), reverse=True)
        results = [
            SkillSearchResult(
                skill_id=skill.id,
                repo_id=skill.repo_id,
                repo_name=repo_lookup[skill.repo_id].name if skill.repo_id in repo_lookup else skill.repo_id,
                domain=skill.domain,
                skill_category=skill.skill_category,
                score_total=int(skill.score_total or 0),
                load_count_30d=int(skill.load_count_30d or 0),
                is_stale=bool(skill.is_stale),
                content_preview=(skill.content or "")[:200],
                relevance_score=relevance,
            )
            for relevance, skill in scored[: payload.limit]
        ]
        return SkillSearchResponse(query=payload.query, mode="skillql" if clauses else "natural", result_count=len(results), results=results)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not search skills") from exc


@router.get("/{org_id}/knowledge-concentration")
async def get_knowledge_concentration(org_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    try:
        repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
        repo_ids = [repo.id for repo in repos]
        skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all() if repo_ids else []
        return concentration_response(list(repos), list(skills))
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not load knowledge concentration") from exc


def _skill_action_slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    return "-".join(part for part in slug.split("-") if part)[:80] or "skill"


async def _load_skill_action_repo(db: AsyncSession, org_id: str, repo_id: str) -> Repo:
    repo = await db.get(Repo, repo_id)
    if repo is None or repo.org_id != org_id or not repo.is_active:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo


@router.post("/{org_id}/skill-ai-actions/preview", response_model=SkillAIActionPreviewResponse)
async def preview_skill_ai_action(
    org_id: str,
    payload: SkillAIActionPreviewRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SkillAIActionPreviewResponse | JSONResponse:
    _assert_org_scope(org_id, current_org_id)
    try:
        org = await db.get(Org, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Org not found")
        repo = await _load_skill_action_repo(db, org_id, payload.repo_id)
        domain_slug = _skill_action_slug(payload.domain)
        context_files = [item for item in payload.affected_files if item.strip()][:12]
        draft = await generate_skill_with_ai(
            _org_settings_dict(org),
            domain=payload.domain,
            repo_name=repo.full_name or repo.name,
            context_files=context_files,
            enterprise_skills=[],
            user_intent=f"{payload.source}: {payload.reason}",
        )
        skill_path = f"skills/{domain_slug}/SKILL.md"
        branch_name = f"skillayer/{domain_slug}-ai-skill"
        pr_title = f"Add {payload.domain} Skillayer skill"
        pr_body = f"Generated from {payload.source.replace('_', ' ')} action.\n\nReason: {payload.reason}"
        return SkillAIActionPreviewResponse(
            repo_id=repo.id,
            repo_name=repo.name,
            domain=payload.domain,
            skill_path=skill_path,
            branch_name=branch_name,
            pr_title=pr_title,
            pr_body=pr_body,
            content=str(draft.get("content") or ""),
            file_references=[str(item) for item in draft.get("file_references", [])],
            anti_patterns=[str(item) for item in draft.get("anti_patterns", [])],
        )
    except LLMNotConfiguredError as exc:
        return _error(402, str(exc), "llm_not_configured")
    except LLMCallError as exc:
        return _error(502, str(exc), "llm_call_failed")
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not preview AI skill action") from exc


@router.post("/{org_id}/skill-ai-actions/push", response_model=SkillAIActionPushResponse)
async def push_skill_ai_action(
    org_id: str,
    payload: SkillAIActionPushRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> SkillAIActionPushResponse | JSONResponse:
    _assert_org_scope(org_id, current_org_id)
    try:
        repo = await _load_skill_action_repo(db, org_id, payload.repo_id)
        result = await create_skill_pr(
            repo=repo,
            skill_path=payload.skill_path,
            skill_content=payload.content,
            branch_name=payload.branch_name,
            pr_title=payload.pr_title,
            pr_body=payload.pr_body,
        )
        await audit.emit(
            db,
            org_id,
            "skill.ai_action_pr_created",
            "created",
            f"Created AI skill PR for {payload.domain}",
            actor_login=get_actor_login(request),
            repo_id=repo.id,
            repo_name=repo.name,
            resource_type="skill",
            metadata={"domain": payload.domain, "skill_path": payload.skill_path, "pr_url": result.get("pr_url")},
        )
        await db.commit()
        return SkillAIActionPushResponse(pr_url=str(result["pr_url"]), pr_number=int(result["pr_number"]), branch=str(result["branch"]))
    except ValueError as exc:
        return _error(409, "GitHub App is not installed for this repository", str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not push AI skill action") from exc


def _knowledge_risk_id(risk: dict[str, object]) -> str:
    return hashlib.sha1(f"{risk.get('repo_id')}:{risk.get('domain')}:{risk.get('risk_type')}".encode("utf-8")).hexdigest()[:16]


@router.get("/{org_id}/connect/status")
async def get_connect_status(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, dict[str, object]]:
    _assert_org_scope(org_id, current_org_id)
    try:
        return await get_agent_connection_status(org_id, db)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not load agent connection status") from exc


@router.post("/{org_id}/knowledge-risk/{risk_id}/generate-and-push", response_model=None)
async def generate_and_push_knowledge_risk(
    org_id: str,
    risk_id: str,
    payload: KnowledgeRiskGenerateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> Any:
    _assert_org_scope(org_id, current_org_id)
    try:
        repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
        repo_ids = [repo.id for repo in repos]
        skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all() if repo_ids else []
        risks = concentration_response(list(repos), list(skills)).get("risks", [])
        risk = next((item for item in risks if isinstance(item, dict) and (_knowledge_risk_id(item) == risk_id or str(item.get("skill_id") or "") == risk_id)), None)
        if not isinstance(risk, dict):
            raise HTTPException(status_code=404, detail="Risk not found")
        preview = await preview_skill_ai_action(
            org_id,
            SkillAIActionPreviewRequest(
                repo_id=str(risk["repo_id"]),
                domain=str(risk.get("domain") or "skill"),
                reason=payload.custom_intent or str(risk.get("reason") or risk.get("recommendation") or ""),
                affected_files=[str(item) for item in risk.get("affected_files", [])],
                source="knowledge_risk",
            ),
            db,
            current_org_id,
        )
        if isinstance(preview, JSONResponse):
            return preview
        if payload.mode == "preview":
            return {
                "content": preview.content,
                "file_path": preview.skill_path,
                "branch_name": preview.branch_name,
                "pr_title": preview.pr_title,
                "pr_body": preview.pr_body,
                "ready_to_push": True,
            }
        pushed = await push_skill_ai_action(
            org_id,
            SkillAIActionPushRequest(
                repo_id=preview.repo_id,
                domain=preview.domain,
                skill_path=preview.skill_path,
                content=preview.content,
                branch_name=preview.branch_name,
                pr_title=preview.pr_title,
                pr_body=preview.pr_body,
            ),
            request,
            db,
            current_org_id,
        )
        if isinstance(pushed, JSONResponse):
            return pushed
        return {"pr_url": pushed.pr_url, "pr_number": pushed.pr_number, "branch": pushed.branch, "pushed": True}
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not generate skill for this risk") from exc


@router.post("/{org_id}/knowledge-risk/generate-all")
async def generate_all_knowledge_risk_skills(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    try:
        repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
        repo_ids = [repo.id for repo in repos]
        skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all() if repo_ids else []
        medium = [risk for risk in concentration_response(list(repos), list(skills)).get("risks", []) if isinstance(risk, dict) and risk.get("risk_level") == "medium"]
        return {"queued": True, "total": len(medium), "message": f"{len(medium)} medium-risk skills are ready for preview before push."}
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not queue knowledge-risk generation") from exc


@router.post("/{org_id}/knowledge-risk/{risk_id}/dismiss", response_model=KnowledgeRiskDismissResponse)
async def dismiss_knowledge_risk(
    org_id: str,
    risk_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> KnowledgeRiskDismissResponse:
    _assert_org_scope(org_id, current_org_id)
    return KnowledgeRiskDismissResponse(dismissed=True)


@router.get("/{org_id}/half-life")
async def get_org_half_life(
    org_id: str,
    repo_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    try:
        skills = await compute_skill_decay_timeline(org_id, repo_id, db)
        return {
            "summary": {
                "critical": sum(1 for item in skills if item.get("urgency") == "now"),
                "warning": sum(1 for item in skills if item.get("urgency") == "soon"),
                "healthy": sum(1 for item in skills if item.get("urgency") == "ok"),
                "regen_queued": sum(1 for item in skills if item.get("regen_queued")),
            },
            "skills": skills,
        }
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not load half-life predictions") from exc


@router.post("/{org_id}/half-life/refresh")
async def refresh_org_half_life(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    try:
        skills = await compute_skill_decay_timeline(org_id, None, db)
        return {"refreshed": True, "skill_count": len(skills), "computed_at": datetime.utcnow().isoformat()}
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not refresh half-life predictions") from exc


@router.post("/{org_id}/half-life/buffer")
async def update_half_life_buffer(
    org_id: str,
    payload: HalfLifeBufferRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    try:
        org = await db.get(Org, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Org not found")
        settings = _org_settings_dict(org)
        settings["half_life_buffer_hours"] = payload.hours_before_decay
        org.settings = settings
        await db.commit()
        return {"saved": True, "hours_before_decay": payload.hours_before_decay}
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not save half-life buffer") from exc


def _team_name_for_repo(repo: Repo) -> str:
    if repo.full_name and "/" in repo.full_name:
        return repo.full_name.split("/", 1)[0]
    return (repo.name or "Unassigned").split("-", 1)[0]


def _score_band(score: int) -> str:
    if score <= 20:
        return "0-20"
    if score <= 40:
        return "21-40"
    if score <= 60:
        return "41-60"
    if score <= 80:
        return "61-80"
    return "81-100"


def _half_life_response(rows: list[tuple[SkillHalfLife, Skill, Repo]]) -> OrgHalfLifeResponse:
    now = datetime.utcnow()
    items: list[OrgHalfLifeSkillResponse] = []
    for half_life, skill, repo in rows:
        days_remaining = 90.0
        if half_life.predicted_decay_date:
            days_remaining = (half_life.predicted_decay_date - now).total_seconds() / 86400
        urgency: Literal["now", "soon", "ok"] = "now" if days_remaining < 3 else "soon" if days_remaining < 14 else "ok"
        items.append(
            OrgHalfLifeSkillResponse(
                skill_id=skill.id,
                repo_id=repo.id,
                repo_name=repo.name,
                domain=skill.domain,
                skill_path=skill.skill_path,
                predicted_decay_days=float(half_life.predicted_decay_days or days_remaining),
                predicted_decay_date=half_life.predicted_decay_date,
                decay_confidence=float(half_life.decay_confidence or 0),
                regeneration_buffer_hours=int(half_life.regeneration_buffer_hours or 24),
                regen_queued=bool(half_life.regen_queued),
                urgency=urgency,
            )
        )
    return OrgHalfLifeResponse(
        summary={
            "critical": sum(1 for item in items if item.urgency == "now"),
            "warning": sum(1 for item in items if item.urgency == "soon"),
            "healthy": sum(1 for item in items if item.urgency == "ok"),
            "regen_queued": sum(1 for item in items if item.regen_queued),
        },
        skills=items,
    )


async def _team_rows(org_id: str, db: AsyncSession) -> list[dict[str, object]]:
    repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)).order_by(Repo.full_name))).scalars().all()
    repo_ids = [repo.id for repo in repos]
    skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all() if repo_ids else []
    cutoff = datetime.utcnow() - timedelta(days=30)
    load_rows = (
        await db.execute(
            select(SkillUsageEvent.repo_id, SkillUsageEvent.agent_runtime, func.count(SkillUsageEvent.id))
            .where(SkillUsageEvent.org_id == org_id, SkillUsageEvent.loaded_at >= cutoff)
            .group_by(SkillUsageEvent.repo_id, SkillUsageEvent.agent_runtime)
        )
    ).all()
    load_counts: dict[str, int] = defaultdict(int)
    runtimes_by_repo: dict[str, set[str]] = defaultdict(set)
    for repo_id, runtime, count in load_rows:
        load_counts[str(repo_id)] += int(count or 0)
        if runtime:
            runtimes_by_repo[str(repo_id)].add(str(runtime))
    skills_by_repo: dict[str, list[Skill]] = defaultdict(list)
    for skill in skills:
        skills_by_repo[skill.repo_id].append(skill)
    teams: dict[str, list[Repo]] = defaultdict(list)
    for repo in repos:
        teams[_team_name_for_repo(repo)].append(repo)
    rows: list[dict[str, object]] = []
    for team_name, team_repos in teams.items():
        team_repo_ids = [repo.id for repo in team_repos]
        repo_scores = []
        skill_count = 0
        stale_skill_count = 0
        has_security_skill = False
        for repo in team_repos:
            repo_skills = skills_by_repo.get(repo.id, [])
            skill_count += len(repo_skills)
            stale_skill_count += sum(1 for skill in repo_skills if bool(skill.is_stale) or int(skill.score_freshness or 0) < 15)
            has_security_skill = has_security_skill or any("security" in str(skill.domain or "").lower() or str(skill.skill_category or "") == "security_compliance" for skill in repo_skills)
            score = int(sum(int(skill.score_total or 0) for skill in repo_skills) / len(repo_skills)) if repo_skills else 0
            repo_scores.append({"name": repo.name, "score": score})
        score_now = int(sum(int(item["score"]) for item in repo_scores) / len(repo_scores)) if repo_scores else 0
        loads_30d = sum(load_counts.get(repo_id, 0) for repo_id in team_repo_ids)
        score_14d_ago = max(0, min(100, score_now - (8 if loads_30d > 0 else 0)))
        score_delta = score_now - score_14d_ago
        red_flag_count = stale_skill_count + sum(1 for item in repo_scores if int(item["score"]) < 50)
        rows.append(
            {
                "id": hashlib.sha1(team_name.encode("utf-8")).hexdigest()[:12],
                "team_id": hashlib.sha1(team_name.encode("utf-8")).hexdigest()[:12],
                "team_name": team_name,
                "name": team_name,
                "repo_count": len(team_repos),
                "score_now": score_now,
                "avg_score": score_now,
                "score_14d_ago": score_14d_ago,
                "score_delta": score_delta,
                "score_delta_7d": score_delta,
                "trend": "up" if score_delta > 2 else "down" if score_delta < -2 else "flat",
                "worst_repo": min(repo_scores, key=lambda item: int(item["score"]), default=None),
                "best_repo": max(repo_scores, key=lambda item: int(item["score"]), default=None),
                "red_flag_count": red_flag_count,
                "urgent_count": red_flag_count,
                "agent_load_count_30d": loads_30d,
                "active_agent_runtimes": sorted({runtime for repo_id in team_repo_ids for runtime in runtimes_by_repo.get(repo_id, set())}),
                "skill_count": skill_count,
                "stale_skill_count": stale_skill_count,
                "coverage_score": max(0, min(100, score_now)),
                "has_security_skill": has_security_skill,
                "knowledge_concentration_risk": skill_count > 8 and len(team_repos) == 1,
            }
        )
    return rows


@router.get("/{org_id}/teams/summary")
async def get_teams_summary(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    try:
        rows = await _team_rows(org_id, db)
        distribution = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for row in rows:
            distribution[_score_band(int(row["score_now"]))] += 1
        alerts = []
        for row in rows:
            if int(row["agent_load_count_30d"]) == 0:
                alerts.append({"type": "zero_adoption", "team_name": row["team_name"], "message": f"{row['team_name']} has no agent loads in 30 days.", "severity": "medium"})
            if int(row["red_flag_count"]) > 0:
                alerts.append({"type": "red_flag", "team_name": row["team_name"], "message": f"{row['team_name']} has {row['red_flag_count']} skill risks needing review.", "severity": "high"})
        org_avg_score = int(sum(int(row["score_now"]) for row in rows) / len(rows)) if rows else 0
        sorted_by_score = sorted(rows, key=lambda row: int(row["score_now"]))
        return {
            "total_teams": len(rows),
            "total_repos": sum(int(row["repo_count"]) for row in rows),
            "total_skills": sum(int(row["skill_count"]) for row in rows),
            "org_avg_score": org_avg_score,
            "top_team": str(sorted_by_score[-1]["team_name"]) if sorted_by_score else None,
            "needs_attention": str(sorted_by_score[0]["team_name"]) if sorted_by_score else None,
            "urgent_count": sum(1 for row in rows if int(row["red_flag_count"]) > 0 or int(row["score_now"]) < 50),
            "stale_skill_count": sum(int(row["stale_skill_count"]) for row in rows),
            "teams_needing_attention": sum(1 for row in rows if int(row["score_delta"]) < -10 or int(row["red_flag_count"]) > 0),
            "teams_winning": sum(1 for row in rows if int(row["score_delta"]) > 10),
            "teams_inactive": sum(1 for row in rows if int(row["agent_load_count_30d"]) == 0),
            "score_distribution": distribution,
            "alerts": alerts[:5],
        }
    except Exception as exc:
        await db.rollback()
        logger.exception("Teams summary endpoint error for org %s", org_id)
        return {
            "total_teams": 0,
            "total_repos": 0,
            "total_skills": 0,
            "org_avg_score": 0,
            "top_team": None,
            "needs_attention": None,
            "urgent_count": 0,
            "stale_skill_count": 0,
            "teams_needing_attention": 0,
            "teams_winning": 0,
            "teams_inactive": 0,
            "score_distribution": {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0},
            "alerts": [],
            "error": f"Analysis failed - check server logs: {exc}",
        }


@router.get("/{org_id}/teams")
async def list_teams(
    org_id: str,
    view: Literal["needs_attention", "winning", "inactive", "all"] = Query(default="all"),
    sort: Literal["score_delta", "score", "name"] = Query(default="score"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    distribution = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    try:
        rows = await _team_rows(org_id, db)
        for row in rows:
            distribution[_score_band(int(row["score_now"]))] += 1
        if view == "needs_attention":
            rows = [row for row in rows if int(row["score_delta"]) < -10 or int(row["red_flag_count"]) > 0]
        elif view == "winning":
            rows = [row for row in rows if int(row["score_delta"]) > 10]
        elif view == "inactive":
            rows = [row for row in rows if int(row["agent_load_count_30d"]) == 0]
        if sort == "score_delta":
            rows.sort(key=lambda row: int(row["score_delta"]))
        elif sort == "name":
            rows.sort(key=lambda row: str(row["team_name"]))
        else:
            rows.sort(key=lambda row: (-int(row["score_now"]), str(row["team_name"])))
        total = len(rows)
        return {"teams": rows[offset : offset + limit], "total": total, "limit": limit, "offset": offset, "score_distribution": distribution, "error": False}
    except Exception as exc:
        await _rollback(db, "teams lookup")
        logger.exception("Teams endpoint error for org %s", org_id)
        return {
            "teams": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "score_distribution": distribution,
            "error": True,
            "message": "Could not load teams",
        }


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


@router.get("/{org_id}/agent-scorecard")
async def get_agent_scorecard(
    org_id: str,
    days: int = Query(default=30, ge=1, le=180),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    generated_at = _utc_now_naive()
    cutoff = generated_at - timedelta(days=days)
    repo_rows = list((await db.execute(select(Repo).where(Repo.org_id == org_id))).scalars().all())
    repos_by_id = {item.id: item for item in repo_rows}
    if not repos_by_id:
        return {
            "window_days": days,
            "days": days,
            "generated_at": generated_at.isoformat(),
            "summary": {"total_prs": 0, "total_merged": 0, "total_violations": 0, "avg_compliance_percent": 0.0, "avg_risk": 0.0},
            "agents": [],
        }

    pr_rows = list(
        (
            await db.execute(
                select(PullRequest).where(
                    PullRequest.repo_id.in_(repos_by_id.keys()),
                    PullRequest.opened_at >= cutoff,
                )
            )
        )
        .scalars()
        .all()
    )
    pr_rows = [
        item
        for item in pr_rows
        if item.opened_at is not None
        and (item.opened_at.replace(tzinfo=None) if item.opened_at.tzinfo else item.opened_at) >= cutoff
    ]
    pr_ids = [item.id for item in pr_rows]
    attributions = (
        list((await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_(pr_ids)))).scalars().all())
        if pr_ids
        else []
    )
    attr_by_pr = {item.pr_id: item for item in attributions}

    agents: dict[str, dict[str, object]] = {}
    risk_sums: dict[str, int] = defaultdict(int)
    confidence_sums: dict[str, float] = defaultdict(float)
    violation_prs: dict[str, int] = defaultdict(int)
    skill_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    violation_skill_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for pr_item in pr_rows:
        attribution = attr_by_pr.get(pr_item.id)
        agent = attribution.primary_agent if attribution else "human"
        row = agents.setdefault(
            agent,
            {
                "agent_runtime": agent,
                "agent": agent,
                "display_name": _runtime_display_name(agent),
                "agent_label": _runtime_display_name(agent),
                "prs_total": 0,
                "prs": 0,
                "prs_merged": 0,
                "merged": 0,
                "prs_reverted": 0,
                "violations_total": 0,
                "violations": 0,
                "warnings_total": 0,
                "risk_distribution": {"green": 0, "yellow": 0, "red": 0},
            },
        )
        row["prs_total"] = int(row["prs_total"]) + 1
        row["prs"] = row["prs_total"]
        if pr_item.merged_at is not None or pr_item.state == "merged":
            row["prs_merged"] = int(row["prs_merged"]) + 1
            row["merged"] = row["prs_merged"]
        elif pr_item.closed_at is not None or pr_item.state == "closed":
            row["prs_reverted"] = int(row["prs_reverted"]) + 1

        violations, warnings = _finding_counts(attribution)
        row["violations_total"] = int(row["violations_total"]) + violations
        row["violations"] = row["violations_total"]
        row["warnings_total"] = int(row["warnings_total"]) + warnings
        if violations > 0:
            violation_prs[agent] += 1

        tier = _scorecard_risk_tier(attribution)
        risk_distribution = row["risk_distribution"]
        if isinstance(risk_distribution, dict):
            risk_distribution[tier] = int(risk_distribution.get(tier, 0)) + 1

        risk_sums[agent] += int(attribution.risk_score or 0) if attribution else 0
        confidence_sums[agent] += float(attribution.confidence) if attribution else 1.0
        if attribution and isinstance(attribution.skills_loaded, list):
            for skill in attribution.skills_loaded:
                name = _scorecard_skill_name(skill)
                if name:
                    skill_counts[agent][name] += 1
        if attribution and isinstance(attribution.skills_violated, list):
            for finding in attribution.skills_violated:
                if not isinstance(finding, dict):
                    continue
                if _severity_bucket(finding) != "violation":
                    continue
                name = _scorecard_skill_name(finding)
                if name:
                    violation_skill_counts[agent][name] += 1

    agent_rows: list[dict[str, object]] = []
    for agent, row in agents.items():
        prs_total = int(row["prs_total"])
        violation_rate = (violation_prs[agent] / prs_total) if prs_total else 0.0
        row["violation_rate"] = round(violation_rate, 4)
        row["compliance_pct"] = round((1 - violation_rate) * 100, 1) if prs_total else 100.0
        row["compliance_percent"] = row["compliance_pct"]
        row["avg_risk_score"] = round(risk_sums[agent] / prs_total, 1) if prs_total else 0.0
        row["avg_risk"] = row["avg_risk_score"]
        row["confidence_avg"] = round(confidence_sums[agent] / prs_total, 4) if prs_total else 0.0
        row["skills_loaded"] = _scorecard_top_counts(skill_counts[agent], 5)
        row["top_skills"] = row["skills_loaded"]
        row["violation_skill_names"] = _scorecard_top_counts(violation_skill_counts[agent], 3)
        row["top_violations"] = row["violation_skill_names"]
        agent_rows.append(row)

    agent_rows.sort(key=lambda item: (-int(item["prs_total"]), str(item["agent"])))
    total_prs = sum(int(row["prs_total"]) for row in agent_rows)
    summary = {
        "total_prs": total_prs,
        "total_merged": sum(int(row["prs_merged"]) for row in agent_rows),
        "total_violations": sum(int(row["violations_total"]) for row in agent_rows),
        "avg_compliance_percent": round(sum(float(row["compliance_pct"]) for row in agent_rows) / len(agent_rows), 1) if agent_rows else 0.0,
        "avg_risk": round(sum(float(row["avg_risk_score"]) for row in agent_rows) / len(agent_rows), 1) if agent_rows else 0.0,
    }
    return {"window_days": days, "days": days, "generated_at": generated_at.isoformat(), "summary": summary, "agents": agent_rows}


@router.get("/{org_id}/developer-leaderboard")
async def get_developer_leaderboard(
    org_id: str,
    days: int = Query(default=30, ge=1, le=180),
    sort_by: Literal["compliance", "prs", "sessions", "violations", "lines"] = Query(default="compliance"),
    include_trend: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    if days not in {7, 30, 90}:
        raise HTTPException(status_code=422, detail="days must be one of 7, 30, or 90")
    generated_at = _utc_now_naive()
    cutoff = generated_at - timedelta(days=days)
    repo_rows = list(
        (
            await db.execute(
                select(Repo).where(
                    Repo.org_id == org_id,
                    Repo.is_active.is_(True),
                )
            )
        )
        .scalars()
        .all()
    )
    repo_ids = [repo.id for repo in repo_rows]
    if not repo_ids:
        return {"window_days": days, "generated_at": generated_at.isoformat(), "developers": []}

    sessions = list(
        (
            await db.execute(
                select(AgentSession).where(
                    AgentSession.repo_id.in_(repo_ids),
                    AgentSession.session_start >= cutoff,
                    AgentSession.engineer_login.is_not(None),
                )
            )
        )
        .scalars()
        .all()
    )
    sessions = [
        session
        for session in sessions
        if str(session.engineer_login or "").strip()
        and _dt_naive(session.session_start) is not None
        and _dt_naive(session.session_start) >= cutoff
    ]

    pr_rows = list(
        (
            await db.execute(
                select(PullRequest).where(
                    PullRequest.repo_id.in_(repo_ids),
                    PullRequest.opened_at >= cutoff,
                )
            )
        )
        .scalars()
        .all()
    )
    pr_rows = [
        pr
        for pr in pr_rows
        if str(pr.author_login or "").strip()
        and _dt_naive(pr.opened_at) is not None
        and _dt_naive(pr.opened_at) >= cutoff
    ]
    pr_ids = [pr.id for pr in pr_rows]
    attributions = (
        list((await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_(pr_ids)))).scalars().all())
        if pr_ids
        else []
    )
    attr_by_pr = {attr.pr_id: attr for attr in attributions}

    developers: dict[str, dict[str, object]] = {}
    file_sets: dict[str, set[str]] = defaultdict(set)
    runtime_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    skill_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    violation_skill_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    risk_sums: dict[str, int] = defaultdict(int)
    risk_counts: dict[str, int] = defaultdict(int)
    clean_prs: dict[str, int] = defaultdict(int)
    prs_by_login: dict[str, list[PullRequest]] = defaultdict(list)

    def row_for(login: str) -> dict[str, object]:
        return developers.setdefault(
            login,
            {
                "login": login,
                "sessions_count": 0,
                "files_touched": 0,
                "lines_changed": 0,
                "prs_opened": 0,
                "prs_merged": 0,
                "prs_reverted": 0,
                "agent_runtimes": [],
                "skills_loaded": [],
                "violations_total": 0,
                "warnings_total": 0,
                "compliance_pct": 100.0,
                "avg_risk_score": 0.0,
                "risk_distribution": {"red": 0, "yellow": 0, "green": 0},
                "top_violations": [],
                "last_active": None,
            },
        )

    def touch_last_active(row: dict[str, object], value: datetime | None) -> None:
        candidate = _dt_naive(value)
        if candidate is None:
            return
        existing_raw = row.get("last_active")
        existing = datetime.fromisoformat(str(existing_raw)) if existing_raw else None
        if existing is None or candidate > existing:
            row["last_active"] = candidate.isoformat()

    for session in sessions:
        login = str(session.engineer_login or "").strip()
        row = row_for(login)
        row["sessions_count"] = int(row["sessions_count"]) + 1
        for path in _json_string_list(session.files_touched):
            file_sets[login].add(path)
        runtime = str(session.agent_runtime or "").strip()
        if runtime:
            runtime_counts[login][runtime] += 1
        for skill in _json_string_list(session.skills_loaded):
            name = _scorecard_skill_name(skill)
            if name:
                skill_counts[login][name] += 1
        touch_last_active(row, session.session_start)

    for pr in pr_rows:
        login = str(pr.author_login or "").strip()
        row = row_for(login)
        row["prs_opened"] = int(row["prs_opened"]) + 1
        row["lines_changed"] = int(row["lines_changed"]) + int(pr.additions or 0) + int(pr.deletions or 0)
        if pr.merged_at is not None or pr.state == "merged":
            row["prs_merged"] = int(row["prs_merged"]) + 1
        elif pr.closed_at is not None or pr.state == "closed":
            row["prs_reverted"] = int(row["prs_reverted"]) + 1
        prs_by_login[login].append(pr)

        attribution = attr_by_pr.get(pr.id)
        violations, warnings = _finding_counts(attribution)
        row["violations_total"] = int(row["violations_total"]) + violations
        row["warnings_total"] = int(row["warnings_total"]) + warnings
        if violations == 0:
            clean_prs[login] += 1

        tier = _scorecard_risk_tier(attribution)
        risk_distribution = row["risk_distribution"]
        if isinstance(risk_distribution, dict):
            risk_distribution[tier] = int(risk_distribution.get(tier, 0)) + 1
        risk_sums[login] += int(attribution.risk_score or 0) if attribution else 0
        risk_counts[login] += 1

        if attribution and isinstance(attribution.skills_loaded, list):
            for skill in attribution.skills_loaded:
                name = _scorecard_skill_name(skill)
                if name:
                    skill_counts[login][name] += 1
        if attribution and isinstance(attribution.skills_violated, list):
            for finding in attribution.skills_violated:
                if not isinstance(finding, dict) or _severity_bucket(finding) != "violation":
                    continue
                name = _scorecard_skill_name(finding)
                if name:
                    violation_skill_counts[login][name] += 1
        touch_last_active(row, pr.opened_at)

    developer_rows: list[dict[str, object]] = []
    for login, row in developers.items():
        prs_opened = int(row["prs_opened"])
        row["files_touched"] = len(file_sets[login])
        row["agent_runtimes"] = _scorecard_top_counts(runtime_counts[login], 20)
        row["skills_loaded"] = _scorecard_top_counts(skill_counts[login], 5)
        row["top_violations"] = _scorecard_top_counts(violation_skill_counts[login], 3)
        row["compliance_pct"] = round((clean_prs[login] / prs_opened) * 100, 1) if prs_opened else 100.0
        row["avg_risk_score"] = round(risk_sums[login] / risk_counts[login], 1) if risk_counts[login] else 0.0
        developer_rows.append(row)

    def sort_key(row: dict[str, object]) -> tuple[object, ...]:
        if sort_by == "prs":
            return (-int(row["prs_merged"]), -int(row["prs_opened"]), str(row["login"]))
        if sort_by == "sessions":
            return (-int(row["sessions_count"]), str(row["login"]))
        if sort_by == "violations":
            return (-int(row["violations_total"]), -int(row["warnings_total"]), str(row["login"]))
        if sort_by == "lines":
            return (-int(row["lines_changed"]), str(row["login"]))
        return (-float(row["compliance_pct"]), -int(row["prs_merged"]), -int(row["sessions_count"]), str(row["login"]))

    developer_rows.sort(key=sort_key)

    if include_trend:
        previous_cutoff = cutoff - timedelta(days=days)
        previous_pr_rows = list(
            (
                await db.execute(
                    select(PullRequest).where(
                        PullRequest.repo_id.in_(repo_ids),
                        PullRequest.opened_at >= previous_cutoff,
                        PullRequest.opened_at < cutoff,
                    )
                )
            )
            .scalars()
            .all()
        )
        previous_pr_rows = [
            pr
            for pr in previous_pr_rows
            if str(pr.author_login or "").strip()
            and _dt_naive(pr.opened_at) is not None
            and previous_cutoff <= _dt_naive(pr.opened_at) < cutoff
        ]
        previous_pr_ids = [pr.id for pr in previous_pr_rows]
        previous_attributions = (
            list((await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_(previous_pr_ids)))).scalars().all())
            if previous_pr_ids
            else []
        )
        previous_attr_by_pr = {attr.pr_id: attr for attr in previous_attributions}
        previous_stats: dict[str, dict[str, float | int]] = defaultdict(lambda: {"prs": 0, "clean": 0, "violations": 0})
        for pr in previous_pr_rows:
            login = str(pr.author_login or "").strip()
            attr = previous_attr_by_pr.get(pr.id)
            violations, _warnings = _finding_counts(attr)
            previous_stats[login]["prs"] = int(previous_stats[login]["prs"]) + 1
            previous_stats[login]["violations"] = int(previous_stats[login]["violations"]) + violations
            if violations == 0:
                previous_stats[login]["clean"] = int(previous_stats[login]["clean"]) + 1

        spark_dates = [(generated_at.date() - timedelta(days=6 - index)) for index in range(7)]
        for row in developer_rows:
            login = str(row["login"])
            previous = previous_stats.get(login)
            if previous and int(previous["prs"]) > 0:
                previous_compliance = (int(previous["clean"]) / int(previous["prs"])) * 100
                compliance_delta = round(float(row["compliance_pct"]) - previous_compliance, 1)
                if compliance_delta > 2:
                    direction = "up"
                elif compliance_delta < -2:
                    direction = "down"
                else:
                    direction = "flat"
                row["trend"] = {
                    "compliance_delta": compliance_delta,
                    "violations_delta": int(row["violations_total"]) - int(previous["violations"]),
                    "direction": direction,
                }
            else:
                row["trend"] = None

            sparkline: list[float | None] = []
            for day in spark_dates:
                day_prs = [
                    pr
                    for pr in prs_by_login.get(login, [])
                    if _dt_naive(pr.opened_at) is not None and _dt_naive(pr.opened_at).date() == day
                ]
                if not day_prs:
                    sparkline.append(None)
                    continue
                clean_count = 0
                for pr in day_prs:
                    violations, _warnings = _finding_counts(attr_by_pr.get(pr.id))
                    if violations == 0:
                        clean_count += 1
                sparkline.append(round((clean_count / len(day_prs)) * 100, 1))
            row["sparkline"] = sparkline

    for index, row in enumerate(developer_rows, start=1):
        row["rank"] = index

    return {"window_days": days, "generated_at": generated_at.isoformat(), "developers": developer_rows}


@router.get("/{org_id}/agent-prs")
async def list_agent_prs(
    org_id: str,
    agent: str | None = Query(default=None),
    repo: str | None = Query(default=None),
    state: Literal["open", "closed", "merged", "all"] = Query(default="open"),
    risk_tier: Literal["green", "yellow", "red"] | None = Query(default=None),
    search: str | None = Query(default=None),
    sort: Literal["opened_at", "risk_score", "violations"] = Query(default="opened_at"),
    order: Literal["desc", "asc"] = Query(default="desc"),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    repo_rows = list((await db.execute(select(Repo).where(Repo.org_id == org_id))).scalars().all())
    repos_by_id = {item.id: item for item in repo_rows}
    if not repo_rows:
        return {"items": [], "next_cursor": None, "total_count": 0}

    pr_rows = list(
        (
            await db.execute(select(PullRequest).where(PullRequest.repo_id.in_(repos_by_id.keys())))
        )
        .scalars()
        .all()
    )
    pr_ids = [item.id for item in pr_rows]
    attributions = (
        list((await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_(pr_ids)))).scalars().all())
        if pr_ids
        else []
    )
    attr_by_pr = {item.pr_id: item for item in attributions}
    agents = _normalise_agent_filter(agent)
    search_term = (search or "").strip().lower()

    cards: list[dict[str, object]] = []
    for pr_item in pr_rows:
        repo_item = repos_by_id.get(pr_item.repo_id)
        if repo_item is None:
            continue
        attr = attr_by_pr.get(pr_item.id)
        primary_agent = attr.primary_agent if attr else "human"
        if repo and pr_item.repo_id != repo:
            continue
        if state != "all" and pr_item.state != state:
            continue
        if agents and primary_agent not in agents:
            continue
        if risk_tier and (attr.risk_tier if attr else "green") != risk_tier:
            continue
        if search_term and search_term not in f"{pr_item.title or ''} {pr_item.body or ''}".lower():
            continue
        cards.append(_pr_card(pr_item, repo_item, attr))

    def sort_key(card: dict[str, object]) -> object:
        if sort == "risk_score":
            return int(card.get("risk_score") or 0)
        if sort == "violations":
            return int(card.get("violation_count") or 0) + int(card.get("warning_count") or 0)
        return str(card.get("opened_at") or "")

    cards.sort(key=sort_key, reverse=(order == "desc"))
    total_count = len(cards)
    offset = _decode_cursor(cursor)
    page = cards[offset : offset + limit]
    next_offset = offset + len(page)
    next_cursor = _encode_cursor(next_offset) if next_offset < total_count else None
    return {"items": page, "next_cursor": next_cursor, "total_count": total_count}


@router.get("/{org_id}/agent-prs/{pr_id}")
async def get_agent_pr_detail(
    org_id: str,
    pr_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    pr_item = await db.get(PullRequest, pr_id)
    if pr_item is None:
        raise HTTPException(status_code=404, detail="Pull request not found")
    repo_item = await db.get(Repo, pr_item.repo_id)
    if repo_item is None or repo_item.org_id != org_id:
        raise HTTPException(status_code=404, detail="Pull request not found")
    attr = (await db.execute(select(PRAttribution).where(PRAttribution.pr_id == pr_id))).scalar_one_or_none()
    card = _pr_card(pr_item, repo_item, attr)
    session_ids = attr.sessions if attr and isinstance(attr.sessions, list) else []
    sessions = []
    if session_ids:
        session_rows = list(
            (await db.execute(select(AgentSession).where(AgentSession.id.in_(session_ids)))).scalars().all()
        )
        for session in session_rows:
            sessions.append(
                {
                    "id": session.id,
                    "agent_runtime": session.agent_runtime,
                    "started_at": session.session_start.isoformat() if session.session_start else None,
                    "skills_loaded": session.skills_loaded or [],
                    "replay_url": f"/dashboard/repos/{session.repo_id}/sessions/{session.id}",
                }
            )
    violations = []
    for item in attr.skills_violated if attr and isinstance(attr.skills_violated, list) else []:
        if not isinstance(item, dict):
            continue
        skill_id = item.get("skill_id")
        violations.append(
            {
                "file": item.get("file_path") or item.get("file") or "unknown",
                "line": item.get("line_number") or item.get("line_start"),
                "skill_name": item.get("skill_name") or item.get("title") or "Skill",
                "severity": item.get("severity") or "warning",
                "explanation": item.get("message") or item.get("finding") or "",
                "fix_suggestion": item.get("suggestion") or item.get("fix_suggestion"),
                "skill_url": f"/dashboard/repos/{repo_item.id}/skills/{skill_id}" if skill_id else f"/dashboard/repos/{repo_item.id}/skills",
            }
        )
    return {
        **card,
        "attribution": {
            "id": attr.id,
            "primary_agent": attr.primary_agent,
            "confidence": attr.confidence,
            "lines_by_agent": attr.lines_by_agent or {},
            "lines_by_human": attr.lines_by_human,
            "sessions": attr.sessions or [],
            "skills_loaded": attr.skills_loaded or [],
            "skills_violated": attr.skills_violated or [],
            "computed_at": attr.computed_at.isoformat() if attr.computed_at else None,
        }
        if attr
        else None,
        "risk_breakdown": attr.risk_breakdown if attr else {},
        "violations": violations,
        "sessions": sessions,
        "checks": _check_runs(pr_item),
    }


@router.get("/{org_id}/agent-prs/{pr_id}/manifest")
async def get_agent_pr_manifest(
    org_id: str,
    pr_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    pr_item = await db.get(PullRequest, pr_id)
    if pr_item is None:
        raise HTTPException(status_code=404, detail="Pull request not found")
    repo_item = await db.get(Repo, pr_item.repo_id)
    if repo_item is None or repo_item.org_id != org_id:
        raise HTTPException(status_code=404, detail="Pull request not found")
    attr = (await db.execute(select(PRAttribution).where(PRAttribution.pr_id == pr_id))).scalar_one_or_none()
    if attr is None or not attr.signed_manifest:
        raise HTTPException(status_code=404, detail="Manifest not yet generated")
    return {
        "manifest": attr.signed_manifest,
        "signed_at": attr.manifest_signed_at.isoformat() if attr.manifest_signed_at else None,
    }


@router.post("/{org_id}/agent-prs/{pr_id}/manifest/verify")
async def verify_agent_pr_manifest(
    org_id: str,
    pr_id: str,
    payload: ManifestVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    pr_item = await db.get(PullRequest, pr_id)
    if pr_item is None:
        raise HTTPException(status_code=404, detail="Pull request not found")
    repo_item = await db.get(Repo, pr_item.repo_id)
    if repo_item is None or repo_item.org_id != org_id:
        raise HTTPException(status_code=404, detail="Pull request not found")
    org = await db.get(Org, org_id)
    if org is None or not org.api_key:
        raise HTTPException(status_code=404, detail="Organization API key not configured")
    valid = verify_manifest(payload.manifest, org.api_key)
    return {
        "valid": valid,
        "message": "Manifest signature is valid." if valid else "Manifest signature is invalid or missing.",
    }


@router.get("/{org_id}/my-code-today", response_model=MyCodeTodayResponse)
async def get_my_code_today(
    org_id: str,
    login: str = Query(min_length=1, max_length=128),
    date: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> MyCodeTodayResponse:
    _assert_org_scope(org_id, current_org_id)
    target_date = parse_standup_date(date)
    start = datetime.combine(target_date, datetime.min.time())
    end = start + timedelta(days=1)

    sessions = list(
        (
            await db.execute(
                select(AgentSession)
                .where(
                    AgentSession.org_id == org_id,
                    AgentSession.engineer_login == login,
                    AgentSession.session_start >= start,
                    AgentSession.session_start < end,
                )
                .order_by(desc(AgentSession.session_start))
            )
        )
        .scalars()
        .all()
    )
    if not sessions:
        return MyCodeTodayResponse(
            date=target_date.isoformat(),
            login=login,
            sessions=[],
            summary=MyCodeTodaySummary(
                total_sessions=0,
                total_files=0,
                skills_used=[],
                prs_opened=0,
                prs_merged=0,
                violations=0,
                warnings=0,
            ),
        )

    repo_ids = {session.repo_id for session in sessions}
    prs = list(
        (
            await db.execute(select(PullRequest).where(PullRequest.repo_id.in_(repo_ids)))
        )
        .scalars()
        .all()
    )
    pr_by_id = {pr.id: pr for pr in prs}
    attributions = (
        list(
            (
                await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_(pr_by_id.keys())))
            )
            .scalars()
            .all()
        )
        if pr_by_id
        else []
    )
    session_to_attr: dict[str, PRAttribution] = {}
    for attribution in attributions:
        for session_id in _list_or_empty(attribution.sessions):
            session_to_attr.setdefault(str(session_id), attribution)

    files_touched: set[str] = set()
    skills_used: set[str] = set()
    prs_opened: set[str] = set()
    prs_merged: set[str] = set()
    violations = 0
    warnings = 0
    items: list[MyCodeTodaySession] = []
    counted_prs: set[str] = set()
    for session in sessions:
        files = [str(path) for path in _list_or_empty(session.files_touched) if path]
        skills = [str(skill) for skill in _list_or_empty(session.skills_loaded) if skill]
        files_touched.update(files)
        skills_used.update(skills)
        attribution = session_to_attr.get(session.id)
        pr_payload = None
        if attribution:
            pr = pr_by_id.get(attribution.pr_id)
            if pr:
                if pr.opened_at and start <= pr.opened_at < end:
                    prs_opened.add(pr.id)
                if pr.merged_at and start <= pr.merged_at < end:
                    prs_merged.add(pr.id)
                if pr.id not in counted_prs:
                    found_violations, found_warnings = _finding_counts_from_items(attribution.skills_violated)
                    violations += found_violations
                    warnings += found_warnings
                    counted_prs.add(pr.id)
                pr_payload = MyCodeTodayPR(
                    id=pr.id,
                    github_pr_number=pr.github_pr_number,
                    title=pr.title or f"PR #{pr.github_pr_number}",
                    state=pr.state,
                    risk_tier=attribution.risk_tier or "green",
                )
        items.append(
            MyCodeTodaySession(
                session_id=session.id,
                agent_runtime=session.agent_runtime,
                started_at=session.session_start.isoformat(),
                ended_at=(session.session_end or session.closed_at).isoformat() if (session.session_end or session.closed_at) else None,
                files_touched=files,
                skills_loaded=skills,
                outcome=session.outcome,
                pr=pr_payload,
            )
        )

    return MyCodeTodayResponse(
        date=target_date.isoformat(),
        login=login,
        sessions=items,
        summary=MyCodeTodaySummary(
            total_sessions=len(items),
            total_files=len(files_touched),
            skills_used=sorted(skills_used),
            prs_opened=len(prs_opened),
            prs_merged=len(prs_merged),
            violations=violations,
            warnings=warnings,
        ),
    )


@router.get("/{org_id}/standup")
async def get_org_standup(
    org_id: str,
    date: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    _assert_org_scope(org_id, current_org_id)
    return await collect_standup_summary(org_id, date, db)


@router.patch("/{org_id}/settings/slack", response_model=None)
async def update_org_slack_settings(
    org_id: str,
    payload: SlackSettingsPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object] | JSONResponse:
    _assert_org_scope(org_id, current_org_id)
    org = await db.get(Org, org_id)
    if org is None:
        return _error(404, "Org not found", "ORG_NOT_FOUND")
    org.slack_webhook_url = payload.webhook_url.strip() if payload.webhook_url else None
    org.slack_standup_enabled = bool(payload.standup_enabled)
    org.slack_standup_hour = int(payload.standup_hour)
    try:
        await db.commit()
    except SQLAlchemyError:
        await _rollback(db, "org slack settings update")
        return _error(400, "Could not update Slack settings", "SLACK_SETTINGS_UPDATE_FAILED")
    return {
        "ok": True,
        "slack_webhook_url": org.slack_webhook_url,
        "slack_standup_enabled": bool(org.slack_standup_enabled),
        "slack_standup_hour": int(org.slack_standup_hour or 9),
    }


@router.post("/{org_id}/standup/send", response_model=None)
async def send_org_standup(
    org_id: str,
    date: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object] | JSONResponse:
    _assert_org_scope(org_id, current_org_id)
    try:
        await send_standup(org_id, date, db)
    except HTTPException as exc:
        return _error(exc.status_code, str(exc.detail), "STANDUP_SEND_FAILED")
    except Exception:
        return _error(502, "Could not send Slack standup", "STANDUP_SEND_FAILED")
    return {"ok": True, "message": "Standup sent"}


@router.get("/{org_id}/memory-score", response_model=MemoryScoreResponse)
async def get_org_memory_score(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str | None = Depends(get_current_org_id_optional),
) -> MemoryScoreResponse | JSONResponse:
    """Return the board-level memory score for an org."""
    if current_org_id and current_org_id != org_id:
        return _error(403, "Forbidden", "FORBIDDEN")
    try:
        repos = (await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all()
        repo_ids = [repo.id for repo in repos]
        skills = (await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids)))).scalars().all() if repo_ids else []
        total_loads_30d = sum(int(skill.load_count_30d or 0) for skill in skills)
        return build_memory_score_response(list(repos), list(skills), total_loads_30d)
    except Exception:
        await _rollback(db, "memory score lookup")
        return _error(400, "Could not load memory score", "MEMORY_SCORE_LOOKUP_FAILED")


@router.get("/{org_id}/settings", response_model=None)
async def get_org_settings(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object] | JSONResponse:
    """Return organization settings for the authenticated organization."""
    _assert_org_scope(org_id, current_org_id)
    try:
        org = await db.get(Org, org_id)
        if org is None:
            return _error(404, "Org not found", "ORG_NOT_FOUND")
        response = (await _load_org_settings(db, org)).model_dump()
        integration = _anthropic_settings_response(org).model_dump()
        response.update(integration)
        return response
    except Exception:
        await _rollback(db, "org settings lookup")
        return _error(400, "Could not load org settings", "ORG_SETTINGS_LOOKUP_FAILED")


@router.post("/{org_id}/settings/anthropic-key", response_model=OrgIntegrationSettingsResponse)
async def save_org_anthropic_key(
    org_id: str,
    payload: AnthropicKeyPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> OrgIntegrationSettingsResponse | JSONResponse:
    """Store an encrypted Anthropic key in org settings."""
    _assert_org_scope(org_id, current_org_id)
    try:
        org = await db.get(Org, org_id)
        if org is None:
            return _error(404, "Org not found", "ORG_NOT_FOUND")
        settings_payload = dict(org.settings or {})
        settings_payload["anthropic_api_key_encrypted"] = encrypt_key(payload.api_key)
        settings_payload["anthropic_api_key_hint"] = key_hint(payload.api_key)
        org.settings = settings_payload
        await db.commit()
        return _anthropic_settings_response(org)
    except Exception:
        await _rollback(db, "org anthropic key update")
        return _error(400, "Could not save Anthropic API key", "ANTHROPIC_KEY_UPDATE_FAILED")


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
        if "slack_standup_enabled" in fields and payload.slack_standup_enabled is not None:
            org.slack_standup_enabled = payload.slack_standup_enabled
        if "slack_standup_hour" in fields and payload.slack_standup_hour is not None:
            org.slack_standup_hour = payload.slack_standup_hour
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
