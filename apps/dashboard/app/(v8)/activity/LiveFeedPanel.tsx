"use client";

import Link from "next/link";
import { Filter, Radio, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { ActivityEvent } from "./activity-data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

function formatTime(value: string | null): string {
  if (!value) return "Unknown";
  return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit", month: "short", day: "numeric" }).format(new Date(value));
}

function riskClass(band: ActivityEvent["risk_band"]): string {
  if (band === "high") return "border-red-500/40 bg-red-500/10 text-red-200";
  if (band === "medium") return "border-amber-500/40 bg-amber-500/10 text-amber-200";
  return "border-[color:var(--accent-green)]/40 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]";
}

export function LiveFeedPanel({
  events,
  feedAvailable,
  orgId,
  searchParams,
  sessionCount,
  streamKey,
}: {
  events: ActivityEvent[];
  feedAvailable: boolean;
  orgId: string;
  searchParams: URLSearchParams;
  sessionCount: number;
  streamKey: string;
}) {
  const [rows, setRows] = useState(events);
  const [status, setStatus] = useState(streamKey ? "connecting" : "offline");

  useEffect(() => setRows(events), [events]);

  useEffect(() => {
    if (!orgId || !streamKey) return undefined;
    const source = new EventSource(`${API_URL}/v8/orgs/${orgId}/activity/feed/stream?key=${encodeURIComponent(streamKey)}`);
    source.onopen = () => setStatus("live");
    source.onerror = () => setStatus("reconnecting");
    source.onmessage = (message) => {
      const event = JSON.parse(message.data) as ActivityEvent;
      setRows((current) => [event, ...current.filter((item) => item.id !== event.id)].slice(0, 50));
    };
    return () => source.close();
  }, [orgId, streamKey]);

  const query = useMemo(() => Object.fromEntries(searchParams.entries()), [searchParams]);

  return (
    <section className="space-y-4">
      <form className="grid gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-[120px_repeat(5,minmax(0,1fr))_auto]" method="get">
        <label className="flex items-center gap-2 text-sm font-semibold text-[color:var(--text-secondary)]">
          <Filter className="h-4 w-4" />
          Filters
        </label>
        <select className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.hours ?? "24"} name="hours">
          <option value="1">1 hour</option>
          <option value="24">24 hours</option>
          <option value="168">7 days</option>
          <option value="720">30 days</option>
        </select>
        <input className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.agent_provider ?? ""} name="agent_provider" placeholder="Provider" />
        <input className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.repo_id ?? ""} name="repo_id" placeholder="Repo ID" />
        <select className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.risk_band ?? ""} name="risk_band">
          <option value="">All risk</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <select className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.repo_sensitivity_tier ?? ""} name="repo_sensitivity_tier">
          <option value="">All tiers</option>
          <option value="public">Public</option>
          <option value="internal">Internal</option>
          <option value="confidential">Confidential</option>
          <option value="restricted">Restricted</option>
        </select>
        <button className="inline-flex items-center justify-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" type="submit">
          <Search className="h-4 w-4" />
          Apply
        </button>
      </form>

      <div className="flex items-center justify-between text-sm text-[color:var(--text-secondary)]">
        <span>{rows.length} events</span>
        <span className="inline-flex items-center gap-2 capitalize">
          <Radio className="h-4 w-4 text-[color:var(--accent-primary)]" />
          {status}
        </span>
      </div>

      <div className="overflow-hidden rounded-lg border border-[color:var(--bg-border)]">
        <div className="grid grid-cols-[132px_minmax(180px,1fr)_minmax(170px,1fr)_120px_110px] bg-[color:var(--bg-surface)] px-4 py-3 text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">
          <span>Time</span>
          <span>Agent</span>
          <span>Action</span>
          <span>Outcome</span>
          <span>Risk</span>
        </div>
        {rows.length ? (
          rows.map((event) => (
            <article className="grid grid-cols-[132px_minmax(180px,1fr)_minmax(170px,1fr)_120px_110px] gap-3 border-t border-[color:var(--bg-border)] px-4 py-3 text-sm" key={event.id}>
              <span className="text-[color:var(--text-secondary)]">{formatTime(event.timestamp)}</span>
              <span>
                <b className="block text-[color:var(--text-primary)]">{event.agent}</b>
                <span className="text-[color:var(--text-tertiary)]">{event.user}</span>
              </span>
              <span>
                <b className="block text-[color:var(--text-primary)]">{event.repo}</b>
                <span className="text-[color:var(--text-secondary)]">{event.skill}</span>
              </span>
              <span className="capitalize text-[color:var(--text-secondary)]">{event.outcome}</span>
              <span className={`h-fit rounded-md border px-2 py-1 text-xs font-semibold capitalize ${riskClass(event.risk_band)}`}>{event.risk_band} {event.risk_score}</span>
            </article>
          ))
        ) : (
          <div className="border-t border-[color:var(--bg-border)] p-8 text-center text-sm text-[color:var(--text-secondary)]">
            <div className="mx-auto max-w-xl">
              <p className="text-[15px] font-semibold text-[color:var(--text-primary)]">
                {feedAvailable ? "No live skill-load events in this window." : "Activity could not reach the API."}
              </p>
              <p className="mt-2 leading-6">
                {sessionCount > 0
                  ? `There ${sessionCount === 1 ? "is" : "are"} ${sessionCount} recorded agent ${sessionCount === 1 ? "session" : "sessions"}. Start with Sessions, then use Replay or Heatmap once events stream in.`
                  : "Start by analyzing a repo or connecting an agent. New agent sessions and skill-load events will appear here."}
              </p>
              <div className="mt-5 flex flex-wrap justify-center gap-3">
                {sessionCount > 0 ? (
                  <Link className="rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-[13px] font-semibold text-[color:var(--bg-base)]" href="/activity/sessions">View sessions</Link>
                ) : null}
                <Link className="rounded-md border border-[color:var(--bg-border)] px-4 py-2 text-[13px] font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href="/skills/repos">Analyze repo</Link>
                <Link className="rounded-md border border-[color:var(--bg-border)] px-4 py-2 text-[13px] font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href="/settings/connectors">Connectors</Link>
              </div>
            </div>
          </div>
        )}
      </div>

      {rows[0]?.session_db_id ? (
        <Link className="inline-flex text-sm font-semibold text-[color:var(--accent-primary)]" href={`/activity/replay/${rows[0].session_db_id}?repo=${rows[0].repo_id}`}>
          Open latest replay
        </Link>
      ) : null}
    </section>
  );
}
