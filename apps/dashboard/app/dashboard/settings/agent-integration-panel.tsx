"use client";

import { CheckCircle2, Clipboard, KeyRound, Loader2, RefreshCw, Terminal, XCircle } from "lucide-react";
import type { ReactElement } from "react";
import { useMemo, useState } from "react";

import type { Repo, SetupStatus } from "../../../lib/data";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type AgentIntegrationPanelProps = {
  accessToken: string;
  apiKey: string;
  orgId: string;
  repos: Repo[];
  setupStatus: SetupStatus | null;
};

function buildHeaders(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

function indicatorTone(done: boolean): string {
  return done ? "border-[#3dd68c]/30 bg-[#3dd68c]/10 text-[#3dd68c]" : "border-[color:var(--bg-border)] bg-[#08080d] text-[color:var(--text-tertiary)]";
}

export function AgentIntegrationPanel({ accessToken, apiKey: initialApiKey, orgId, repos, setupStatus }: AgentIntegrationPanelProps): ReactElement {
  const [apiKey, setApiKey] = useState(initialApiKey);
  const [repoId, setRepoId] = useState(repos[0]?.id ?? "");
  const [rotating, setRotating] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const selectedRepo = repos.find((repo) => repo.id === repoId) ?? null;
  const quickSetup = useMemo(() => {
    return `export SKILLAYER_API_KEY=${apiKey}\nexport SKILLAYER_REPO_ID=${repoId}\nskilgen deliver --project-root .`;
  }, [apiKey, repoId]);

  async function copySetup(): Promise<void> {
    await navigator.clipboard.writeText(quickSetup);
    setStatus("Quick setup copied");
  }

  async function copyApiKey(): Promise<void> {
    await navigator.clipboard.writeText(apiKey);
    setStatus("API key copied");
  }

  async function rotateKey(): Promise<void> {
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
      setStatus("API key rotated");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not rotate API key");
    } finally {
      setRotating(false);
    }
  }

  const steps =
    setupStatus?.setup_steps ?? [
      { id: "connect_repo", title: "Connect a repository", done: repos.length > 0 },
      { id: "generate_skills", title: "Generate skills", done: false },
      { id: "connect_agent", title: "Connect an agent", done: false },
      { id: "improve_skills", title: "Improve skills", done: false },
    ];

  return (
    <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Agent Integration</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Org credential, repository target, and setup progress for local agents.</p>
        </div>
        <span className="rounded-full bg-[#C9973A]/15 px-3 py-1 text-[13px] font-semibold text-[#C9973A]">{setupStatus?.completion_percent ?? 0}% ready</span>
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-5">
          <div>
            <div className="mb-2 flex items-center justify-between gap-3">
              <label className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]" htmlFor="agent-api-key">
                API key
              </label>
              <div className="flex gap-2">
                <button className="inline-flex h-8 items-center rounded-md border border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:text-[color:var(--text-primary)]" onClick={copyApiKey} type="button">
                  <Clipboard className="mr-2 h-3.5 w-3.5" />
                  Copy
                </button>
                <button className="inline-flex h-8 items-center rounded-md border border-[#C9973A]/60 px-3 text-[12px] font-semibold text-[#C9973A] transition-colors hover:bg-[#C9973A]/10 disabled:cursor-wait disabled:opacity-60" disabled={rotating} onClick={rotateKey} type="button">
                  {rotating ? <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="mr-2 h-3.5 w-3.5" />}
                  Rotate
                </button>
              </div>
            </div>
            <div className="flex min-h-11 items-center rounded-md border border-[color:var(--bg-border)] bg-[#08080d] px-3 font-mono text-[13px] text-white">
              <KeyRound className="mr-2 h-4 w-4 shrink-0 text-[#C9973A]" />
              <span id="agent-api-key" className="break-all">
                {apiKey}
              </span>
            </div>
          </div>

          <label className="block">
            <span className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Repository</span>
            <select className="mt-2 h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[#08080d] px-3 text-[14px] text-white outline-none transition-colors focus:border-[#C9973A]" onChange={(event) => setRepoId(event.target.value)} value={repoId}>
              {repos.length ? repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.full_name}</option>) : <option value="">No repositories connected</option>}
            </select>
            <div className="mt-2 flex items-center justify-between gap-3 rounded-md border border-[color:var(--bg-border)] bg-[#08080d] px-3 py-2">
              <span className="break-all font-mono text-[12px] text-[color:var(--text-secondary)]">SKILLAYER_REPO_ID={selectedRepo?.id ?? ""}</span>
              <button className="inline-flex h-7 shrink-0 items-center rounded-md border border-[color:var(--bg-border)] px-2 text-[12px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:text-[color:var(--text-primary)]" onClick={() => { void navigator.clipboard.writeText(selectedRepo?.id ?? ""); setStatus("Repo ID copied"); }} type="button">
                <Clipboard className="mr-1.5 h-3.5 w-3.5" />
                Copy
              </button>
            </div>
          </label>

          <div className="rounded-md border border-[color:var(--bg-border)] bg-[#08080d] p-4">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Quick setup</div>
              <button className="inline-flex h-8 items-center rounded-md bg-[#C9973A] px-3 text-[12px] font-semibold text-black transition-colors hover:bg-[#d7aa55]" onClick={copySetup} type="button">
                <Clipboard className="mr-2 h-3.5 w-3.5" />
                Copy
              </button>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap break-all font-mono text-[13px] leading-6 text-[color:var(--text-secondary)]">{quickSetup}</pre>
            <p className="mt-3 text-[12px] leading-5 text-[color:var(--text-tertiary)]">Run this in your repo. Delivery automatically configures Claude Code load tracking and syncs skills to Skillayer.</p>
          </div>
          {status ? <div className="text-[13px] font-medium text-[#C9973A]">{status}</div> : null}
        </div>

        <div className="space-y-3">
          <div className="rounded-md border border-[color:var(--bg-border)] bg-[#08080d] p-4">
            <div className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Selected repo ID</div>
            <div className="mt-2 break-all font-mono text-[13px] text-[color:var(--text-primary)]">{selectedRepo?.id ?? "None"}</div>
          </div>
          {steps.map((step) => (
            <div className={`flex min-h-12 items-center gap-3 rounded-md border px-3 text-[13px] font-medium ${indicatorTone(step.done)}`} key={step.id}>
              {step.done ? <CheckCircle2 className="h-4 w-4 shrink-0" /> : <XCircle className="h-4 w-4 shrink-0" />}
              <span>{step.title}</span>
            </div>
          ))}
          <div className="flex min-h-12 items-center gap-3 rounded-md border border-[color:var(--bg-border)] bg-[#08080d] px-3 text-[13px] text-[color:var(--text-secondary)]">
            <Terminal className="h-4 w-4 shrink-0 text-[#C9973A]" />
            <span>Use the quick setup in the repo root.</span>
          </div>
        </div>
      </div>
    </section>
  );
}
