"use client";

import Link from "next/link";
import { Filter, Radio, Search } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import type { ActivityEvent, ActivityFeedResponse, ActivityRepoOption } from "./activity-data";

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

function compactNumber(value: number | null | undefined): string {
  const safe = Number(value ?? 0);
  if (safe >= 1_000_000) return `${(safe / 1_000_000).toFixed(safe >= 10_000_000 ? 0 : 1)}M`;
  if (safe >= 1_000) return `${(safe / 1_000).toFixed(safe >= 10_000 ? 0 : 1)}K`;
  return String(safe);
}

function formatMoney(value: number | null | undefined): string {
  const safe = Number(value ?? 0);
  return safe > 0 ? `$${safe.toFixed(safe >= 1 ? 2 : 4)}` : "$0.00";
}

function providerLabel(value: string): string {
  const normalized = value.toLowerCase();
  if (normalized === "codex_cli") return "Codex CLI";
  if (normalized === "claude_code") return "Claude Code";
  if (normalized === "codex") return "Codex";
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function activitySummary(event: ActivityEvent): string | null {
  const metrics = event.activity_metrics;
  if (!metrics) return null;
  const parts = [
    [`edited ${metrics.edited_files ?? 0} files`, metrics.edited_files],
    [`explored ${metrics.explored_files ?? 0}`, metrics.explored_files],
    [`${metrics.searches ?? 0} searches`, metrics.searches],
    [`${metrics.lists ?? 0} lists`, metrics.lists],
    [`ran ${metrics.commands ?? 0} commands`, metrics.commands],
  ];
  return parts.some(([, value]) => Number(value ?? 0) > 0) ? parts.map(([label]) => label).join(" · ") : null;
}

const filterLabels: Record<string, string> = {
  hours: "Window",
  agent_provider: "Provider",
  user: "User",
  repo_id: "Repo",
  skill_id: "Skill",
  action_class: "Action",
  outcome: "Outcome",
  risk_band: "Risk",
  repo_sensitivity_tier: "Tier",
};

function filterValue(key: string, value: string): string {
  if (key === "hours") {
    if (value === "1") return "1 hour";
    if (value === "24") return "24 hours";
    if (value === "168") return "7 days";
    if (value === "720") return "30 days";
  }
  return value.replaceAll("_", " ");
}

export function LiveFeedPanel({
  events,
  feedAvailable,
  orgId,
  query,
  repoOptions,
  sessionCount,
  streamKey,
  hasMore,
  nextOffset,
  total,
}: {
  events: ActivityEvent[];
  feedAvailable: boolean;
  orgId: string;
  query: Record<string, string>;
  repoOptions: ActivityRepoOption[];
  sessionCount: number;
  streamKey: string;
  hasMore: boolean;
  nextOffset: number | null;
  total: number;
}) {
  const [rows, setRows] = useState(events);
  const [status, setStatus] = useState(streamKey ? "connecting" : "offline");
  const [canLoadMore, setCanLoadMore] = useState(hasMore);
  const [loadOffset, setLoadOffset] = useState(nextOffset);
  const [loadingMore, setLoadingMore] = useState(false);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const repoById = useMemo(() => new Map(repoOptions.map((repo) => [repo.id, repo])), [repoOptions]);
  const providerOptions = useMemo(
    () => Array.from(new Set(repoOptions.flatMap((repo) => repo.providers ?? []))).sort((a, b) => providerLabel(a).localeCompare(providerLabel(b))),
    [repoOptions],
  );
  const selectedRepo = query.repo_id ? repoById.get(query.repo_id) : null;
  const repoRowCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const event of rows) {
      counts.set(event.repo_id, (counts.get(event.repo_id) ?? 0) + 1);
    }
    return counts;
  }, [rows]);
  const taskRepos = useMemo(
    () => repoOptions.filter((repo) => (repo.session_count ?? 0) > 0 || (repoRowCounts.get(repo.id) ?? 0) > 0),
    [repoOptions, repoRowCounts],
  );

  function feedHref(overrides: Record<string, string | null>): string {
    const params = new URLSearchParams(query);
    if (!params.get("hours")) params.set("hours", "24");
    for (const [key, value] of Object.entries(overrides)) {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    }
    return `/activity/live-feed?${params.toString()}`;
  }

  useEffect(() => {
    setRows(events);
    setCanLoadMore(hasMore);
    setLoadOffset(nextOffset);
  }, [events, hasMore, nextOffset]);

  useEffect(() => {
    if (!orgId || !streamKey) return undefined;
    const streamParams = new URLSearchParams({ key: streamKey });
    for (const key of Object.keys(filterLabels)) {
      const value = query[key];
      if (value) streamParams.set(key, value);
    }
    const source = new EventSource(`${API_URL}/v8/orgs/${orgId}/activity/feed/stream?${streamParams.toString()}`);
    source.onopen = () => setStatus("live");
    source.onerror = () => setStatus("reconnecting");
    source.onmessage = (message) => {
      const event = JSON.parse(message.data) as ActivityEvent;
      setRows((current) => [event, ...current.filter((item) => item.id !== event.id)].slice(0, 50));
    };
    return () => source.close();
  }, [orgId, query, streamKey]);

  useEffect(() => {
    if (!canLoadMore || loadingMore || loadOffset === null || !loadMoreRef.current || !orgId) return undefined;
    const node = loadMoreRef.current;
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      setLoadingMore(true);
      const params = new URLSearchParams(query);
      params.set("offset", String(loadOffset));
      params.set("limit", params.get("limit") || "25");
      fetch(`${API_URL}/v8/orgs/${orgId}/activity/feed?${params.toString()}`, { headers: { "Content-Type": "application/json" } })
        .then((response) => (response.ok ? response.json() : null))
        .then((payload: ActivityFeedResponse | null) => {
          if (!payload) {
            setCanLoadMore(false);
            return;
          }
          setRows((current) => {
            const seen = new Set(current.map((item) => item.id));
            const nextRows = payload.events.filter((item) => !seen.has(item.id));
            return [...current, ...nextRows];
          });
          setCanLoadMore(Boolean(payload.has_more));
          setLoadOffset(payload.next_offset ?? null);
        })
        .catch(() => setCanLoadMore(false))
        .finally(() => setLoadingMore(false));
    }, { rootMargin: "400px 0px" });
    observer.observe(node);
    return () => observer.disconnect();
  }, [canLoadMore, loadOffset, loadingMore, orgId, query]);

  const activeFilters = useMemo(
    () =>
      Object.entries(query).filter(([key, value]) => {
        if (!value) return false;
        if (key === "hours" && value === "24") return false;
        return key in filterLabels;
      }),
    [query],
  );
  const visibleLimit = Number(query.limit ?? 25);
  const expandedLimit = Math.max(visibleLimit + 25, rows.length + 25);

  return (
    <section className="space-y-4">
      <form className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" method="get">
        <label className="flex items-center gap-2 text-sm font-semibold text-[color:var(--text-secondary)]">
          <Filter className="h-4 w-4" />
          Filters
        </label>
        {activeFilters.length ? (
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-[color:var(--text-secondary)]">
            <span className="w-full font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)] md:w-auto">Shareable filter set</span>
            {activeFilters.map(([key, value]) => (
              <span className="rounded-full border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-2.5 py-1" key={key}>
                {filterLabels[key]}: {key === "repo_id" ? (repoById.get(value)?.full_name ?? filterValue(key, value)) : key === "agent_provider" ? providerLabel(value) : filterValue(key, value)}
              </span>
            ))}
            <Link className="rounded-full border border-[color:var(--bg-border)] px-2.5 py-1 font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href="/activity/live-feed">
              Clear
            </Link>
          </div>
        ) : null}
        <div className="mt-3 grid gap-3 md:grid-cols-4 xl:grid-cols-[140px_minmax(170px,1fr)_minmax(190px,1.2fr)_repeat(5,minmax(0,1fr))_auto]">
          <select aria-label="Time window" className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.hours ?? "24"} name="hours">
            <option value="1">1 hour</option>
            <option value="24">24 hours</option>
            <option value="168">7 days</option>
            <option value="720">30 days</option>
          </select>
          <select aria-label="Agent provider" className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.agent_provider ?? ""} name="agent_provider">
            <option value="">All providers</option>
            {providerOptions.map((provider) => (
              <option key={provider} value={provider}>
                {providerLabel(provider)}
              </option>
            ))}
          </select>
          <input aria-label="User" className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.user ?? ""} name="user" placeholder="User" />
          <select aria-label="Repository" className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.repo_id ?? ""} name="repo_id">
            <option value="">All repos</option>
            {repoOptions.map((repo) => (
              <option key={repo.id} value={repo.id}>
                {repo.full_name} ({(repo.session_count ?? 0).toLocaleString()})
              </option>
            ))}
          </select>
          <input aria-label="Skill ID" className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.skill_id ?? ""} name="skill_id" placeholder="Skill ID" />
          <select aria-label="Action class" className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.action_class ?? ""} name="action_class">
            <option value="">All actions</option>
            <option value="read">Read</option>
            <option value="write">Write</option>
            <option value="exec">Exec</option>
            <option value="network">Network</option>
          </select>
          <select aria-label="Outcome" className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.outcome ?? ""} name="outcome">
            <option value="">All outcomes</option>
            <option value="allowed">Allowed</option>
            <option value="denied">Denied</option>
            <option value="blocked">Blocked</option>
          </select>
          <select aria-label="Risk band" className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.risk_band ?? ""} name="risk_band">
            <option value="">All risk</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <select aria-label="Repository sensitivity tier" className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.repo_sensitivity_tier ?? ""} name="repo_sensitivity_tier">
            <option value="">All tiers</option>
            <option value="public">Public</option>
            <option value="internal">Internal</option>
            <option value="confidential">Confidential</option>
            <option value="restricted">Restricted</option>
            <option value="regulated">Regulated</option>
          </select>
          <button className="inline-flex min-h-10 items-center justify-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" type="submit">
            <Search className="h-4 w-4" />
            Apply
          </button>
        </div>
      </form>

      {taskRepos.length ? (
        <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Repository task feed</h2>
              <p className="mt-1 text-xs leading-5 text-[color:var(--text-secondary)]">
                Click a repository to show only the Codex, Claude Code, and coding-agent tasks tied to that repo.
              </p>
            </div>
            {selectedRepo ? (
              <Link className="w-fit rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href={feedHref({ repo_id: null })}>
                Show all repositories
              </Link>
            ) : null}
          </div>
          <div className="mt-4 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
            <Link
              className={`rounded-md border px-3 py-3 text-sm transition-colors ${!query.repo_id ? "border-[color:var(--accent-primary)] bg-[color:var(--accent-primary)]/10 text-[color:var(--text-primary)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-base)] text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]"}`}
              href={feedHref({ repo_id: null })}
            >
              <span className="block font-semibold">All repositories</span>
              <span className="mt-1 block text-xs text-[color:var(--text-tertiary)]">{query.repo_id ? "Clear repo filter" : `${rows.length} visible tasks`}</span>
            </Link>
            {taskRepos.map((repo) => {
              const rowCount = repoRowCounts.get(repo.id) ?? 0;
              const isActive = query.repo_id === repo.id;
              return (
                <Link
                  className={`rounded-md border px-3 py-3 text-sm transition-colors ${isActive ? "border-[color:var(--accent-primary)] bg-[color:var(--accent-primary)]/10 text-[color:var(--text-primary)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-base)] text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]"}`}
                  href={feedHref({ repo_id: repo.id })}
                  key={repo.id}
                >
                  <span className="block truncate font-semibold">{repo.full_name}</span>
                  <span className="mt-1 block text-xs text-[color:var(--text-tertiary)]">
                    {rowCount ? `${rowCount} tasks in this window` : `${(repo.session_count ?? 0).toLocaleString()} total runs`}
                  </span>
                </Link>
              );
            })}
          </div>
        </section>
      ) : null}

      <div className="flex items-center justify-between text-sm text-[color:var(--text-secondary)]">
        <span>
          {rows.length} events
          {total > rows.length ? <span className="ml-1 text-[color:var(--text-tertiary)]">of {total}+</span> : null}
          {selectedRepo ? <span className="ml-2 text-[color:var(--text-tertiary)]">{" "}for {selectedRepo.full_name}</span> : null}
        </span>
        <span className="inline-flex items-center gap-2 capitalize">
          <Radio className="h-4 w-4 text-[color:var(--accent-primary)]" />
          {status}
        </span>
      </div>

      <div className="overflow-x-auto rounded-lg border border-[color:var(--bg-border)]">
        <div className="grid min-w-[1180px] grid-cols-[132px_minmax(170px,1fr)_minmax(260px,1.2fr)_120px_150px_160px_110px] bg-[color:var(--bg-surface)] px-4 py-3 text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">
          <span>Time</span>
          <span>Agent</span>
          <span>Scope</span>
          <span>Action</span>
          <span>Outcome</span>
          <span>Risk</span>
          <span>Replay</span>
        </div>
        {rows.length ? (
          rows.map((event) => (
            <article className="grid min-w-[1180px] grid-cols-[132px_minmax(170px,1fr)_minmax(260px,1.2fr)_120px_150px_160px_110px] gap-3 border-t border-[color:var(--bg-border)] px-4 py-3 text-sm" key={event.id}>
              <span className="text-[color:var(--text-secondary)]">{formatTime(event.timestamp)}</span>
              <span>
                <b className="block text-[color:var(--text-primary)]">{event.agent}</b>
                <span className="text-[color:var(--text-tertiary)]">{event.user}</span>
                {event.model ? <span className="mt-1 block text-xs text-[color:var(--text-secondary)]">{event.model}{event.intelligence_tier ? ` · ${event.intelligence_tier}` : ""}</span> : null}
              </span>
              <span>
                <Link className="block font-semibold text-[color:var(--text-primary)] hover:text-[color:var(--accent-primary)] hover:underline" href={feedHref({ repo_id: event.repo_id })}>
                  {event.repo}
                </Link>
                <span className="text-[color:var(--text-secondary)]">{event.skill}</span>
                <span className="mt-1 block text-xs capitalize text-[color:var(--text-tertiary)]">{event.repo_sensitivity_tier} tier</span>
                {event.tokens_total ? <span className="mt-1 block text-xs text-[color:var(--accent-primary)]">{compactNumber(event.tokens_total)} tokens · {formatMoney(event.cost_usd)}</span> : null}
                {activitySummary(event) ? <span className="mt-1 block text-xs text-[color:var(--text-tertiary)]">{activitySummary(event)}</span> : null}
              </span>
              <span className="capitalize text-[color:var(--text-secondary)]">{event.action_class}</span>
              <span>
                <b className="block capitalize text-[color:var(--text-secondary)]">{event.outcome.replaceAll("_", " ")}</b>
                {event.trigger ? <span className="text-xs text-[color:var(--text-tertiary)]">{event.trigger.label}</span> : null}
              </span>
              <span>
                <span className={`inline-flex h-fit rounded-md border px-2 py-1 text-xs font-semibold capitalize ${riskClass(event.risk_band)}`}>{event.risk_band} {event.risk_score}</span>
                {event.risk_reasons?.length ? <span className="mt-1 block text-xs leading-4 text-[color:var(--text-tertiary)]">{event.risk_reasons.slice(0, 3).join(" · ")}</span> : null}
              </span>
              <span>
                {event.replay_url ? (
                  <Link className="text-sm font-semibold text-[color:var(--accent-primary)]" href={event.replay_url}>Open</Link>
                ) : event.session_db_id ? (
                  <Link className="text-sm font-semibold text-[color:var(--accent-primary)]" href={`/activity/replay/${event.session_db_id}?repo=${event.repo_id}`}>Open</Link>
                ) : (
                  <span className="text-xs text-[color:var(--text-tertiary)]">No replay</span>
                )}
              </span>
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
      <div ref={loadMoreRef} className="rounded-lg border border-dashed border-[color:var(--bg-border)] px-4 py-3 text-center text-sm text-[color:var(--text-secondary)]">
        {loadingMore ? "Loading more activity..." : canLoadMore && loadOffset !== null ? (
          <Link className="font-semibold text-[color:var(--accent-primary)]" href={feedHref({ offset: null, limit: String(expandedLimit) })}>
            Load more activity
          </Link>
        ) : "All visible activity for this filter is loaded."}
      </div>
    </section>
  );
}
