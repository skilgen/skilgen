import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowRight, CheckCircle2, ShieldAlert, TrendingDown, TrendingUp, Users2 } from "lucide-react";

import { API_URL, getBootstrapOrg, getMyOrg, getOrgTeamRollup, type TeamRollupResponse, type TeamRollupTeam } from "../../../lib/data";

export const dynamic = "force-dynamic";

type TeamSummary = {
  org_avg_score?: number | null;
  top_team?: string | null;
  needs_attention?: string | null;
  total_teams?: number | null;
  total_repos?: number | null;
  total_skills?: number | null;
  urgent_count?: number | null;
  stale_skill_count?: number | null;
};

type TeamItem = {
  id?: string;
  team_name?: string;
  name?: string;
  repo_count?: number;
  avg_score?: number | null;
  score_delta_7d?: number | null;
  coverage_score?: number;
  skill_count?: number;
  stale_skill_count?: number;
  urgent_count?: number;
  best_repo?: { id?: string; name: string; score: number | null } | null;
  worst_repo?: { id?: string; name: string; score: number | null } | null;
  action?: string | null;
  action_url?: string | null;
  repos?: { id: string; name: string; score: number | null }[];
};

type TeamsData = {
  accessToken: string;
  orgId: string;
  summary: TeamSummary | null;
  teams: TeamItem[];
  source: "teams-api" | "rollup" | "empty";
  errorDetail?: string | null;
};

async function apiFetch<T>(accessToken: string | null, path: string): Promise<{ data: T | null; errorDetail: string | null }> {
  try {
    const headers: HeadersInit = { "Content-Type": "application/json" };
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
    const response = await fetch(`${API_URL}${path}`, { headers, cache: "no-store" });
    const body = await response.json().catch(() => null);
    const detail =
      body && typeof body === "object"
        ? String((body as { detail?: unknown; message?: unknown; error?: unknown }).detail ?? (body as { message?: unknown }).message ?? (body as { error?: unknown }).error ?? "")
        : "";
    if (!response.ok) return { data: null, errorDetail: detail || `Request failed with ${response.status}` };
    if (body && typeof body === "object" && (body as { error?: unknown }).error) {
      return { data: null, errorDetail: detail || "The teams API returned an error." };
    }
    return { data: body as T, errorDetail: null };
  } catch (error) {
    console.error(`Failed to load ${path}:`, error);
    return { data: null, errorDetail: error instanceof Error ? error.message : "Could not load teams data." };
  }
}

function teamName(team: TeamItem): string {
  return team.team_name ?? team.name ?? "Unassigned";
}

function clampScore(score: number | null | undefined): number {
  return Math.max(0, Math.min(100, Math.round(score ?? 0)));
}

function scoreTone(score: number | null | undefined): string {
  const value = clampScore(score);
  if (value < 50) return "text-[color:var(--accent-red)]";
  if (value < 70) return "text-[color:var(--accent-primary)]";
  return "text-[color:var(--accent-green)]";
}

function progressTone(score: number | null | undefined): string {
  const value = clampScore(score);
  if (value < 50) return "bg-[color:var(--accent-red)]";
  if (value < 70) return "bg-[color:var(--accent-primary)]";
  return "bg-[color:var(--accent-green)]";
}

function actionForTeam(team: TeamItem): { label: string; href: string; priority: "urgent" | "recommended" | "healthy" } {
  if (team.action && team.action_url) {
    return { label: team.action, href: team.action_url, priority: (team.urgent_count ?? 0) > 0 ? "urgent" : "recommended" };
  }
  const score = clampScore(team.avg_score);
  if ((team.urgent_count ?? 0) > 0 || score < 50) {
    return { label: "Open risk review", href: "/dashboard/red-flags", priority: "urgent" };
  }
  if ((team.coverage_score ?? 100) < 75) {
    return { label: "Close coverage gaps", href: "/dashboard/debt?tab=gaps", priority: "recommended" };
  }
  if ((team.stale_skill_count ?? 0) > 0 || score < 70) {
    return { label: "Refresh stale skills", href: "/dashboard/autopilot", priority: "recommended" };
  }
  return { label: "Review top repos", href: "/dashboard/repos", priority: "healthy" };
}

function adaptRollup(rollup: TeamRollupResponse | null): { summary: TeamSummary | null; teams: TeamItem[] } {
  if (!rollup) return { summary: null, teams: [] };
  const teams = rollup.teams.map((team: TeamRollupTeam) => ({
    team_name: team.team_name,
    repo_count: team.repo_count,
    avg_score: team.avg_score,
    score_delta_7d: team.score_delta_7d,
    coverage_score: team.coverage_score,
    skill_count: team.skill_count,
    best_repo: team.best_repo,
    worst_repo: team.worst_repo,
    repos: team.repos,
  }));
  return {
    summary: {
      org_avg_score: rollup.org_avg_score,
      top_team: rollup.top_team,
      needs_attention: rollup.needs_attention,
      total_teams: teams.length,
      total_repos: teams.reduce((sum, team) => sum + (team.repo_count ?? 0), 0),
      total_skills: teams.reduce((sum, team) => sum + (team.skill_count ?? 0), 0),
      urgent_count: teams.filter((team) => clampScore(team.avg_score) < 50).length,
      stale_skill_count: 0,
    },
    teams,
  };
}

