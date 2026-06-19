"use client";

import { AlertTriangle, Filter, GitPullRequest, Inbox, MoreHorizontal, RefreshCcw, Search, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { cn } from "@skillayer/ui";
import type { AgentPrCard, AgentPrDetail, AgentPrListResponse, Repo } from "../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type Props = {
  accessToken: string;
  apiKey: string;
  orgId: string;
  initialData: AgentPrListResponse | null;
  initialParams: string;
  repos: Repo[];
};

const AGENTS = [
  { key: "", label: "All", color: "var(--text-secondary)" },
  { key: "claude_code", label: "Claude", color: "#D97706" },
  { key: "codex", label: "Codex", color: "#10B981" },
  { key: "cursor", label: "Cursor", color: "#8B5CF6" },
  { key: "copilot", label: "Copilot", color: "#24292F" },
  { key: "devin", label: "Devin", color: "#3B82F6" },
  { key: "human", label: "Human", color: "var(--text-secondary)" },
];

const AGENT_LABELS: Record<string, string> = {
  claude_code: "Claude",
  codex: "Codex",
  codex_cli: "Codex CLI",
  cursor: "Cursor",
  copilot: "Copilot",
  github_copilot: "Copilot",
  gemini_cli: "Gemini CLI",
  gemini: "Gemini CLI",
  devin: "Devin",
  human: "Human",
  mixed: "Mixed",
  unidentified_agent: "Codex CLI",
  unknown: "Unknown",
};

const AGENT_COLORS: Record<string, string> = {
  claude_code: "#D97706",
  codex: "#10B981",
  cursor: "#8B5CF6",
  copilot: "#24292F",
  devin: "#3B82F6",
  human: "var(--text-secondary)",
  mixed: "var(--accent-primary)",
};

const STORAGE_PREFIX = "skillayer.agentPrInbox";

function relativeTime(ts: string | null): string {
  if (!ts) return "unknown";
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(ts).getTime()) / 1000));
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

function riskMeta(tier: string): { label: string; className: string; dot: string } {
  if (tier === "red") return { label: "High", className: "border-red-500/40 bg-red-500/12 text-red-200", dot: "bg-red-400" };
  if (tier === "yellow") return { label: "Medium", className: "border-amber-500/40 bg-amber-500/12 text-amber-200", dot: "bg-amber-400" };
  return { label: "Low", className: "border-[color:var(--accent-green)]/40 bg-[color:var(--accent-green)]/12 text-[color:var(--accent-green)]", dot: "bg-[color:var(--accent-green)]" };
}

