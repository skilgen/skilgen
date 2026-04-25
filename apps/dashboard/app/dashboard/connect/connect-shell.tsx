"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { CheckCircle2, Clipboard, Radio, Terminal } from "lucide-react";

import type { Repo, SetupStatus } from "../../../lib/data";

type ConnectShellProps = {
  accessToken: string;
  orgId: string;
  apiKey: string;
  repos: Repo[];
  setupStatus: SetupStatus | null;
};

type AgentId = "codex" | "claude" | "cursor";

function CopyButton({ value, label = "Copy" }: { value: string; label?: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-2 text-[12px] font-semibold text-[color:var(--text-primary)] transition-colors hover:bg-white/5"
      onClick={async () => {
        await navigator.clipboard.writeText(value);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
      type="button"
    >
      {copied ? <CheckCircle2 className="h-4 w-4 text-[color:var(--accent-green)]" /> : <Clipboard className="h-4 w-4" />}
      {copied ? "Copied!" : label}
    </button>
  );
}

function CodeBlock({ code, copyLabel }: { code: string; copyLabel: string }) {
  return (
    <div className="relative rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)]">
      <pre className="overflow-x-auto p-4 pr-36 font-mono text-[12px] leading-6 text-[color:var(--text-primary)]">
        <code>{code}</code>
      </pre>
      <div className="absolute right-3 top-3">
        <CopyButton label={copyLabel} value={code} />
      </div>
    </div>
  );
}

export function ConnectShell({ accessToken, orgId, apiKey, repos, setupStatus }: ConnectShellProps) {
  const [selectedRepoId, setSelectedRepoId] = useState<string>(repos[0]?.id ?? "");
  const [activeTab, setActiveTab] = useState<AgentId>("codex");
  const [status, setStatus] = useState(setupStatus);
  const [checking, setChecking] = useState(false);
  const [checkMessage, setCheckMessage] = useState<string | null>(null);

  const repoId = selectedRepoId || repos[0]?.id || "";
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
  const authToken = accessToken || apiKey;
  const connected = Boolean(status?.has_agent_loads);

  const credentialsBlock = useMemo(() => `export SKILLAYER_API_KEY=${apiKey}\nexport SKILLAYER_REPO_ID=${repoId}`, [apiKey, repoId]);
  const zshrcCommand = useMemo(
    () => `echo 'export SKILLAYER_API_KEY=${apiKey}' >> ~/.zshrc && echo 'export SKILLAYER_REPO_ID=${repoId}' >> ~/.zshrc`,
    [apiKey, repoId],
  );

  const codexBlock = `# Skillayer Integration
Before coding, load skills from:
https://api.skillayer.com/repos/${repoId}/skills/load
API-Key: ${apiKey}
Use loaded skills as authoritative repo guidance.`;

  const claudeBlock = `# Skillayer Integration
Load skills before working: https://api.skillayer.com/repos/${repoId}/skills/load
API-Key: ${apiKey}`;

  const claudeHookBlock = `{
  "env": {
    "SKILLAYER_API_KEY": "${apiKey}",
    "SKILLAYER_REPO_ID": "${repoId}"
  },
  "hooks": {
    "PostToolUse": [{
      "matcher": "Read",
      "hooks": [{"type": "command",
        "command": "python -m skilgen.hooks.claude_code_hook \\"$CLAUDE_TOOL_INPUT_FILE_PATH\\""}]
    }]
  }
}`;

  const cursorBlock = `# Skillayer Integration
Load skills from: https://api.skillayer.com/repos/${repoId}/skills/load
API-Key: ${apiKey}
Follow all patterns and anti-patterns in loaded skills.`;

  const cursorWatchCommand = `skilgen watch --repo-id ${repoId}`;

  async function checkNow() {
    setChecking(true);
    setCheckMessage(null);
    try {
      const response = await fetch(`${apiUrl}/orgs/${orgId}/setup-status`, {
        headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      });
      if (!response.ok) {
        setCheckMessage("Not yet - use your agent once first");
        return;
      }
      const next = (await response.json()) as SetupStatus;
      setStatus(next);
      setCheckMessage(next.has_agent_loads ? "Connected" : "Not yet - use your agent once first");
    } finally {
      setChecking(false);
    }
  }

  function tabClass(tab: AgentId): string {
    return activeTab === tab
      ? "border-b-2 border-[color:var(--accent-primary)] text-[color:var(--accent-primary)]"
      : "border-b-2 border-transparent text-[color:var(--text-tertiary)] hover:text-[color:var(--text-primary)]";
  }

  return (
    <div className="space-y-6">
      <section>
        <div className="inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[rgb(var(--accent-primary-rgb)/0.08)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
          <Terminal className="h-4 w-4" />
          Agent setup
        </div>
        <h1 className="mt-4 text-[32px] font-semibold text-[color:var(--text-primary)]">Connect your AI agent</h1>
        <p className="mt-2 max-w-2xl text-[15px] leading-7 text-[color:var(--text-secondary)]">
          Copy credentials once, then paste one agent instruction block into your repo.
        </p>
      </section>

      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Your Skillayer credentials</h2>
            <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Copy these into your terminal once. All agents use them.</p>
          </div>
          {repos.length > 1 ? (
            <label className="flex items-center gap-2 text-[12px] font-semibold text-[color:var(--text-secondary)]">
              Repo
              <select
                className="h-9 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[12px] text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]"
                onChange={(event) => setSelectedRepoId(event.target.value)}
                value={selectedRepoId}
              >
                {repos.map((repo) => (
                  <option key={repo.id} value={repo.id}>
                    {repo.full_name || repo.name}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
        </div>

        {apiKey && repoId ? (
          <div className="space-y-4">
            <CodeBlock code={credentialsBlock} copyLabel="Copy both" />
            <div>
              <p className="mb-2 text-[12px] font-semibold text-[color:var(--text-tertiary)]">Add to ~/.zshrc to make permanent:</p>
              <div className="flex flex-wrap items-center gap-2 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
                <code className="min-w-0 flex-1 break-all font-mono text-[12px] leading-5 text-[color:var(--text-primary)]">{zshrcCommand}</code>
                <CopyButton label="Copy" value={zshrcCommand} />
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-lg border border-[#f59e0b]/30 bg-[#f59e0b]/10 p-4 text-[13px] font-semibold text-[#f59e0b]">
            <Link className="underline underline-offset-4" href="/dashboard/settings">
              Generate your API key in Settings →
            </Link>
          </div>
        )}
      </section>

      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Now tell your agent</h2>
            <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">One paste into the agent file your team already uses.</p>
          </div>
          <div className="flex gap-4 text-[13px] font-semibold">
            <button className={`pb-2 transition-colors ${tabClass("codex")}`} onClick={() => setActiveTab("codex")} type="button">
              Codex
            </button>
            <button className={`pb-2 transition-colors ${tabClass("claude")}`} onClick={() => setActiveTab("claude")} type="button">
              Claude Code
            </button>
            <button className={`pb-2 transition-colors ${tabClass("cursor")}`} onClick={() => setActiveTab("cursor")} type="button">
              Cursor
            </button>
          </div>
        </div>

        {activeTab === "codex" ? (
          <div>
            <p className="mb-2 text-[13px] font-semibold text-[color:var(--text-primary)]">Paste into AGENTS.md in your repo root</p>
            <CodeBlock code={codexBlock} copyLabel="Copy for AGENTS.md" />
            <p className="mt-3 text-[13px] text-[color:var(--text-secondary)]">
              That&apos;s it. Codex reads AGENTS.md before every task and will load your skills automatically.
            </p>
          </div>
        ) : null}

        {activeTab === "claude" ? (
          <div>
            <p className="mb-2 text-[13px] font-semibold text-[color:var(--text-primary)]">Paste into CLAUDE.md in your repo root</p>
            <CodeBlock code={claudeBlock} copyLabel="Copy for CLAUDE.md" />
            <div className="my-5 border-t border-[color:var(--bg-border)]" />
            <p className="mb-2 text-[13px] font-semibold text-[color:var(--text-primary)]">Auto-track loads - paste into .claude/settings.json</p>
            <CodeBlock code={claudeHookBlock} copyLabel="Copy for .claude/settings.json" />
          </div>
        ) : null}

        {activeTab === "cursor" ? (
          <div>
            <p className="mb-2 text-[13px] font-semibold text-[color:var(--text-primary)]">Paste into .cursorrules in your repo root</p>
            <CodeBlock code={cursorBlock} copyLabel="Copy for .cursorrules" />
            <div className="mt-4 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-secondary)]">
              <span>Also run in a terminal while using Cursor:</span>
              <code className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-2 py-1 font-mono text-[12px] text-[color:var(--text-primary)]">
                {cursorWatchCommand}
              </code>
              <CopyButton label="Copy" value={cursorWatchCommand} />
            </div>
          </div>
        ) : null}
      </section>

      <section className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-5 py-4">
        <div className="text-[13px] text-[color:var(--text-secondary)]">Done? Check that Skillayer is receiving loads:</div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            className="inline-flex items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-[12px] font-semibold text-[color:var(--bg-base)] transition-opacity hover:opacity-90 disabled:cursor-wait disabled:opacity-60"
            disabled={checking || !orgId}
            onClick={checkNow}
            type="button"
          >
            <Radio className="h-4 w-4" />
            {checking ? "Checking..." : "Check connection"}
          </button>
          {checkMessage ? (
            <span className={`text-[13px] font-semibold ${connected ? "text-[color:var(--accent-green)]" : "text-[#f59e0b]"}`}>
              {connected ? "✓ " : ""}
              {checkMessage}
            </span>
          ) : null}
        </div>
      </section>
    </div>
  );
}
