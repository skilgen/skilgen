const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch(path: string, token: string, options?: RequestInit) {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || `API error ${res.status}`);
  }
  return res.json();
}

export const api = {
  getOrgStats: (orgId: string, token: string) => apiFetch(`/orgs/${orgId}/stats`, token),

  getRepos: (orgId: string, token: string) => apiFetch(`/orgs/${orgId}/repos`, token),

  getRepo: (repoId: string, token: string) => apiFetch(`/repos/${repoId}`, token),

  getSkills: (repoId: string, token: string) => apiFetch(`/repos/${repoId}/skills`, token),

  getScoreHistory: (repoId: string, token: string) => apiFetch(`/repos/${repoId}/score-history`, token),

  getRuns: (repoId: string, token: string) => apiFetch(`/repos/${repoId}/runs`, token),

  triggerAnalysis: (repoId: string, token: string) =>
    apiFetch(`/repos/${repoId}/analyse`, token, {
      method: "POST",
    }),

  getSkill: (skillId: string, token: string) => apiFetch(`/skills/${skillId}`, token),

  recordSkillUsage: (
    skillId: string,
    token: string,
    body: { agent_runtime: string; session_id: string },
  ) =>
    apiFetch(`/skills/${skillId}/usage`, token, {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
