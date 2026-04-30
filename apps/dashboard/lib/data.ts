import "server-only";

export const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

export type Score = {
  total: number;
  groundedness: number;
  coverage: number;
  freshness: number;
  structure: number;
};

export type Org = {
  id: string;
  login: string;
  name: string;
  plan: string;
};

export type BootstrapOrg = Org;

export type OrgSettings = {
  id: string;
  login: string;
  name: string;
  plan: string;
  score_threshold: number;
  slack_webhook_url: string | null;
  slack_signing_secret_set?: boolean;
  slack_team_id?: string | null;
  slack_standup_enabled?: boolean;
  slack_standup_hour?: number;
  digest_email?: string | null;
  digest_enabled?: boolean;
  digest_day?: number;
  digest_hour?: number;
  digest_last_sent_at?: string | null;
  notify_on_pr: boolean;
  notify_on_stale: boolean;
  github_app_installed: boolean;
  github_installation_id: number | null;
  webhook_url: string;
  anthropic_api_key_set?: boolean;
  recent_deliveries: {
    id: string;
    status: string;
    trigger: string;
    created_at: string | null;
  }[];
};

export type EmailDigestSettings = {
  digest_email: string | null;
  digest_enabled: boolean;
  digest_day: number;
  digest_hour: number;
  digest_last_sent_at?: string | null;
};

export type OrgAISettings = {
  anthropic_api_key_set: boolean;
};

export type OrgStats = {
  repo_count: number;
  avg_score: number;
  skill_count: number;
  active_agents: number;
  score_trend: { date: string; score: number }[];
};

export type OverviewScoreTrendPoint = {
  week: string;
  date: string;
  score: number;
  delta: number;
  repos_changed: number;
  events: Array<{
    repo_id: string;
    repo_name: string;
    score: number;
    date: string;
  }>;
};

export type MemoryScore = {
  score: number;
  breakdown: {
    coverage: number;
    load_frequency: number;
    compliance: number;
    quality?: number;
    freshness: number;
  };
  trend_7d: number;
  trend_30d: number;
  computed_at: string;
  trend?: string | null;
  grade: "A" | "B" | "C" | "D" | "F";
};

export type AgentName = "claude_code" | "codex" | "cursor" | "copilot" | "devin" | "human" | "mixed" | string;

export type AdminOverview = {
  orgs: { total: number; active_30d: number; suspended: number; by_plan: Record<string, number> };
  users: { total_unique: number; logins_7d: number; logins_30d: number; most_active: Array<{ login: string; count: number }> };
  data: Record<string, number>;
  generated_at: string;
};

export type AdminOrg = {
  id: string;
  name: string;
  login?: string;
  plan: string;
  is_suspended: boolean;
  suspended_at?: string | null;
  suspended_reason?: string | null;
  created_at: string | null;
  last_active_at: string | null;
  user_count: number;
  login_count: number;
  last_login_at: string | null;
  skill_count: number;
  session_count: number;
  pr_count: number;
  analysis_run_count: number;
  repo_count: number;
  api_key_hint?: string | null;
};

export type AdminOrgDetail = AdminOrg & {
  repos: Array<{ id: string; full_name: string; skill_count: number; last_analysed_at: string | null; is_active?: boolean }>;
  recent_sessions: Array<{ id: string; engineer_login: string | null; agent_runtime: string; session_start: string | null; files_touched_count: number; outcome?: string | null }>;
  sessions?: Array<{ id: string; engineer_login: string | null; agent_runtime: string; session_start: string | null; files_touched_count: number; outcome?: string | null }>;
  recent_logins: Array<{ user_login: string | null; user_email: string | null; ip_address: string | null; user_agent?: string | null; created_at: string | null }>;
  skills_by_category: Record<string, number>;
  violations_30d: number;
  risk_distribution: { red: number; yellow: number; green: number };
};

export type AdminUser = {
  user_login: string;
  user_email: string | null;
  orgs: Array<{ org_id: string; org_name: string }>;
  login_count: number;
  last_login_at: string | null;
  first_login_at: string | null;
  sessions_count: number;
  prs_count: number;
};

export type AdminLoginEvent = {
  id: string;
  org_id: string | null;
  org_name: string | null;
  user_login: string | null;
  user_email: string | null;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string | null;
};

export type UsageSeries = {
  days: number;
  series: Array<{ date: string; agent_sessions: number; prs_opened: number; logins: number; analysis_runs: number; violations: number }>;
};

export type AgentPrCard = {
  pr_id: string;
  repo_id: string;
  repo_name: string;
  github_pr_number: number;
  title: string;
  url: string | null;
  author_login: string | null;
  primary_agent: AgentName;
  confidence: number;
  lines_by_agent: Record<string, number>;
  additions: number;
  deletions: number;
  changed_files: number;
  skills_loaded: string[];
  violation_count: number;
  warning_count: number;
  risk_score: number;
  risk_tier: "green" | "yellow" | "red" | string;
  ci_status: string;
  opened_at: string | null;
  merged_at: string | null;
  session_ids: string[];
};

export type AgentPrListResponse = {
  items: AgentPrCard[];
  next_cursor: string | null;
  total_count: number;
};

export type AgentPrDetail = AgentPrCard & {
  attribution: {
    id: string;
    primary_agent: AgentName;
    confidence: number;
    lines_by_agent: Record<string, number>;
    lines_by_human: number;
    sessions: string[];
    skills_loaded: string[];
    skills_violated: Array<Record<string, unknown>>;
    computed_at: string | null;
  } | null;
  risk_breakdown: Record<string, { points?: number; explanation?: string }>;
  violations: Array<{
    file: string;
    line: number | null;
    skill_name: string;
    severity: string;
    explanation: string;
    fix_suggestion: string | null;
    skill_url: string;
  }>;
  sessions: Array<{
    id: string;
    agent_runtime: string;
    started_at: string | null;
    skills_loaded: string[];
    replay_url: string;
  }>;
  checks: Array<{ name: string; status: string; conclusion: string | null; details_url: string | null }>;
};

export type AgentPrManifestResponse = {
  manifest: Record<string, unknown>;
  signed_at: string | null;
};

export type MyCodeTodayPR = {
  id: string;
  github_pr_number: number;
  title: string;
  state: string | null;
  risk_tier: "green" | "yellow" | "red" | string;
};

export type MyCodeTodaySession = {
  session_id: string;
  agent_runtime: string;
  started_at: string;
  ended_at: string | null;
  files_touched: string[];
  skills_loaded: string[];
  outcome: string | null;
  pr: MyCodeTodayPR | null;
};

export type MyCodeTodayResponse = {
  date: string;
  login: string;
  sessions: MyCodeTodaySession[];
  prs?: MyCodeTodayPR[];
  summary: {
    total_sessions: number;
    total_files: number;
    skills_used: string[];
    prs_opened: number;
    prs_merged: number;
    violations: number;
    warnings: number;
  };
};

export type AgentScorecardRow = {
  agent: AgentName;
  agent_label?: string | null;
  prs: number;
  merged: number;
  violations: number;
  compliance_percent: number;
  avg_risk: number;
  risk_distribution: {
    green: number;
    yellow: number;
    red: number;
  };
  top_skills: string[];
  top_violations: string[];
};

export type AgentScorecardSummary = {
  total_prs: number;
  total_merged: number;
  total_violations: number;
  avg_compliance_percent: number;
  avg_risk: number;
};

export type AgentScorecardResponse = {
  days: number;
  generated_at: string | null;
  summary: AgentScorecardSummary;
  agents: AgentScorecardRow[];
};

export type DeveloperLeaderboardEntry = {
  login: string;
  rank: number;
  sessions_count: number;
  files_touched: number;
  lines_changed: number;
  prs_opened: number;
  prs_merged: number;
  prs_reverted: number;
  agent_runtimes: string[];
  skills_loaded: string[];
  violations_total: number;
  warnings_total: number;
  compliance_pct: number;
  avg_risk_score: number;
  risk_distribution: { red: number; yellow: number; green: number };
  top_violations: string[];
  last_active: string | null;
  trend?: {
    compliance_delta: number;
    violations_delta: number;
    direction: "up" | "down" | "flat";
  } | null;
  sparkline?: Array<number | null>;
};

