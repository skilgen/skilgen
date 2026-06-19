"use client";

import { useState } from "react";
import { GitPullRequest, Send, WandSparkles, X } from "lucide-react";

import type { CompatibilityMatrix, SkillRegistryEntry } from "../../../lib/data";
import { RegistryShell } from "./registry-shell";
import { RegistrySkillMap } from "./skill-map";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type BaseTab = "org" | "marketplace" | "import" | "compatibility";
type RegistryTab = BaseTab | "skill-map";

type ChatMessage = { role: "user" | "assistant"; content: string };

export function RegistryAIClient({
  accessToken,
  activeTab,
  compatibility,
  marketplaceEntries,
  orgEntries,
  orgId,
}: {
  accessToken: string;
  activeTab: RegistryTab;
  compatibility: CompatibilityMatrix | null;
  marketplaceEntries: SkillRegistryEntry[];
  orgEntries: SkillRegistryEntry[];
  orgId: string;
}) {
  const [tab, setTab] = useState<RegistryTab>(activeTab);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const baseTab: BaseTab = tab === "skill-map" ? "org" : tab;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-wrap gap-2">
          {[
            ["org", "Registry"],
            ["skill-map", "Skill Map"],
            ["marketplace", "Marketplace"],
            ["import", "Import"],
            ["compatibility", "Compatibility"],
          ].map(([key, label]) => (
            <button
              className={`rounded-lg px-4 py-2 text-[13px] font-semibold ${tab === key ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "text-[color:var(--text-secondary)] hover:bg-[color:var(--bg-elevated)]"}`}
              key={key}
              onClick={() => setTab(key as RegistryTab)}
              type="button"
            >
              {label}
            </button>
          ))}
        </div>
        <button
          className="inline-flex items-center justify-center gap-2 rounded-full bg-[color:var(--accent-primary)] px-4 py-2 text-[13px] font-semibold text-[color:var(--bg-base)]"
          onClick={() => setDrawerOpen(true)}
          type="button"
        >
          <WandSparkles className="h-4 w-4" />
          Create skill with AI
        </button>
      </div>

      {tab === "skill-map" ? (
        <RegistrySkillMap accessToken={accessToken} orgId={orgId} />
      ) : (
        <RegistryShell accessToken={accessToken} activeTab={baseTab} compatibility={compatibility} marketplaceEntries={marketplaceEntries} orgEntries={orgEntries} orgId={orgId} />
      )}

      {drawerOpen ? <CreateSkillDrawer accessToken={accessToken} onClose={() => setDrawerOpen(false)} orgId={orgId} /> : null}
    </div>
  );
}

function authHeaders(accessToken: string) {
  return { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` };
}

function CreateSkillDrawer({ accessToken, orgId, onClose }: { accessToken: string; orgId: string; onClose: () => void }) {
  const [repoId, setRepoId] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState<{ content?: string; meta?: { domain?: string; repo?: string } } | null>(null);
  const [status, setStatus] = useState("");
  const [prUrl, setPrUrl] = useState("");

  async function send() {
    const next = [...messages, { role: "user" as const, content: input }];
    setMessages(next);
    setInput("");
    setStatus("Thinking...");
    const response = await fetch(`${API_URL}/registry/orgs/${orgId}/chat-create`, {
      method: "POST",
      headers: authHeaders(accessToken),
      body: JSON.stringify({ repo_id: repoId || null, messages: next }),
    });
    if (!response.ok) {
      setStatus(response.status === 402 ? "Connect an LLM provider in Settings first." : "Could not create a draft.");
      return;
    }
    const body = (await response.json()) as { assistant_reply: string; ready_to_create: boolean; draft_skill: { content?: string; meta?: { domain?: string; repo?: string } } | null };
    setMessages([...next, { role: "assistant", content: body.assistant_reply }]);
    setDraft(body.draft_skill);
    setStatus(body.ready_to_create ? "Draft ready" : "");
  }

  async function push() {
    if (!draft?.content || !repoId) {
      setStatus("Repo UUID and draft content are required before pushing.");
      return;
    }
    setStatus("Creating PR...");
    const domain = draft.meta?.domain || "generated-skill";
    const response = await fetch(`${API_URL}/registry/orgs/${orgId}/chat-create/push`, {
      method: "POST",
      headers: authHeaders(accessToken),
      body: JSON.stringify({ repo_id: repoId, domain, content: draft.content }),
    });
    if (!response.ok) {
      setStatus("Could not create PR.");
      return;
    }
    const body = (await response.json()) as { pr_url: string };
    setPrUrl(body.pr_url);
    setStatus("PR created");
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50">
      <aside className="ml-auto h-full w-full max-w-[560px] overflow-y-auto border-l border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-[22px] font-semibold text-[color:var(--text-primary)]">Create skill with AI</h2>
            <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Describe the skill and let the registry author a SKILL.md draft.</p>
          </div>
          <button className="rounded-lg p-2 text-[color:var(--text-tertiary)] hover:bg-[color:var(--bg-surface)]" onClick={onClose} type="button"><X className="h-4 w-4" /></button>
        </div>
        <input className="mt-5 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 text-[13px]" onChange={(event) => setRepoId(event.target.value)} placeholder="Target repo UUID for context and PR push" value={repoId} />
        <div className="mt-4 h-[260px] overflow-y-auto rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          {messages.length ? messages.map((message, index) => <div className={`mb-3 rounded-lg p-3 text-[13px] ${message.role === "user" ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "bg-[color:var(--bg-elevated)] text-[color:var(--text-secondary)]"}`} key={`${message.role}-${index}`}>{message.content}</div>) : <div className="text-[13px] text-[color:var(--text-tertiary)]">Try: “Create a testing skill for our API routes. Include rollback gotchas and endpoint verification.”</div>}
        </div>
        <div className="mt-3 flex gap-2">
          <textarea className="min-h-[80px] flex-1 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3 text-[13px]" onChange={(event) => setInput(event.target.value)} placeholder="Tell the assistant what skill to create..." value={input} />
          <button className="h-11 rounded-full bg-[color:var(--accent-primary)] px-4 text-[color:var(--bg-base)]" disabled={!input.trim()} onClick={send} type="button"><Send className="h-4 w-4" /></button>
        </div>
        {draft?.content ? (
          <div className="mt-5">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Draft</h3>
              <button className="inline-flex items-center gap-2 rounded-full border border-[color:var(--bg-border)] px-4 py-2 text-[12px] font-semibold text-[color:var(--text-primary)]" onClick={push} type="button"><GitPullRequest className="h-4 w-4" />Push PR</button>
            </div>
            <pre className="max-h-[360px] overflow-auto rounded-xl bg-[color:var(--bg-surface)] p-4 font-mono text-[12px] leading-6 text-[color:var(--text-secondary)]">{draft.content}</pre>
          </div>
        ) : null}
        {status ? <p className="mt-4 text-[13px] text-[color:var(--text-secondary)]">{status}</p> : null}
        {prUrl ? <a className="mt-3 block text-[13px] font-semibold text-[color:var(--accent-primary)]" href={prUrl} rel="noreferrer" target="_blank">Open pull request</a> : null}
      </aside>
    </div>
  );
}
