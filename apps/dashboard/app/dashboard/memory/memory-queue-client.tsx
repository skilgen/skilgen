"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Sparkles } from "lucide-react";

import type { MemoryQueueResponse, MemoryStub } from "../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

const typeLabels: Record<MemoryStub["discovery_type"], { label: string; className: string }> = {
  undocumented_pattern: { label: "Pattern", className: "bg-purple-500/15 text-purple-300" },
  workaround: { label: "Workaround", className: "bg-amber-500/15 text-amber-300" },
  architectural_insight: { label: "Architecture", className: "bg-blue-500/15 text-blue-300" },
  gotcha: { label: "Gotcha", className: "bg-red-500/15 text-red-300" },
  dependency_insight: { label: "Dependency", className: "bg-teal-500/15 text-teal-300" },
  contradiction: { label: "Contradiction", className: "bg-orange-500/15 text-orange-300" },
};

function formatRelativeTime(value: string): string {
  const timestamp = new Date(value).getTime();
  if (Number.isNaN(timestamp)) return "Unknown";
  const minutes = Math.max(0, Math.floor((Date.now() - timestamp) / 60000));
  if (minutes < 60) return `${Math.max(1, minutes)}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function words(value: string): number {
  return value.split(/\s+/).filter(Boolean).length;
}

export function MemoryQueueClient({ accessToken, orgId, initialQueue }: { accessToken: string; orgId: string; initialQueue: MemoryQueueResponse }) {
  const [queue, setQueue] = useState(initialQueue);
  const [status, setStatus] = useState("pending");
  const [focused, setFocused] = useState(0);
  const [expanded, setExpanded] = useState<string | null>(initialQueue.items[0]?.id ?? null);
  const [editing, setEditing] = useState<string | null>(null);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [confirmReject, setConfirmReject] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const items = queue.items;
  const focusedItem = items[focused];

  async function fetchQueue(nextStatus: string) {
    setStatus(nextStatus);
    const params = new URLSearchParams({ status: nextStatus });
    const response = await fetch(`${API_URL}/orgs/${orgId}/memory-queue?${params.toString()}`, { headers: { Authorization: `Bearer ${accessToken}` } });
    if (response.ok) {
      const nextQueue = (await response.json()) as MemoryQueueResponse;
      setQueue(nextQueue);
      setFocused(0);
      setExpanded(nextQueue.items[0]?.id ?? null);
    }
  }

  const review = useCallback(async (item: MemoryStub, action: "approve" | "reject") => {
    setBusy(item.id);
    const response = await fetch(`${API_URL}/orgs/${orgId}/memory-queue/${item.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify({ action, edited_content: action === "approve" ? drafts[item.id] : undefined, reviewer_note: notes[item.id] }),
    });
    setBusy(null);
    if (!response.ok) {
      setMessage("Unable to review this discovery.");
      return;
    }
    const updated = (await response.json()) as MemoryStub;
    setQueue((current) => ({ ...current, items: current.items.map((stub) => (stub.id === updated.id ? updated : stub)) }));
    setMessage(action === "approve" ? `✓ Merged into ${updated.domain} skill v${updated.merged_version_number ?? "?"}` : "Rejected");
    setTimeout(() => setMessage(null), 2000);
  }, [accessToken, drafts, notes, orgId]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (!items.length) return;
      const target = event.target as HTMLElement | null;
      if (target?.tagName === "TEXTAREA" && event.key !== "Escape") return;
      if (event.key === "ArrowDown" || event.key === "j") {
        event.preventDefault();
        setFocused((index) => Math.min(items.length - 1, index + 1));
      } else if (event.key === "ArrowUp" || event.key === "k") {
        event.preventDefault();
        setFocused((index) => Math.max(0, index - 1));
      } else if (event.key === "Escape") {
        setExpanded(null);
      } else if (focusedItem && event.key.toLowerCase() === "e") {
        setExpanded(focusedItem.id);
        setEditing((value) => (value === focusedItem.id ? null : focusedItem.id));
      } else if (focusedItem && event.key.toLowerCase() === "a") {
        void review(focusedItem, "approve");
      } else if (focusedItem && event.key.toLowerCase() === "r") {
        setConfirmReject(focusedItem.id);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [focusedItem, items, review]);

  const tabs = useMemo(() => ["all", "pending", "approved", "rejected"], []);

  return (
    <section>
      {items.length > 0 ? <div className="mb-4 inline-flex rounded-lg bg-white/5 px-4 py-2 text-[11px] text-[color:var(--text-tertiary)]">↑↓ navigate · A approve · R reject · E edit</div> : null}
      <div className="mb-4 flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button className={`rounded-full border px-4 py-2 text-[12px] font-semibold capitalize ${status === tab ? "border-[color:var(--accent-primary)] bg-[rgb(var(--accent-primary-rgb)/0.15)] text-[color:var(--accent-primary)]" : "border-[color:var(--bg-border)] text-[color:var(--text-secondary)]"}`} key={tab} onClick={() => void fetchQueue(tab)} type="button">
            {tab}
          </button>
        ))}
      </div>
      {items.length === 0 ? (
        <div className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-6 py-16 text-center">
          <Sparkles className="mx-auto h-7 w-7 text-[color:var(--accent-primary)]" />
          <h2 className="mt-4 text-[18px] font-semibold text-[color:var(--text-primary)]">No sessions captured yet</h2>
          <p className="mt-2 text-[13px] text-[color:var(--text-secondary)]">Upload a session from the CLI to start building your skill memory.</p>
          <pre className="mx-auto mt-5 max-w-xl rounded-lg bg-black/40 px-4 py-3 text-left font-mono text-[12px] text-[color:var(--text-secondary)]">SKILLAYER_API_KEY=&lt;key&gt; skilgen memory --upload --repo-id &lt;repo-uuid&gt;</pre>
        </div>
      ) : (
        <div>
          {message ? <div className="mb-3 rounded-xl border border-green-500/25 bg-green-500/10 px-4 py-3 text-[13px] font-semibold text-green-300">{message}</div> : null}
          {items.map((item, index) => {
            const isExpanded = expanded === item.id || focused === index;
            const draft = drafts[item.id] ?? item.proposed_content;
            const type = typeLabels[item.discovery_type] ?? typeLabels.undocumented_pattern;
            return (
              <article className={`mb-3 cursor-pointer rounded-[24px] border bg-[color:var(--bg-surface)] p-5 transition-all ${focused === index ? "border-[color:var(--accent-primary)] bg-[rgb(var(--accent-primary-rgb)/0.04)]" : "border-[color:var(--bg-border)]"}`} key={item.id} onClick={() => { setFocused(index); setExpanded(isExpanded ? null : item.id); }}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`rounded-full px-2.5 py-1 text-[12px] font-semibold ${type.className}`}>{type.label}</span>
                    <span className="rounded-full bg-[color:var(--bg-elevated)] px-2.5 py-1 font-mono text-[12px] text-[color:var(--text-secondary)]">{item.domain}</span>
                  </div>
                  <div className="flex flex-wrap justify-end gap-2 text-[12px]">
                    <span className="rounded-full bg-white/5 px-2.5 py-1 text-[color:var(--text-secondary)]">{Math.round(item.confidence * 100)}% confidence</span>
                    {item.status !== "pending" ? <span className="rounded-full bg-green-500/15 px-2.5 py-1 text-green-300">{item.status === "merged" ? "✓ Merged" : item.status}</span> : null}
                  </div>
                </div>
                <h3 className="mt-2 text-[16px] font-semibold text-[color:var(--text-primary)]">{item.title}</h3>
                <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">{item.agent_runtime} · {item.engineer_login ?? "Unknown engineer"} · {formatRelativeTime(item.session_created_at)}{item.task_description ? ` · Task: ${item.task_description.slice(0, 60)}${item.task_description.length > 60 ? "..." : ""}` : ""}</div>
                {item.evidence ? <div className="mt-1 text-[12px] italic text-[color:var(--text-tertiary)]">📂 {item.evidence}</div> : null}
                {isExpanded ? (
                  <div className="mt-5 grid gap-6 lg:grid-cols-2">
                    <div>
                      <div className="mb-2 text-[13px] font-semibold text-[color:var(--text-secondary)]">Proposed skill addition</div>
                      {editing === item.id ? (
                        <>
                          <textarea className="min-h-[200px] w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 font-mono text-[12px] text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]" value={draft} onChange={(event) => setDrafts((current) => ({ ...current, [item.id]: event.target.value }))} />
                          <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{words(draft)} words</div>
                        </>
                      ) : (
                        <pre className="max-h-[300px] overflow-y-auto whitespace-pre-wrap rounded-xl bg-[color:var(--bg-base)] p-4 font-mono text-[12px] leading-6 text-[color:var(--text-primary)]">{item.proposed_content}</pre>
                      )}
                    </div>
                    <div>
                      <div className="mb-2 text-[13px] font-semibold text-[color:var(--text-secondary)]">Current skill content</div>
                      {item.existing_skill_content ? <pre className="max-h-[300px] overflow-y-auto whitespace-pre-wrap rounded-xl bg-[color:var(--bg-base)] p-4 font-mono text-[12px] leading-6 text-[color:var(--text-tertiary)]">{item.existing_skill_content}</pre> : <div className="rounded-xl border border-amber-500/25 bg-amber-500/10 px-4 py-3 text-[13px] text-amber-300">No matching skill found for domain &apos;{item.domain}&apos;. Approve to save as a standalone discovery.</div>}
                    </div>
                    <div className="lg:col-span-2">
                      <div className="mb-3 flex flex-wrap gap-3">
                        <button className="rounded-full bg-[color:var(--accent-primary)] px-5 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)] disabled:opacity-60" disabled={busy === item.id} onClick={(event) => { event.stopPropagation(); void review(item, "approve"); }} type="button">{busy === item.id ? "Merging…" : "Approve & merge"}</button>
                        {editing !== item.id ? <button className="rounded-full border border-[color:var(--bg-border)] px-4 py-2 text-[13px] font-semibold text-[color:var(--text-secondary)]" onClick={(event) => { event.stopPropagation(); setEditing(item.id); }} type="button">Edit & approve</button> : null}
                        <button className="text-[13px] text-[color:var(--text-tertiary)] hover:text-red-300" onClick={(event) => { event.stopPropagation(); setConfirmReject(item.id); }} type="button">Reject</button>
                      </div>
                      {confirmReject === item.id ? <div className="mb-3 rounded-xl bg-white/5 px-4 py-3 text-[13px] text-[color:var(--text-secondary)]">Reject this discovery? <button className="ml-3 font-semibold text-red-300" onClick={(event) => { event.stopPropagation(); void review(item, "reject"); }} type="button">Reject</button> <button className="ml-3 text-[color:var(--text-tertiary)]" onClick={(event) => { event.stopPropagation(); setConfirmReject(null); }} type="button">Cancel</button></div> : null}
                      <textarea className="w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-[12px] text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]" onChange={(event) => setNotes((current) => ({ ...current, [item.id]: event.target.value }))} onClick={(event) => event.stopPropagation()} placeholder="Add a note for your team (optional)…" rows={2} value={notes[item.id] ?? ""} />
                    </div>
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
