"use client";

import { ChevronDown, ChevronRight, Download, RotateCcw, ScrollText, Search } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import type { AuditLogEvent, AuditLogResponse, Repo } from "../../../lib/data";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
const SEVERITIES = ["all", "info", "warning", "critical"] as const;

type SeverityFilter = (typeof SEVERITIES)[number];

type Props = {
  accessToken: string;
  orgId: string;
  initialAudit: AuditLogResponse | null;
  eventTypes: string[];
  repos: Repo[];
};

function authHeaders(accessToken: string): HeadersInit {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

function relativeTime(value: string): string {
  const time = new Date(value).getTime();
  const diff = Date.now() - time;
  const abs = Math.abs(diff);
  const minutes = Math.floor(abs / 60000);
  const suffix = diff >= 0 ? "ago" : "from now";
  if (minutes < 1) return diff >= 0 ? "Just now" : "Soon";
  if (minutes < 60) return `${minutes}m ${suffix}`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ${suffix}`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ${suffix}`;
  return new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function dateGroup(value: string): string {
  const date = new Date(value);
  const today = new Date();
  const start = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const eventStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const days = Math.round((start.getTime() - eventStart.getTime()) / 86400000);
  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  return date.toLocaleDateString(undefined, { month: "long", day: "numeric" });
}

function initials(actor: string | null): string {
  const value = actor || "system";
  const parts = value.replace(/^@/, "").split(/[^a-zA-Z0-9]+/).filter(Boolean);
  const letters = parts.length > 1 ? `${parts[0][0]}${parts[1][0]}` : value.slice(0, 2);
  return letters.toUpperCase();
}

function severityClasses(severity: AuditLogEvent["severity"]): { dot: string; text: string; bg: string } {
  if (severity === "critical") return { dot: "bg-red-400", text: "text-red-300", bg: "bg-red-500/10 border-red-400/30" };
  if (severity === "warning") return { dot: "bg-amber-400", text: "text-amber-300", bg: "bg-amber-500/10 border-amber-400/30" };
  return { dot: "bg-sky-400", text: "text-sky-300", bg: "bg-sky-500/10 border-sky-400/30" };
}

function buildQuery(filters: {
  eventType: string;
  severity: SeverityFilter;
  repoId: string;
  dateFrom: string;
  dateTo: string;
  search?: string;
  cursor?: string | null;
}): URLSearchParams {
  const query = new URLSearchParams({ limit: "50" });
  if (filters.search) query.set("search", filters.search);
  if (filters.eventType) query.set("event_type", filters.eventType);
  if (filters.severity !== "all") query.set("severity", filters.severity);
  if (filters.repoId) query.set("repo_id", filters.repoId);
  if (filters.dateFrom) query.set("date_from", `${filters.dateFrom}T00:00:00`);
  if (filters.dateTo) query.set("date_to", `${filters.dateTo}T23:59:59`);
  if (filters.cursor) query.set("cursor", filters.cursor);
  return query;
}

export function AuditLogClient({ accessToken, orgId, initialAudit, eventTypes, repos }: Props) {
  const [events, setEvents] = useState<AuditLogEvent[]>(initialAudit?.events ?? []);
  const [nextCursor, setNextCursor] = useState<string | null>(initialAudit?.next_cursor ?? null);
  const [hasMore, setHasMore] = useState(Boolean(initialAudit?.has_more));
  const [eventType, setEventType] = useState("");
  const [severity, setSeverity] = useState<SeverityFilter>("all");
  const [repoId, setRepoId] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [expandedDescription, setExpandedDescription] = useState<string | null>(null);
  const [expandedMetadata, setExpandedMetadata] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "loadingMore" | "error">("idle");
  const skippedInitialLoad = useRef(false);

  const filtersActive = Boolean(eventType || severity !== "all" || repoId || dateFrom || dateTo || debouncedSearch);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(search.trim()), 250);
    return () => window.clearTimeout(timer);
  }, [search]);

  const filteredEvents = useMemo(() => {
    const term = debouncedSearch.toLowerCase();
    if (!term) return events;
    return events.filter((event) => `${event.actor_login ?? "system"} ${event.summary}`.toLowerCase().includes(term));
  }, [debouncedSearch, events]);

  const groupedEvents = useMemo(() => {
    const groups: Array<{ label: string; events: AuditLogEvent[] }> = [];
    for (const event of filteredEvents) {
      const label = dateGroup(event.created_at);
      const group = groups.find((item) => item.label === label);
      if (group) group.events.push(event);
      else groups.push({ label, events: [event] });
    }
    return groups;
  }, [filteredEvents]);

  const loadEvents = useCallback(
    async ({ append = false, cursor = null }: { append?: boolean; cursor?: string | null } = {}) => {
      if (!orgId) return;
      setStatus(append ? "loadingMore" : "loading");
      const query = buildQuery({ eventType, severity, repoId, dateFrom, dateTo, search: debouncedSearch, cursor });
      try {
        const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/audit-log?${query.toString()}`, {
          headers: authHeaders(accessToken),
        });
        if (!response.ok) throw new Error("Could not load audit events");
        const body = (await response.json()) as AuditLogResponse;
        setEvents((current) => (append ? [...current, ...(body.events ?? [])] : body.events ?? []));
        setHasMore(Boolean(body.has_more));
        setNextCursor(body.next_cursor ?? null);
        setStatus("idle");
      } catch {
        setStatus("error");
      }
    },
    [accessToken, dateFrom, dateTo, debouncedSearch, eventType, orgId, repoId, severity],
  );

  useEffect(() => {
    if (!skippedInitialLoad.current) {
      skippedInitialLoad.current = true;
      return;
    }
    void loadEvents();
  }, [loadEvents]);

  const clearFilters = () => {
    setEventType("");
    setSeverity("all");
    setRepoId("");
    setDateFrom("");
    setDateTo("");
    setSearch("");
    setDebouncedSearch("");
  };

  const exportParams = buildQuery({ eventType, severity, repoId, dateFrom, dateTo, search: debouncedSearch });
  exportParams.delete("limit");
  const emptyText = filtersActive ? "No audit events match these filters." : "No audit events recorded yet.";

  const exportCsv = async () => {
    if (!orgId) return;
    const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/audit-log/export${exportParams.toString() ? `?${exportParams.toString()}` : ""}`, {
      headers: authHeaders(accessToken),
    });
    if (!response.ok) {
      setStatus("error");
      return;
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "audit-log.csv";
    link.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Audit Log</h1>
        <p className="mt-2 max-w-[760px] text-[15px] text-[color:var(--text-secondary)]">Every governance event across your org</p>
      </div>

      <div className="sticky top-0 z-20 border-y border-[color:var(--bg-border)] bg-[color:var(--bg-base)]/95 py-3 backdrop-blur">
        <div className="flex flex-wrap items-center gap-3">
          <label className="relative min-w-[240px] flex-1">
            <span className="sr-only">Search audit events</span>
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
            <input
              className="h-10 w-full rounded-lg border border-[color:var(--bg-border)] bg-black/15 pl-9 pr-3 text-sm text-[color:var(--text-primary)] outline-none transition-colors focus:border-[color:var(--accent-primary)]"
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search actor or description"
              value={search}
            />
          </label>
          <select className="h-10 rounded-lg border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]" onChange={(event) => setEventType(event.target.value)} value={eventType}>
            <option value="">All event types</option>
            {eventTypes.map((type) => <option key={type} value={type}>{type}</option>)}
          </select>
          <select className="h-10 rounded-lg border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]" onChange={(event) => setRepoId(event.target.value)} value={repoId}>
            <option value="">All repos</option>
            {repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.name || repo.full_name}</option>)}
          </select>
          <input aria-label="From date" className="h-10 rounded-lg border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]" onChange={(event) => setDateFrom(event.target.value)} type="date" value={dateFrom} />
          <input aria-label="To date" className="h-10 rounded-lg border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]" onChange={(event) => setDateTo(event.target.value)} type="date" value={dateTo} />
          <div className="flex items-center gap-1">
            {SEVERITIES.map((item) => (
              <button
                className={`h-9 rounded-full border px-3 text-xs font-semibold capitalize transition-colors ${severity === item ? "border-[color:var(--accent-primary)] bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[color:var(--accent-primary)]" : "border-[color:var(--bg-border)] text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]"}`}
                key={item}
                onClick={() => setSeverity(item)}
                type="button"
              >
                {item}
              </button>
            ))}
          </div>
          <button className="inline-flex h-10 items-center gap-2 rounded-lg border border-[color:var(--bg-border)] px-3 text-sm font-semibold text-[color:var(--text-primary)] transition-colors hover:border-[color:var(--accent-primary)]" onClick={exportCsv} type="button">
            <Download className="h-4 w-4" />
            Export CSV
          </button>
          {filtersActive ? (
            <button className="text-sm font-semibold text-[color:var(--text-secondary)] underline-offset-4 hover:text-[color:var(--text-primary)] hover:underline" onClick={clearFilters} type="button">
              Clear filters
            </button>
          ) : null}
        </div>
      </div>

      {status === "error" ? (
        <div className="flex items-center justify-between rounded-lg border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          <span>Unable to load audit events.</span>
          <button className="inline-flex items-center gap-2 rounded-md border border-red-300/30 px-3 py-1.5 font-semibold" onClick={() => loadEvents()} type="button">
            <RotateCcw className="h-3.5 w-3.5" />
            Retry
          </button>
        </div>
      ) : null}

      <div className="text-sm text-[color:var(--text-secondary)]">Showing {filteredEvents.length} events</div>

      {filteredEvents.length === 0 && status !== "loading" ? (
        <div className="border-y border-[color:var(--bg-border)] py-16 text-center">
          <ScrollText className="mx-auto h-8 w-8 text-[color:var(--text-tertiary)]" />
          <h2 className="mt-4 text-xl font-semibold text-[color:var(--text-primary)]">{emptyText}</h2>
          <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{filtersActive ? "Try a wider date range or fewer filters." : "Governance events will appear here as your team uses Skillayer."}</p>
        </div>
      ) : (
        <div className="space-y-8">
          {groupedEvents.map((group) => (
            <section key={group.label}>
              <h2 className="mb-4 text-sm font-semibold text-[color:var(--text-secondary)]">{group.label}</h2>
              <div className="relative border-l border-[color:var(--bg-border)] pl-5">
                {group.events.map((event) => {
                  const severity = severityClasses(event.severity);
                  const descriptionExpanded = expandedDescription === event.id;
                  const metadataExpanded = expandedMetadata === event.id;
                  const description = event.summary || "No description";
                  return (
                    <article className="relative pb-6 last:pb-0" key={event.id}>
                      <span className={`absolute -left-[25px] top-4 h-3 w-3 rounded-full ring-4 ring-[color:var(--bg-base)] ${severity.dot}`} />
                      <div className="flex flex-col gap-3 border-b border-[color:var(--bg-border)] pb-5 md:flex-row md:items-start md:justify-between">
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className={`inline-flex h-8 w-8 items-center justify-center rounded-full border text-xs font-semibold ${severity.bg} ${severity.text}`}>{initials(event.actor_login)}</span>
                            <span className="font-mono text-sm text-[color:var(--text-primary)]">@{event.actor_login || "system"}</span>
                            <span className="rounded-md border border-[color:var(--bg-border)] bg-black/20 px-2 py-1 font-mono text-xs text-[color:var(--text-secondary)]">{event.event_type}</span>
                            {event.repo_id ? (
                              <Link className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs font-semibold text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${event.repo_id}`}>
                                {event.repo_name || event.repo_id}
                              </Link>
                            ) : event.repo_name ? (
                              <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs font-semibold text-[color:var(--text-secondary)]">{event.repo_name}</span>
                            ) : null}
                          </div>
                          <button className="mt-3 block max-w-full text-left text-sm leading-6 text-[color:var(--text-primary)]" onClick={() => setExpandedDescription(descriptionExpanded ? null : event.id)} type="button">
                            <span className={descriptionExpanded ? "" : "line-clamp-2"}>{description}</span>
                          </button>
                          {metadataExpanded ? (
                            <pre className="mt-3 max-h-[280px] overflow-auto rounded-lg border border-[color:var(--bg-border)] bg-black/30 p-3 font-mono text-xs leading-5 text-[color:var(--text-secondary)]">{JSON.stringify(event.metadata ?? {}, null, 2)}</pre>
                          ) : null}
                        </div>
                        <div className="flex shrink-0 items-center gap-3 text-sm text-[color:var(--text-secondary)]">
                          <span title={new Date(event.created_at).toLocaleString()}>{relativeTime(event.created_at)}</span>
                          <button className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-[color:var(--bg-border)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--accent-primary)]" onClick={() => setExpandedMetadata(metadataExpanded ? null : event.id)} type="button">
                            {metadataExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                            <span className="sr-only">Toggle metadata</span>
                          </button>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      )}

      {hasMore ? (
        <div className="pt-2 text-center">
          <button className="rounded-lg border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" disabled={status === "loadingMore"} onClick={() => loadEvents({ append: true, cursor: nextCursor })} type="button">
            {status === "loadingMore" ? "Loading..." : "Load more"}
          </button>
        </div>
      ) : null}
    </div>
  );
}
