"use client";

import { CheckCircle2, Loader2, Mail, Save, Send } from "lucide-react";
import { useMemo, useState } from "react";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Props = {
  accessToken: string;
  orgId: string;
  initialEmail?: string | null;
  initialEnabled?: boolean;
  initialDay?: number;
  initialHour?: number;
  initialLastSentAt?: string | null;
};

type Status = {
  tone: "success" | "error";
  message: string;
} | null;

const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

function headers(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

function lastSentLabel(value: string | null | undefined): string {
  if (!value) return "Never sent";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Never sent";
  return date.toLocaleString();
}

export function EmailDigestCard({ accessToken, orgId, initialEmail, initialEnabled = false, initialDay = 1, initialHour = 8, initialLastSentAt = null }: Props) {
  const [email, setEmail] = useState(initialEmail ?? "");
  const [enabled, setEnabled] = useState(Boolean(initialEnabled));
  const [day, setDay] = useState(Number.isFinite(initialDay) ? initialDay : 1);
  const [hour, setHour] = useState(Number.isFinite(initialHour) ? initialHour : 8);
  const [lastSentAt, setLastSentAt] = useState<string | null>(initialLastSentAt);
  const [saving, setSaving] = useState(false);
  const [sending, setSending] = useState(false);
  const [status, setStatus] = useState<Status>(null);

  const body = useMemo(
    () => ({
      digest_email: email.trim() || null,
      digest_enabled: enabled,
      digest_day: day,
      digest_hour: hour,
    }),
    [day, email, enabled, hour],
  );

  async function save(): Promise<void> {
    setSaving(true);
    setStatus(null);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/settings/email-digest`, {
        method: "PATCH",
        headers: headers(accessToken),
        body: JSON.stringify(body),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || "Could not save email digest settings");
      setEmail(payload.digest_email ?? body.digest_email ?? "");
      setEnabled(Boolean(payload.digest_enabled));
      setDay(Number.isFinite(payload.digest_day) ? Number(payload.digest_day) : day);
      setHour(Number.isFinite(payload.digest_hour) ? Number(payload.digest_hour) : hour);
      setLastSentAt(payload.digest_last_sent_at ?? lastSentAt);
      setStatus({ tone: "success", message: "Email digest settings saved" });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "Could not save email digest settings" });
    } finally {
      setSaving(false);
    }
  }

  async function sendTest(): Promise<void> {
    setSending(true);
    setStatus(null);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/digest/send`, {
        method: "POST",
        headers: headers(accessToken),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) throw new Error(payload.message || payload.detail || "Could not send the email digest");
      setLastSentAt(new Date().toISOString());
      setStatus({ tone: "success", message: payload.message || "Test digest sent" });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "Could not send the email digest" });
    } finally {
      setSending(false);
    }
  }

  return (
    <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-6">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-[color:var(--bg-border)] bg-black/15 px-3 py-1 text-xs font-semibold text-[color:var(--text-secondary)]">
            <Mail className="h-3.5 w-3.5" /> Weekly digest
          </div>
          <h2 className="mt-3 text-[20px] font-semibold text-[color:var(--text-primary)]">Weekly Email Digest</h2>
          <p className="mt-1 max-w-2xl text-[13px] text-[color:var(--text-secondary)]">Send agent scorecards, top developers, and skill violations to your team inbox.</p>
          <p className="mt-2 text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Last digest sent: {lastSentLabel(lastSentAt)}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="inline-flex h-9 items-center rounded-md border border-[#C9973A]/60 px-4 text-[13px] font-semibold text-[#C9973A] transition-colors hover:bg-[#C9973A]/10 disabled:cursor-wait disabled:opacity-60" disabled={sending || !email.trim()} onClick={sendTest} type="button">
            {sending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
            Send test digest now
          </button>
          <button className="inline-flex h-9 items-center rounded-md bg-[#C9973A] px-4 text-[13px] font-semibold text-black transition-colors hover:bg-[#d7aa55] disabled:cursor-wait disabled:opacity-60" disabled={saving} onClick={save} type="button">
            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
            Save
          </button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_180px_180px_180px]">
        <label className="block">
          <span className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Digest email</span>
          <input className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[#08080d] px-3 text-[13px] text-white outline-none transition-colors focus:border-[#C9973A]" onChange={(event) => setEmail(event.target.value)} placeholder="team@example.com" type="email" value={email} />
        </label>
        <label className="block">
          <span className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Day</span>
          <select className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[#08080d] px-3 text-[14px] text-[color:var(--text-primary)]" onChange={(event) => setDay(Number(event.target.value))} value={day}>
            {days.map((label, value) => (
              <option key={label} value={value}>{label}</option>
            ))}
          </select>
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
          <span className="text-[14px] font-semibold text-[color:var(--text-primary)]">Digest enabled</span>
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
