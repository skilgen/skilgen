import Link from "next/link";
import { redirect } from "next/navigation";
import { History, Search } from "lucide-react";

import { ActivityHeader } from "../ActivityNav";
import { RepoTaskStrip } from "../RepoTaskStrip";
import { getActivityAgentRepos, getActivitySessions, loadActivityContext, normalizeSearchParams, type ActivitySession } from "../activity-data";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

function formatTime(value: string | null): string {
  if (!value) return "Unknown";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

function riskClass(band: ActivitySession["risk_band"]): string {
  if (band === "high") return "border-red-500/40 text-red-200";
  if (band === "medium") return "border-amber-500/40 text-amber-200";
  return "border-[color:var(--accent-green)]/40 text-[color:var(--accent-green)]";
}

function compactNumber(value: number | null | undefined): string {
  const safe = Number(value ?? 0);
  if (safe >= 1_000_000) return `${(safe / 1_000_000).toFixed(safe >= 10_000_000 ? 0 : 1)}M`;
  if (safe >= 1_000) return `${(safe / 1_000).toFixed(safe >= 10_000 ? 0 : 1)}K`;
  return String(safe);
}

function formatMoney(value: number | null | undefined): string {
  const safe = Number(value ?? 0);
  return safe > 0 ? `$${safe.toFixed(safe >= 1 ? 2 : 4)}` : "$0.00";
}

export default async function ActivitySessionsPage({ searchParams }: { searchParams?: PageSearchParams }) {
  const params = await normalizeSearchParams(searchParams);
  const limit = Number(params.get("limit") ?? 25);
  const offset = Number(params.get("offset") ?? 0);
  params.set("limit", String(limit));
  if (offset > 0) {
    params.delete("offset");
    params.set("limit", String(offset + limit));
    redirect(`/activity/sessions?${params.toString()}`);
  }
  const context = await loadActivityContext();
  const [payload, repoOptions] = context.org?.id
    ? await Promise.all([
        getActivitySessions(context.accessToken, context.org.id, params),
        getActivityAgentRepos(context.accessToken, context.org.id),
      ])
    : [null, []];
  const sessions = payload?.sessions ?? [];
  const providers = payload?.rollup.providers ?? [];
  const nextParams = new URLSearchParams(params);
  nextParams.delete("offset");
  nextParams.set("limit", String(limit + 25));
  const hasMore = payload ? sessions.length < payload.total : false;

  return (
    <div className="space-y-6">
      <ActivityHeader active="sessions" />

      <RepoTaskStrip basePath="/activity/sessions" currentParams={params} repos={repoOptions} selectedRepoId={params.get("repo_id")} title="Repository runs" />

      <form className="grid gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-[repeat(4,minmax(0,1fr))_auto]" method="get">
        <input className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("agent_provider") ?? ""} name="agent_provider" placeholder="Provider" />
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("repo_id") ?? ""} name="repo_id">
          <option value="">All repos</option>
          {repoOptions.map((repo) => (
            <option key={repo.id} value={repo.id}>{repo.full_name}</option>
          ))}
        </select>
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("risk_band") ?? ""} name="risk_band">
          <option value="">All risk</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={String(limit)} name="limit">
          <option value="25">25 sessions</option>
          <option value="50">50 sessions</option>
          <option value="100">100 sessions</option>
        </select>
        <input name="offset" type="hidden" value="0" />
        <button className="inline-flex items-center justify-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" type="submit">
          <Search className="h-4 w-4" />
          Apply
        </button>
      </form>

      <section className="grid gap-3 md:grid-cols-3">
        {providers.slice(0, 3).map((provider) => (
          <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={provider.agent_provider}>
            <div className="text-sm font-semibold text-[color:var(--text-primary)]">{provider.agent}</div>
            <div className="mt-3 text-2xl font-semibold">{provider.sessions}</div>
            <div className="mt-1 text-xs text-[color:var(--text-secondary)]">Avg risk {provider.avg_risk_score} - {provider.high_risk} high risk</div>
          </article>
        ))}
      </section>

      <section className="space-y-3">
        {sessions.length ? (
          sessions.map((session) => (
            <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={session.id}>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="text-xs text-[color:var(--text-tertiary)]">{formatTime(session.started_at)}</div>
                  <h2 className="mt-1 text-lg font-semibold text-[color:var(--text-primary)]">{session.agent} - {session.repo_name}</h2>
                  <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{session.user} - {session.files_touched.length} files - {session.skills_loaded.length} skills</p>
                  <p className="mt-1 text-xs text-[color:var(--text-tertiary)]">{session.model ?? "model unknown"}{session.intelligence_tier ? ` · ${session.intelligence_tier}` : ""} · {compactNumber(session.tokens_total)} tokens · {formatMoney(session.cost_usd)}</p>
                  {session.risk_reasons?.length ? <p className="mt-1 text-xs text-[color:var(--text-tertiary)]">Risk: {session.risk_reasons.slice(0, 4).join(" · ")}</p> : null}
                </div>
                <span className={`rounded-md border px-2 py-1 text-xs font-semibold capitalize ${riskClass(session.risk_band)}`}>{session.risk_band} {session.risk_score}</span>
              </div>
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap gap-2">
                  {session.skills_loaded.slice(0, 5).map((skill) => (
                    <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={skill}>{skill}</span>
                  ))}
                </div>
                <Link className="text-sm font-semibold text-[color:var(--accent-primary)]" href={session.replay_url}>Replay</Link>
              </div>
            </article>
          ))
        ) : (
          <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center text-sm text-[color:var(--text-secondary)]">
            <History className="mx-auto mb-3 h-8 w-8 text-[color:var(--accent-primary)]" />
            No sessions matched the current filters.
          </div>
        )}
      </section>
      {hasMore ? (
        <Link className="inline-flex w-full items-center justify-center rounded-md border border-[color:var(--bg-border)] px-4 py-3 text-sm font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href={`/activity/sessions?${nextParams.toString()}`}>
          Load more runs
        </Link>
      ) : sessions.length ? (
        <div className="rounded-lg border border-dashed border-[color:var(--bg-border)] px-4 py-3 text-center text-sm text-[color:var(--text-secondary)]">All runs for this filter are loaded.</div>
      ) : null}
    </div>
  );
}
