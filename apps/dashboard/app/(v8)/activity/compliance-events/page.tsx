import { FileKey2, Search, ShieldCheck } from "lucide-react";

import { ActivityHeader } from "../ActivityNav";
import { getActivityComplianceEvents, loadActivityContext, normalizeSearchParams, type ActivityComplianceEvent } from "../activity-data";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

function formatTime(value: string | null): string {
  if (!value) return "Unknown";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

function riskClass(band: ActivityComplianceEvent["risk_band"]): string {
  if (band === "high") return "border-red-500/40 bg-red-500/10 text-red-200";
  if (band === "medium") return "border-amber-500/40 bg-amber-500/10 text-amber-200";
  return "border-[color:var(--accent-green)]/40 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]";
}

export default async function ActivityComplianceEventsPage({ searchParams }: { searchParams?: PageSearchParams }) {
  const params = await normalizeSearchParams(searchParams);
  if (!params.has("hours")) params.set("hours", "24");
  const context = await loadActivityContext();
  const payload = context.org?.id ? await getActivityComplianceEvents(context.accessToken, context.org.id, params) : null;
  const events = payload?.events ?? [];
  const providers = new Set(events.map((event) => event.provider).filter(Boolean));
  const actors = new Set(events.map((event) => event.actor_login).filter(Boolean));

  return (
    <div className="space-y-6">
      <ActivityHeader active="compliance-events" />

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Compliance events</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{payload?.total ?? 0}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{params.get("hours")} hour live investigation window.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Providers</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{providers.size}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{actors.size} actors represented in metadata.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Retention</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">Metadata</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{payload?.content_retention ?? "metadata-only"} · no raw prompt, chat, or file content.</p>
        </article>
      </section>

      <form className="grid gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-[120px_repeat(3,minmax(0,1fr))_auto]" method="get">
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("hours") ?? "24"} name="hours">
          <option value="1">1 hour</option>
          <option value="24">24 hours</option>
          <option value="168">7 days</option>
          <option value="720">30 days</option>
        </select>
        <input className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("provider") ?? ""} name="provider" placeholder="Provider" />
        <input className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("actor") ?? ""} name="actor" placeholder="Actor" />
        <input className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("access_scope") ?? ""} name="access_scope" placeholder="Access scope" />
        <button className="inline-flex items-center justify-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" type="submit">
          <Search className="h-4 w-4" />
          Apply
        </button>
      </form>

      <section className="rounded-lg border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-[color:var(--accent-primary)]" />
          <p className="text-[13px] leading-6 text-[color:var(--text-secondary)]">
            Activity compliance events are normalized operational metadata for investigations. AgentRun session payloads are mirrored here as metadata-only compliance records, and raw prompts, chat content, diffs, tool parameters, and file content stay out of this view unless a tenant explicitly enables retention elsewhere.
          </p>
        </div>
      </section>

      {events.length ? (
        <section className="overflow-hidden rounded-lg border border-[color:var(--bg-border)]">
          <div className="grid grid-cols-[150px_1fr_150px_150px_130px] gap-3 bg-black/20 px-4 py-3 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] max-lg:hidden">
            <span>Time</span>
            <span>Provider</span>
            <span>Actor</span>
            <span>Access</span>
            <span>Risk</span>
          </div>
          {events.map((event) => (
            <article className="grid gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm first:border-t-0 lg:grid-cols-[150px_1fr_150px_150px_130px]" key={event.id}>
              <div className="font-mono text-xs text-[color:var(--text-secondary)]">{formatTime(event.timestamp)}</div>
              <div>
                <h2 className="font-semibold text-[color:var(--text-primary)]">{event.provider}</h2>
                <p className="mt-1 text-xs text-[color:var(--text-secondary)]">{event.model ?? "model unknown"} · {event.intelligence_tier ?? "tier unknown"} · {event.repo_name ?? "repo unknown"}</p>
                <p className="mt-2 text-xs leading-5 text-[color:var(--text-tertiary)]">{event.summary}</p>
                <p className="mt-2 font-mono text-xs text-[color:var(--accent-primary)]">{event.source_envelope_hash ? event.source_envelope_hash.slice(0, 16) : "envelope pending"}</p>
              </div>
              <div className="flex items-center justify-between gap-3 text-[color:var(--text-secondary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Actor</span>
                <span>{event.actor_login ?? "system"}</span>
              </div>
              <div className="flex items-center justify-between gap-3 text-[color:var(--text-secondary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Access</span>
                <span>{event.access_scope ?? "unspecified"}</span>
              </div>
              <div className="flex items-center justify-between gap-3 lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Risk</span>
                <span className={`rounded-md border px-2 py-1 text-xs font-semibold capitalize ${riskClass(event.risk_band)}`}>{event.risk_band} {event.risk_score}</span>
              </div>
            </article>
          ))}
        </section>
      ) : (
        <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
          <FileKey2 className="mx-auto h-8 w-8 text-[color:var(--text-tertiary)]" />
          <h2 className="mt-3 font-semibold text-[color:var(--text-primary)]">{payload ? "No compliance events matched" : "Compliance events unavailable"}</h2>
          <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-[color:var(--text-secondary)]">Connect OpenAI, Anthropic, Codex CLI, Cursor, or Claude Code telemetry sources to populate operational activity evidence.</p>
        </section>
      )}
    </div>
  );
}
