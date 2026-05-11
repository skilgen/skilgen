import { ActivityHeader } from "../ActivityNav";
import { getActivityComplianceSessions, loadActivityContext, normalizeSearchParams, type ActivityComplianceSession } from "../activity-data";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

function riskClass(band: ActivityComplianceSession["risk_band"]): string {
  if (band === "high") return "text-[color:var(--accent-red)]";
  if (band === "medium") return "text-[#f59e0b]";
  return "text-[color:var(--accent-green)]";
}

export default async function ActivityComplianceSessionsPage({ searchParams }: { searchParams?: PageSearchParams }) {
  const context = await loadActivityContext();
  const params = await normalizeSearchParams(searchParams);
  if (!params.has("hours")) params.set("hours", "24");
  const payload = context.org?.id ? await getActivityComplianceSessions(context.accessToken, context.org.id, params) : null;
  const sessions = payload?.sessions ?? [];

  return (
    <section className="mx-auto max-w-7xl space-y-6">
      <ActivityHeader active="compliance-sessions" />

      <div className="grid gap-3 md:grid-cols-4">
        <Metric label="Sessions" value={sessions.length} />
        <Metric label="Events" value={sessions.reduce((sum, item) => sum + item.event_count, 0)} />
        <Metric label="Tool calls" value={sessions.reduce((sum, item) => sum + item.tool_calls, 0)} />
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
          <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Retention</div>
          <div className="mt-1 text-sm font-semibold text-[color:var(--accent-primary)]">{payload?.content_retention ?? "metadata-only"}</div>
        </div>
      </div>

      {sessions.length ? (
        <div className="divide-y divide-[color:var(--bg-border)] rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          {sessions.map((session) => (
            <article className="grid gap-4 p-4 lg:grid-cols-[minmax(0,1fr)_180px_190px] lg:items-center" key={session.session_id}>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="font-semibold text-[color:var(--text-primary)]">{session.provider}</h2>
                  <span className={`text-[12px] font-semibold ${riskClass(session.risk_band)}`}>{session.risk_band}</span>
                  {session.source_record_types.slice(0, 2).map((type) => (
                    <span className="rounded-sm border border-[color:var(--bg-border)] px-2 py-0.5 text-[11px] text-[color:var(--text-tertiary)]" key={`${session.session_id}-${type}`}>{type}</span>
                  ))}
                </div>
                <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">
                  {session.actor_login ?? "Unknown actor"} · {session.repo_name ?? "Org scope"} · {session.model ?? "model unknown"}
                </div>
                <div className="mt-1 truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{session.session_id}</div>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {[session.intelligence_tier, ...session.access_scopes, ...session.mcp_tools].filter(Boolean).slice(0, 5).map((tag) => (
                    <span className="rounded-sm border border-[color:var(--bg-border)] px-2 py-0.5 text-[11px] text-[color:var(--text-secondary)]" key={`${session.session_id}-${tag}`}>{tag}</span>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[12px] text-[color:var(--text-secondary)]">
                <span>{session.event_count} events</span>
                <span>{session.tool_calls} tools</span>
                <span>{session.file_targets.length} files</span>
                <span>{session.duration_minutes ?? 0}m</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[12px] text-[color:var(--text-secondary)]">
                <span>{session.tokens_input + session.tokens_output} tokens</span>
                <span>${session.cost_usd.toFixed(4)}</span>
                <span>{session.errors} errors</span>
                <span>{Object.keys(session.policy_decisions).length} decisions</span>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
          <h2 className="font-semibold text-[color:var(--text-primary)]">{payload ? "No agent sessions matched" : "Agent sessions unavailable"}</h2>
          <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-[color:var(--text-secondary)]">
            Metadata-only compliance sessions appear here after provider or coding-agent telemetry includes a session id. Raw prompts, file content, diffs, and tool parameters are not displayed.
          </p>
        </div>
      )}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
      <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-1 text-xl font-semibold text-[color:var(--text-primary)]">{value}</div>
    </div>
  );
}
