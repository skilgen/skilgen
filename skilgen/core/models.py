from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

SourceConfigValue = bool | str | list[str]


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
class CorpusSettings:
    enabled: bool = True
    budget: int = 60
    hub_budget: int = 40
    cluster_budget: int = 10
    config_budget: int = 5
    doc_budget: int = 5
    exclude_generated: bool = True
    min_cluster_size: int = 3
    exclude_patterns: list[str] = field(default_factory=list)
    cache_path: str = ".skilgen/corpus/index.json"


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
    model_endpoint: str | None = None
    model_extra_kwargs: dict[str, object] = field(default_factory=dict)
    model_temperature: float | None = None
    model_max_tokens: int | None = None
    model_retry_attempts: int = 3
    model_retry_base_delay_seconds: float = 1.0
    model_timeout_seconds: float = 60.0
    model_redaction_mode: str = "balanced"
    redact_model_error_secrets: bool = True
    corpus: CorpusSettings = field(default_factory=CorpusSettings)
    sources: dict[str, SourceConfigValue] = field(default_factory=dict)
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
    mcp_policy_pack_path: str | None = None
    enterprise_skill_paths: list[str] = field(default_factory=list)
    enterprise_skill_git_urls: list[str] = field(default_factory=list)
    enterprise_skill_urls: list[str] = field(default_factory=list)
    runtime_retention_days: int = 30


@dataclass(frozen=True)
class ModelSettings:
    provider: str | None
    model: str | None
    api_key_env: str | None
    api_key_present: bool
    endpoint: str | None
    extra_kwargs: dict[str, object]
    temperature: float | None
    max_tokens: int | None
    retry_attempts: int
    retry_base_delay_seconds: float
    timeout_seconds: float
    redaction_mode: str
    redact_error_secrets: bool


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
class WorkspacePackage:
    id: str
    name: str
    root_path: str
    package_type: str | None
    manifest_paths: list[str]
    config_evidence: list[str]


@dataclass(frozen=True)
class WorkspaceDependency:
    source: str
    target: str
    evidence: list[str]


@dataclass(frozen=True)
class WorkspaceGraph:
    tool: str | None
    packages: list[WorkspacePackage]
    dependencies: list[WorkspaceDependency]
    entrypoints: list[str]
    confidence: float
    detection_evidence: list[str]


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
    workspace_graph: WorkspaceGraph = field(default_factory=lambda: WorkspaceGraph(None, [], [], [], 0.0, []))
    repo_archetype: str = "generic"


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
    legacy_programs: list[str] = field(default_factory=list)
    copybooks: list[str] = field(default_factory=list)
    language_inventory: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceItem:
    path: str
    kind: str
    language: str | None
    tags: list[str]
    snippet: list[str]
    related_imports: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SymbolRelationship:
    source_path: str
    source_symbol: str
    relationship: str
    target_symbol: str
    target_path: str | None
    confidence: float


@dataclass(frozen=True)
class RuntimeSignalArtifact:
    path: str
    kind: str
    format: str
    signal_count: int
    related_paths: list[str]
    summary: str


@dataclass(frozen=True)
class RuntimeSignals:
    artifacts: list[RuntimeSignalArtifact] = field(default_factory=list)
    coverage_by_path: dict[str, float] = field(default_factory=dict)
    test_results: dict[str, dict[str, object]] = field(default_factory=dict)
    sast_findings: dict[str, list[str]] = field(default_factory=dict)
    trace_services: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DependencyRiskNode:
    id: str
    kind: str
    risk_score: float
    signals: list[str]
    dependencies: list[str]


@dataclass(frozen=True)
class DependencyRiskEdge:
    source: str
    target: str
    kind: str
    risk_signals: list[str]


@dataclass(frozen=True)
class DependencyRiskGraph:
    nodes: list[DependencyRiskNode] = field(default_factory=list)
    edges: list[DependencyRiskEdge] = field(default_factory=list)
    cycles: list[list[str]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DependencyFinding:
    name: str
    version: str | None
    ecosystem: str
    manifest_path: str
    risk_level: str
    cves: list[str]
    latest_version: str | None
    license: str | None
    signals: list[str]
    upgrade_command: str | None


@dataclass(frozen=True)
class DependencyRiskReport:
    dependencies: list[DependencyFinding]
    high_risk: list[DependencyFinding]
    medium_risk: list[DependencyFinding]
    healthy: list[DependencyFinding]
    total_count: int
    risk_score: int
    recommendations: list[str]


@dataclass(frozen=True)
class EvidenceGraph:
    language_inventory: dict[str, int]
    dominant_languages: list[str]
    import_graph: dict[str, list[str]]
    items: list[EvidenceItem]
    recommendations: list[str]
    parser_summary: dict[str, dict[str, object]] = field(default_factory=dict)
    symbol_graph: dict[str, list[str]] = field(default_factory=dict)
    call_graph: dict[str, list[str]] = field(default_factory=dict)
    config_runtime_graph: dict[str, list[str]] = field(default_factory=dict)
    test_mapping: dict[str, list[str]] = field(default_factory=dict)
    workspace_graph: WorkspaceGraph = field(default_factory=lambda: WorkspaceGraph(None, [], [], [], 0.0, []))
    symbol_relationships: list[SymbolRelationship] = field(default_factory=list)
    runtime_signals: RuntimeSignals = field(default_factory=RuntimeSignals)
    dependency_risk_graph: DependencyRiskGraph = field(default_factory=DependencyRiskGraph)


@dataclass(frozen=True)
class ArchitectureDomain:
    name: str
    summary: str
    confidence: float
    responsibilities: list[str]
    evidence_paths: list[str]
    related_domains: list[str]
    recommended_skill_path: str | None = None


@dataclass(frozen=True)
class SkillMaterializationPlan:
    domain: str
    parent_skill_path: str | None
    child_skill_paths: list[str]
    cross_links: list[str]
    decision: str
    rationale: str


@dataclass(frozen=True)
class ArchitectureBlueprint:
    headline: str
    system_summary: str
    domains: list[ArchitectureDomain]
    hotspots: list[str]
    recommendations: list[str]
    materialization_plan: list[SkillMaterializationPlan] = field(default_factory=list)


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
