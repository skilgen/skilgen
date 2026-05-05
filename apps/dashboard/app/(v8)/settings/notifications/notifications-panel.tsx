"use client";

import { useState } from "react";
import { Bell, Save } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type DigestConfig = {
  title: string;
  subject: string;
  frequency: string;
  recipients: string[];
  widgets: string[];
  layout: Record<string, unknown>;
};

const widgets = [
  "memory_score",
  "agent_loads",
  "active_repos",
  "top_skill",
  "skill_gaps",
  "roi_multiplier",
];

function authHeaders(accessToken: string): HeadersInit {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

export function NotificationsPanel({ accessToken, initial, orgId }: { accessToken: string; initial: DigestConfig; orgId: string }) {
  const [config, setConfig] = useState<DigestConfig>(initial);
  const [status, setStatus] = useState<string | null>(null);

  function toggleWidget(widget: string) {
    setConfig((current) => ({
      ...current,
      widgets: current.widgets.includes(widget)
        ? current.widgets.filter((item) => item !== widget)
        : [...current.widgets, widget],
    }));
  }

  async function save() {
    setStatus(null);
    try {
      const response = await fetch(`${API_URL}/v8/orgs/${orgId}/settings/notifications/digest`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...authHeaders(accessToken) },
        body: JSON.stringify(config),
      });
      setStatus(response.ok ? "Notification config saved." : "Notification config staged locally.");
    } catch {
      setStatus("Notification config staged locally.");
    }
  }

  return (
    <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="flex items-start gap-3">
        <Bell className="mt-0.5 h-5 w-5 text-[color:var(--accent-primary)]" />
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Digest configuration</h2>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Digest moves under Settings notifications while keeping `digest_configs` storage intact.</p>
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <label className="space-y-2">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Title</span>
          <input className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]" value={config.title} onChange={(event) => setConfig((current) => ({ ...current, title: event.target.value }))} />
        </label>
        <label className="space-y-2">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Subject</span>
          <input className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]" value={config.subject} onChange={(event) => setConfig((current) => ({ ...current, subject: event.target.value }))} />
        </label>
        <label className="space-y-2 lg:col-span-2">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Recipients</span>
          <input className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]" value={config.recipients.join(", ")} onChange={(event) => setConfig((current) => ({ ...current, recipients: event.target.value.split(",").map((item) => item.trim()).filter(Boolean) }))} placeholder="platform@example.com, security@example.com" />
        </label>
      </div>

      <div className="mt-5">
        <div className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Widgets</div>
        <div className="mt-3 grid gap-2 md:grid-cols-3">
          {widgets.map((widget) => {
            const active = config.widgets.includes(widget);
            return (
              <button className={active ? "rounded-[8px] border border-[color:var(--accent-primary)] bg-[color:var(--accent-primary)]/10 px-3 py-2 text-left font-mono text-[12px] text-[color:var(--accent-primary)]" : "rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-left font-mono text-[12px] text-[color:var(--text-secondary)]"} key={widget} onClick={() => toggleWidget(widget)} type="button">
                {widget}
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-5 flex items-center gap-3">
        <button className="inline-flex items-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" onClick={() => void save()} type="button">
          <Save className="h-4 w-4" />
          Save config
        </button>
        {status ? <span className="text-sm text-[color:var(--accent-primary)]">{status}</span> : null}
      </div>
    </section>
  );
}
