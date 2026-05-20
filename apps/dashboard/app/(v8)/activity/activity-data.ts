import "server-only";

import { withAuth } from "@workos-inc/authkit-nextjs";

import { API_URL, getBootstrapOrg, getMyOrg, getOrgApiKey, getOrgRepos, getOrgSetupStatus, type Org, type Repo, type SetupStatus } from "../../../lib/data";

export type ActivityMetrics = {
  edited_files?: number;
  explored_files?: number;
  searches?: number;
  lists?: number;
  commands?: number;
  tool_calls?: number;
  mcp_tools?: number;
};

export type ActivityDetails = {
  edited_files?: string[];
  explored_files?: string[];
  searches?: string[];
  lists?: string[];
  commands?: string[];
  tools?: string[];
};

export type ActivityEvent = {
  id: string;
  timestamp: string | null;
  agent: string;
  agent_provider: string;
  user: string;
  repo_id: string;
  repo: string;
  repo_name: string;
  repo_sensitivity_tier: string;
  skill_id: string;
  skill: string;
  skill_signature_status: string;
  action: string;
  action_class: string;
  file_scope: string[];
  outcome: string;
  trigger: { label: string; url: string | null } | null;
  risk_score: number;
  risk_band: "low" | "medium" | "high";
  risk_reasons?: string[];
  tokens_total?: number;
  cost_usd?: number;
  model?: string | null;
  intelligence_tier?: string | null;
  access_scope?: string | null;
  activity_metrics?: ActivityMetrics;
  activity_details?: ActivityDetails;
  replay_url?: string;
  session_id: string;
  session_db_id: string | null;
};

export type ActivityComplianceEvent = {
  id: string;
  timestamp: string | null;
  provider: string;
  actor_login: string | null;
  repo_name: string | null;
  model: string | null;
  intelligence_tier: string | null;
  access_scope: string | null;
  policy_decision: string | null;
  source_envelope_hash: string | null;
  summary: string;
  risk_score: number;
  risk_band: "low" | "medium" | "high";
};

export type ActivityComplianceSession = {
  session_id: string;
  provider: string;
  actor_login: string | null;
  repo_name: string | null;
  model: string | null;
  intelligence_tier: string | null;
  access_scopes: string[];
  source_record_types: string[];
  event_count: number;
  tool_calls: number;
  mcp_tools: string[];
  file_targets: string[];
  policy_decisions: Record<string, number>;
  tokens_input: number;
  tokens_output: number;
  cost_usd: number;
  errors: number;
  risk_score: number;
  risk_band: "low" | "medium" | "high";
  started_at: string | null;
  last_event_at: string | null;
  duration_minutes: number | null;
  content_retention: "metadata-only";
};

export type ActivitySession = {
  id: string;
  session_id: string;
  repo_id: string;
  repo_name: string;
  repo_sensitivity_tier: string;
  agent_provider: string;
  agent: string;
  user: string;
  started_at: string | null;
  ended_at: string | null;
  duration_minutes: number | null;
  files_touched: string[];
  skills_loaded: string[];
  skill_signature_statuses: string[];
  outcome: string;
  trigger: { label: string; url: string | null } | null;
  risk_score: number;
  risk_band: "low" | "medium" | "high";
  risk_reasons?: string[];
  tokens_total?: number;
  cost_usd?: number;
  model?: string | null;
  intelligence_tier?: string | null;
  access_scope?: string | null;
  mcp_tools?: string[];
  activity_metrics?: ActivityMetrics;
  activity_details?: ActivityDetails;
  replay_url: string;
};

export type ActivityRollup = {
  providers: Array<{ agent_provider: string; agent: string; sessions: number; high_risk: number; avg_risk_score: number }>;
  outcomes: Record<string, number>;
  total_sessions: number;
};

export type ActivityRepoOption = {
  id: string;
  full_name: string;
  name: string;
  providers?: string[];
  session_count?: number;
};

export type ActivityFeedResponse = {
  events: ActivityEvent[];
  total: number;
  has_more?: boolean;
  next_offset?: number | null;
};

export type ReplayStep = {
  index: number;
  timestamp: string | null;
  action: string;
  action_class: string;
  reasoning: string | null;
  tool_call: Record<string, unknown> | null;
  result: Record<string, unknown>;
  policy_decision: string;
  file_diff: string;
  risk_score: number;
  risk_band: "low" | "medium" | "high";
};

export type HeatmapCell = {
  repo_id: string;
  repo_name: string;
  hour: number;
  action_count: number;
  messages?: number;
  sessions?: number;
  tokens_total?: number;
  cost_usd?: number;
  active_days?: number;
  favorite_model?: string | null;
  deny_rate: number | null;
  risk_band: "low" | "medium" | "high";
};

export type HeatmapModel = {
  platform: string;
  model: string;
  tokens_total: number;
  cost_usd: number;
  sessions: number;
  messages: number;
};

export type HeatmapTrend = {
  platform: string;
  date: string;
  sessions: number;
  messages: number;
  tokens_total: number;
  cost_usd: number;
};

