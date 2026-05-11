"use client";

import { Archive, CheckCircle2, FileKey2, PackagePlus, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type EvidenceResult = {
  control?: string;
  period_start?: string;
  period_end?: string;
  index_format?: string;
  content_retention?: string;
  included_files?: string[];
  excluded_raw_content_keys?: string[];
  agent_compliance?: {
    status?: string;
    metrics?: string[];
    summary?: Record<string, number | string | null>;
  };
};

type V8EvidencePackage = {
  job_id: string;
  status: string;
  queued: boolean;
  result?: EvidenceResult;
  created_at?: string;
};

const defaultControls = ["SOC2 CC8.1", "ISO 27001 A.8.15", "NIST AI RMF GOVERN-1"];

const coreMetricLabels: Record<string, string> = {
  events: "Events",
  users: "Users",
  providers: "Providers",
  sessions: "Sessions",
  repos: "Repos",
  tool_permission_events: "Tool permissions",
  mcp_tool_events: "MCP tools",
  file_targets: "File targets",
  full_access_events: "Full access",
  autonomous_events: "Autonomous",
  approvals: "Approvals",
  denials: "Denials",
  warnings: "Warnings",
  violations: "Violations",
  errors: "Errors",
  tokens_total: "Tokens",
  cost_usd: "Cost",
  source_envelope_hashes: "Envelope hashes",
  top_tools: "Top tools",
  top_mcp_tools: "Top MCP tools",
  top_files: "Top files",
  policy_decisions: "Policy decisions",
  approval_statuses: "Approval statuses",
  source_record_types: "Source record types",
  retention_states: "Retention states",
};

function labelForMetric(metric: string) {
  return coreMetricLabels[metric] ?? metric.replaceAll("_", " ");
}

function shortId(value: string) {
  return value.length > 12 ? `${value.slice(0, 8)}...${value.slice(-4)}` : value;
}

export function EvidencePackagesClient({ accessToken, orgId }: { accessToken: string; orgId: string }) {
  const [control, setControl] = useState(defaultControls[0]);
  const [days, setDays] = useState(90);
  const [result, setResult] = useState<V8EvidencePackage | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const previewMetrics = useMemo(() => result?.result?.agent_compliance?.metrics ?? [], [result]);
  const includedFiles = result?.result?.included_files ?? ["index.html", "manifest.json", "events.json", "agent-compliance-summary.json", "chain-root.json"];
  const excludedKeys = result?.result?.excluded_raw_content_keys ?? ["prompt", "raw_prompt", "messages", "diff", "file_content", "tool_parameters"];

  async function createPackage() {
    setBusy(true);
    setError(null);
    const now = new Date();
    const start = new Date(now);
    start.setDate(now.getDate() - days);
    try {
      const response = await fetch(`${CLIENT_API_URL}/v8/orgs/${orgId}/audit/evidence-packages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        },
        body: JSON.stringify({ control, period_start: start.toISOString(), period_end: now.toISOString() }),
      });
      if (!response.ok) {
        setResult(null);
        setError("Evidence package request failed. Check audit API access and try again.");
        return;
      }
      setResult((await response.json()) as V8EvidencePackage);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-5">
      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="flex items-start gap-3">
            <FileKey2 className="mt-1 h-5 w-5 shrink-0 text-[color:var(--accent-primary)]" />
            <div>
              <h2 className="text-base font-semibold text-[color:var(--text-primary)]">Agent compliance evidence package</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-[color:var(--text-secondary)]">
                Queue auditor-ready proof for the selected control with hash-chain context, policy snapshots, skill versions, and consolidated coding-agent compliance metrics.
              </p>
            </div>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-[1fr_150px_auto]">
            <select
              aria-label="Evidence control"
              className="h-10 rounded-md border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm text-[color:var(--text-primary)]"
              onChange={(event) => setControl(event.target.value)}
              value={control}
            >
              {defaultControls.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <select
              aria-label="Evidence window"
              className="h-10 rounded-md border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm text-[color:var(--text-primary)]"
              onChange={(event) => setDays(Number(event.target.value))}
              value={days}
            >
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
              <option value={180}>180 days</option>
            </select>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 text-sm font-semibold text-[color:var(--bg-base)] disabled:opacity-60"
              disabled={busy || !orgId}
              onClick={createPackage}
              type="button"
            >
              <PackagePlus className="h-4 w-4" />
              {busy ? "Queueing" : "Create"}
            </button>
          </div>
        </div>

        <div className="rounded-[8px] border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-[color:var(--accent-primary)]" />
            <div>
              <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Metadata-only retention</h2>
              <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">
                Packages include every normalized compliance metric from agent telemetry while excluding raw prompts, chat content, diffs, file content, and tool arguments.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Package status</div>
          <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">{result ? result.status : "Ready"}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{result?.queued ? `Queued as ${shortId(result.job_id)}` : "Select a control and queue the package."}</p>
        </article>
        <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Control</div>
          <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">{control}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{days}-day evidence window.</p>
        </article>
        <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Retention</div>
          <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">Metadata</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{result?.result?.content_retention ?? "metadata-only"} package contents.</p>
        </article>
      </section>

      {error ? <div className="rounded-[8px] border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">{error}</div> : null}

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="flex items-center gap-2 border-b border-[color:var(--bg-border)] px-4 py-3">
          <Archive className="h-4 w-4 text-[color:var(--accent-primary)]" />
          <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Package contents</h2>
        </div>
        <div className="grid gap-4 p-4 lg:grid-cols-[0.9fr_1.1fr]">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Included files</div>
            <div className="mt-3 grid gap-2">
              {includedFiles.map((file) => (
                <div className="flex items-center gap-2 text-sm text-[color:var(--text-secondary)]" key={file}>
                  <CheckCircle2 className="h-4 w-4 text-[color:var(--accent-primary)]" />
                  <span className="font-mono text-xs">{file}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Compliance metrics covered</div>
            <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3 xl:grid-cols-4">
              {(previewMetrics.length ? previewMetrics : Object.keys(coreMetricLabels)).map((metric) => (
                <div className="rounded-[6px] border border-[color:var(--bg-border)] bg-black/15 px-3 py-2 text-xs font-medium capitalize text-[color:var(--text-secondary)]" key={metric}>
                  {labelForMetric(metric)}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Excluded raw content keys</div>
        <div className="mt-3 flex flex-wrap gap-2">
          {excludedKeys.map((key) => (
            <span className="rounded-[6px] border border-[color:var(--bg-border)] bg-black/15 px-2.5 py-1 font-mono text-xs text-[color:var(--text-secondary)]" key={key}>
              {key}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}
