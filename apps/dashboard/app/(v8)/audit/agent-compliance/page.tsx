import { FileKey2, ShieldCheck } from "lucide-react";

import { getV8AgentComplianceAudit } from "../../../../lib/data";
import { loadAuditOrg } from "../common";

export default async function AgentComplianceAuditPage() {
  const { accessToken, orgId } = await loadAuditOrg();
  const data = orgId ? await getV8AgentComplianceAudit(accessToken, orgId) : null;
  const events = data?.events ?? [];
  const providers = new Set(events.map((event) => event.provider).filter(Boolean));
  const actors = new Set(events.map((event) => event.actor_login).filter(Boolean));

  if (data === null) {
    return (
      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
        <FileKey2 className="mx-auto h-8 w-8 text-[color:var(--text-tertiary)]" />
        <h2 className="mt-3 text-[15px] font-semibold text-[color:var(--text-primary)]">Agent compliance audit unavailable</h2>
        <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-[color:var(--text-secondary)]">Refresh after sign-in. Normalized agent compliance audit events will appear here when the authenticated API call succeeds.</p>
      </section>
    );
  }

  return (
    <div className="space-y-5">
      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Compliance events</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{data.total}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{data.window_days}-day normalized audit window.</p>
        </article>
        <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Providers</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{providers.size}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">OpenAI, Anthropic, Cowork, CLI, and IDE telemetry sources.</p>
        </article>
        <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Retention</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">Metadata</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{data.content_retention} · raw prompt and file content stay out of this view.</p>
        </article>
      </section>

      <section className="rounded-[8px] border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-[color:var(--accent-primary)]" />
          <p className="text-[13px] leading-6 text-[color:var(--text-secondary)]">
            This trail shows normalized agent compliance metadata only: provider, model tier, access scope, policy decision, repo, and source-envelope hash. AgentRun ingestion contributes metadata-only envelopes; raw prompts, chat content, diffs, tool parameters, and file content require explicit tenant retention settings.
          </p>
        </div>
      </section>

      {events.length ? (
        <section className="overflow-hidden rounded-[8px] border border-[color:var(--bg-border)]">
          <div className="grid grid-cols-[170px_1fr_160px_160px_140px_180px] gap-3 bg-black/20 px-4 py-3 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] max-lg:hidden">
            <span>Time</span>
            <span>Source</span>
            <span>Actor</span>
            <span>Access</span>
            <span>Decision</span>
            <span>Envelope</span>
          </div>
          {events.map((event) => (
            <article className="grid gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm first:border-t-0 lg:grid-cols-[170px_1fr_160px_160px_140px_180px]" key={event.id}>
              <div className="font-mono text-xs text-[color:var(--text-secondary)]">{new Date(event.created_at).toLocaleString()}</div>
              <div>
                <h2 className="font-semibold text-[color:var(--text-primary)]">{event.provider ?? event.event_type}</h2>
                <p className="mt-1 text-xs text-[color:var(--text-secondary)]">{event.model ?? "model unknown"} · {event.intelligence_tier ?? "tier unknown"} · {event.repo_name ?? "repo unknown"}</p>
                <p className="mt-2 text-xs leading-5 text-[color:var(--text-tertiary)]">{event.summary}</p>
              </div>
              <div className="flex items-center justify-between gap-3 text-[color:var(--text-secondary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Actor</span>
                <span>{event.actor_login ?? "system"}</span>
              </div>
              <div className="flex items-center justify-between gap-3 text-[color:var(--text-secondary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Access</span>
                <span>{event.access_scope ?? "unspecified"}</span>
              </div>
              <div className="flex items-center justify-between gap-3 text-[color:var(--text-secondary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Decision</span>
                <span>{event.policy_decision ?? "-"}</span>
              </div>
              <div className="flex items-center justify-between gap-3 font-mono text-xs text-[color:var(--accent-primary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Envelope</span>
                <span>{event.source_envelope_hash ? event.source_envelope_hash.slice(0, 16) : "pending"}</span>
              </div>
            </article>
          ))}
        </section>
      ) : (
        <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
          <FileKey2 className="mx-auto h-8 w-8 text-[color:var(--text-tertiary)]" />
          <h2 className="mt-3 font-semibold text-[color:var(--text-primary)]">No agent compliance events yet</h2>
          <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-[color:var(--text-secondary)]">Connect compliance telemetry sources to populate provider, model tier, access scope, and source-envelope evidence.</p>
        </section>
      )}

      <div className="sr-only">{actors.size} actors represented in agent compliance audit metadata.</div>
    </div>
  );
}
