"use client";

import { CheckCircle2, Clipboard, Eye, EyeOff, KeyRound, Loader2, RefreshCw } from "lucide-react";
import type { ReactElement } from "react";
import { useMemo, useState } from "react";

import type { Repo } from "../../../lib/data";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type ApiAccessPanelProps = {
  accessToken: string;
  apiKey: string;
  orgId: string;
  repos: Repo[];
};

function buildHeaders(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

function maskApiKey(value: string): string {
  if (!value) return "sk-••••••••••••";
  return `${value.slice(0, 3)}${"•".repeat(24)}`;
}

export function ApiAccessPanel({ accessToken, apiKey: initialApiKey, orgId, repos }: ApiAccessPanelProps): ReactElement {
  const [apiKey, setApiKey] = useState(initialApiKey);
  const [revealed, setRevealed] = useState(false);
  const [copied, setCopied] = useState(false);
  const [rotating, setRotating] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const repoId = repos[0]?.id ?? "<repo-uuid>";
  const usage = useMemo(() => `export SKILLAYER_API_KEY=${apiKey || "sk-..."}\nexport SKILLAYER_REPO_ID=${repoId}\nskilgen deliver --project-root .`, [apiKey, repoId]);

  async function copyKey(): Promise<void> {
    if (!apiKey) return;
    await navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setStatus("API key copied");
    window.setTimeout(() => setCopied(false), 1600);
  }

  async function rotateKey(): Promise<void> {
    const ok = window.confirm("This will immediately invalidate your current key. All agents using it will stop working until you update them. Continue?");
    if (!ok) return;
    setRotating(true);
    setStatus(null);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/api-key/rotate`, {
        method: "POST",
        headers: buildHeaders(accessToken),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Could not rotate API key");
      setApiKey(String(body.api_key || ""));
      setRevealed(false);
      setStatus("API key rotated. Update every integration that used the previous key.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not rotate API key");
    } finally {
      setRotating(false);
    }
  }

  return (
    <section className="mb-8 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <KeyRound className="h-5 w-5 text-[color:var(--accent-primary)]" />
            <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">API Access</h2>
          </div>
          <p className="mt-2 max-w-2xl text-[13px] leading-6 text-[color:var(--text-secondary)]">
            Your org API key. Use this to connect agents and the Skilgen CLI to Skillayer.
          </p>
        </div>
        <button
          className="inline-flex h-9 items-center rounded-md border border-[#f59e0b]/50 px-3 text-[12px] font-semibold text-[#f59e0b] transition-colors hover:bg-[#f59e0b]/10 disabled:cursor-wait disabled:opacity-60"
          disabled={rotating}
          onClick={rotateKey}
          type="button"
        >
          {rotating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
          Rotate key
        </button>
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-4">
          <div>
            <div className="mb-2 text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">API Key</div>
            <div className="flex flex-wrap items-stretch gap-2">
              <div className="flex min-h-11 flex-1 items-center rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 font-mono text-[13px] text-[color:var(--text-primary)]">
                <span className="break-all">{revealed ? apiKey || "No key available" : maskApiKey(apiKey)}</span>
              </div>
              <button
                className="inline-flex h-11 items-center rounded-md border border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:text-[color:var(--text-primary)]"
                onClick={() => setRevealed((value) => !value)}
                type="button"
              >
                {revealed ? <EyeOff className="mr-2 h-4 w-4" /> : <Eye className="mr-2 h-4 w-4" />}
                {revealed ? "Hide" : "Reveal"}
              </button>
              <button
                className="inline-flex h-11 items-center rounded-md bg-[color:var(--accent-primary)] px-3 text-[12px] font-semibold text-[color:var(--bg-base)] transition-colors hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
                disabled={!apiKey}
                onClick={copyKey}
                type="button"
              >
                {copied ? <CheckCircle2 className="mr-2 h-4 w-4" /> : <Clipboard className="mr-2 h-4 w-4" />}
                {copied ? "Copied" : "Copy"}
              </button>
            </div>
          </div>

          <div className="rounded-md border border-[#f59e0b]/30 bg-[#f59e0b]/10 px-4 py-3 text-[13px] leading-6 text-[#f59e0b]">
            Rotating invalidates your current key immediately. Update all integrations before rotating.
          </div>
          {status ? <div className="text-[13px] font-medium text-[color:var(--accent-primary)]">{status}</div> : null}
        </div>

        <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
          <div className="mb-3 text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Usage</div>
          <pre className="whitespace-pre-wrap break-all font-mono text-[12px] leading-6 text-[color:var(--text-primary)]">{usage}</pre>
        </div>
      </div>
    </section>
  );
}