export type DeveloperLeaderboardResponse = {
  window_days: number;
  generated_at: string;
  developers: DeveloperLeaderboardEntry[];
};

export type SkillQLResultFormat = "table" | "number" | "list" | "timeline";

export type SkillQLResult = {
  query: string;
  intent: string;
  result_format: SkillQLResultFormat;
  columns: string[];
  rows: Array<Record<string, unknown>>;
  row_count: number;
  data_sources: string[];
  suggested_followups: string[];
};

export type SkillQLSuggestions = Record<string, string[]>;

export type SetupStep = {
  id: "connect_repo" | "generate_skills" | "connect_agent" | "improve_skills" | string;
  title: string;
  done: boolean;
  action_url?: string | null;
  description?: string | null;
  cli_command?: string | null;
};

export type SetupStatus = {
  has_repos: boolean;
  has_skills: boolean;
  has_agent_loads: boolean;
  has_high_score_skills: boolean;
  setup_steps: SetupStep[];
  completion_percent: number;
};

export type OrgApiKey = {
  api_key: string;
};

export type ActionItem = {
  id: string;
  type: "improve" | "generate" | "refresh" | "review" | string;
  title: string;
  description: string;
  action_url: string;
  priority: "urgent" | "recommended" | "suggested" | string;
};

export type ActionItemsResponse = {
  items: ActionItem[];
};

export type SkillHeatmapSkill = {
  skill_id: string;
  domain: string;
  repo_id: string;
  repo_name: string;
  skill_category: string | null;
  source_type: string | null;
  score_total: number;
  is_stale: boolean;
  loads_30d: number;
  loads_7d: number;
  criticality_score: number;
  last_loaded_at: string | null;
  agent_runtimes: string[];
  alert: "stale_but_active" | "dead_skill" | "healthy";
};

export type SkillHeatmapSummary = {
  total_skills: number;
  dead_skills: number;
  stale_but_active: number;
  healthy: number;
  avg_criticality: number;
};

export type SkillHeatmapResponse = {
  skills: SkillHeatmapSkill[];
  summary: SkillHeatmapSummary;
};

export type SourceConnection = {
  id: string;
  source_type: string;
  display_name: string;
  repo_id?: string | null;
  connected: boolean;
  skill_count: number;
  last_skill_generated_at: string | null;
  can_generate_skills: boolean;
  generate_command: string | null;
  coverage_domains: string[];
};

export type OrgSessionSkill = {
  domain: string;
  score: number;
  loaded_at: string;
};

export type OrgSessionItem = {
  session_id: string;
  agent_runtime: string;
  agent_display_name?: string;
  repo_id: string;
  repo_name: string;
  started_at: string;
  ended_at: string;
  duration_minutes: number;
  skills_loaded: OrgSessionSkill[];
  skill_count: number;
  session_context: string;
  quality_signal: "strong" | "mixed" | "weak";
  avg_skill_score: number;
};

export type OrgSessionsResponse = {
  sessions: OrgSessionItem[];
  total: number;
};

export type IntelligenceInsight = {
  type: "anomaly" | "opportunity" | "trend" | "gap";
  title: string;
  description: string;
  cta_label: string | null;
  cta_url: string | null;
  severity: "high" | "medium" | "low";
};

export type RuntimeBreakdownItem = {
  runtime: string;
  display_name: string;
  loads_30d: number;
  unique_skills: number;
  top_skill_domain: string | null;
  unique_domains: number;
  avg_skill_score: number;
  top_domains: string[];
  knowledge_breadth_score: number;
  most_recent_load: string | null;
  pattern: string;
};

export type RuntimeBreakdownResponse = {
  runtimes: RuntimeBreakdownItem[];
  total_loads_30d: number;
};

export type TeamRollupRepo = {
  id: string;
  name: string;
  score: number | null;
};

export type TeamRollupTeam = {
  team_name: string;
  repo_count: number;
  avg_score: number | null;
  worst_repo: TeamRollupRepo | null;
  best_repo: TeamRollupRepo | null;
  score_delta_7d: number | null;
  skill_count: number;
  coverage_score: number;
  repos: TeamRollupRepo[];
};

export type TeamRollupResponse = {
  teams: TeamRollupTeam[];
  org_avg_score: number | null;
  top_team: string | null;
  needs_attention: string | null;
};

export type OrgRepoSummary = {
  id: string;
  name: string;
  score: number;
  score_trend: number | null;
  skill_count: number;
  dead_skill_count: number;
  stale_skill_count: number;
  last_analysed_at: string | null;
  dormant: boolean;
};

export type CategoryMatrixEntry = {
  repo_id: string;
  repo_name: string;
  covered: boolean;
  avg_score: number;
  skill_count: number;
};

export type StaleAlert = {
  skill_id: string;
  repo_id: string;
  repo_name: string;
  domain: string;
  skill_path: string;
  alert_type: "dead" | "stale_but_active" | "dormant_repo";
  last_loaded_at: string | null;
  loads_30d: number;
};

export type TopSkill = {
  skill_id: string;
  repo_id: string;
  repo_name: string;
  domain: string;
  loads_30d: number;
  score: number;
};

export type OrgIntelligence = {
  org_health_score: number;
  org_health_trend: number | null;
  total_repos: number;
  total_skills: number;
  total_loads_30d: number;
  repos: OrgRepoSummary[];
  category_matrix: Record<string, CategoryMatrixEntry[]>;
  stale_alerts: StaleAlert[];
  top_skills: TopSkill[];
};

export type IntelligenceBehaviorBar = {
  label: string;
  value: number;
  total?: number | null;
  tone?: "good" | "warning" | "danger" | "neutral" | string;
};

export type IntelligenceRepoRing = {
  repo_id: string;
  repo_name: string;
  score: number;
  label?: string | null;
  href?: string | null;
};

export type DiscoveryType =
  | "undocumented_pattern"
  | "workaround"
  | "architectural_insight"
  | "gotcha"
  | "dependency_insight"
  | "contradiction";

export type MemoryStub = {
  id: string;
  repo_id: string;
  repo_name: string;
  domain: string;
  skill_id: string | null;
  discovery_type: DiscoveryType;
  title: string;
  proposed_content: string;
  evidence: string | null;
  confidence: number;
  agent_runtime: string;
  engineer_login: string | null;
  task_description: string | null;
  status: "pending" | "approved" | "rejected" | "merged";
  reviewer_note: string | null;
  merged_version_number: number | null;
  created_at: string;
  reviewed_at: string | null;
  session_created_at: string;
  existing_skill_content: string | null;
};

export type MemoryQueueResponse = {
  total: number;
  pending_count: number;
  items: MemoryStub[];
};

export type KnowledgeVelocityWeek = {
  week_start: string;
  discovered: number;
  approved: number;
};

export type KnowledgeVelocity = {
  weekly: KnowledgeVelocityWeek[];
  total_discoveries_all_time: number;
  approval_rate: number | null;
};

export type RedFlagType =
  | "stale_but_active"
  | "dead_high_quality"
  | "conflict"
  | "missing_security"
  | "freshness_critical";

export type RedFlag = {
  flag_type: RedFlagType;
  severity: "critical" | "high" | "medium";
  repo_id: string;
  repo_name: string;
  skill_id: string | null;
  domain: string | null;
  title: string;
  description: string;
  loads_30d: number;
  action: string;
  action_url: string | null;
};

export type OrgRedFlags = {
  critical_count: number;
  high_count: number;
  medium_count: number;
  flags: RedFlag[];
};

export type RedFlagDismissal = {
  id: string;
  org_id: string;
  flag_type: string;
  repo_id: string;
  skill_id: string | null;
  dismissed_by: string | null;
  reason: string;
  dismissed_at: string;
};

