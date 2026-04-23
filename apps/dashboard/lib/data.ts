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

export type Repo = {
  id: string;
  name: string;
  full_name: string;
  installation_id: number | null;
  language: string | null;
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

export type SkillCategoryCoverage = {
  covered: boolean;
  skill_count: number;
  avg_score: number;
};

export type RepoSkillSource = {
  source_type: string;
  detected: boolean;
  skill_count: number;
  last_analysed_at: string | null;
  skills: { id: string; domain: string; score: number }[];
};

export type RepoSkillSources = {
  sources: RepoSkillSource[];
  coverage_map: Record<SkillCategory, SkillCategoryCoverage>;
  coverage_score: number;
};

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

async function apiFetch<T>(path: string, accessToken?: string | null): Promise<T | null> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  try {
    const res = await fetch(`${API_URL}${path}`, {
      headers,
      next: { revalidate: 60 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    console.error(`Failed to fetch ${path}:`, error);
    return null;
  }
}

export async function getMyOrg(accessToken: string | null): Promise<Org | null> {
  return apiFetch<Org>("/me/org", accessToken);
}

export async function getOrgStats(accessToken: string | null, orgId: string): Promise<OrgStats | null> {
  return apiFetch<OrgStats>(`/orgs/${orgId}/stats`, accessToken);
}

export async function getOrgRepos(accessToken: string | null, orgId: string): Promise<Repo[] | null> {
  return apiFetch<Repo[]>(`/orgs/${orgId}/repos`, accessToken);
}

export async function getOrgAnalytics(accessToken: string | null, orgId: string): Promise<OrgAnalytics | null> {
  return apiFetch<OrgAnalytics>(`/orgs/${orgId}/analytics`, accessToken);
}

export async function getOrgCoverageSummary(accessToken: string | null, orgId: string): Promise<OrgCoverageSummary | null> {
  return apiFetch<OrgCoverageSummary>(`/orgs/${orgId}/coverage-summary`, accessToken);
}

export async function getOrgSettings(accessToken: string | null, orgId: string): Promise<OrgSettings | null> {
  return apiFetch<OrgSettings>(`/orgs/${orgId}/settings`, accessToken);
}

export async function getRepo(accessToken: string | null, repoId: string): Promise<Repo | null> {
  return apiFetch<Repo>(`/repos/${repoId}`, accessToken);
}

export async function getRepoSkills(accessToken: string | null, repoId: string): Promise<Skill[] | null> {
  return apiFetch<Skill[]>(`/repos/${repoId}/skills`, accessToken);
}

export async function getRepoScoreHistory(accessToken: string | null, repoId: string): Promise<ScoreHistoryPoint[] | null> {
  return apiFetch<ScoreHistoryPoint[]>(`/repos/${repoId}/score-history`, accessToken);
}

export async function getRepoDependencies(accessToken: string | null, repoId: string): Promise<DependencyReport | null> {
  return apiFetch<DependencyReport>(`/repos/${repoId}/dependencies`, accessToken);
}

export async function getRepoSkillSources(accessToken: string | null, repoId: string): Promise<RepoSkillSources | null> {
  return apiFetch<RepoSkillSources>(`/repos/${repoId}/skill-sources`, accessToken);
}

export async function getSkill(accessToken: string | null, skillId: string): Promise<Skill | null> {
  return apiFetch<Skill>(`/skills/${skillId}`, accessToken);
}

export async function getSkillVersions(accessToken: string | null, skillId: string): Promise<SkillVersionSummary[] | null> {
  return apiFetch<SkillVersionSummary[]>(`/skills/${skillId}/versions`, accessToken);
}

export async function getSkillVersion(accessToken: string | null, skillId: string, versionId: string): Promise<SkillVersion | null> {
  return apiFetch<SkillVersion>(`/skills/${skillId}/versions/${versionId}`, accessToken);
}

export async function getRegistrySkills(params: URLSearchParams): Promise<RegistryList | null> {
  const query = params.toString();
  return apiFetch<RegistryList>(`/registry${query ? `?${query}` : ""}`, null);
}