async function loadTeamsData(): Promise<TeamsData> {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Teams auth unavailable:", error);
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const orgId = org?.id ?? "";
  if (!orgId) return { accessToken, orgId, summary: null, teams: [], source: "empty" };

  const [summaryResult, teamsResult] = await Promise.all([
    apiFetch<TeamSummary>(accessToken, `/orgs/${orgId}/teams/summary`),
    apiFetch<TeamItem[] | { teams?: TeamItem[] }>(accessToken, `/orgs/${orgId}/teams`),
  ]);
  const teamsPayload = teamsResult.data;
  const teams = Array.isArray(teamsPayload) ? teamsPayload : Array.isArray(teamsPayload?.teams) ? teamsPayload.teams : [];
  const apiErrorDetail = summaryResult.errorDetail ?? teamsResult.errorDetail;
  if (summaryResult.data || teams.length || teamsResult.data) {
    return { accessToken, orgId, summary: summaryResult.data, teams, source: teams.length ? "teams-api" : "empty", errorDetail: apiErrorDetail };
  }

  const rollup = await getOrgTeamRollup(accessToken, orgId);
  const adapted = adaptRollup(rollup);
  return {
    accessToken,
    orgId,
    summary: adapted.summary,
    teams: adapted.teams,
    source: adapted.teams.length ? "rollup" : "empty",
    errorDetail: apiErrorDetail,
  };
}

function MetricCard({ label, value, sub }: { label: string; value: string | number; sub: string }) {
  return (
    <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-3 truncate text-[28px] font-semibold text-[color:var(--text-primary)]">{value}</div>
      <div className="mt-3 text-[12px] text-[color:var(--text-secondary)]">{sub}</div>
    </article>
  );
}