export type AutopilotTask = {
  id: string;
  org_id: string;
  repo_id: string;
  repo_name?: string | null;
  skill_id: string | null;
  skill_name?: string | null;
  skill_domain?: string | null;
  skill_path?: string | null;
  task_type: "regenerate" | "archive" | "notify" | string;
  trigger_reason: string;
  freshness_at_trigger: number;
  status: "pending" | "approved" | "skipped" | "done" | string;
  improvement_status?: "generated" | "approved" | "rejected" | "failed" | string | null;
  original_content?: string | null;
  generated_content?: string | null;
  final_content?: string | null;
  generation_error?: string | null;
  pr_url?: string | null;
  pr_number?: number | null;
  generated_at?: string | null;
  reviewed_at?: string | null;
  created_at: string;
  resolved_at: string | null;
};

export type AuditLogEvent = {
  id: string;
  event_type: string;
  action: string;
  actor_login: string | null;
  repo_name: string | null;
  repo_id: string | null;
  skill_id: string | null;
  skill_domain: string | null;
  resource_type: string | null;
  resource_id: string | null;
  summary: string;
  severity: "info" | "warning" | "critical";
  metadata: Record<string, unknown>;
  created_at: string;
};

export type AuditLogResponse = {
  total: number;
  events: AuditLogEvent[];
  has_more: boolean;
  next_cursor: string | null;
};

export type AuditLogStats = {
  total_events: number;
  by_severity: Record<string, number>;
  by_resource_type: Record<string, number>;
  most_active_actor: string | null;
  critical_events_7d: number;
  analysis_runs_30d: number;
  gate_failures_30d: number;
  gate_pass_rate: number | null;
};

export type GovernancePolicy = {
  id: string;
  name: string;
  type: "min_score" | "max_staleness_days" | "required_categories" | "min_groundedness";
  threshold: number | string[] | null;
  scope: string;
  action: "warn" | "block_pr" | "notify_slack";
  enabled: boolean;
  created_at?: string | null;
};

export type GovernancePoliciesResponse = {
  policies: GovernancePolicy[];
};

export type PolicyRule = {
  id: string;
  name: string;
  description: string | null;
  rule_type: string;
  rule_config: Record<string, unknown>;
  severity: "error" | "warning";
  enabled: boolean;
  created_at: string;
  violation_count: number;
};

export type PolicyViolation = {
  policy_id: string;
  policy_name: string;
  rule_type: string;
  severity: "error" | "warning";
  repo_id: string | null;
  repo_name: string | null;
  skill_id: string | null;
  skill_domain: string | null;
  description: string;
  fix_url: string | null;
};

export type PolicyCheckResult = {
  passed: boolean;
  error_count: number;
  warning_count: number;
  violations: PolicyViolation[];
  checked_at: string;
};

export type LLMConfig = {
  provider: string | null;
  model: string | null;
  base_url: string | null;
  api_key_hint: string | null;
  is_configured: boolean;
};

export type SkillUsageDailyLoad = {
  date: string;
  loads: number;
};

export type SkillUsageStats = {
  criticality_score: number;
  loads_30d: number;
  loads_7d: number;
  last_loaded_at: string | null;
  alert: "stale_but_active" | "dead_skill" | "healthy" | string;
  daily_loads: SkillUsageDailyLoad[];
  agent_runtimes: Record<string, number>;
};

export type Repo = {
  id: string;
  name: string;
  full_name: string;
  installation_id: number | null;
  language: string | null;
  languages?: string[];
  display_language?: string;
  is_monorepo?: boolean;
  last_analysed_at: string | null;
  score: Score | null;
  skill_count: number;
  score_delta: number | null;
};

export type Skill = {
  id: string;
  repo_id: string;
  repo_name: string;
  domain: string;
  skill_path: string;
  score: Score;
  content: string | null;
  content_hash: string | null;
  source_type: string | null;
  skill_category: string | null;
  is_stale: boolean;
  load_count_30d: number;
  last_loaded_at: string | null;
  version_count: number;
  latest_version_number: number | null;
};

export type SkillCategory =
  | "codebase_architecture"
  | "code_style"
  | "testing_conventions"
  | "internal_tools"
  | "security_compliance"
  | "design_system"
  | "data_schema"
  | "operational_knowledge";

export type CategoryCoverage = {
  covered: boolean;
  skill_count: number;
  avg_score: number | null;
};

export type SkillSourceEntry = {
  source_type: string;
  skill_category: string;
  skill_count: number;
  avg_score: number | null;
  last_analysed_at: string | null;
};

export type RepoSkillSources = {
  sources: SkillSourceEntry[];
  coverage_map: Record<string, CategoryCoverage>;
  coverage_score: number;
};

export type SkillCategoryCoverage = CategoryCoverage;
export type RepoSkillSource = SkillSourceEntry;

export type RepoCoverageSummary = {
  repo_id: string;
  name: string;
  coverage_score: number;
  missing_categories: SkillCategory[];
};

export type OrgCoverageSummary = {
  repos: RepoCoverageSummary[];
  org_coverage_score: number;
  most_missing_category: SkillCategory | null;
};

export type SkillVersionSummary = {
  id: string;
  version_number: number;
  is_latest: boolean;
  content_hash: string;
  created_at: string;
  run_id: string;
};

export type SkillVersion = {
  id: string;
  version_number: number;
  content: string;
  content_hash: string;
  created_at: string;
  is_latest: boolean;
};

export type SkillVersionDiff = {
  skill_id: string;
  repo_id: string;
  domain: string;
  version_id: string;
  version_number: number;
  prev_version_number: number | null;
  is_first_version: boolean;
  lines: Array<{
    type: "meta" | "added" | "removed" | "context";
    text: string;
  }>;
  added_count: number;
  removed_count: number;
};

export type SkillSnapshot = {
  id: string;
  skill_id: string;
  repo_id: string;
  snapshot_type: "auto" | "manual" | "pre_edit" | string;
  label: string | null;
  content?: string;
  score_total: number | null;
  score_groundedness: number | null;
  score_coverage: number | null;
  score_freshness: number | null;
  score_structure: number | null;
  created_by: string | null;
  created_at: string | null;
};

export type SkillRollbackResult = {
  ok: boolean;
  snapshot_id: string;
  pre_edit_snapshot_id: string;
};

export type SkillContentUpdateResult = {
  updated: boolean;
  version_number: number;
  score: Score;
};

export type EvalBucket = {
  bucket: string;
  task_count: number;
  success_rate: number | null;
};

export type EvalRuntimeRow = {
  runtime: string;
  task_count: number;
  success_rate: number | null;
  avg_token_count: number | null;
  best_domain?: string | null;
};

export type EvalTrendPoint = {
  week: string;
  success_rate: number | null;
  avg_skill_score: number | null;
};

export type EvalSkillGap = {
  id: string;
  repo_id: string;
  repo_name: string;
  domain: string;
  gap_type: "missing_skill" | "low_quality" | "stale" | "never_loaded" | "implied_need";
  severity: "critical" | "high" | "medium";
  current_score: number | null;
  evidence: string;
  recommendation: string;
  fix_command: string | null;
  estimated_impact: string;
  status: "open" | "acknowledged" | "resolved";
  failure_count?: number;
  existing_skill_id?: string | null;
  existing_skill_score?: number | null;
  existing_score?: number | null;
  suggested_action?: string;
  detected_at?: string;
  task_ids?: string[];
  failed_tasks?: Array<{ id: string; description: string | null; outcome: string; failure_reason: string | null; started_at: string }>;
};

export type EvalSkillGapsResponse = {
  total_gaps: number;
  critical_gap_count: number;
  high_gap_count: number;
  medium_gap_count: number;
  checked_repos: number;
  checked_skills: number;
  checked_domains: number;
  last_scan: string;
  gaps: EvalSkillGap[];
};

