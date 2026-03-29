from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SkillSpec:
    path: str
    name: str
    domain: str
    sub_domain: str
    overview: str
    checks: list[str]
    patterns: list[tuple[str, list[str]]]
    how_to: list[str]
    references: list[str]


@dataclass(frozen=True)
class RequirementsContext:
    requirements_path: Path
    raw_text: str
    lines: list[str]
    domains: dict[str, bool]
    source_hash: str
    summary: list[str]


@dataclass(frozen=True)
class ProjectIntent:
    features: list[str]
    domain_concepts: list[str]
    entities: list[str]
    endpoints: list[str]
    ui_flows: list[str]


@dataclass(frozen=True)
class FeatureRecord:
    name: str
    domain: str
    location: str
    description: str
    status: str
    last_modified: str


@dataclass(frozen=True)
class FrameworkMatch:
    name: str
    confidence: float
    evidence: list[str]


@dataclass(frozen=True)
class FrameworkFingerprint:
    frontend: FrameworkMatch | None = None
    backend: FrameworkMatch | None = None
    test_framework: FrameworkMatch | None = None
    build_tool: FrameworkMatch | None = None


@dataclass(frozen=True)
class SkilgenConfig:
    include_paths: list[str]
    exclude_paths: list[str]
    domains_override: list[str]
    skill_depth: int
    update_trigger: str
    langsmith_project: str | None
    model_provider: str | None
    model: str | None
    api_key_env: str | None
    model_temperature: float | None = None
    model_max_tokens: int | None = None
    model_retry_attempts: int = 3
    model_retry_base_delay_seconds: float = 1.0
    auto_install_external_skills: bool = True
    external_skills_allowed_trust_levels: list[str] = field(default_factory=list)
    external_skills_allowlist: list[str] = field(default_factory=list)
    external_skills_denylist: list[str] = field(default_factory=list)
    external_skills_auto_activate: bool = True
    external_skills_policy_mode: str = "permissive"
    auto_activate_mcp_connectors: bool = True
    mcp_connectors_require_official_source: bool = True
    mcp_connectors_require_oauth: bool = True
    mcp_connector_allowlist: list[str] = field(default_factory=list)
    mcp_connector_denylist: list[str] = field(default_factory=list)
    enterprise_skill_paths: list[str] = field(default_factory=list)
    enterprise_skill_git_urls: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ModelSettings:
    provider: str | None
    model: str | None
    api_key_env: str | None
    api_key_present: bool
    temperature: float | None
    max_tokens: int | None
    retry_attempts: int
    retry_base_delay_seconds: float


@dataclass(frozen=True)
class PlanStep:
    phase: str
    title: str
    description: str
    status: str


@dataclass(frozen=True)
class RoadmapPlan:
    model: ModelSettings
    steps: list[PlanStep]


@dataclass(frozen=True)
class DomainRecord:
    name: str
    confidence: float
    key_files: list[str]
    key_patterns: list[str]
    sub_domains: list[str]


@dataclass(frozen=True)
class DomainGraphNode:
    name: str
    summary: str
    confidence: float
    key_files: list[str]
    key_patterns: list[str]
    parent_domain: str | None
    child_domains: list[str]
    related_domains: list[str]
    skill_path: str | None = None


@dataclass(frozen=True)
class DomainGraph:
    nodes: list[DomainGraphNode]
    recommendations: list[str]


@dataclass(frozen=True)
class SkillTreeNode:
    path: str
    domain: str
    parent_skill: str | None
    child_skills: list[str]
    cross_references: list[str]


@dataclass(frozen=True)
class CodebaseContext:
    project_root: Path
    file_tree: list[str]
    domain_graph: DomainGraph
    detected_domains: list[DomainRecord]
    dependency_map: dict[str, list[str]]
    framework_fingerprint: FrameworkFingerprint
    skill_tree: list[SkillTreeNode]


@dataclass(frozen=True)
class CodebaseSignals:
    backend_routes: list[str]
    frontend_routes: list[str]
    components: list[str]
    services: list[str]
    tests: list[str]
    data_models: list[str]
    persistence_layers: list[str]
    background_jobs: list[str]
    auth_files: list[str]
    state_files: list[str]
    design_system_files: list[str]


@dataclass
class DeliveryResult:
    generated_files: list[Path] = field(default_factory=list)
    test_command: str | None = None
    tests_passed: bool = False
    branch_name: str | None = None


@dataclass(frozen=True)
class FreshnessState:
    source_hashes: dict[str, str]
    requirements_source_hash: str
    domain_graph_nodes: list[dict[str, object]]
    top_level_domains: list[str]


@dataclass(frozen=True)
class FreshnessReport:
    changed_files: list[str]
    impacted_domains: list[str]
    stale_skill_paths: list[str]
    top_level_domains: list[str]
    reason: str


@dataclass(frozen=True)
class RunMemory:
    run_id: str
    status: str
    project_root: str
    requirements_path: str | None
    objective: str
    runtime: str
    impacted_domains: list[str]
    selected_domains: list[str]
    selected_skill_paths: list[str]
    changed_files: list[str]
    generated_files: list[str]
    active_file_focus: list[str]
    unresolved_questions: list[str]
    pending_validations: list[str]
    resumable_steps: list[str]
    recent_events: list[str]


@dataclass(frozen=True)
class AgentDecision:
    should_refresh: bool
    reason: str
    prioritized_domains: list[str]
    prioritized_skill_paths: list[str]
    memory_to_load: list[str]
    next_actions: list[str]
