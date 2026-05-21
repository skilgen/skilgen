import { Filter, ListChecks, ShieldAlert } from "lucide-react";

import { EmptyPanel, Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";
import { AdminAuditConfigPanel, type AdminAuditConfig } from "./admin-audit-config-panel";

type AuditEvent = {
  id: string;
  event_type: string;
  actor_login: string | null;
  action: string;
  summary: string;
  resource_type: string | null;
  resource_id?: string | null;
  severity: "info" | "warning" | "critical";
  created_at: string | null;
};

type CountRow = {
  key: string;
  label: string;
  count: number;
};

type AdminAuditPayload = {
  window_days: number;
  summary: {
    events: number;
    actors: number;
    critical: number;
    warnings: number;
    resource_types: number;
  };
  event_types: CountRow[];
  resource_types: CountRow[];
  rollup?: {
    source_events: number;
    limit: number;
    truncated: boolean;
  };
  severity_counts: Record<"info" | "warning" | "critical", number>;
  events: AuditEvent[];
};

const fallbackConfig: AdminAuditConfig = {
  default_window_days: 30,
  default_severity: "all",
  retention_days: 365,
  export_event_filter: "warnings",
};

function value(params: URLSearchParams, key: string) {
  return params.get(key) ?? "";
}

function severityClass(severity: AuditEvent["severity"]) {
  if (severity === "critical") return "border-red-500/40 bg-red-500/10 text-red-200";
  if (severity === "warning") return "border-amber-500/40 bg-amber-500/10 text-amber-100";
  return "border-[color:var(--bg-border)] bg-black/15 text-[color:var(--text-secondary)]";
}

export default async function AdminAuditSettingsPage({ searchParams }: { searchParams?: Promise<Record<string, string | string[] | undefined>> }) {
  const { accessToken, org } = await loadSettingsContext();
  const rawParams = await searchParams;
  const params = new URLSearchParams();
  for (const [key, rawValue] of Object.entries(rawParams ?? {})) {
    const current = Array.isArray(rawValue) ? rawValue[0] : rawValue;
    if (current) params.set(key, current);
  }
  const query = params.toString();
  const [payload, config] = await Promise.all([
    v8Fetch<AdminAuditPayload>(accessToken, org.id, `/admin-audit${query ? `?${query}` : ""}`),
    v8Fetch<AdminAuditConfig>(accessToken, org.id, "/admin-audit/config"),
  ]);
  const events = payload?.events ?? [];
  const summary = payload?.summary ?? { events: 0, actors: 0, critical: 0, warnings: 0, resource_types: 0 };
  const windowDays = payload?.window_days ?? (Number(value(params, "window_days")) || 30);
  const auditConfig = config ?? fallbackConfig;

  return (
    <SettingsShell active="Admin audit">
      <div className="grid gap-4 md:grid-cols-5">
        <Metric label="Events" value={summary.events} sub={`${windowDays}-day window`} />
        <Metric label="Actors" value={summary.actors} sub="Administrators represented" />
        <Metric label="Warnings" value={summary.warnings} sub="Needs review" />
        <Metric label="Critical" value={summary.critical} sub="Escalate immediately" />
        <Metric label="Resources" value={summary.resource_types} sub="Touched settings areas" />
      </div>

      <AdminAuditConfigPanel accessToken={accessToken} initial={auditConfig} orgId={org.id} />

      <form className="grid gap-3 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-[repeat(5,minmax(0,1fr))_auto]" method="get">
        <input className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={value(params, "actor")} name="actor" placeholder="Actor" />
        <input className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={value(params, "event_type")} name="event_type" placeholder="Event type" />
        <input className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={value(params, "resource_type")} name="resource_type" placeholder="Resource" />
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={value(params, "severity")} name="severity">
          <option value="">Any severity</option>
          <option value="info">Info</option>
          <option value="warning">Warning</option>
          <option value="critical">Critical</option>
        </select>
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={value(params, "window_days") || String(auditConfig.default_window_days)} name="window_days">
          <option value="7">7 days</option>
          <option value="30">30 days</option>
          <option value="90">90 days</option>
          <option value="180">180 days</option>
          <option value="365">365 days</option>
        </select>
        <button className="inline-flex items-center justify-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" type="submit">
          <Filter className="h-4 w-4" />
          Apply
        </button>
      </form>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Event type mix</h2>
          <div className="mt-4 space-y-3">
            {(payload?.event_types ?? []).map((row) => (
              <div className="grid grid-cols-[1fr_auto] gap-3 text-sm" key={row.key}>
                <span className="truncate font-mono text-xs text-[color:var(--text-secondary)]">{row.label}</span>
                <span className="font-semibold text-[color:var(--text-primary)]">{row.count}</span>
              </div>
            ))}
            {!payload?.event_types?.length ? <p className="text-sm text-[color:var(--text-secondary)]">No settings audit event types in this window.</p> : null}
          </div>
        </div>
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Resource coverage</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {(payload?.resource_types ?? []).map((row) => (
              <span className="rounded-md border border-[color:var(--bg-border)] bg-black/15 px-2.5 py-1 text-xs text-[color:var(--text-secondary)]" key={row.key}>
                {row.label} · {row.count}
              </span>
            ))}
            {!payload?.resource_types?.length ? <p className="text-sm text-[color:var(--text-secondary)]">No settings resources touched yet.</p> : null}
          </div>
        </div>
      </section>

      {payload?.rollup?.truncated ? (
        <div className="rounded-[8px] border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
          Rollups are based on the latest {payload.rollup.limit.toLocaleString()} matching events. Narrow the filters for a complete distribution.
        </div>
      ) : null}

      {events.length ? (
        <section className="overflow-hidden rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="grid grid-cols-[minmax(220px,0.9fr)_minmax(0,1.6fr)_150px_120px_170px] gap-3 bg-black/20 px-4 py-3 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] max-lg:hidden">
            <span>Event</span>
            <span>Summary</span>
            <span>Actor</span>
            <span>Severity</span>
            <span>Time</span>
          </div>
          {events.map((event) => (
            <article className="grid gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm first:border-t-0 lg:grid-cols-[minmax(220px,0.9fr)_minmax(0,1.6fr)_150px_120px_170px]" key={event.id}>
              <div className="min-w-0 truncate font-mono text-xs text-[color:var(--text-tertiary)]" title={event.event_type}>{event.event_type}</div>
              <div className="min-w-0">
                <div className="font-semibold text-[color:var(--text-primary)]">{event.summary}</div>
                <div className="mt-1 text-xs text-[color:var(--text-secondary)]">{event.action} · {event.resource_type ?? "settings"}{event.resource_id ? ` · ${event.resource_id}` : ""}</div>
              </div>
              <div className="text-[color:var(--text-secondary)]">{event.actor_login ?? "system"}</div>
              <div>
                <span className={`inline-flex rounded-md border px-2 py-1 text-xs font-semibold capitalize ${severityClass(event.severity)}`}>{event.severity}</span>
              </div>
              <div className="text-right text-xs text-[color:var(--text-tertiary)] lg:text-left">{event.created_at ? new Date(event.created_at).toLocaleString() : "Unknown"}</div>
            </article>
          ))}
        </section>
      ) : (
        <EmptyPanel detail="Settings mutations, member changes, and API key rotations will appear here as filtered audit evidence." icon={<ListChecks className="h-5 w-5" />} title={payload ? "No admin audit events matched." : "Admin audit unavailable."} />
      )}

      <div className="sr-only">
        <ShieldAlert className="h-4 w-4" />
        {payload?.severity_counts.critical ?? 0} critical settings audit events.
      </div>
    </SettingsShell>
  );
}
