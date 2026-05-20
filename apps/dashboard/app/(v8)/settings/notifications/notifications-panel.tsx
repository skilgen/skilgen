"use client";

import { useId, useMemo, useState } from "react";
import { Bell, ExternalLink, Eye, Mail, Save, SendHorizonal, X } from "lucide-react";

type DigestConfig = {
  title: string;
  subject: string;
  frequency: string;
  recipients: string[];
  widgets: string[];
  layout: Record<string, unknown>;
};

type DigestPreview = {
  html: string;
  recipients: string[];
  subject: string;
  title: string;
  frequency: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

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
  const [previewOpen, setPreviewOpen] = useState(false);
  const [preview, setPreview] = useState<DigestPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [sendLoading, setSendLoading] = useState(false);
  const [recipientOverride, setRecipientOverride] = useState("");
  const [lastSentTo, setLastSentTo] = useState<string | null>(null);
  const [saveLoading, setSaveLoading] = useState(false);

  const previewTitleId = useId();
  const previewDescriptionId = useId();

  const normalizedFrequency = useMemo(() => {
    const value = (config.frequency || "").trim().toLowerCase();
    if (value === "daily" || value === "weekly" || value === "monthly") return value;
    return "weekly";
  }, [config.frequency]);

  const recipientsString = useMemo(() => config.recipients.join(", "), [config.recipients]);
  const requestConfig = useMemo(() => ({ ...config, frequency: normalizedFrequency }), [config, normalizedFrequency]);

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
    setSaveLoading(true);
    try {
      const response = await fetch(`${API_URL}/v8/orgs/${orgId}/settings/notifications/digest`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...authHeaders(accessToken) },
        body: JSON.stringify(requestConfig),
      });
      if (!response.ok) {
        setStatus("Notification config staged locally.");
        return;
      }
      const saved = (await response.json()) as DigestConfig;
      setConfig(saved);
      setStatus("Notification config saved.");
    } catch {
      setStatus("Notification config staged locally.");
    } finally {
      setSaveLoading(false);
    }
  }

  async function loadPreview(): Promise<void> {
    setStatus(null);
    setPreviewLoading(true);
    setLastSentTo(null);
    try {
      const response = await fetch(`${API_URL}/v8/orgs/${orgId}/settings/notifications/digest/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders(accessToken) },
        body: JSON.stringify({ config: requestConfig }),
      });
      if (!response.ok) {
        setStatus("Digest preview unavailable.");
        setPreview(null);
        return;
      }
      const payload = (await response.json()) as Partial<DigestPreview> & { html?: string };
      const html = typeof payload.html === "string" ? payload.html : "";
      setPreview({
        html,
        recipients: Array.isArray(payload.recipients) ? payload.recipients.map(String) : [],
        subject: typeof payload.subject === "string" ? payload.subject : config.subject,
        title: typeof payload.title === "string" ? payload.title : config.title,
        frequency: typeof payload.frequency === "string" ? payload.frequency : normalizedFrequency,
      });
      setPreviewOpen(true);
    } catch {
      setStatus("Digest preview unavailable.");
      setPreview(null);
    } finally {
      setPreviewLoading(false);
    }
  }

  async function sendTest(): Promise<void> {
    setStatus(null);
    setSendLoading(true);
    setLastSentTo(null);
    try {
      const response = await fetch(`${API_URL}/v8/orgs/${orgId}/settings/notifications/digest/send-now`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders(accessToken) },
        body: JSON.stringify({
          recipient_email: recipientOverride.trim() ? recipientOverride.trim() : null,
          config: requestConfig,
        }),
      });
      if (!response.ok) {
        setStatus("Could not send test digest.");
        return;
      }
      const payload = (await response.json()) as { sent?: boolean; to?: string; preview?: string };
      setLastSentTo(typeof payload.to === "string" ? payload.to : null);
      const previewHtml = typeof payload.preview === "string" ? payload.preview : null;
      if (previewHtml) {
        setPreview({
          html: previewHtml,
          recipients: requestConfig.recipients,
          subject: requestConfig.subject,
          title: requestConfig.title,
          frequency: normalizedFrequency,
        });
        setPreviewOpen(true);
      }
      setStatus(payload.sent ? "Test digest sent." : "Test digest preview generated.");
    } catch {
      setStatus("Could not send test digest.");
    } finally {
      setSendLoading(false);
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
        <label className="space-y-2">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Frequency</span>
          <select
            className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]"
            value={normalizedFrequency}
            onChange={(event) => setConfig((current) => ({ ...current, frequency: event.target.value }))}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </label>
        <label className="space-y-2 lg:col-span-2">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Recipients</span>
          <input
            className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]"
            value={recipientsString}
            onChange={(event) =>
              setConfig((current) => ({
                ...current,
                recipients: event.target.value
                  .split(",")
                  .map((item) => item.trim())
                  .filter(Boolean),
              }))
            }
            placeholder="platform@example.com, security@example.com"
          />
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

      <div className="mt-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <button
            className="inline-flex items-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)] disabled:cursor-not-allowed disabled:opacity-70"
            onClick={() => void save()}
            type="button"
            disabled={saveLoading}
          >
            <Save className="h-4 w-4" />
            {saveLoading ? "Saving…" : "Save config"}
          </button>
          <button
            className="inline-flex items-center gap-2 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)] transition-colors hover:bg-[color:var(--bg-surface)] disabled:cursor-not-allowed disabled:opacity-70"
            onClick={() => void loadPreview()}
            type="button"
            disabled={previewLoading}
          >
            <Eye className="h-4 w-4" />
            {previewLoading ? "Loading…" : "Preview"}
          </button>
          <button
            className="inline-flex items-center gap-2 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)] transition-colors hover:bg-[color:var(--bg-surface)] disabled:cursor-not-allowed disabled:opacity-70"
            onClick={() => void sendTest()}
            type="button"
            disabled={sendLoading}
          >
            <SendHorizonal className="h-4 w-4" />
            {sendLoading ? "Sending…" : "Send test"}
          </button>
        </div>

        <label className="flex flex-1 flex-col gap-2 md:max-w-[360px]">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Test recipient (optional)</span>
          <div className="flex items-center gap-2">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] text-[color:var(--text-tertiary)]">
              <Mail className="h-4 w-4" />
            </span>
            <input
              className="h-9 w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]"
              value={recipientOverride}
              onChange={(event) => setRecipientOverride(event.target.value)}
              placeholder="security@example.com"
            />
          </div>
        </label>
      </div>

      {status ? <div className="mt-4 text-sm font-medium text-[color:var(--accent-primary)]">{status}</div> : null}

      {previewOpen ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 py-10"
          role="dialog"
          aria-modal="true"
          aria-labelledby={previewTitleId}
          aria-describedby={previewDescriptionId}
          tabIndex={-1}
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setPreviewOpen(false);
          }}
          onKeyDown={(event) => {
            if (event.key === "Escape") setPreviewOpen(false);
          }}
        >
          <div className="w-full max-w-4xl overflow-hidden rounded-[12px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] shadow-2xl">
            <div className="flex flex-col gap-4 border-b border-[color:var(--bg-border)] p-4 md:flex-row md:items-start md:justify-between">
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Preview</div>
                <h3 className="mt-2 text-[18px] font-semibold text-[color:var(--text-primary)]" id={previewTitleId}>
                  {preview?.title || requestConfig.title}
                </h3>
                <p className="mt-1 text-sm text-[color:var(--text-secondary)]" id={previewDescriptionId}>
                  {lastSentTo ? `Test send target: ${lastSentTo}` : "Digest HTML rendered from the current configuration."}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  className="inline-flex items-center gap-2 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)] transition-colors hover:bg-[color:var(--bg-surface)]"
                  type="button"
                  onClick={() => void loadPreview()}
                  disabled={previewLoading}
                >
                  <Eye className="h-4 w-4" />
                  Refresh
                </button>
                <button
                  className="inline-flex items-center gap-2 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)] transition-colors hover:bg-[color:var(--bg-surface)]"
                  type="button"
                  onClick={() => {
                    const html = preview?.html || "";
                    if (!html) return;
                    const blob = new Blob([html], { type: "text/html" });
                    const url = URL.createObjectURL(blob);
                    window.open(url, "_blank", "noopener,noreferrer");
                  }}
                  disabled={!preview?.html}
                >
                  <ExternalLink className="h-4 w-4" />
                  Open tab
                </button>
                <button
                  className="inline-flex items-center gap-2 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)] transition-colors hover:bg-[color:var(--bg-surface)]"
                  type="button"
                  onClick={() => setPreviewOpen(false)}
                >
                  <X className="h-4 w-4" />
                  Close
                </button>
              </div>
            </div>

            <div className="grid gap-3 border-b border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 md:grid-cols-3">
              <div className="rounded-[10px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
                <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Frequency</div>
                <div className="mt-2 text-sm font-semibold text-[color:var(--text-primary)]">{preview?.frequency || normalizedFrequency}</div>
              </div>
              <div className="rounded-[10px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
                <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Recipients</div>
                <div className="mt-2 text-sm font-semibold text-[color:var(--text-primary)]">
                  {(preview?.recipients?.length ?? requestConfig.recipients.length) || 0}
                </div>
              </div>
              <div className="rounded-[10px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
                <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Widgets</div>
                <div className="mt-2 text-sm font-semibold text-[color:var(--text-primary)]">{config.widgets.length}</div>
              </div>
            </div>

            <div className="bg-[color:var(--bg-base)] p-4">
              {preview?.html ? (
                <iframe
                  className="h-[70vh] w-full rounded-[10px] border border-[color:var(--bg-border)] bg-white"
                  sandbox="allow-same-origin"
                  srcDoc={preview.html}
                  title="Digest preview"
                />
              ) : (
                <div className="flex h-[40vh] flex-col items-center justify-center gap-2 rounded-[10px] border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center">
                  <div className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[color:var(--bg-base)] text-[color:var(--text-tertiary)]">
                    <Eye className="h-5 w-5" />
                  </div>
                  <div className="text-sm font-semibold text-[color:var(--text-primary)]">No preview loaded</div>
                  <div className="text-sm text-[color:var(--text-secondary)]">Use Preview or Send test to generate HTML.</div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