export type EvalSummary = {
  total_sessions: number;
  strong_sessions: number;
  mixed_sessions: number;
  weak_sessions: number;
  strong_pct: number;
  top_skill_impact: Array<{
    domain: string;
    load_count: number;
    avg_score: number;
    strong_appearances: number;
    weak_appearances: number;
    impact_label: string;
  }>;
  weekly_trend: Array<{ week: string; sessions: number; avg_quality: number; strong_pct: number; weak_pct: number }>;
  insight: string;
};

export type EvalSessionQuality = {
  session_id: string;
  agent_runtime: string;
  agent_display_name?: string;
  repo_id: string;
  repo_name: string;
  started_at: string;
  duration_seconds: number | null;
  skills_loaded: string[];
  avg_skill_quality: number;
  quality_signal: "strong" | "mixed" | "weak";
  session_context: string;
  outcome: "success" | "needs_rework" | "unknown";
};

export type EvalSessionsResponse = {
  total: number;
  sessions: EvalSessionQuality[];
};

export type CriticalityItem = {
  skill_id: string;
  domain: string;
  repo_id: string;
  repo_name: string;
  load_count_30d: number;
  score_total: number;
  risk_level: "critical" | "high" | "medium" | "low";
  risk_reason: string;
  dependency_rank: number;
  is_every_session: boolean;
  last_loaded_at: string | null;
};

export type EvalROI = {
  total_tasks: number;
  success_rate: number | null;
  multiplier: number | null;
  high_skill_success_rate: number | null;
  low_skill_success_rate: number | null;
  by_skill_score_bucket: EvalBucket[];
  by_agent_runtime: EvalRuntimeRow[];
  skill_gaps: EvalSkillGap[];
  trend: EvalTrendPoint[];
  benchmark: Record<string, unknown>;
};

export type ABTest = {
  id: string;
  skill_id: string;
  skill_name?: string;
  repo_name?: string;
  name: string;
  status: string;
  winner: string | null;
  control_success_rate: number | null;
  treatment_success_rate: number | null;
  improvement_pct: number | null;
  confidence: string | null;
  recommendation: string | null;
  control_task_count?: number;
  treatment_task_count?: number;
  control_session_id?: string | null;
  treatment_session_id?: string | null;
  created_at: string;
  completed_at: string | null;
};

export type ScoreHistoryPoint = {
  date: string;
  score_total: number;
  groundedness: number;
  coverage: number;
  freshness: number;
  structure: number;
};

export type Dependency = {
  id: string;
  name: string;
  version: string | null;
  ecosystem: string;
  risk_level: "high" | "medium" | "low" | "healthy";
  cves: string[];
  latest_version: string | null;
  license: string | null;
  created_at: string;
  upgrade_command: string | null;
};

export type DependencyReport = {
  high_risk: Dependency[];
  medium_risk: Dependency[];
  healthy: Dependency[];
  total_count: number;
  risk_score: number;
};

export type ScoreForecast = {
  has_forecast: boolean;
  reason: string | null;
  current_score: number | null;
  forecast_30d: number | null;
  forecast_90d: number | null;
  trend: "improving" | "declining" | "stable";
  slope_per_day?: number;
  data_points?: number;
};

export type SkillDebtSkill = {
  id: string;
  domain: string;
  repo_id: string;
  score_total: number;
  score_groundedness?: number | null;
  score_coverage?: number | null;
  score_freshness?: number | null;
  score_structure?: number | null;
  is_stale: boolean;
  load_count_30d: number;
};

export type SkillDebtResponse = {
  debt_score: number;
  health_score?: number;
  estimated_if_fixed?: number;
  total_skills: number;
  stale_skills: SkillDebtSkill[];
  low_score_skills: SkillDebtSkill[];
  never_loaded_skills: SkillDebtSkill[];
  zero_subscore_skills: SkillDebtSkill[];
  repo_coverage_gaps: Array<{
    repo_id: string;
    repo_name: string;
    last_debt_analysis_at?: string | null;
    covered_categories: string[];
    missing_categories: string[];
    gaps?: Array<{ gap_id: string; domain: string; gap_type: string; status: string; skill_id?: string | null }>;
    coverage_score: number;
  }>;
  summary: {
    stale_count: number;
    low_score_count: number;
    never_loaded_count: number;
    zero_subscore_count: number;
    repos_with_gaps: number;
    last_debt_analysis_at?: string | null;
  };
};

export type AnalyticsSkill = {
  id: string;
  domain: string;
  skill_path: string;
  repo_id: string;
  repo_name: string;
  repo_full_name: string;
  loads?: number;
  last_loaded_at?: string | null;
};

export type OrgAnalytics = {
  total_loads_30d: number;
  unique_skills_loaded: number;
  total_skills: number;
  top_skills: AnalyticsSkill[];
  never_loaded: AnalyticsSkill[];
  agent_breakdown: Record<string, number>;
  daily_loads: { date: string; loads: number }[];
  most_active_repo: { id: string; name: string; full_name: string; loads: number } | null;
  most_loaded_skill: AnalyticsSkill | null;
};

export type RegistrySkill = {
  id: string;
  org_id: string;
  repo_id: string;
  skill_id: string;
  domain: string;
  name: string;
  description: string;
  is_public: boolean;
  is_official: boolean;
  import_count: number;
  tags: string[];
  created_at: string;
  score_total: number;
};

export type SkillRegistryEntry = {
  id: string;
  name: string;
  domain: string;
  version: string;
  visibility: "private" | "org" | "public" | string;
  tags: string[];
  description: string;
  publisher_login: string;
  compatible_runtimes: string[];
  install_count: number;
  score_total: number;
  score_groundedness: number;
  score_coverage: number;
  score_freshness: number;
  score_structure: number;
  is_verified: boolean;
  is_deprecated: boolean;
  deprecation_message: string | null;
  successor_entry_id: string | null;
  content_preview: string | null;
  predicted_decay_date: string | null;
  predicted_decay_days: number | null;
  decay_confidence: number | null;
  regen_queued: boolean;
  created_at: string;
  updated_at: string;
};

export type RegistryEntriesResponse = {
  entries: SkillRegistryEntry[];
  total: number;
  page: number;
  page_size: number;
};

export type HalfLifeSummary = {
  critical: HalfLifeSkill[];
  warning: HalfLifeSkill[];
  healthy: HalfLifeSkill[];
  total_skills: number;
  regen_queued_count: number;
};

export type HalfLifeSkill = {
  skill_id: string;
  name: string;
  domain: string;
  repo_id: string;
  repo_name: string;
  freshness: number;
  commits_30d: number;
  predicted_decay_date: string | null;
  predicted_decay_days: number;
  decay_confidence: number;
  regen_queued: boolean;
};

export type DependencyGraph = {
  nodes: { skill_id: string; name: string; domain: string; repo_id: string; repo_name: string; score_total: number }[];
  edges: { source_skill_id: string; target_entry_id: string; target_name: string }[];
  stale_upstream_count: number;
};

export type DependencyGraphCache = {
  nodes: Array<Record<string, unknown>>;
  edges: Array<Record<string, unknown>>;
  opportunities: Array<Record<string, unknown>>;
  computed_at: string | null;
};

export type CompatibilityMatrix = {
  skills: { skill_id: string; name: string; domain: string }[];
  runtimes: string[];
  matrix: Record<string, Record<string, "compatible" | "untested" | "incompatible" | string>>;
};

export type RepoSnapshot = {
  id: string;
  captured_at: string;
  label: string;
  summary: string;
  score_total: number;
  skill_count: number;
  changed_paths: string[];
  content_preview: string;
  diff_to_now: { added: number; removed: number; summary: string };
};

export type KnowledgeRiskItem = {
  risk_type: string;
  risk_level: "critical" | "high" | "medium" | string;
  repo_id: string;
  repo_name: string;
  domain: string;
  reason: string;
  recommendation: string;
  affected_files: string[];
  skill_exists: boolean;
  skill_id: string | null;
};