function DeltaBadge({ delta }: { delta: number | null | undefined }) {
  const value = delta ?? 0;
  if (value === 0) return <span className="text-[12px] text-[color:var(--text-tertiary)]">Stable</span>;
  const positive = value > 0;
  return (
    <span className={`inline-flex items-center gap-1 text-[12px] font-semibold ${positive ? "text-[color:var(--accent-green)]" : "text-[color:var(--accent-red)]"}`}>
      {positive ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
      {positive ? `+${value}` : value} this week
    </span>
  );
}

function TeamRow({ team }: { team: TeamItem }) {
  const score = clampScore(team.avg_score);
  const coverage = clampScore(team.coverage_score);
  const action = actionForTeam(team);
  return (
    <tr className="border-t border-[color:var(--bg-border)]">
      <td className="py-4 pr-4 align-top">
        <div className="font-semibold text-[color:var(--text-primary)]">{teamName(team)}</div>
        <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{team.repo_count ?? 0} repos · {team.skill_count ?? 0} skills</div>
      </td>
      <td className="px-4 py-4 align-top">
        <div className={`text-[20px] font-semibold ${scoreTone(team.avg_score)}`}>{score}/100</div>
        <DeltaBadge delta={team.score_delta_7d} />
      </td>
      <td className="px-4 py-4 align-top">
        <div className="flex min-w-[140px] items-center gap-3">
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-white/10">
            <div className={`h-full rounded-full ${progressTone(team.coverage_score)}`} style={{ width: `${coverage}%` }} />
          </div>
          <span className="w-10 text-right text-[12px] font-semibold text-[color:var(--text-secondary)]">{coverage}%</span>
        </div>
      </td>
      <td className="px-4 py-4 align-top">
        <div className="text-[13px] text-[color:var(--text-secondary)]">Best: <span className="text-[color:var(--text-primary)]">{team.best_repo ? `${team.best_repo.name} ${team.best_repo.score ?? 0}/100` : "none"}</span></div>
        <div className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Weakest: <span className={scoreTone(team.worst_repo?.score)}>{team.worst_repo ? `${team.worst_repo.name} ${team.worst_repo.score ?? 0}/100` : "none"}</span></div>
      </td>
      <td className="py-4 pl-4 align-top">
        <Link className={`inline-flex items-center gap-2 rounded-[8px] px-3 py-2 text-[13px] font-semibold ${action.priority === "urgent" ? "bg-[color:var(--accent-red)]/15 text-[color:var(--accent-red)] hover:bg-[color:var(--accent-red)]/20" : action.priority === "healthy" ? "bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)] hover:bg-[color:var(--accent-green)]/15" : "bg-[color:var(--accent-primary)]/15 text-[color:var(--accent-primary)] hover:bg-[color:var(--accent-primary)]/20"}`} href={action.href}>
          {action.label}
          <ArrowRight className="h-4 w-4" />
        </Link>
      </td>
    </tr>
  );
}

function EmptyState({ orgId }: { orgId: string }) {
  return (
    <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
      <Users2 className="mx-auto h-10 w-10 text-[color:var(--text-tertiary)]" />
      <h2 className="mt-4 text-[22px] font-semibold text-[color:var(--text-primary)]">Teams appear once repos are connected.</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm text-[color:var(--text-secondary)]">Skillayer groups repositories by ownership signals and repo naming, then rolls risk, coverage, and score movement into one operating view.</p>
      <Link className="mt-6 inline-flex items-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-5 py-3 text-[14px] font-semibold text-black hover:bg-[color:var(--accent-bright)]" href={orgId ? "/dashboard/connect" : "/dashboard/repos"}>
        Connect repositories
        <ArrowRight className="h-4 w-4" />
      </Link>
    </section>
  );
}

function ErrorDetail({ detail }: { detail: string }) {
  return (
    <section className="rounded-[8px] border border-[color:var(--accent-red)]/30 bg-[color:var(--accent-red)]/10 p-4 text-sm text-[color:var(--text-secondary)]">
      <span className="font-semibold text-[color:var(--accent-red)]">Teams API notice: </span>
      {detail}
    </section>
  );
}

export default async function TeamsPage() {
  const data = await loadTeamsData();
  const teams = data.teams;
  const summary = data.summary;
  const totalSkills = summary?.total_skills ?? teams.reduce((sum, team) => sum + (team.skill_count ?? 0), 0);
  const urgentCount = summary?.urgent_count ?? teams.filter((team) => actionForTeam(team).priority === "urgent").length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-end">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--accent-primary)]">VP Engineering command center</p>
          <h1 className="mt-2 text-2xl font-semibold text-[color:var(--text-primary)]">Teams</h1>
          <p className="mt-1 max-w-3xl text-sm text-[color:var(--text-secondary)]">Track which teams are codifying knowledge, where skill quality is drifting, and what action should happen next.</p>
        </div>
        <div className="inline-flex items-center gap-2 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-2 text-[12px] text-[color:var(--text-secondary)]">
          {urgentCount > 0 ? <ShieldAlert className="h-4 w-4 text-[color:var(--accent-red)]" /> : <CheckCircle2 className="h-4 w-4 text-[color:var(--accent-green)]" />}
          {urgentCount > 0 ? `${urgentCount} team actions need attention` : "No urgent team actions"}
        </div>
      </div>

      {data.errorDetail ? <ErrorDetail detail={data.errorDetail} /> : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Org Avg Score" value={`${clampScore(summary?.org_avg_score)}/100`} sub="Average memory health across teams" />
        <MetricCard label="Top Team" value={summary?.top_team ?? "—"} sub="Highest operating score" />
        <MetricCard label="Needs Attention" value={summary?.needs_attention ?? "—"} sub="Lowest score or most urgent risk" />
        <MetricCard label="Total Skills" value={totalSkills} sub={`${summary?.total_repos ?? teams.reduce((sum, team) => sum + (team.repo_count ?? 0), 0)} repos monitored`} />
      </section>

      {teams.length === 0 ? (
        <EmptyState orgId={data.orgId} />
      ) : (
        <section className="overflow-hidden rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="flex flex-col justify-between gap-3 border-b border-[color:var(--bg-border)] px-5 py-4 md:flex-row md:items-center">
            <div>
              <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">Team action queue</h2>
              <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Sorted for executive review: score, coverage, weakest repo, and next action.</p>
            </div>
            <span className="text-[12px] text-[color:var(--text-tertiary)]">{data.source === "rollup" ? "Using team rollup fallback" : "Live teams API"}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[920px] text-left">
              <thead>
                <tr className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">
                  <th className="px-5 py-3">Team</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">Coverage</th>
                  <th className="px-4 py-3">Repo Signal</th>
                  <th className="px-5 py-3">Next Action</th>
                </tr>
              </thead>
              <tbody>
                {[...teams].sort((a, b) => {
                  const actionRank = { urgent: 0, recommended: 1, healthy: 2 };
                  const aAction = actionForTeam(a).priority;
                  const bAction = actionForTeam(b).priority;
                  return actionRank[aAction] - actionRank[bAction] || clampScore(a.avg_score) - clampScore(b.avg_score) || teamName(a).localeCompare(teamName(b));
                }).map((team) => (
                  <TeamRow key={team.id ?? teamName(team)} team={team} />
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