export type ActivityContext = {
  accessToken: string;
  org: Pick<Org, "id" | "name" | "plan"> | null;
  streamKey: string;
};

export type SearchParamsInput = Record<string, string | string[] | undefined> | Promise<Record<string, string | string[] | undefined>>;

export async function normalizeSearchParams(input?: SearchParamsInput): Promise<URLSearchParams> {
  const raw = input ? await input : {};
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(raw)) {
    if (Array.isArray(value)) {
      if (value[0]) params.set(key, value[0]);
    } else if (value) {
      params.set(key, value);
    }
  }
  return params;
}

export async function loadActivityContext(): Promise<ActivityContext> {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const apiKey = org?.id && accessToken ? await getOrgApiKey(accessToken, org.id) : null;
  return { accessToken, org, streamKey: apiKey?.api_key ?? "" };
}

async function activityFetch<T>(accessToken: string, path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_URL}${path}`, {
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getActivityFeed(accessToken: string, orgId: string, params: URLSearchParams): Promise<ActivityFeedResponse | null> {
  const query = params.toString();
  return activityFetch<ActivityFeedResponse>(accessToken, `/v8/orgs/${orgId}/activity/feed${query ? `?${query}` : ""}`);
}

export async function getActivityComplianceEvents(accessToken: string, orgId: string, params: URLSearchParams): Promise<{ events: ActivityComplianceEvent[]; total: number; content_retention: "metadata-only" } | null> {
  const query = params.toString();
  return activityFetch<{ events: ActivityComplianceEvent[]; total: number; content_retention: "metadata-only" }>(accessToken, `/v8/orgs/${orgId}/activity/compliance-events${query ? `?${query}` : ""}`);
}

export async function getActivityComplianceSessions(accessToken: string, orgId: string, params: URLSearchParams): Promise<{ sessions: ActivityComplianceSession[]; total: number; content_retention: "metadata-only" } | null> {
  const query = params.toString();
  return activityFetch<{ sessions: ActivityComplianceSession[]; total: number; content_retention: "metadata-only" }>(accessToken, `/v8/orgs/${orgId}/activity/compliance-sessions${query ? `?${query}` : ""}`);
}

export async function getActivitySessions(accessToken: string, orgId: string, params: URLSearchParams): Promise<{ sessions: ActivitySession[]; total: number; rollup: ActivityRollup } | null> {
  const query = params.toString();
  return activityFetch<{ sessions: ActivitySession[]; total: number; rollup: ActivityRollup }>(accessToken, `/v8/orgs/${orgId}/activity/sessions${query ? `?${query}` : ""}`);
}

export async function getActivityReplay(accessToken: string, orgId: string, repoId: string, sessionId: string): Promise<{ session: ActivitySession; timeline: ReplayStep[]; export_html: string; compliance_events: ActivityComplianceEvent[] } | null> {
  return activityFetch<{ session: ActivitySession; timeline: ReplayStep[]; export_html: string; compliance_events: ActivityComplianceEvent[] }>(accessToken, `/v8/orgs/${orgId}/repos/${repoId}/activity/sessions/${sessionId}/replay`);
}

export async function getActivityHeatmap(accessToken: string, orgId: string, repoId: string, params: URLSearchParams): Promise<{ cells: HeatmapCell[]; models?: HeatmapModel[]; trend?: HeatmapTrend[]; max_action_count: number; hours: number; group_by?: string; summary?: { sessions: number; messages: number; tokens_total: number; cost_usd: number; active_days: number; peak_hour: number | null; favorite_model: string | null; platforms: number } } | null> {
  const query = params.toString();
  return activityFetch<{ cells: HeatmapCell[]; models?: HeatmapModel[]; trend?: HeatmapTrend[]; max_action_count: number; hours: number; group_by?: string; summary?: { sessions: number; messages: number; tokens_total: number; cost_usd: number; active_days: number; peak_hour: number | null; favorite_model: string | null; platforms: number } }>(accessToken, `/v8/orgs/${orgId}/repos/${repoId}/activity/heatmap${query ? `?${query}` : ""}`);
}

export async function getActivityRepos(accessToken: string, orgId: string): Promise<Repo[]> {
  return (await getOrgRepos(accessToken, orgId)) ?? [];
}

export async function getActivityAgentRepos(accessToken: string, orgId: string): Promise<ActivityRepoOption[]> {
  const response = await activityFetch<{ repos: ActivityRepoOption[] }>(accessToken, `/v8/orgs/${orgId}/skills/repos/available`);
  const unique = new Map<string, ActivityRepoOption>();
  for (const repo of response?.repos ?? []) {
    const key = repo.full_name.toLowerCase();
    const existing = unique.get(key);
    if (!existing || (repo.session_count ?? 0) > (existing.session_count ?? 0)) {
      unique.set(key, repo);
    }
  }
  return Array.from(unique.values()).sort((a, b) => a.full_name.localeCompare(b.full_name));
}

export async function getActivitySetupStatus(accessToken: string, orgId: string): Promise<SetupStatus | null> {
  return getOrgSetupStatus(accessToken, orgId);
}
