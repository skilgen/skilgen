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
  is_stale: boolean;
  load_count_30d: number;
  last_loaded_at: string | null;
  version_count: number;
  latest_version_number: number | null;
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

async function apiFetch<T>(path: string, accessToken?: string | null): Promise<T | null> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    headers,
    next: { revalidate: 60 },
  });
  if (!res.ok) return null;
  return res.json();
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

export async function getRepo(accessToken: string | null, repoId: string): Promise<Repo | null> {
  return apiFetch<Repo>(`/repos/${repoId}`, accessToken);
}

export async function getRepoSkills(accessToken: string | null, repoId: string): Promise<Skill[] | null> {
  return apiFetch<Skill[]>(`/repos/${repoId}/skills`, accessToken);
}

export async function getRepoScoreHistory(accessToken: string | null, repoId: string): Promise<ScoreHistoryPoint[] | null> {
  return apiFetch<ScoreHistoryPoint[]>(`/repos/${repoId}/score-history`, accessToken);
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
