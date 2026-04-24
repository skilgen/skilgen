import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowRight, TrendingDown, TrendingUp, Users2 } from "lucide-react";

import { getBootstrapOrg, getMyOrg, getOrgTeamRollup, type TeamRollupResponse, type TeamRollupTeam } from "../../../lib/data";

export const dynamic = "force-dynamic";

function ringTone(score: number): string {
  if (score < 50) return "#ef4444";
  if (score < 70) return "#f59e0b";
  return "#22c55e";
}

function ScoreRing({ score }: { score: number }) {
  const radius = 22;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.max(0, Math.min(100, score)) / 100) * circumference;
  return (
    <div className="relative h-[60px] w-[60px]">
      <svg className="h-[60px] w-[60px] -rotate-90" viewBox="0 0 64 64">
        <circle cx="32" cy="32" fill="none" r={radius} stroke="rgba(255,255,255,0.08)" strokeWidth="7" />
        <circle cx="32" cy="32" fill="none" r={radius} stroke={ringTone(score)} strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" strokeWidth="7" />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center text-[15px] font-semibold text-[color:var(--text-primary)]">{score}</div>
    </div>
  );
}

function MetricCard({ label, value, sub }: { label: string; value: string | number; sub: string }) {
  return (
    <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-3 text-[30px] font-semibold text-[color:var(--text-primary)]">{value}</div>
      <div className="mt-4 text-[12px] text-[color:var(--text-secondary)]">{sub}</div>
    </article>
  );
}

function TeamCard({ team }: { team: TeamRollupTeam }) {
  const delta = team.score_delta_7d ?? 0;
  return (
    <article className="rounded-[28px] border border-[color:var(--bg-border)] bg-[linear-gradient(160deg,rgba(255,255,255,0.04),rgba(255,255,255,0.015))] p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-[22px] font-semibold text-[color:var(--text-primary)]">{team.team_name}</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{team.repo_count} repos</p>
        </div>
        <ScoreRing score={team.avg_score ?? 0} />
      </div>

      <div className="mt-4 inline-flex items-center gap-2 rounded-full bg-black/20 px-3 py-1 text-[12px] font-semibold text-[color:var(--text-secondary)]">
        {delta > 0 ? <TrendingUp className="h-4 w-4 text-emerald-400" /> : delta < 0 ? <TrendingDown className="h-4 w-4 text-red-400" /> : null}
        {delta > 0 ? `+${delta}` : delta} vs last week
      </div>

      <div className="mt-6">
        <div className="mb-2 flex items-center justify-between text-[13px]">
          <span className="text-[color:var(--text-secondary)]">Coverage</span>
          <span className="font-semibold text-[color:var(--text-primary)]">{team.coverage_score}%</span>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-white/10">
          <div className="h-full rounded-full bg-[#C9973A]" style={{ width: `${team.coverage_score}%` }} />
        </div>
      </div>

      <div className="mt-6 space-y-3 text-[14px]">
        <div className="flex items-center justify-between gap-3">
          <span className="text-[color:var(--text-secondary)]">Best</span>
          <span className="font-medium text-[color:var(--text-primary)]">{team.best_repo ? `${team.best_repo.name} ${team.best_repo.score}/100` : "—"}</span>
        </div>
        <div className="flex items-center justify-between gap-3">
          <span className="text-[color:var(--text-secondary)]">Worst</span>
          <span className={`font-medium ${(team.worst_repo?.score ?? 100) < 50 ? "text-red-300" : "text-[color:var(--text-primary)]"}`}>
            {team.worst_repo ? `${team.worst_repo.name} ${team.worst_repo.score}/100` : "—"}
          </span>
        </div>
      </div>

      <div className="mt-6 flex items-center justify-between gap-4 border-t border-white/6 pt-4 text-[13px]">
        <span className="text-[color:var(--text-secondary)]">{team.skill_count} skills</span>
        <Link className="inline-flex items-center gap-2 font-semibold text-[color:var(--accent-primary)] hover:text-[color:var(--accent-bright)]" href="/dashboard/repos">
          View repos
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </article>
  );
}

async function loadTeamRollup(): Promise<TeamRollupResponse | null> {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Teams auth unavailable:", error);
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  if (!org) return null;
  return getOrgTeamRollup(accessToken, org.id);
}

export default async function TeamsPage() {
  const rollup = await loadTeamRollup();

  if (!rollup || rollup.teams.length < 2) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Teams</h1>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">The VP Engineering command center for team-by-team repo health.</p>
        </div>
        <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
          <Users2 className="mx-auto h-10 w-10 text-[color:var(--text-tertiary)]" />
          <h2 className="mt-4 text-[22px] font-semibold text-[color:var(--text-primary)]">Teams appear once you have multiple connected repositories.</h2>
          <Link className="mt-6 inline-flex items-center gap-2 rounded-full bg-[color:var(--accent-primary)] px-5 py-3 text-[14px] font-semibold text-black hover:bg-[color:var(--accent-bright)]" href="/dashboard/repos">
            Connect more repos
            <ArrowRight className="h-4 w-4" />
          </Link>
        </section>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Teams</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">The VP Engineering command center for team-by-team repo health.</p>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Org Avg Score" value={`${rollup.org_avg_score ?? 0}/100`} sub="Average across all teams" />
        <MetricCard label="Top Team" value={rollup.top_team ?? "—"} sub="Highest average score" />
        <MetricCard label="Needs Attention" value={rollup.needs_attention ?? "—"} sub="Lowest performing team" />
        <MetricCard label="Total Skills" value={rollup.teams.reduce((sum, team) => sum + team.skill_count, 0)} sub="Tracked skill inventory" />
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        {rollup.teams.map((team) => (
          <TeamCard key={team.team_name} team={team} />
        ))}
      </section>
    </div>
  );
}
