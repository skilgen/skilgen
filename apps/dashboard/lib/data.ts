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
  notify_on_pr: boolean;
  notify_on_stale: boolean;
  github_app_installed: boolean;
  github_installation_id: number | null;
  webhook_url: string;
  recent_deliveries: {
    id: string;
    status: string;
    trigger: string;
    created_at: string | null;
  }[];
};

export type OrgStats = {
  repo_count: number;
  avg_score: number;
  skill_count: number;
  active_agents: number;
  score_trend: { date: string; score: number }[];
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

export type RuntimeBreakdownItem = {
  runtime: string;
  display_name: string;
  loads_30d: number;
  unique_skills: number;
  top_skill_domain: string | null;
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
  provider: string;
  model: string | null;
  endpoint_url: string | null;
  api_key_hint: string | null;
  azure_deployment: string | null;
  azure_api_version: string | null;
  is_configured: boolean;
  last_tested_at: string | null;
  last_test_ok: boolean | null;
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

export type SkillContentUpdateResult = {
  updated: boolean;
  version_number: number;
  score: Score;
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
  is_stale: boolean;
  load_count_30d: number;
};

export type SkillDebtResponse = {
  debt_score: number;
  total_skills: number;
  stale_skills: SkillDebtSkill[];
  low_score_skills: SkillDebtSkill[];
  never_loaded_skills: SkillDebtSkill[];
  zero_subscore_skills: SkillDebtSkill[];
  repo_coverage_gaps: Array<{
    repo_id: string;
    repo_name: string;
    covered_categories: string[];
    missing_categories: string[];
    coverage_score: number;
  }>;
  summary: {
    stale_count: number;
    low_score_count: number;
    never_loaded_count: number;
    zero_subscore_count: number;
    repos_with_gaps: number;
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

export async function getOrgAuditLog(accessToken: string | null, orgId: string, params?: URLSearchParams): Promise<AuditLogResponse | null> {
  const query = params?.toString();
  return apiFetch<AuditLogResponse>(`/orgs/${orgId}/audit-log${query ? `?${query}` : ""}`, { accessToken, cache: "no-store" });
}

export async function getAuditLogStats(accessToken: string | null, orgId: string): Promise<AuditLogStats | null> {
  return apiFetch<AuditLogStats>(`/orgs/${orgId}/audit-log/stats`, { accessToken, cache: "no-store" });
}

export function exportAuditLogCsvUrl(orgId: string): string {
  return `${API_URL}/orgs/${orgId}/audit-log?format=csv`;
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

export async function testLLMConfig(accessToken: string, orgId: string): Promise<{ ok: boolean; latency_ms: number; error: string | null } | null> {
  return apiFetch<{ ok: boolean; latency_ms: number; error: string | null }>(`/orgs/${orgId}/llm-config/test`, { accessToken, method: "POST", cache: "no-store" });
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

export async function getRegistrySkills(params: URLSearchParams): Promise<RegistryList | null> {
  const query = params.toString();
  return apiFetch<RegistryList>(`/registry${query ? `?${query}` : ""}`, { revalidate: 60 });
}

export async function getRegistrySkillDetail(registryId: string): Promise<RegistrySkillDetail | null> {
  return apiFetch<RegistrySkillDetail>(`/registry/${registryId}`, { cache: "no-store" });
}
