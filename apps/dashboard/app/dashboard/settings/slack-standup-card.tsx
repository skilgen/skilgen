"use client";

import { CheckCircle2, Loader2, Send, Slack, Save } from "lucide-react";
import { useMemo, useState } from "react";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Props = {
  accessToken: string;
  orgId: string;
  initialWebhookUrl: string | null;
  initialEnabled?: boolean;
  initialHour?: number;
};

type Status = {
  tone: "success" | "error";
  message: string;
} | null;

function headers(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

export function SlackStandupCard({ accessToken, orgId, initialWebhookUrl, initialEnabled = false, initialHour = 9 }: Props) {
  const [webhookUrl, setWebhookUrl] = useState(initialWebhookUrl ?? "");
  const [enabled, setEnabled] = useState(Boolean(initialEnabled));
  const [hour, setHour] = useState(Number.isFinite(initialHour) ? initialHour : 9);
  const [saving, setSaving] = useState(false);
  const [sending, setSending] = useState(false);
  const [status, setStatus] = useState<Status>(null);

  const body = useMemo(
    () => ({
      webhook_url: webhookUrl.trim() || null,
      standup_enabled: enabled,
      standup_hour: hour,
    }),
    [enabled, hour, webhookUrl],
  );

  async function save(): Promise<void> {
    setSaving(true);
    setStatus(null);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/settings/slack`, {
        method: "PATCH",
        headers: headers(accessToken),
        body: JSON.stringify(body),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || "Could not save Slack standup settings");
      setStatus({ tone: "success", message: "Slack standup settings saved" });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "Could not save Slack standup settings" });
    } finally {
      setSaving(false);
    }
  }

  async function sendTest(): Promise<void> {
    setSending(true);
    setStatus(null);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/standup/send`, {
        method: "POST",
        headers: headers(accessToken),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) throw new Error(payload.message || payload.detail || "Could not send the standup");
      setStatus({ tone: "success", message: payload.message || "Test standup sent to Slack" });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "Could not send the standup" });
    } finally {
      setSending(false);
    }
  }

  return (
    <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-6">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-[color:var(--bg-border)] bg-black/15 px-3 py-1 text-xs font-semibold text-[color:var(--text-secondary)]">
            <Slack className="h-3.5 w-3.5" /> Daily standup
          </div>
          <h2 className="mt-3 text-[20px] font-semibold text-[color:var(--text-primary)]">Slack Integration</h2>
          <p className="mt-1 max-w-2xl text-[13px] text-[color:var(--text-secondary)]">Post a daily Skillayer standup with agent sessions, PR risk, top skills, and violations across the org.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="inline-flex h-9 items-center rounded-md border border-[#C9973A]/60 px-4 text-[13px] font-semibold text-[#C9973A] transition-colors hover:bg-[#C9973A]/10 disabled:cursor-wait disabled:opacity-60" disabled={sending || !webhookUrl.trim()} onClick={sendTest} type="button">
            {sending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
            Send test
          </button>
          <button className="inline-flex h-9 items-center rounded-md bg-[#C9973A] px-4 text-[13px] font-semibold text-black transition-colors hover:bg-[#d7aa55] disabled:cursor-wait disabled:opacity-60" disabled={saving} onClick={save} type="button">
            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
            Save
          </button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_180px_180px]">
        <label className="block">
          <span className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Slack webhook URL</span>
          <input className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[#08080d] px-3 font-mono text-[13px] text-white outline-none transition-colors focus:border-[#C9973A]" onChange={(event) => setWebhookUrl(event.target.value)} placeholder="https://hooks.slack.com/services/..." value={webhookUrl} />
        </label>
        <label className="block">
          <span className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">UTC hour</span>
          <select className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[#08080d] px-3 text-[14px] text-[color:var(--text-primary)]" onChange={(event) => setHour(Number(event.target.value))} value={hour}>
            {Array.from({ length: 24 }, (_, value) => (
              <option key={value} value={value}>{String(value).padStart(2, "0")}:00 UTC</option>
            ))}
          </select>
        </label>
        <button aria-pressed={enabled} className="mt-6 flex h-11 items-center justify-between rounded-xl border border-[color:var(--bg-border)] bg-[#08080d] px-4 text-left transition-colors hover:border-[#C9973A]/50" onClick={() => setEnabled((current) => !current)} type="button">
          <span className="text-[14px] font-semibold text-[color:var(--text-primary)]">Standup enabled</span>
          <span className={enabled ? "relative h-6 w-11 rounded-full bg-[#C9973A]" : "relative h-6 w-11 rounded-full bg-[color:var(--bg-border)]"}>
            <span className={enabled ? "absolute right-1 top-1 h-4 w-4 rounded-full bg-black" : "absolute left-1 top-1 h-4 w-4 rounded-full bg-[color:var(--text-tertiary)]"} />
          </span>
        </button>
      </div>

      {status ? (
        <div className={status.tone === "success" ? "mt-5 flex items-center gap-2 rounded-md border border-[#3dd68c]/30 bg-[#3dd68c]/10 px-3 py-2 text-[13px] font-medium text-[#91efbd]" : "mt-5 rounded-md border border-[color:var(--accent-red)]/30 bg-[color:var(--accent-red)]/10 px-3 py-2 text-[13px] font-medium text-[color:var(--accent-red)]"}>
          {status.tone === "success" ? <CheckCircle2 className="h-4 w-4" /> : null}
          {status.message}
        </div>
      ) : null}
    </section>
  );
}
