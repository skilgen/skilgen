import { ListChecks } from "lucide-react";

import { EmptyPanel, Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";

type AuditEvent = {
  id: string;
  event_type: string;
  actor_login: string | null;
  action: string;
  summary: string;
  resource_type: string | null;
  created_at: string | null;
};

export default async function AdminAuditSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const payload = await v8Fetch<{ events: AuditEvent[] }>(accessToken, org.id, "/admin-audit");
  const events = payload?.events ?? [];

  return (
    <SettingsShell active="Admin audit">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Events" value={events.length} sub="Settings, members, API keys" />
        <Metric label="Retention" value="Audit" sub="Composed from existing audit events" />
        <Metric label="Fallback" value="Empty" sub="Safe when Audit branch is absent" />
      </div>

      {events.length ? (
        <section className="overflow-hidden rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          {events.map((event) => (
            <div className="grid gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 first:border-t-0 md:grid-cols-[180px_1fr_180px]" key={event.id}>
              <div className="font-mono text-[12px] text-[color:var(--text-tertiary)]">{event.event_type}</div>
              <div>
                <div className="text-sm font-semibold text-[color:var(--text-primary)]">{event.summary}</div>
                <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">{event.actor_login ?? "unknown actor"} · {event.resource_type ?? "settings"}</div>
              </div>
              <div className="text-right text-[12px] text-[color:var(--text-tertiary)]">{event.created_at ? new Date(event.created_at).toLocaleString() : "Unknown"}</div>
            </div>
          ))}
        </section>
      ) : (
        <EmptyPanel detail="Settings mutations will appear here as audit events. The table intentionally renders empty when the Audit branch or data is not present." icon={<ListChecks className="h-5 w-5" />} title="No admin audit events yet." />
      )}
    </SettingsShell>
  );
}
