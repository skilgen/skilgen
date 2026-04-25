"use client";

import { useEffect, useMemo, useState } from "react";
import { Tag } from "lucide-react";

type FeedEvent = { id: string; repo: string; skill: string; agent: string; ts: string };

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

function label(agent: string): string {
  return ({ claude_code: "Claude Code", codex: "Codex", cursor: "Cursor", unknown: "Unknown" } as Record<string, string>)[agent] || agent;
}

function pill(agent: string): string {
  if (agent === "claude_code") return "bg-violet-500/15 text-violet-200 ring-1 ring-violet-400/30";
  if (agent === "codex") return "bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-400/30";
  if (agent === "cursor") return "bg-blue-500/15 text-blue-200 ring-1 ring-blue-400/30";
  return "bg-white/10 text-[color:var(--text-secondary)] ring-1 ring-white/10";
}

function relative(ts: string, now: number): string {
  const diff = Math.max(0, Math.floor((now - new Date(ts).getTime()) / 1000));
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
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
        setEvents(body.events.slice(0, 50));
      }
    }

    function connect() {
      source?.close();
      source = new EventSource(`${API_URL}/orgs/${orgId}/feed/stream?key=${encodeURIComponent(apiKey)}`);
      source.onopen = () => setStatus("connected");
      source.onmessage = (message) => {
        const event = JSON.parse(message.data) as FeedEvent;
        setEvents((current) => [event, ...current.filter((item) => item.id !== event.id)].slice(0, 50));
      };
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
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-[color:var(--accent-green)]" />
          <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">Live Agent Activity</h2>
          <span className="rounded-full bg-white/10 px-2 py-0.5 text-[11px] text-[color:var(--text-secondary)]">{events.length}</span>
        </div>
        <span className={`text-[12px] font-semibold capitalize ${statusClass}`}>{status === "reconnecting" ? "Reconnecting..." : status}</span>
      </div>
      <div className="max-h-[400px] space-y-2 overflow-y-auto">
        {events.length ? (
          events.map((event) => (
            <div className="grid gap-2 rounded-lg border border-white/6 bg-black/10 p-3 text-[13px] md:grid-cols-[120px_1fr_1fr_80px] md:items-center" key={event.id}>
              <span className={`inline-flex w-fit rounded-full px-2.5 py-1 text-[11px] font-semibold ${pill(event.agent)}`}>{label(event.agent)}</span>
              <span className="font-medium text-[color:var(--text-primary)]">{event.repo}</span>
              <span className="inline-flex items-center gap-1 text-[color:var(--text-secondary)]"><Tag className="h-3.5 w-3.5" />{event.skill}</span>
              <span className="text-right text-[color:var(--text-tertiary)]">{relative(event.ts, now)}</span>
            </div>
          ))
        ) : (
          <div className="rounded-lg border border-dashed border-[color:var(--bg-border)] p-6 text-center text-[13px] text-[color:var(--text-secondary)]">Waiting for agent activity...</div>
        )}
      </div>
    </section>
  );
}