export type KnowledgeRiskResponse = {
  critical_count: number;
  high_count: number;
  medium_count: number;
  risks: KnowledgeRiskItem[];
};

export type SLAPolicy = {
  id: string;
  org_id: string;
  repo_id: string | null;
  repo_name: string | null;
  name: string;
  coverage_target_pct: number;
  alert_email: string | null;
  is_active: boolean;
  created_at: string;
  last_checked_at: string | null;
  last_status: "compliant" | "breaching" | "unknown" | string;
};

export type RegistryList = {
  skills: RegistrySkill[];
  total: number;
  limit: number;
  offset: number;
};

export type RegistrySkillDetail = RegistrySkill & {
  content: string;
  content_hash: string | null;
  skill_path: string | null;
  repo_name: string;
  repo_full_name: string;
};

type FetchOptions = {
  accessToken?: string | null;
  cache?: RequestCache;
  revalidate?: number | false;
  method?: string;
  body?: BodyInit | null;
  headers?: HeadersInit;
};

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T | null> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (options.headers) {
    Object.assign(headers, options.headers as Record<string, string>);
  }
  if (options.accessToken) {
    headers.Authorization = `Bearer ${options.accessToken}`;
  }

  try {
    const res = await fetch(`${API_URL}${path}`, {
      method: options.method ?? "GET",
      body: options.body,
      headers,
      ...(options.cache ? { cache: options.cache } : {}),
      ...(typeof options.revalidate === "number" ? { next: { revalidate: options.revalidate } } : {}),
      ...(options.revalidate === false ? { cache: "no-store" } : {}),
    });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    console.error(`Failed to fetch ${path}:`, error);
    return null;
  }
}

export async function getMyOrg(accessToken: string | null): Promise<Org | null> {
  return apiFetch<Org>("/me/org", { accessToken, cache: "no-store" });
}

export async function getBootstrapOrg(): Promise<BootstrapOrg | null> {
  return apiFetch<BootstrapOrg>("/orgs/bootstrap", { cache: "no-store" });
}

export async function getOrgStats(accessToken: string | null, orgId: string): Promise<OrgStats | null> {
  return apiFetch<OrgStats>(`/orgs/${orgId}/stats`, { accessToken, cache: "no-store" });
}

export async function getOverviewScoreTrend(accessToken: string | null, orgId: string, weeks = 30): Promise<OverviewScoreTrendPoint[] | null> {
  return apiFetch<OverviewScoreTrendPoint[]>(`/orgs/${orgId}/overview/score-trend?weeks=${weeks}`, { accessToken, cache: "no-store" });
}

export async function getOrgSetupStatus(accessToken: string | null, orgId: string, revalidate?: number): Promise<SetupStatus | null> {
  return apiFetch<SetupStatus>(`/orgs/${orgId}/setup-status`, { accessToken, ...(revalidate ? { revalidate } : { cache: "no-store" }) });
}

export async function getOrgApiKey(accessToken: string | null, orgId: string): Promise<OrgApiKey | null> {
  return apiFetch<OrgApiKey>(`/orgs/${orgId}/api-key`, { accessToken, cache: "no-store" });
}

export async function getOrgActionItems(accessToken: string | null, orgId: string): Promise<ActionItemsResponse | null> {
  return apiFetch<ActionItemsResponse>(`/orgs/${orgId}/action-items`, { accessToken, cache: "no-store" });
}

export async function getOrgRepos(accessToken: string | null, orgId: string): Promise<Repo[] | null> {
  return apiFetch<Repo[]>(`/orgs/${orgId}/repos`, { accessToken, cache: "no-store" });
}

export async function getOrgAnalytics(accessToken: string | null, orgId: string): Promise<OrgAnalytics | null> {
  return apiFetch<OrgAnalytics>(`/orgs/${orgId}/analytics`, { accessToken, cache: "no-store" });
}

export async function getOrgCoverageSummary(accessToken: string | null, orgId: string): Promise<OrgCoverageSummary | null> {
  return apiFetch<OrgCoverageSummary>(`/orgs/${orgId}/coverage-summary`, { accessToken, cache: "no-store" });
}

export async function getOrgSettings(accessToken: string | null, orgId: string): Promise<OrgSettings | null> {
  return apiFetch<OrgSettings>(`/orgs/${orgId}/settings`, { accessToken, cache: "no-store" });
}

export async function getEmailDigestSettings(accessToken: string | null, orgId: string): Promise<EmailDigestSettings | null> {
  const settings = await getOrgSettings(accessToken, orgId);
  if (!settings) return null;
  return {
    digest_email: settings.digest_email ?? null,
    digest_enabled: Boolean(settings.digest_enabled),
    digest_day: Number.isFinite(settings.digest_day) ? Number(settings.digest_day) : 1,
    digest_hour: Number.isFinite(settings.digest_hour) ? Number(settings.digest_hour) : 8,
    digest_last_sent_at: settings.digest_last_sent_at ?? null,
  };
}

export async function updateEmailDigestSettings(accessToken: string | null, orgId: string, payload: EmailDigestSettings): Promise<EmailDigestSettings | null> {
  return apiFetch<EmailDigestSettings>(`/orgs/${orgId}/settings/email-digest`, {
    accessToken,
    body: JSON.stringify(payload),
    cache: "no-store",
    method: "PATCH",
  });
}

export async function getOrgAISettings(accessToken: string | null, orgId: string): Promise<OrgAISettings | null> {
  return apiFetch<OrgAISettings>(`/orgs/${orgId}/settings`, { accessToken, cache: "no-store" });
}

export async function getOrgMemoryScore(accessToken: string | null, orgId: string): Promise<MemoryScore | null> {
  return apiFetch<MemoryScore>(`/orgs/${orgId}/memory-score`, { accessToken, cache: "no-store" });
}

export async function getAgentPrs(accessToken: string | null, orgId: string, params?: URLSearchParams): Promise<AgentPrListResponse | null> {
  const query = params?.toString();
  return apiFetch<AgentPrListResponse>(`/orgs/${orgId}/agent-prs${query ? `?${query}` : ""}`, { accessToken, cache: "no-store" });
}

export async function getAgentPrDetail(accessToken: string | null, orgId: string, prId: string): Promise<AgentPrDetail | null> {
  return apiFetch<AgentPrDetail>(`/orgs/${orgId}/agent-prs/${prId}`, { accessToken, cache: "no-store" });
}

export async function getMyCodeToday(accessToken: string | null, orgId: string, login: string, date?: string): Promise<MyCodeTodayResponse | null> {
  const params = new URLSearchParams({ login });
  if (date) params.set("date", date);
  return apiFetch<MyCodeTodayResponse>(`/orgs/${orgId}/my-code-today?${params.toString()}`, { accessToken, cache: "no-store" });
}

export async function getAgentScorecard(accessToken: string | null, orgId: string, days = 30): Promise<AgentScorecardResponse | null> {
  const params = new URLSearchParams({ days: String(days) });
  return apiFetch<AgentScorecardResponse>(`/orgs/${orgId}/agent-scorecard?${params.toString()}`, { accessToken, cache: "no-store" });
}

export async function getDeveloperLeaderboard(accessToken: string | null, orgId: string, days = 30, sortBy = "compliance", includeTrend = false): Promise<DeveloperLeaderboardResponse | null> {
  const params = new URLSearchParams({ days: String(days), sort_by: sortBy });
  if (includeTrend) params.set("include_trend", "true");
  return apiFetch<DeveloperLeaderboardResponse>(`/orgs/${orgId}/developer-leaderboard?${params.toString()}`, { accessToken, cache: "no-store" });
}

function adminHeaders(adminSecret: string): HeadersInit {
  return { "X-Admin-Secret": adminSecret };
}

export async function getAdminOverview(adminSecret: string): Promise<AdminOverview | null> {
  return apiFetch<AdminOverview>("/admin/overview", { headers: adminHeaders(adminSecret), cache: "no-store" });
}

