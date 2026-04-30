"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type QualitySignal = "strong" | "mixed" | "weak";
type FeedEvent = {
  id: string;
  session_id: string;
  agent_runtime: string;
  agent?: string;
  repo_name: string;
  repo?: string;
  loaded_at: string;
  ts?: string;
  skills_loaded: string[];
  session_context: string;
  skill_count: number;
  quality_signal: QualitySignal;
  quality_reason: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

const AGENT_LABELS: Record<string, string> = {
  claude_code: "Claude Code",
  codex: "Codex",
  codex_cli: "Codex CLI",
  cursor: "Cursor",
  copilot: "GitHub Copilot",
  github_copilot: "GitHub Copilot",
  gemini_cli: "Gemini CLI",
  gemini: "Gemini CLI",
  devin: "Devin",
  unknown: "Unknown",
  unidentified_agent: "Unidentified Agent",
};

function label(agent: string): string {
  return AGENT_LABELS[agent] ?? AGENT_LABELS[agent?.replace(/-/g, "_")] ?? (agent ? agent.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()) : "Unknown");
}

function relative(ts: string, now: number): string {
  const diff = Math.max(0, Math.floor((now - new Date(ts).getTime()) / 1000));
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

function signalTone(signal: QualitySignal): string {
  if (signal === "strong") return "bg-[color:var(--accent-green)]";
  if (signal === "mixed") return "bg-[#f59e0b]";
  return "bg-[#ef4444]";
}

export function LiveFeed({ orgId, apiKey }: { orgId: string; apiKey: string }) {
  const [events, setEvents] = useState<FeedEvent[]>([]);
  const [status, setStatus] = useState<"connected" | "reconnecting" | "disconnected">("reconnecting");
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const tick = window.setInterval(() => setNow(Date.now()), 10000);
    return () => window.clearInterval(tick);
  }, []);

  useEffect(() => {
    let source: EventSource | null = null;
    let retry: number | null = null;
    let cancelled = false;

    async function loadRecent() {
      const response = await fetch(`${API_URL}/orgs/${orgId}/feed/recent`, { headers: { Authorization: `Bearer ${apiKey}` } });
      if (response.ok) {
        const body = (await response.json()) as { events: FeedEvent[] };
        setEvents(body.events.slice(0, 10));
      }
    }

    function connect() {
      source?.close();
      source = new EventSource(`${API_URL}/orgs/${orgId}/feed/stream?key=${encodeURIComponent(apiKey)}`);
      source.onopen = () => setStatus("connected");
      source.onerror = () => {
        source?.close();
        setStatus("reconnecting");
        if (!cancelled) retry = window.setTimeout(connect, 3000);
      };
    }

    if (orgId && apiKey) {
      void loadRecent();
      connect();
    } else {
      setStatus("disconnected");
    }
    return () => {
      cancelled = true;
      source?.close();
      if (retry) window.clearTimeout(retry);
    };
  }, [apiKey, orgId]);

  const statusClass = useMemo(() => {
    if (status === "connected") return "text-[color:var(--accent-green)]";
    if (status === "reconnecting") return "text-[#f59e0b]";
    return "text-[#ef4444]";
  }, [status]);

  return (
    <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Recent Agent Sessions</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">What your agents were working on and whether they had the right guidance.</p>
        </div>
        <span className={`text-[12px] font-semibold capitalize ${statusClass}`}>{status === "reconnecting" ? "Reconnecting..." : status}</span>
      </div>
      <div className="space-y-3">
        {events.length ? (
          events.map((event) => {
            const visible = event.skills_loaded.slice(0, 4);
            const extra = Math.max(0, event.skills_loaded.length - visible.length);
            return (
              <article className="rounded-xl border border-white/6 bg-black/10 p-4" key={event.session_id}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="font-semibold text-[color:var(--text-primary)]">{label(event.agent_runtime)} · {event.repo_name ?? event.repo}</div>
                  <div className="text-sm text-[color:var(--text-secondary)]">{event.session_context} · {relative(event.loaded_at ?? event.ts ?? "", now)}</div>
                </div>
                <p className="mt-3 text-sm text-[color:var(--text-secondary)]">
                  Skills loaded: {visible.join(", ")}{extra ? ` (+${extra} more)` : ""}
                </p>
                <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
                  <div className="inline-flex items-center gap-2 text-sm text-[color:var(--text-secondary)]">
                    <span className={`h-2.5 w-2.5 rounded-full ${signalTone(event.quality_signal)}`} />
                    <span className="capitalize">{event.quality_signal}</span>
                    <span>{event.quality_reason}</span>
                  </div>
                  <Link className="text-sm font-semibold text-[color:var(--accent-primary)]" href={`/dashboard/sessions/${event.session_id}`}>View session details →</Link>
                </div>
              </article>
            );
          })
        ) : (
          <div className="rounded-lg border border-dashed border-[color:var(--bg-border)] p-6 text-center text-[13px] text-[color:var(--text-secondary)]">
            No agent sessions recorded yet. Start a coding session with Claude Code or Codex and load skills to see activity here.
          </div>
        )}
      </div>
    </section>
  );
}
