"use client";

import { useState } from "react";
import { Save, SlidersHorizontal } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

export type AdminAuditConfig = {
  default_window_days: number;
  default_severity: "all" | "info" | "warning" | "critical";
  retention_days: number;
  export_event_filter: "all" | "warnings" | "critical";
  updated_at?: string | null;
};

function authHeaders(accessToken: string): HeadersInit {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

export function AdminAuditConfigPanel({ accessToken, initial, orgId }: { accessToken: string; initial: AdminAuditConfig; orgId: string }) {
  const [config, setConfig] = useState<AdminAuditConfig>(initial);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  async function saveConfig() {
    setSaving(true);
    setStatus(null);
    try {
      const response = await fetch(`${API_URL}/v8/orgs/${orgId}/settings/admin-audit/config`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...authHeaders(accessToken) },
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        setStatus("Could not save audit settings.");
        return;
      }
      const saved = (await response.json()) as AdminAuditConfig;
      setConfig(saved);
      setStatus("Audit settings saved.");
    } catch {
      setStatus("Could not save audit settings.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-5 w-5 text-[color:var(--accent-primary)]" />
          <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Audit controls</h2>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {status ? <p className="text-sm font-medium text-[color:var(--text-secondary)]" role="status">{status}</p> : null}
          <button
            className="inline-flex min-h-10 items-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-4 text-sm font-semibold text-black transition hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={saving}
            onClick={() => void saveConfig()}
            type="button"
          >
            <Save className="h-4 w-4" />
            {saving ? "Saving" : "Save audit settings"}
          </button>
        </div>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <label className="block rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Default window</span>
          <select
            className="mt-2 w-full rounded-md border border-[color:var(--bg-border)] bg-black/20 px-3 py-2 text-sm text-[color:var(--text-primary)]"
            onChange={(event) => setConfig((current) => ({ ...current, default_window_days: Number(event.target.value) }))}
            value={config.default_window_days}
          >
            <option value={7}>7 days</option>
            <option value={30}>30 days</option>
            <option value={90}>90 days</option>
            <option value={180}>180 days</option>
            <option value={365}>365 days</option>
          </select>
        </label>
        <label className="block rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Default severity</span>
          <select
            className="mt-2 w-full rounded-md border border-[color:var(--bg-border)] bg-black/20 px-3 py-2 text-sm text-[color:var(--text-primary)]"
            onChange={(event) => setConfig((current) => ({ ...current, default_severity: event.target.value as AdminAuditConfig["default_severity"] }))}
            value={config.default_severity}
          >
            <option value="all">All</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
        </label>
        <label className="block rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Retention</span>
          <select
            className="mt-2 w-full rounded-md border border-[color:var(--bg-border)] bg-black/20 px-3 py-2 text-sm text-[color:var(--text-primary)]"
            onChange={(event) => setConfig((current) => ({ ...current, retention_days: Number(event.target.value) }))}
            value={config.retention_days}
          >
            <option value={90}>90 days</option>
            <option value={180}>180 days</option>
            <option value={365}>365 days</option>
            <option value={730}>730 days</option>
            <option value={2555}>2555 days</option>
          </select>
        </label>
        <label className="block rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Export filter</span>
          <select
            className="mt-2 w-full rounded-md border border-[color:var(--bg-border)] bg-black/20 px-3 py-2 text-sm text-[color:var(--text-primary)]"
            onChange={(event) => setConfig((current) => ({ ...current, export_event_filter: event.target.value as AdminAuditConfig["export_event_filter"] }))}
            value={config.export_event_filter}
          >
            <option value="all">All</option>
            <option value="warnings">Warnings</option>
            <option value="critical">Critical</option>
          </select>
        </label>
      </div>
    </section>
  );
}