export async function getAdminOrgs(adminSecret: string, params?: URLSearchParams): Promise<{ orgs: AdminOrg[]; next_cursor: string | null; total: number } | null> {
  const query = params?.toString();
  return apiFetch<{ orgs: AdminOrg[]; next_cursor: string | null; total: number }>(`/admin/orgs${query ? `?${query}` : ""}`, { headers: adminHeaders(adminSecret), cache: "no-store" });
}

export async function getAdminOrg(orgId: string, adminSecret: string): Promise<AdminOrgDetail | null> {
  return apiFetch<AdminOrgDetail>(`/admin/orgs/${orgId}`, { headers: adminHeaders(adminSecret), cache: "no-store" });
}

export async function getAdminOrgUsage(orgId: string, adminSecret: string, days = 30): Promise<UsageSeries | null> {
  return apiFetch<UsageSeries>(`/admin/orgs/${orgId}/usage?days=${days}`, { headers: adminHeaders(adminSecret), cache: "no-store" });
}

export async function getAdminUsers(adminSecret: string, params?: URLSearchParams): Promise<{ users: AdminUser[]; next_cursor: string | null; total: number } | null> {
  const query = params?.toString();
  return apiFetch<{ users: AdminUser[]; next_cursor: string | null; total: number }>(`/admin/users${query ? `?${query}` : ""}`, { headers: adminHeaders(adminSecret), cache: "no-store" });
}

export async function getAdminLogins(adminSecret: string, params?: URLSearchParams): Promise<{ logins: AdminLoginEvent[]; next_cursor: string | null; total: number } | null> {
  const query = params?.toString();
  return apiFetch<{ logins: AdminLoginEvent[]; next_cursor: string | null; total: number }>(`/admin/logins${query ? `?${query}` : ""}`, { headers: adminHeaders(adminSecret), cache: "no-store" });
}

export async function suspendOrg(orgId: string, adminSecret: string, reason: string): Promise<AdminOrg | null> {
  return apiFetch<AdminOrg>(`/admin/orgs/${orgId}/suspend`, { headers: adminHeaders(adminSecret), method: "POST", body: JSON.stringify({ reason }), cache: "no-store" });
}

export async function unsuspendOrg(orgId: string, adminSecret: string): Promise<AdminOrg | null> {
  return apiFetch<AdminOrg>(`/admin/orgs/${orgId}/unsuspend`, { headers: adminHeaders(adminSecret), method: "POST", cache: "no-store" });
}

export async function deleteOrg(orgId: string, adminSecret: string): Promise<{ ok: boolean; deleted_org_id: string } | null> {
  return apiFetch<{ ok: boolean; deleted_org_id: string }>(`/admin/orgs/${orgId}`, { headers: adminHeaders(adminSecret), method: "DELETE", cache: "no-store" });
}

export async function executeSkillQL(accessToken: string | null, orgId: string, query: string): Promise<SkillQLResult | null> {
  return apiFetch<SkillQLResult>(`/orgs/${orgId}/skillql`, { accessToken, method: "POST", body: JSON.stringify({ query }), cache: "no-store" });
}

export async function getSkillQLSuggestions(accessToken: string | null, orgId: string): Promise<SkillQLSuggestions | null> {
  return apiFetch<SkillQLSuggestions>(`/orgs/${orgId}/skillql/suggestions`, { accessToken, cache: "no-store" });
}

export async function getAutopilotQueue(accessToken: string | null, orgId: string): Promise<AutopilotTask[] | null> {
  return apiFetch<AutopilotTask[]>(`/orgs/${orgId}/autopilot/queue`, { accessToken, cache: "no-store" });
}

export async function getRedFlagDismissals(accessToken: string | null, orgId: string): Promise<RedFlagDismissal[] | null> {
  return apiFetch<RedFlagDismissal[]>(`/orgs/${orgId}/red-flags/dismissed`, { accessToken, cache: "no-store" });
}

export async function getOrgSkillHeatmap(accessToken: string | null, orgId: string): Promise<SkillHeatmapResponse | null> {
  return apiFetch<SkillHeatmapResponse>(`/orgs/${orgId}/skill-heatmap`, { accessToken, cache: "no-store" });
}

export async function getOrgRuntimeBreakdown(accessToken: string | null, orgId: string): Promise<RuntimeBreakdownResponse | null> {
  return apiFetch<RuntimeBreakdownResponse>(`/orgs/${orgId}/runtime-breakdown`, { accessToken, cache: "no-store" });
}

export async function getOrgTeamRollup(accessToken: string | null, orgId: string): Promise<TeamRollupResponse | null> {
  return apiFetch<TeamRollupResponse>(`/orgs/${orgId}/team-rollup`, { accessToken, cache: "no-store" });
}

export async function getOrgIntelligence(accessToken: string, orgId: string): Promise<OrgIntelligence | null> {
  return apiFetch<OrgIntelligence>(`/orgs/${orgId}/intelligence`, { accessToken, cache: "no-store" });
}

export async function getMemoryQueue(
  accessToken: string | null,
  orgId: string,
  params?: { status?: string; repo_id?: string; limit?: number; offset?: number },
): Promise<MemoryQueueResponse | null> {
  const query = new URLSearchParams();
  if (params?.status) query.set("status", params.status);
  if (params?.repo_id) query.set("repo_id", params.repo_id);
  if (params?.limit !== undefined) query.set("limit", String(params.limit));
  if (params?.offset !== undefined) query.set("offset", String(params.offset));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return apiFetch<MemoryQueueResponse>(`/orgs/${orgId}/memory-queue${suffix}`, { accessToken, cache: "no-store" });
}

export async function reviewMemoryStub(
  accessToken: string,
  orgId: string,
  stubId: string,
  action: "approve" | "reject",
  editedContent?: string,
  reviewerNote?: string,
): Promise<MemoryStub | null> {
  return apiFetch<MemoryStub>(`/orgs/${orgId}/memory-queue/${stubId}`, {
    accessToken,
    method: "PATCH",
    body: JSON.stringify({ action, edited_content: editedContent, reviewer_note: reviewerNote }),
    cache: "no-store",
  });
}

export async function getKnowledgeVelocity(accessToken: string | null, orgId: string): Promise<KnowledgeVelocity | null> {
  return apiFetch<KnowledgeVelocity>(`/orgs/${orgId}/knowledge-velocity`, { accessToken, cache: "no-store" });
}

export async function getOrgRedFlags(accessToken: string | null, orgId: string, severity?: string, repoId?: string): Promise<OrgRedFlags | null> {
  const query = new URLSearchParams();
  if (severity) query.set("severity", severity);
  if (repoId) query.set("repo_id", repoId);
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return apiFetch<OrgRedFlags>(`/orgs/${orgId}/red-flags${suffix}`, { accessToken, cache: "no-store" });
}

export async function getAuditLog(accessToken: string | null, orgId: string, params?: URLSearchParams): Promise<AuditLogResponse | null> {
  const query = params?.toString();
  return apiFetch<AuditLogResponse>(`/orgs/${orgId}/audit-log${query ? `?${query}` : ""}`, { accessToken, cache: "no-store" });
}

export async function getOrgAuditLog(accessToken: string | null, orgId: string, params?: URLSearchParams): Promise<AuditLogResponse | null> {
  return getAuditLog(accessToken, orgId, params);
}

export async function getAuditLogEventTypes(accessToken: string | null, orgId: string): Promise<string[] | null> {
  return apiFetch<string[]>(`/orgs/${orgId}/audit-log/event-types`, { accessToken, cache: "no-store" });
}

export async function getAuditLogStats(accessToken: string | null, orgId: string): Promise<AuditLogStats | null> {
  return apiFetch<AuditLogStats>(`/orgs/${orgId}/audit-log/stats`, { accessToken, cache: "no-store" });
}

export function exportAuditLogCsvUrl(orgId: string, params?: URLSearchParams): string {
  const query = params?.toString();
  return `${API_URL}/orgs/${orgId}/audit-log/export${query ? `?${query}` : ""}`;
}

