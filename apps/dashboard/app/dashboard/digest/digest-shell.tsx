"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { BarChart3, CheckCircle2, Eye, GripVertical, Mail, MousePointer2, Save, Send } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

export type Digest = {
  week: string;
  org_name: string;
  title?: string;
  subject?: string;
  total_agent_loads: number;
  loads_last_week: number;
  loads_trend: "up" | "down" | "flat";
  active_repos: number;
  top_skill: { name: string; loads: number };
  skill_gap_count: number;
  roi_multiplier: number | null;
  top_gaps: { pattern: string; frequency: number }[];
  memory_score: number;
  html?: string;
};

export type DigestConfig = {
  title: string;
  subject: string;
  frequency: string;
  recipients: string[];
  widgets: string[];
  layout: Record<string, unknown>;
};

type Widget = {
  id: string;
  label: string;
  description: string;
};

const WIDGETS: Widget[] = [
  { id: "memory_score", label: "Memory Score", description: "Board-level knowledge health" },
  { id: "agent_loads", label: "Agent Loads", description: "Weekly agent pull-through" },
  { id: "active_repos", label: "Active Repos", description: "Repos with live skill context" },
  { id: "top_skill", label: "Top Skill", description: "Most-used skill this week" },
  { id: "skill_gaps", label: "Skill Gaps", description: "Open AI quality gaps" },
  { id: "roi_multiplier", label: "ROI Multiplier", description: "Outcome lift from better skills" },
];

const DEFAULT_CONFIG: DigestConfig = {
  title: "Weekly AI Readiness Digest",
  subject: "Your Weekly AI Readiness Report",
  frequency: "weekly",
  recipients: [],
  widgets: WIDGETS.map((widget) => widget.id),
  layout: { columns: 2 },
};

function normalizeConfig(config: Partial<DigestConfig> | null, email: string): DigestConfig {
  return {
    title: config?.title || DEFAULT_CONFIG.title,
    subject: config?.subject || DEFAULT_CONFIG.subject,
    frequency: config?.frequency || DEFAULT_CONFIG.frequency,
    recipients: config?.recipients?.length ? config.recipients : email ? [email] : [],
    widgets: config?.widgets?.length ? config.widgets : DEFAULT_CONFIG.widgets,
    layout: config?.layout || DEFAULT_CONFIG.layout,
  };
}