async function fetchAgentPrs(accessToken: string, orgId: string, params: URLSearchParams): Promise<AgentPrListResponse> {
  const response = await fetch(`${API_URL}/orgs/${orgId}/agent-prs?${params.toString()}`, {
    headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
    cache: "no-store",
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<AgentPrListResponse>;
}

async function fetchAgentPrDetail(accessToken: string, orgId: string, prId: string): Promise<AgentPrDetail> {
  const response = await fetch(`${API_URL}/orgs/${orgId}/agent-prs/${prId}`, {
    headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
    cache: "no-store",
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<AgentPrDetail>;
}

async function fetchManifest(accessToken: string, orgId: string, prId: string): Promise<{ manifest: Record<string, unknown>; signed_at: string | null }> {
  const response = await fetch(`${API_URL}/orgs/${orgId}/agent-prs/${prId}/manifest`, {
    headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
    cache: "no-store",
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<{ manifest: Record<string, unknown>; signed_at: string | null }>;
}

async function verifyManifest(accessToken: string, orgId: string, prId: string, manifest: Record<string, unknown>): Promise<{ valid: boolean; message: string }> {
  const response = await fetch(`${API_URL}/orgs/${orgId}/agent-prs/${prId}/manifest/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
    body: JSON.stringify({ manifest }),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<{ valid: boolean; message: string }>;
}

function EmptyState() {
  return (
    <div className="rounded-[28px] border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-6 py-16 text-center">
      <Inbox className="mx-auto h-12 w-12 text-[color:var(--text-tertiary)]" />
      <h2 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">No PRs match these filters</h2>
      <p className="mx-auto mt-2 max-w-lg text-sm text-[color:var(--text-secondary)]">GitHub is connected. Try All agents, All risk, and All states to see the full PR history.</p>
      <Link className="mt-6 inline-flex rounded-lg bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-black transition-colors hover:bg-[color:var(--accent-bright)]" href="/dashboard/agent-prs?state=all">
        Show all PRs
      </Link>
    </div>
  );
}

function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="rounded-[28px] border border-red-500/30 bg-red-500/10 px-6 py-12 text-center">
      <AlertTriangle className="mx-auto h-12 w-12 text-red-300" />
      <h2 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">Couldn't load agent PRs</h2>
      <p className="mx-auto mt-2 max-w-2xl text-sm text-red-100/80">{error || "The API did not return the inbox payload."}</p>
      <button className="mt-6 rounded-lg border border-red-300/40 px-4 py-2 text-sm font-semibold text-red-100 transition-colors hover:bg-red-500/20" onClick={onRetry} type="button">
        Retry
      </button>
    </div>
  );
}

function PrCard({ item, active, selected, onOpen }: { item: AgentPrCard; active: boolean; selected: boolean; onOpen: () => void }) {
  const color = AGENT_COLORS[item.primary_agent] ?? "var(--text-secondary)";
  const risk = riskMeta(item.risk_tier);
  const visibleSkills = item.skills_loaded.slice(0, 3);
  const extraSkills = Math.max(0, item.skills_loaded.length - visibleSkills.length);
  return (
    <article
      className={cn(
        "group relative min-h-[100px] cursor-pointer overflow-hidden rounded-[20px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5 transition-all hover:-translate-y-0.5 hover:border-[color:var(--accent-primary)]/50 hover:shadow-md",
        selected && "border-[color:var(--accent-primary)] shadow-md",
        active && "ring-1 ring-amber-400/40",
      )}
      onClick={onOpen}
      tabIndex={0}
    >
      <div className="absolute inset-y-0 left-0 w-1" style={{ backgroundColor: color }} />
      <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_170px_160px]">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-bold" style={{ borderColor: `${color}66`, backgroundColor: `${color}22`, color }}>
              {AGENT_LABELS[item.primary_agent] ?? item.primary_agent}
              <span className="ml-1 text-[color:var(--text-tertiary)]">{Math.round((item.confidence ?? 0) * 100)}%</span>
            </span>
            <span className="text-xs text-[color:var(--text-secondary)]">{item.repo_name} · #{item.github_pr_number}</span>
          </div>
          <h2 className="mt-2 line-clamp-2 text-[15px] font-semibold text-[color:var(--text-primary)]" title={item.title}>{item.title}</h2>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-[color:var(--text-tertiary)]">
            <span>@{item.author_login ?? "unknown"}</span>
            <span className="font-mono text-[color:var(--text-secondary)]">+{item.additions} -{item.deletions} · {item.changed_files} files</span>
          </div>
        </div>
        <div className="space-y-3">
          <div className="text-right text-xs text-[color:var(--text-tertiary)] md:text-left">{relativeTime(item.opened_at)}</div>
          <div className="flex flex-wrap gap-1.5">
            {visibleSkills.map((skill) => (
              <button className="rounded-full border border-[color:var(--bg-border)] bg-black/20 px-2 py-1 text-[11px] text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)]" key={skill} onClick={(event) => event.stopPropagation()} type="button">
                {skill}
              </button>
            ))}
            {extraSkills > 0 ? <span className="rounded-full bg-white/5 px-2 py-1 text-[11px] text-[color:var(--text-tertiary)]">+{extraSkills}</span> : null}
          </div>
        </div>
        <div className="flex items-start justify-between gap-3 md:flex-col md:items-end">
          <div className="flex items-center gap-2">
            {item.violation_count > 0 ? <span className="rounded-full bg-red-500 px-2 py-1 text-xs font-bold text-white">{item.violation_count}</span> : null}
            {item.warning_count > 0 ? <span className="rounded-full bg-amber-500 px-2 py-1 text-xs font-bold text-black">{item.warning_count}</span> : null}
            <span className={cn("inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold", risk.className)}><span className={cn("h-2 w-2 rounded-full", risk.dot)} />{risk.label}</span>
          </div>
          <div className="flex items-center gap-2" onClick={(event) => event.stopPropagation()}>
            {item.url ? (
              <Link className="rounded-lg border border-[color:var(--bg-border)] px-3 py-1.5 text-xs font-semibold text-[color:var(--text-secondary)] transition-colors group-hover:border-[color:var(--accent-primary)] group-hover:text-[color:var(--text-primary)]" href={item.url} target="_blank">
                Approve in GitHub
              </Link>
            ) : null}
            <button className="rounded-lg border border-[color:var(--bg-border)] p-1.5 text-[color:var(--text-tertiary)] hover:text-[color:var(--text-primary)]" type="button"><MoreHorizontal className="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </article>
  );
}

function DetailPanel({ accessToken, detail, loading, onClose, orgId }: { accessToken: string; detail: AgentPrDetail | null; loading: boolean; onClose: () => void; orgId: string }) {
  const [manifest, setManifest] = useState<Record<string, unknown> | null>(null);
  const [manifestOpen, setManifestOpen] = useState(false);
  const [manifestError, setManifestError] = useState("");
  const [manifestLoading, setManifestLoading] = useState(false);
  const [verifyMessage, setVerifyMessage] = useState<{ valid: boolean; message: string } | null>(null);

  async function openManifest() {
    if (!detail) return;
    setManifestLoading(true);
    setManifestError("");
    setVerifyMessage(null);
    try {
      const response = await fetchManifest(accessToken, orgId, detail.pr_id);
      setManifest(response.manifest);
      setManifestOpen(true);
    } catch {
      setManifestError("Manifest not yet generated — triggers on next PR push");
    } finally {
      setManifestLoading(false);
    }
  }

  function downloadManifest() {
    if (!manifest || !detail) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(manifest, null, 2)], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `skillayer-manifest-pr-${detail.github_pr_number}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  async function runVerify() {
    if (!detail || !manifest) return;
    try {
      setVerifyMessage(await verifyManifest(accessToken, orgId, detail.pr_id, manifest));
    } catch (err) {
      setVerifyMessage({ valid: false, message: err instanceof Error ? err.message : "Verification failed" });
    }
  }

  return (
    <aside className="fixed inset-y-0 right-0 z-[80] w-full overflow-y-auto border-l border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-6 shadow-2xl md:w-[40vw] md:min-w-[520px]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">PR detail</div>
          <h2 className="mt-2 text-xl font-semibold text-[color:var(--text-primary)]">{detail?.title ?? "Loading review..."}</h2>
        </div>
        <button className="rounded-lg p-2 text-[color:var(--text-secondary)] hover:bg-[color:var(--bg-surface)]" onClick={onClose} type="button"><X className="h-5 w-5" /></button>
      </div>
      {loading || !detail ? (
        <div className="mt-8 space-y-4">
          {[...Array(5)].map((_, index) => <div className="h-24 animate-pulse rounded-2xl bg-white/5" key={index} />)}
        </div>
      ) : (
        <div className="mt-6 space-y-5">
          <section className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
            <h3 className="font-semibold">Attribution</h3>
            <div className="mt-4 flex h-3 overflow-hidden rounded-full bg-white/5">
              {Object.entries(detail.lines_by_agent || {}).map(([agent, lines]) => {
                const total = Object.values(detail.lines_by_agent || {}).reduce((sum, value) => sum + Number(value || 0), 0) || 1;
                return <div key={agent} style={{ width: `${(Number(lines) / total) * 100}%`, backgroundColor: AGENT_COLORS[agent] ?? "var(--text-secondary)" }} />;
              })}
            </div>
            <p className="mt-3 text-sm text-[color:var(--text-secondary)]">
              {Object.entries(detail.lines_by_agent || {}).map(([agent, lines]) => `${Math.round((Number(lines) / Math.max(1, Object.values(detail.lines_by_agent || {}).reduce((sum, value) => sum + Number(value || 0), 0))) * 100)}% ${AGENT_LABELS[agent] ?? agent}`).join(" · ")}
            </p>
          </section>
          <section className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Risk breakdown</h3>
              <div className="text-3xl font-bold text-[color:var(--text-primary)]">{detail.risk_score}</div>
            </div>
            <div className="mt-4 space-y-3">
              {["violations", "incidents", "coverage", "ownership"].map((key) => {
                const row = detail.risk_breakdown?.[key] ?? {};
                return (
                  <div className="flex items-start justify-between gap-4 rounded-xl bg-black/15 p-3" key={key}>
                    <div>
                      <div className="text-sm font-semibold capitalize">{key}</div>
                      <div className="text-xs text-[color:var(--text-secondary)]">{row.explanation ?? "No signal recorded"}</div>
                    </div>
                    <span className="text-sm font-bold">{row.points ?? 0} pts</span>
                  </div>
                );
              })}
            </div>
          </section>
          <section className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="font-semibold">Provenance Manifest</h3>
                <p className="mt-1 text-xs text-[color:var(--text-secondary)]">Tamper-evident proof of agent attribution, loaded skills, risk, and policy outcome.</p>
              </div>
              <button className="rounded-lg border border-[color:var(--bg-border)] px-3 py-1.5 text-xs font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)] disabled:cursor-wait disabled:opacity-60" disabled={manifestLoading} onClick={openManifest} type="button">
                {manifestLoading ? "Loading..." : "View Manifest"}
              </button>
            </div>
            {manifestError ? <p className="mt-3 rounded-lg border border-amber-500/25 bg-amber-500/10 p-3 text-xs text-amber-100">{manifestError}</p> : null}
          </section>
          <section className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
            <h3 className="font-semibold">Violations</h3>
            <div className="mt-4 space-y-3">
              {detail.violations.length ? detail.violations.map((violation, index) => (
                <article className="rounded-xl border border-[color:var(--bg-border)] bg-black/15 p-3" key={`${violation.file}-${index}`}>
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-mono text-xs text-[color:var(--text-secondary)]">{violation.file}{violation.line ? `:${violation.line}` : ""}</span>
                    <span className="rounded-full bg-white/8 px-2 py-1 text-xs capitalize">{violation.severity}</span>
                  </div>
                  <p className="mt-2 text-sm text-[color:var(--text-primary)]">{violation.explanation}</p>
                  {violation.fix_suggestion ? <p className="mt-2 rounded-lg bg-[color:var(--accent-green)]/10 p-2 text-xs text-[color:var(--accent-green)]">{violation.fix_suggestion}</p> : null}
                  <Link className="mt-3 inline-flex text-xs font-semibold text-[color:var(--accent-primary)]" href={violation.skill_url} target="_blank">View skill</Link>
                </article>
              )) : <div className="rounded-xl border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 p-4 text-sm text-[color:var(--accent-green)]">No skill violations recorded for this PR.</div>}
            </div>
          </section>
          <section className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
            <h3 className="font-semibold">Sessions timeline</h3>
            <div className="mt-4 space-y-3">
              {detail.sessions.length ? detail.sessions.map((session) => (
                <div className="flex items-center justify-between gap-3 rounded-xl bg-black/15 p-3" key={session.id}>
                  <div>
                    <div className="text-sm font-semibold">{AGENT_LABELS[session.agent_runtime] ?? session.agent_runtime}</div>
                    <div className="text-xs text-[color:var(--text-secondary)]">{session.skills_loaded.length} skills loaded</div>
                  </div>
                  <Link className="text-sm font-semibold text-[color:var(--accent-primary)]" href={session.replay_url}>Replay →</Link>
                </div>
              )) : <p className="text-sm text-[color:var(--text-secondary)]">No agent session was linked to this PR.</p>}
            </div>
          </section>
        </div>
      )}
      {manifestOpen && manifest ? (
        <div className="fixed inset-0 z-[90] flex items-center justify-center bg-black/70 p-4">
          <div className="max-h-[86vh] w-full max-w-3xl overflow-hidden rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] shadow-2xl">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[color:var(--bg-border)] p-4">
              <div>
                <h3 className="font-semibold text-[color:var(--text-primary)]">Signed Provenance Manifest</h3>
                <p className="text-xs text-[color:var(--text-secondary)]">PR #{detail?.github_pr_number}</p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button className="rounded-lg border border-[color:var(--bg-border)] px-3 py-1.5 text-xs font-semibold text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)]" onClick={downloadManifest} type="button">Download</button>
                <button className="rounded-lg border border-[color:var(--bg-border)] px-3 py-1.5 text-xs font-semibold text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)]" onClick={runVerify} type="button">Verify</button>
                <button className="rounded-lg p-2 text-[color:var(--text-secondary)] hover:bg-[color:var(--bg-surface)]" onClick={() => setManifestOpen(false)} type="button"><X className="h-4 w-4" /></button>
              </div>
            </div>
            {verifyMessage ? (
              <div className={cn("mx-4 mt-4 rounded-lg border p-3 text-sm", verifyMessage.valid ? "border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : "border-red-500/30 bg-red-500/10 text-red-100")}>
                {verifyMessage.valid ? "✓" : "✗"} {verifyMessage.message}
              </div>
            ) : null}
            <pre className="m-4 max-h-[62vh] overflow-auto rounded-xl bg-black/30 p-4 text-xs leading-relaxed text-[color:var(--text-secondary)]">{JSON.stringify(manifest, null, 2)}</pre>
          </div>
        </div>
      ) : null}
    </aside>
  );
}

export function AgentPrInboxClient({ accessToken, apiKey, orgId, initialData, initialParams, repos }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [data, setData] = useState<AgentPrListResponse | null>(initialData);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<AgentPrDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [cursorIndex, setCursorIndex] = useState(0);
  const [highlightIds, setHighlightIds] = useState<Set<string>>(new Set());
  const [now, setNow] = useState(Date.now());

  const params = useMemo(() => new URLSearchParams(searchParams.toString() || initialParams), [initialParams, searchParams]);
  const items = useMemo(() => data?.items ?? [], [data?.items]);

  const load = useCallback(async (nextParams = params) => {
    if (!orgId) return;
    setLoading(true);
    setError("");
    try {
      const nextData = await fetchAgentPrs(accessToken, orgId, nextParams);
      setData(nextData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown API error");
    } finally {
      setLoading(false);
    }
  }, [accessToken, orgId, params]);

  const updateParam = (key: string, value: string) => {
    const next = new URLSearchParams(params.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    if (!next.has("state")) next.set("state", "all");
    router.replace(`${pathname}?${next.toString()}`, { scroll: false });
    void load(next);
  };

  const openDetail = useCallback(async (id: string) => {
    setSelectedId(id);
    setDetailLoading(true);
    try {
      setDetail(await fetchAgentPrDetail(accessToken, orgId, id));
    } finally {
      setDetailLoading(false);
    }
  }, [accessToken, orgId]);

  useEffect(() => {
    const interval = window.setInterval(() => setNow(Date.now()), 10000);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!orgId || !items.length) return;
    const lastVisitedKey = `${STORAGE_PREFIX}.lastVisited.${orgId}`;
    const unreadKey = `${STORAGE_PREFIX}.unreadCount.${orgId}`;
    const lastVisited = Number.parseInt(window.localStorage.getItem(lastVisitedKey) || "0", 10);
    const unread = items.filter((item) => item.opened_at && new Date(item.opened_at).getTime() > lastVisited).length;
    window.localStorage.setItem(unreadKey, String(unread));
    window.dispatchEvent(new StorageEvent("storage", { key: unreadKey, newValue: String(unread) }));
    window.localStorage.setItem(lastVisitedKey, String(Date.now()));
  }, [items, orgId]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") {
        event.preventDefault();
        searchInputRef.current?.focus();
      }
      if (event.key === "Escape") setSelectedId(null);
      if (!items.length) return;
      if (event.key === "j") {
        event.preventDefault();
        setCursorIndex((index) => Math.min(items.length - 1, index + 1));
      }
      if (event.key === "k") {
        event.preventDefault();
        setCursorIndex((index) => Math.max(0, index - 1));
      }
      if (event.key === "Enter") {
        event.preventDefault();
        const item = items[cursorIndex];
        if (item) void openDetail(item.pr_id);
      }
      if (event.key === "a") {
        const url = items[cursorIndex]?.url;
        if (url) window.open(url, "_blank", "noopener,noreferrer");
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [cursorIndex, items, openDetail]);

  useEffect(() => {
    if (!orgId) return;
    const interval = window.setInterval(() => void load(), 30000);
    let source: EventSource | null = null;
    if (apiKey) {
      source = new EventSource(`${API_URL}/orgs/${orgId}/feed/stream?key=${encodeURIComponent(apiKey)}`);
      source.onmessage = () => {
        void load();
      };
    }
    return () => {
      window.clearInterval(interval);
      source?.close();
    };
  }, [apiKey, load, orgId]);

  useEffect(() => {
    const requestedPr = params.get("pr");
    if (requestedPr && requestedPr !== selectedId) {
      void openDetail(requestedPr);
    }
  }, [openDetail, params, selectedId]);

  const newestPrId = items[0]?.pr_id;
  useEffect(() => {
    if (!items.length) return;
    const newest = newestPrId;
    if (!newest) return;
    setHighlightIds((existing) => new Set([...existing, newest]));
    const timeout = window.setTimeout(() => setHighlightIds((existing) => {
      const next = new Set(existing);
      next.delete(newest);
      return next;
    }), 2000);
    return () => window.clearTimeout(timeout);
  }, [items, newestPrId]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-1 text-xs font-semibold text-[color:var(--text-secondary)]">
            <GitPullRequest className="h-3.5 w-3.5" /> Agent code review
          </div>
          <h1 className="mt-3 text-[32px] font-semibold tracking-[-0.02em] text-[color:var(--text-primary)]">Agent PR Inbox</h1>
          <p className="mt-2 max-w-2xl text-sm text-[color:var(--text-secondary)]">Every GitHub PR, scored by risk and attribution, with agent context when Skillayer can prove it.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" disabled={loading} onClick={() => void load()} type="button">
          <RefreshCcw className={cn("h-4 w-4", loading && "animate-spin")} /> Refresh
        </button>
      </div>
      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-wrap gap-2">
          {AGENTS.map((agent) => (
            <button className={cn("rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors", (params.get("agent") ?? "") === agent.key ? "border-[color:var(--accent-primary)] bg-[color:var(--accent-primary)]/15 text-[color:var(--accent-primary)]" : "border-[color:var(--bg-border)] text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]")} key={agent.key || "all"} onClick={() => updateParam("agent", agent.key)} type="button">
              <span className="mr-1.5 inline-block h-2 w-2 rounded-full" style={{ backgroundColor: agent.color }} />{agent.label}
            </button>
          ))}
        </div>
        <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_1fr_150px_180px_170px]">
          <div className="flex rounded-xl border border-[color:var(--bg-border)] bg-black/15 p-1">
            {[["", "All risk"], ["red", "Red"], ["yellow", "Yellow"], ["green", "Green"]].map(([key, label]) => (
              <button className={cn("flex-1 rounded-lg px-3 py-2 text-xs font-semibold", (params.get("risk_tier") ?? "") === key ? "bg-white/10 text-[color:var(--text-primary)]" : "text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]")} key={key || "all-risk"} onClick={() => updateParam("risk_tier", key)} type="button">{label}</button>
            ))}
          </div>
          <label className="relative block">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
            <input className="h-10 w-full rounded-xl border border-[color:var(--bg-border)] bg-black/15 pl-9 pr-3 text-sm text-[color:var(--text-primary)] outline-none transition-colors focus:border-[color:var(--accent-primary)]" defaultValue={params.get("search") ?? ""} onKeyDown={(event) => { if (event.key === "Enter") updateParam("search", event.currentTarget.value); }} placeholder="Search PR title..." ref={searchInputRef} />
          </label>
          <select className="h-10 rounded-xl border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm text-[color:var(--text-primary)]" onChange={(event) => updateParam("state", event.target.value)} value={params.get("state") ?? "all"}>
            <option value="all">All states</option>
            <option value="open">Open</option>
            <option value="merged">Merged</option>
            <option value="closed">Closed</option>
          </select>
          <select className="h-10 rounded-xl border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm text-[color:var(--text-primary)]" onChange={(event) => updateParam("repo", event.target.value)} value={params.get("repo") ?? ""}>
            <option value="">All repos</option>
            {repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.name}</option>)}
          </select>
          <select className="h-10 rounded-xl border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm text-[color:var(--text-primary)]" onChange={(event) => updateParam("sort", event.target.value)} value={params.get("sort") ?? "opened_at"}>
            <option value="opened_at">Newest</option>
            <option value="risk_score">Risk score</option>
            <option value="violations">Violations</option>
          </select>
        </div>
      </section>
      {error ? <ErrorState error={error} onRetry={() => void load()} /> : items.length ? (
        <div className="space-y-3">
          {items.map((item, index) => (
            <PrCard active={cursorIndex === index || highlightIds.has(item.pr_id)} item={item} key={item.pr_id} onOpen={() => void openDetail(item.pr_id)} selected={selectedId === item.pr_id} />
          ))}
        </div>
      ) : <EmptyState />}
      <div className="flex items-center justify-between text-xs text-[color:var(--text-tertiary)]">
        <span>{data?.total_count ?? 0} PRs · Updated {relativeTime(new Date(now).toISOString())}</span>
        <span className="inline-flex items-center gap-1"><Filter className="h-3.5 w-3.5" /> Press / to search, j/k to move, Enter to open</span>
      </div>
      {selectedId ? <DetailPanel accessToken={accessToken} detail={detail} loading={detailLoading} onClose={() => { setSelectedId(null); setDetail(null); }} orgId={orgId} /> : null}
    </div>
  );
}