export async function configureAuditWebhook(
  accessToken: string,
  orgId: string,
  body: { webhook_url: string; secret?: string | null; enabled: boolean; event_filter?: string },
): Promise<boolean> {
  const result = await apiFetch<{ configured: boolean }>(`/orgs/${orgId}/audit-log/webhook`, {
    accessToken,
    method: "POST",
    body: JSON.stringify(body),
    cache: "no-store",
  });
  return Boolean(result?.configured);
}

export async function getPolicies(accessToken: string | null, orgId: string): Promise<PolicyRule[]> {
  return (await apiFetch<PolicyRule[]>(`/orgs/${orgId}/policies`, { accessToken, cache: "no-store" })) ?? [];
}

export async function getPolicyTemplates(accessToken: string | null, orgId: string): Promise<PolicyRule[]> {
  return (await apiFetch<PolicyRule[]>(`/orgs/${orgId}/policy-templates`, { accessToken, cache: "no-store" })) ?? [];
}

export async function createPolicy(accessToken: string, orgId: string, body: Partial<PolicyRule>): Promise<PolicyRule | null> {
  return apiFetch<PolicyRule>(`/orgs/${orgId}/policies`, { accessToken, method: "POST", body: JSON.stringify(body), cache: "no-store" });
}

export async function updatePolicy(accessToken: string, orgId: string, policyId: string, body: Partial<PolicyRule>): Promise<PolicyRule | null> {
  return apiFetch<PolicyRule>(`/orgs/${orgId}/policies/${policyId}`, { accessToken, method: "PATCH", body: JSON.stringify(body), cache: "no-store" });
}

export async function deletePolicy(accessToken: string, orgId: string, policyId: string): Promise<boolean> {
  const result = await apiFetch<{ deleted: boolean }>(`/orgs/${orgId}/policies/${policyId}`, { accessToken, method: "DELETE", cache: "no-store" });
  return Boolean(result?.deleted);
}

export async function runPolicyCheck(accessToken: string, orgId: string): Promise<PolicyCheckResult | null> {
  return apiFetch<PolicyCheckResult>(`/orgs/${orgId}/policy-check`, { accessToken, cache: "no-store" });
}

export async function getLLMConfig(accessToken: string | null, orgId: string): Promise<LLMConfig | null> {
  return apiFetch<LLMConfig>(`/orgs/${orgId}/llm-config`, { accessToken, cache: "no-store" });
}

export async function saveLLMConfig(accessToken: string, orgId: string, body: Partial<LLMConfig> & { api_key?: string | null }): Promise<LLMConfig | null> {
  return apiFetch<LLMConfig>(`/orgs/${orgId}/llm-config`, { accessToken, method: "POST", body: JSON.stringify(body), cache: "no-store" });
}

export async function testLLMConfig(accessToken: string, orgId: string, body: { provider: string; model: string; api_key: string; base_url?: string | null }): Promise<{ success: boolean; response: string | null; error: string | null } | null> {
  return apiFetch<{ success: boolean; response: string | null; error: string | null }>(`/orgs/${orgId}/llm-config/test`, { accessToken, method: "POST", body: JSON.stringify(body), cache: "no-store" });
}

export async function getOrgPolicies(accessToken: string | null, orgId: string): Promise<GovernancePoliciesResponse | null> {
  const policies = await getPolicies(accessToken, orgId);
  return {
    policies: policies.map((policy) => ({
      id: policy.id,
      name: policy.name,
      type: "min_score",
      threshold: Number(policy.rule_config.min_score ?? policy.rule_config.max_days ?? 0),
      scope: "all_repos",
      action: policy.severity === "error" ? "block_pr" : "warn",
      enabled: policy.enabled,
      created_at: policy.created_at,
    })),
  };
}

export async function getRepo(accessToken: string | null, repoId: string): Promise<Repo | null> {
  return apiFetch<Repo>(`/repos/${repoId}`, { accessToken, cache: "no-store" });
}

export async function getRepoSkills(accessToken: string | null, repoId: string): Promise<Skill[] | null> {
  return apiFetch<Skill[]>(`/repos/${repoId}/skills`, { accessToken, cache: "no-store" });
}

export async function getRepoScoreHistory(accessToken: string | null, repoId: string): Promise<ScoreHistoryPoint[] | null> {
  return apiFetch<ScoreHistoryPoint[]>(`/repos/${repoId}/score-history`, { accessToken, cache: "no-store" });
}

export async function getRepoScoreForecast(accessToken: string | null, repoId: string): Promise<ScoreForecast | null> {
  return apiFetch<ScoreForecast>(`/repos/${repoId}/score-forecast`, { accessToken, cache: "no-store" });
}

export async function getRepoDependencies(accessToken: string | null, repoId: string): Promise<DependencyReport | null> {
  return apiFetch<DependencyReport>(`/repos/${repoId}/dependencies`, { accessToken, cache: "no-store" });
}

export async function getRepoSkillSources(accessToken: string | null, repoId: string): Promise<RepoSkillSources | null> {
  return apiFetch<RepoSkillSources>(`/repos/${repoId}/skill-sources`, { accessToken, cache: "no-store" });
}

export async function getRepoSkillUsageStats(accessToken: string | null, repoId: string, skillId: string): Promise<SkillUsageStats | null> {
  return apiFetch<SkillUsageStats>(`/repos/${repoId}/skills/${skillId}/usage-stats`, { accessToken, cache: "no-store" });
}

export async function getSkill(accessToken: string | null, skillId: string): Promise<Skill | null> {
  return apiFetch<Skill>(`/skills/${skillId}`, { accessToken, cache: "no-store" });
}

export async function getSkillVersions(accessToken: string | null, skillId: string): Promise<SkillVersionSummary[] | null> {
  return apiFetch<SkillVersionSummary[]>(`/skills/${skillId}/versions`, { accessToken, cache: "no-store" });
}

export async function getSkillVersion(accessToken: string | null, skillId: string, versionId: string): Promise<SkillVersion | null> {
  return apiFetch<SkillVersion>(`/skills/${skillId}/versions/${versionId}`, { accessToken, cache: "no-store" });
}

export async function getSkillVersionDiff(
  accessToken: string | null,
  repoId: string,
  skillId: string,
  versionId: string,
): Promise<SkillVersionDiff | null> {
  return apiFetch<SkillVersionDiff>(`/repos/${repoId}/skills/${skillId}/versions/${versionId}/diff`, { accessToken, cache: "no-store" });
}

export async function getSkillSnapshots(
  accessToken: string | null,
  repoId: string,
  skillId: string,
  params?: URLSearchParams,
): Promise<SkillSnapshot[] | null> {
  const query = params?.toString();
  return apiFetch<SkillSnapshot[]>(`/repos/${repoId}/skills/${skillId}/snapshots${query ? `?${query}` : ""}`, { accessToken, cache: "no-store" });
}

export async function getSkillSnapshot(
  accessToken: string | null,
  repoId: string,
  skillId: string,
  snapshotId: string,
): Promise<SkillSnapshot | null> {
  return apiFetch<SkillSnapshot>(`/repos/${repoId}/skills/${skillId}/snapshots/${snapshotId}`, { accessToken, cache: "no-store" });
}

export async function getSkillSnapshotDiff(
  accessToken: string | null,
  repoId: string,
  skillId: string,
  snapshotId: string,
): Promise<string | null> {
  const headers: Record<string, string> = {};
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
  try {
    const response = await fetch(`${API_URL}/repos/${repoId}/skills/${skillId}/snapshots/${snapshotId}/diff`, {
      headers,
      cache: "no-store",
    });
    if (!response.ok) return null;
    return response.text();
  } catch (error) {
    console.error(`Failed to fetch snapshot diff ${snapshotId}:`, error);
    return null;
  }
}