function authHeader(apiKey: string, accessToken: string): HeadersInit {
  const token = apiKey || accessToken;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function DigestShell({
  orgId,
  apiKey,
  accessToken,
  email,
  initialConfig,
  initialDigest,
}: {
  orgId: string;
  apiKey: string;
  accessToken: string;
  email: string;
  initialConfig: Partial<DigestConfig> | null;
  initialDigest: Digest | null;
}) {
  const [config, setConfig] = useState<DigestConfig>(() => normalizeConfig(initialConfig, email));
  const [digest, setDigest] = useState<Digest | null>(initialDigest);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [htmlPreview, setHtmlPreview] = useState<string | null>(null);
  const selectedWidgets = useMemo(() => WIDGETS.filter((widget) => config.widgets.includes(widget.id)), [config.widgets]);

  function toggleWidget(widgetId: string) {
    setConfig((current) => ({
      ...current,
      widgets: current.widgets.includes(widgetId)
        ? current.widgets.filter((id) => id !== widgetId)
        : [...current.widgets, widgetId],
    }));
  }

  function updateRecipients(value: string) {
    setConfig((current) => ({ ...current, recipients: value.split(",").map((item) => item.trim()).filter(Boolean) }));
  }

  async function saveConfig() {
    setBusy("save");
    setStatus(null);
    try {
      const response = await fetch(`${API_URL}/orgs/${orgId}/digest/config`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...authHeader(apiKey, accessToken) },
        body: JSON.stringify(config),
      });
      setStatus(response.ok ? "Digest configuration saved." : "Could not save digest configuration.");
    } catch {
      setStatus("Could not save digest configuration.");
    } finally {
      setBusy(null);
    }
  }

  async function previewDigest() {
    setBusy("preview");
    setStatus(null);
    try {
      const response = await fetch(`${API_URL}/orgs/${orgId}/digest/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeader(apiKey, accessToken) },
        body: JSON.stringify({ config }),
      });
      const body = response.ok ? ((await response.json()) as Digest) : null;
      if (body) {
        setDigest(body);
        setHtmlPreview(body.html || null);
        setStatus("Preview refreshed.");
      } else {
        setStatus("Could not generate preview.");
      }
    } catch {
      setStatus("Could not generate preview.");
    } finally {
      setBusy(null);
    }
  }

  async function sendNow() {
    setBusy("send");
    setStatus(null);
    try {
      const response = await fetch(`${API_URL}/orgs/${orgId}/digest/send-now`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeader(apiKey, accessToken) },
        body: JSON.stringify({ recipient_email: config.recipients[0] || email || null, config }),
      });
      const body = await response.json().catch(() => null);
      setStatus(body?.sent ? "Digest sent." : "Send provider is not configured. Preview generated instead.");
      if (body?.preview) setHtmlPreview(body.preview);
    } catch {
      setStatus("Could not send digest.");
    } finally {
      setBusy(null);
    }
  }

  if (!orgId) {
    return (
      <div className="space-y-6">
        <Header />
        <EmptyState />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Header />
      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="grid gap-4 lg:grid-cols-[1fr_1fr_auto]">
          <label className="space-y-2">
            <span className="text-[12px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Digest title</span>
            <input className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]" value={config.title} onChange={(event) => setConfig((current) => ({ ...current, title: event.target.value }))} />
          </label>
          <label className="space-y-2">
            <span className="text-[12px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Recipients</span>
            <input className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]" value={config.recipients.join(", ")} onChange={(event) => updateRecipients(event.target.value)} placeholder="vp-eng@example.com, team@example.com" />
          </label>
          <div className="flex flex-wrap items-end gap-2">
            <button className="inline-flex items-center gap-2 rounded-[8px] border border-[color:var(--bg-border)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)] disabled:opacity-50" disabled={busy !== null} onClick={() => void saveConfig()}><Save className="h-4 w-4" />{busy === "save" ? "Saving" : "Save"}</button>
            <button className="inline-flex items-center gap-2 rounded-[8px] border border-[color:var(--bg-border)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)] disabled:opacity-50" disabled={busy !== null} onClick={() => void previewDigest()}><Eye className="h-4 w-4" />{busy === "preview" ? "Previewing" : "Preview"}</button>
            <button className="inline-flex items-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)] disabled:opacity-50" disabled={busy !== null} onClick={() => void sendNow()}><Send className="h-4 w-4" />{busy === "send" ? "Sending" : "Send now"}</button>
          </div>
        </div>
        {status ? <p className="mt-3 text-sm text-[color:var(--accent-primary)]">{status}</p> : null}
      </section>

      <div className="grid gap-5 xl:grid-cols-[360px_1fr]">
        <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">Widget library</h2>
            <span className="text-[12px] text-[color:var(--text-tertiary)]">{config.widgets.length}/{WIDGETS.length} active</span>
          </div>
          <div className="mt-4 space-y-3">
            {WIDGETS.map((widget) => {
              const active = config.widgets.includes(widget.id);
              return (
                <button key={widget.id} className={`w-full rounded-[8px] border p-4 text-left transition ${active ? "border-[color:var(--accent-primary)] bg-[color:var(--accent-primary)]/10" : "border-[color:var(--bg-border)] bg-black/10 hover:border-[color:var(--accent-primary)]/40"}`} onClick={() => toggleWidget(widget.id)}>
                  <div className="flex items-start gap-3">
                    <div className={`mt-0.5 flex h-5 w-5 items-center justify-center rounded-full border ${active ? "border-[color:var(--accent-primary)] text-[color:var(--accent-primary)]" : "border-[color:var(--text-tertiary)] text-transparent"}`}>
                      <CheckCircle2 className="h-3.5 w-3.5" />
                    </div>
                    <div>
                      <div className="font-semibold text-[color:var(--text-primary)]">{widget.label}</div>
                      <div className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{widget.description}</div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </section>

        <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="flex flex-col justify-between gap-3 border-b border-[color:var(--bg-border)] px-5 py-4 md:flex-row md:items-center">
            <div>
              <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">Digest canvas</h2>
              <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Selected widgets render in the order they will appear in the digest.</p>
            </div>
            <span className="inline-flex items-center gap-2 text-[12px] text-[color:var(--text-tertiary)]"><MousePointer2 className="h-4 w-4" /> Click widgets to add or remove</span>
          </div>
          <div className="p-5">
            {selectedWidgets.length === 0 ? (
              <div className="rounded-[8px] border border-dashed border-[color:var(--bg-border)] p-10 text-center text-sm text-[color:var(--text-secondary)]">Choose at least one widget to build a digest.</div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {selectedWidgets.map((widget) => (
                  <CanvasWidget key={widget.id} digest={digest} widget={widget} />
                ))}
              </div>
            )}
          </div>
        </section>
      </div>

      {htmlPreview ? <PreviewModal html={htmlPreview} onClose={() => setHtmlPreview(null)} /> : null}
    </div>
  );
}

function Header() {
  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--accent-primary)]">Digest builder</p>
      <h1 className="mt-2 text-2xl font-semibold text-[color:var(--text-primary)]">Custom AI Readiness Digest</h1>
      <p className="mt-1 max-w-3xl text-sm text-[color:var(--text-secondary)]">Design the executive update your team receives: pick widgets, preview the email, save the layout, and send a one-off digest.</p>
    </div>
  );
}

function CanvasWidget({ digest, widget }: { digest: Digest | null; widget: Widget }) {
  if (!digest) {
    return <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-5 text-sm text-[color:var(--text-secondary)]">{widget.label} preview will appear after agent activity is available.</article>;
  }
  const content = widgetValue(widget.id, digest);
  return (
    <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-[12px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">{widget.label}</div>
          <div className="mt-3 text-3xl font-semibold text-[color:var(--text-primary)]">{content.value}</div>
        </div>
        <GripVertical className="h-5 w-5 text-[color:var(--text-tertiary)]" />
      </div>
      <p className="mt-3 text-sm text-[color:var(--text-secondary)]">{content.sub}</p>
    </article>
  );
}

function widgetValue(widgetId: string, digest: Digest): { value: string | number; sub: string } {
  if (widgetId === "memory_score") return { value: `${digest.memory_score}/100`, sub: "Current organizational memory score" };
  if (widgetId === "agent_loads") return { value: digest.total_agent_loads, sub: `${digest.loads_last_week} loads in the previous week` };
  if (widgetId === "active_repos") return { value: digest.active_repos, sub: "Repositories represented in this digest" };
  if (widgetId === "top_skill") return { value: digest.top_skill.name, sub: `${digest.top_skill.loads} loads this week` };
  if (widgetId === "skill_gaps") return { value: digest.skill_gap_count, sub: digest.top_gaps.length ? digest.top_gaps.map((gap) => gap.pattern).join(", ") : "No open gaps detected" };
  if (widgetId === "roi_multiplier") return { value: digest.roi_multiplier ? `${digest.roi_multiplier}x` : "N/A", sub: "High-score skill outcome lift" };
  return { value: "Ready", sub: "Widget configured" };
}

function EmptyState() {
  return (
    <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center">
      <Mail className="mx-auto h-10 w-10 text-[color:var(--accent-primary)]" />
      <h2 className="mt-4 text-xl font-semibold text-[color:var(--text-primary)]">Connect an organization to build a digest.</h2>
      <p className="mt-2 text-[color:var(--text-secondary)]">Once Skillayer can read your org, this page becomes a configurable executive report.</p>
      <Link className="mt-5 inline-flex rounded-[8px] bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]" href="/dashboard/connect">Connect agent</Link>
    </section>
  );
}

function PreviewModal({ html, onClose }: { html: string; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4">
      <div className="max-h-[82vh] w-full max-w-4xl overflow-auto rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div className="inline-flex items-center gap-2 text-sm font-semibold text-[color:var(--text-primary)]"><BarChart3 className="h-4 w-4" /> Email preview</div>
          <button className="rounded-[8px] border border-[color:var(--bg-border)] px-3 py-1.5 text-sm text-[color:var(--text-primary)]" onClick={onClose}>Close</button>
        </div>
        <div dangerouslySetInnerHTML={{ __html: html }} />
      </div>
    </div>
  );
}
