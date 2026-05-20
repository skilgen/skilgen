import Link from "next/link";
import { redirect } from "next/navigation";
import { AlertTriangle, ArrowRight, Code2, FileText, RadioTower, Search } from "lucide-react";

import { ActivityHeader } from "../ActivityNav";
import { RepoTaskStrip } from "../RepoTaskStrip";
import { getActivityAgentRepos, getActivitySessions, loadActivityContext, normalizeSearchParams, type ActivitySession } from "../activity-data";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

function formatTime(value: string | null): string {
  if (!value) return "Unknown time";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
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

function riskClass(band: ActivitySession["risk_band"]): string {
  if (band === "high") return "border-red-500/40 bg-red-500/10 text-red-200";
  if (band === "medium") return "border-amber-500/40 bg-amber-500/10 text-amber-200";
  return "border-[color:var(--accent-green)]/40 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]";
}

function runSignal(session: ActivitySession): string {
  const metrics = session.activity_metrics ?? {};
  if (session.access_scope === "full-access") return "Full-access run";
  if (session.risk_band === "high") return "High-risk run";
  if ((metrics.commands ?? 0) >= 50) return "Heavy command usage";
  if ((session.tokens_total ?? 0) >= 10_000_000) return "High token usage";
  if ((metrics.edited_files ?? session.files_touched.length) >= 10) return "Large edit surface";
  return "Review evidence";
}

function evidenceHref(session: ActivitySession): string {
  const metrics = session.activity_metrics ?? {};
  if ((metrics.commands ?? 0) > 0) return `${session.replay_url}#activity-commands`;
  if ((metrics.edited_files ?? session.files_touched.length) > 0) return `${session.replay_url}#activity-edited`;
  if ((metrics.searches ?? 0) > 0) return `${session.replay_url}#activity-searches`;
  return session.replay_url;
}

function ReviewMetric({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2">
      <div className="text-[10px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-1 font-mono text-sm text-[color:var(--text-primary)]">{value}</div>
    </div>
  );
}

function ReplayReviewCard({ session }: { session: ActivitySession }) {
  const metrics = session.activity_metrics ?? {};
  const edited = metrics.edited_files ?? session.files_touched.length;
  const explored = metrics.explored_files ?? 0;
  const searches = metrics.searches ?? 0;
  const commands = metrics.commands ?? 0;
  const tools = metrics.tool_calls ?? session.mcp_tools?.length ?? 0;
  const signal = runSignal(session);
  return (
    <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${riskClass(session.risk_band)}`}>{signal}</span>
            {session.access_scope ? <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]">{session.access_scope}</span> : null}
            {session.intelligence_tier ? <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]">{session.intelligence_tier}</span> : null}
          </div>
          <h2 className="mt-3 text-lg font-semibold text-[color:var(--text-primary)]">{session.agent} - {session.repo_name}</h2>
          <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{formatTime(session.started_at)} · {session.user} · {session.model ?? "model unknown"}</p>
          <p className="mt-2 text-xs leading-5 text-[color:var(--text-tertiary)]">
            {session.risk_reasons?.length ? session.risk_reasons.slice(0, 4).join(" · ") : "Open the replay to inspect metadata-only evidence for this coding-agent run."}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <ReviewMetric label="Tokens" value={compactNumber(session.tokens_total)} />
          <ReviewMetric label="Cost" value={formatMoney(session.cost_usd)} />
          <ReviewMetric label="Edited" value={edited} />
          <ReviewMetric label="Commands" value={commands} />
        </div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-[1fr_auto]">
        <div className="grid gap-2 sm:grid-cols-5">
          <ReviewMetric label="Explored" value={explored} />
          <ReviewMetric label="Searches" value={searches} />
          <ReviewMetric label="Tools" value={tools} />
          <ReviewMetric label="Risk" value={`${session.risk_band} ${session.risk_score}`} />
          <ReviewMetric label="Outcome" value={session.outcome.replaceAll("_", " ")} />
        </div>
        <div className="flex flex-wrap items-center gap-2 md:justify-end">
          <Link className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href={evidenceHref(session)}>
            Evidence
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link className="inline-flex items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" href={session.replay_url}>
            Open run
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </article>
  );
}

export default async function ActivityReplayIndexPage({ searchParams }: { searchParams?: PageSearchParams }) {
  const params = await normalizeSearchParams(searchParams);
  const limit = Number(params.get("limit") ?? 25);
  const offset = Number(params.get("offset") ?? 0);
  params.set("limit", String(limit));
  if (offset > 0) {
    params.delete("offset");
    params.set("limit", String(offset + limit));
    redirect(`/activity/replay?${params.toString()}`);
  }
  const context = await loadActivityContext();
  const [payload, repoOptions] = context.org?.id
    ? await Promise.all([
        getActivitySessions(context.accessToken, context.org.id, params),
        getActivityAgentRepos(context.accessToken, context.org.id),
      ])
    : [null, []];
  const sessions = payload?.sessions ?? [];
  const nextParams = new URLSearchParams(params);
  nextParams.delete("offset");
  nextParams.set("limit", String(limit + 25));
  const hasMore = payload ? sessions.length < payload.total : false;
  const totalTokens = sessions.reduce((sum, session) => sum + Number(session.tokens_total ?? 0), 0);
  const totalCommands = sessions.reduce((sum, session) => sum + Number(session.activity_metrics?.commands ?? 0), 0);
  const totalEdited = sessions.reduce((sum, session) => sum + Number(session.activity_metrics?.edited_files ?? session.files_touched.length), 0);
  const reviewQueue = sessions.filter((session) => session.risk_band === "high" || session.access_scope === "full-access" || Number(session.activity_metrics?.commands ?? 0) >= 50).length;

  return (
    <div className="space-y-6">
      <ActivityHeader active="replay" />

      <RepoTaskStrip basePath="/activity/replay" currentParams={params} repos={repoOptions} selectedRepoId={params.get("repo_id")} title="Repository replay queue" />

      <form className="grid gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-[minmax(220px,1fr)_180px_auto]" method="get">
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("repo_id") ?? ""} name="repo_id">
          <option value="">All repos</option>
          {repoOptions.map((repo) => (
            <option key={repo.id} value={repo.id}>{repo.full_name}</option>
          ))}
        </select>
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("limit") ?? "25"} name="limit">
          <option value="25">25 runs</option>
          <option value="50">50 runs</option>
          <option value="100">100 runs</option>
        </select>
        <input name="offset" type="hidden" value="0" />
        <button className="inline-flex items-center justify-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" type="submit">
          <Search className="h-4 w-4" />
          Apply
        </button>
      </form>

      <section className="rounded-lg border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
        <div className="flex items-start gap-3">
          <Search className="mt-1 h-4 w-4 text-[color:var(--accent-primary)]" />
          <div>
            <h2 className="font-semibold text-[color:var(--text-primary)]">Run review queue</h2>
            <p className="mt-1 text-sm leading-6 text-[color:var(--text-secondary)]">Replay is for investigation: find expensive, risky, broad-access, or noisy coding-agent runs, then open the exact evidence behind the run.</p>
          </div>
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-4">
        <ReviewMetric label="Runs loaded" value={sessions.length} />
        <ReviewMetric label="Needs review" value={reviewQueue} />
        <ReviewMetric label="Tokens" value={compactNumber(totalTokens)} />
        <ReviewMetric label="Commands" value={totalCommands} />
      </section>

      <section className="grid gap-3 md:grid-cols-3">
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <FileText className="h-4 w-4 text-[color:var(--accent-primary)]" />
          <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">{totalEdited}</div>
          <p className="mt-1 text-xs text-[color:var(--text-secondary)]">Files edited across loaded runs.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <RadioTower className="h-4 w-4 text-[color:var(--accent-primary)]" />
          <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">{sessions.reduce((sum, session) => sum + Number(session.activity_metrics?.tool_calls ?? 0), 0)}</div>
          <p className="mt-1 text-xs text-[color:var(--text-secondary)]">Tool calls captured from run metadata.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <AlertTriangle className="h-4 w-4 text-[color:var(--accent-primary)]" />
          <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">{sessions.filter((session) => session.risk_band !== "low").length}</div>
          <p className="mt-1 text-xs text-[color:var(--text-secondary)]">Runs with medium or high risk signals.</p>
        </article>
      </section>

      <section className="space-y-3">
        {sessions.map((session) => <ReplayReviewCard key={session.id} session={session} />)}
        {sessions.length === 0 ? (
          <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center text-sm text-[color:var(--text-secondary)]">
            <Code2 className="mx-auto mb-3 h-8 w-8 text-[color:var(--accent-primary)]" />
            No sessions are available for replay.
          </div>
        ) : null}
      </section>
      {hasMore ? (
        <Link className="inline-flex w-full items-center justify-center rounded-md border border-[color:var(--bg-border)] px-4 py-3 text-sm font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href={`/activity/replay?${nextParams.toString()}`}>
          Load more replay candidates
        </Link>
      ) : sessions.length ? (
        <div className="rounded-lg border border-dashed border-[color:var(--bg-border)] px-4 py-3 text-center text-sm text-[color:var(--text-secondary)]">All replay candidates for this filter are loaded.</div>
      ) : null}
    </div>
  );
}