export async function createSkillSnapshot(
  accessToken: string,
  repoId: string,
  skillId: string,
  label?: string,
): Promise<SkillSnapshot | null> {
  return apiFetch<SkillSnapshot>(`/repos/${repoId}/skills/${skillId}/snapshots`, {
    accessToken,
    method: "POST",
    body: JSON.stringify({ label }),
    cache: "no-store",
  });
}

export async function rollbackSkill(
  accessToken: string,
  repoId: string,
  skillId: string,
  snapshotId: string,
): Promise<SkillRollbackResult | null> {
  return apiFetch<SkillRollbackResult>(`/repos/${repoId}/skills/${skillId}/rollback/${snapshotId}`, {
    accessToken,
    method: "POST",
    cache: "no-store",
  });
}

export async function updateSkillContent(
  accessToken: string,
  repoId: string,
  skillId: string,
  content: string,
): Promise<SkillContentUpdateResult> {
  const result = await apiFetch<SkillContentUpdateResult>(`/repos/${repoId}/skills/${skillId}/content`, {
    accessToken,
    method: "PATCH",
    body: JSON.stringify({ content }),
    cache: "no-store",
  });
  if (!result) {
    throw new Error("Unable to update skill content");
  }
  return result;
}

export async function getOrgSkillDebt(accessToken: string | null, orgId: string): Promise<SkillDebtResponse | null> {
  return apiFetch<SkillDebtResponse>(`/orgs/${orgId}/skill-debt`, { accessToken, cache: "no-store" });
}

export async function runDebtAnalysis(accessToken: string | null, orgId: string): Promise<{ health_score: number; repos_analyzed: number; gaps_found: number; analysis_id: string } | null> {
  return apiFetch<{ health_score: number; repos_analyzed: number; gaps_found: number; analysis_id: string }>(`/orgs/${orgId}/debt/run-analysis`, { accessToken, method: "POST", cache: "no-store" });
}

export async function getEvalROI(accessToken: string | null, orgId: string, params?: URLSearchParams): Promise<EvalROI | null> {
  const query = params?.toString();
  return apiFetch<EvalROI>(`/eval/orgs/${orgId}/roi${query ? `?${query}` : ""}`, { accessToken, cache: "no-store" });
}

export async function getEvalSkillGaps(accessToken: string | null, orgId: string, status = "open"): Promise<EvalSkillGap[] | null> {
  const response = await getEvalSkillGapsResponse(accessToken, orgId, status);
  return response?.gaps ?? null;
}

export async function getEvalSkillGapsResponse(accessToken: string | null, orgId: string, status = "all"): Promise<EvalSkillGapsResponse | null> {
  return apiFetch<EvalSkillGapsResponse>(`/eval/orgs/${orgId}/skill-gaps?status=${encodeURIComponent(status)}`, { accessToken, cache: "no-store" });
}

export async function getEvalSummary(accessToken: string | null, orgId: string): Promise<EvalSummary | null> {
  return apiFetch<EvalSummary>(`/eval/orgs/${orgId}/eval/summary`, { accessToken, cache: "no-store" });
}

export async function getEvalSessions(accessToken: string | null, orgId: string): Promise<EvalSessionsResponse | null> {
  return apiFetch<EvalSessionsResponse>(`/eval/orgs/${orgId}/eval/sessions`, { accessToken, cache: "no-store" });
}

export async function getAnalyticsCriticality(accessToken: string | null, orgId: string): Promise<CriticalityItem[] | null> {
  return apiFetch<CriticalityItem[]>(`/orgs/${orgId}/analytics/criticality`, { accessToken, cache: "no-store" });
}

export async function getABTests(accessToken: string | null, orgId: string): Promise<ABTest[] | null> {
  return apiFetch<ABTest[]>(`/eval/orgs/${orgId}/ab-tests`, { accessToken, cache: "no-store" });
}

export async function getRegistrySkills(params: URLSearchParams): Promise<RegistryList | null> {
  const query = params.toString();
  return apiFetch<RegistryList>(`/registry${query ? `?${query}` : ""}`, { revalidate: 60 });
}

export async function getRegistrySkillDetail(registryId: string): Promise<RegistrySkillDetail | null> {
  return apiFetch<RegistrySkillDetail>(`/registry/${registryId}`, { cache: "no-store" });
}

export async function getOrgRegistryEntries(accessToken: string | null, orgId: string, params?: URLSearchParams): Promise<RegistryEntriesResponse | null> {
  const query = params?.toString();
  return apiFetch<RegistryEntriesResponse>(`/registry/orgs/${orgId}/entries${query ? `?${query}` : ""}`, { accessToken, cache: "no-store" });
}

export async function getMarketplaceEntries(params?: URLSearchParams): Promise<RegistryEntriesResponse | null> {
  const query = params?.toString();
  return apiFetch<RegistryEntriesResponse>(`/registry/marketplace${query ? `?${query}` : ""}`, { cache: "no-store" });
}

export async function getHalfLifeSummary(accessToken: string | null, orgId: string): Promise<HalfLifeSummary | null> {
  return apiFetch<HalfLifeSummary>(`/registry/orgs/${orgId}/half-life`, { accessToken, cache: "no-store" });
}

export async function refreshHalfLife(accessToken: string, orgId: string): Promise<{ queued: boolean; skill_count: number } | null> {
  return apiFetch<{ queued: boolean; skill_count: number }>(`/registry/orgs/${orgId}/half-life/refresh`, { accessToken, method: "POST", cache: "no-store" });
}

export async function getDependencyGraph(accessToken: string | null, orgId: string): Promise<DependencyGraph | null> {
  return apiFetch<DependencyGraph>(`/registry/orgs/${orgId}/dependency-graph`, { accessToken, cache: "no-store" });
}

export async function getRepoDependencyGraph(accessToken: string | null, orgId: string, repoId: string): Promise<DependencyGraphCache | null> {
  return apiFetch<DependencyGraphCache>(`/orgs/${orgId}/dependency-graph/repo/${repoId}`, { accessToken, cache: "no-store" });
}

export async function getCrossRepoDependencyGraph(accessToken: string | null, orgId: string): Promise<DependencyGraphCache | null> {
  return apiFetch<DependencyGraphCache>(`/orgs/${orgId}/dependency-graph/cross-repo`, { accessToken, cache: "no-store" });
}

export async function getCompatibilityMatrix(accessToken: string | null, orgId: string): Promise<CompatibilityMatrix | null> {
  return apiFetch<CompatibilityMatrix>(`/registry/orgs/${orgId}/compatibility-matrix`, { accessToken, cache: "no-store" });
}

export async function getRepoSnapshots(accessToken: string | null, repoId: string): Promise<RepoSnapshot[] | null> {
  return apiFetch<RepoSnapshot[]>(`/repos/${repoId}/snapshots`, { accessToken, cache: "no-store" });
}

export async function getKnowledgeRisk(accessToken: string | null, orgId: string): Promise<KnowledgeRiskResponse | null> {
  return apiFetch<KnowledgeRiskResponse>(`/orgs/${orgId}/knowledge-concentration`, { accessToken, cache: "no-store" });
}

export async function getSLAPolicies(accessToken: string | null, orgId: string): Promise<SLAPolicy[] | null> {
  return apiFetch<SLAPolicy[]>(`/orgs/${orgId}/sla`, { accessToken, cache: "no-store" });
}

export async function getOrgSources(accessToken: string | null, orgId: string): Promise<SourceConnection[] | null> {
  return apiFetch<SourceConnection[]>(`/orgs/${orgId}/sources`, { accessToken, cache: "no-store" });
}

export async function getOrgSessions(accessToken: string | null, orgId: string): Promise<OrgSessionsResponse | null> {
  return apiFetch<OrgSessionsResponse>(`/orgs/${orgId}/sessions`, { accessToken, cache: "no-store" });
}

export async function getIntelligenceInsights(accessToken: string | null, orgId: string): Promise<IntelligenceInsight[] | null> {
  return apiFetch<IntelligenceInsight[]>(`/orgs/${orgId}/intelligence/insights`, { accessToken, cache: "no-store" });
}
