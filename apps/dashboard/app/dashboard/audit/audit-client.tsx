"use client";

import { Fragment, useCallback, useEffect, useMemo, useState } from "react";

import type { AuditLogEvent, AuditLogResponse } from "../../../lib/data";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type Props = {
  accessToken: string;
  orgId: string;
  initialAudit: AuditLogResponse | null;
};

function relativeTime(value: string): string {
  const time = new Date(value).getTime();
  const diff = Math.max(0, Date.now() - time);
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function AuditClient({ accessToken, orgId, initialAudit }: Props) {
  const [events, setEvents] = useState<AuditLogEvent[]>(initialAudit?.events ?? []);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [severity, setSeverity] = useState("all");
  const [resourceType, setResourceType] = useState("all");
  const [actor, setActor] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");

  const filtered = useMemo(() => {
    const search = actor.trim().toLowerCase();
    return events.filter((event) => {
      if (severity !== "all" && event.severity !== severity) return false;
      if (resourceType !== "all" && event.resource_type !== resourceType) return false;
      if (!search) return true;
      return `${event.summary} ${event.actor_login ?? ""} ${event.repo_name ?? ""}`.toLowerCase().includes(search);
    });
  }, [actor, events, resourceType, severity]);

  const refresh = useCallback(async () => {
    if (!orgId) return;
    setStatus("loading");
    const query = new URLSearchParams({ limit: "50" });
    if (severity !== "all") query.set("severity", severity);
    if (resourceType !== "all") query.set("resource_type", resourceType);
    if (actor.trim()) query.set("actor", actor.trim());
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/audit-log?${query.toString()}`, {
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
      });
      if (!response.ok) throw new Error("Could not load audit events");
      const body = (await response.json()) as AuditLogResponse;
      setEvents(body.events ?? []);
      setStatus("idle");
    } catch {
      setStatus("error");
    }
  }, [accessToken, actor, orgId, resourceType, severity]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      void refresh();
    }, 30000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  return (
    <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="flex flex-col gap-4 border-b border-[color:var(--bg-border)] px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <input
            className="h-10 min-w-[260px] rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px] text-[color:var(--text-primary)] outline-none transition-colors focus:border-[color:var(--accent-primary)]"
            onChange={(event) => setActor(event.target.value)}
            placeholder="Search events, actors, repos..."
            value={actor}
          />
          <select className="h-10 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px]" onChange={(event) => setResourceType(event.target.value)} value={resourceType}>
            {["all", "repo", "skill", "analysis", "gate", "persona", "team", "policy", "settings", "member"].map((value) => (
              <option key={value} value={value}>
                {value === "all" ? "All resources" : value}
              </option>
            ))}
          </select>
          {["all", "info", "warning", "critical"].map((value) => (
            <button
              className={`rounded-full border px-3 py-1.5 text-[12px] font-semibold transition-colors ${
                severity === value ? "border-[color:var(--accent-primary)] bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[color:var(--accent-primary)]" : "border-[color:var(--bg-border)] text-[color:var(--text-secondary)]"
              }`}
              key={value}
              onClick={() => setSeverity(value)}
              type="button"
            >
              {value}
            </button>
          ))}
          <button className="rounded-full border border-[color:var(--bg-border)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" onClick={refresh} type="button">
            {status === "loading" ? "Refreshing..." : "Apply filters"}
          </button>
        </div>
        <div className="text-[11px] font-semibold text-green-400">
          <span className="mr-2 inline-block h-2 w-2 animate-pulse rounded-full bg-green-400" />
          Live
        </div>
      </div>
      {status === "error" ? <div className="border-b border-[color:var(--bg-border)] px-5 py-3 text-[12px] text-red-300">Unable to refresh audit events.</div> : null}
      {filtered.length === 0 ? (
        <div className="px-5 py-12 text-center text-[13px] text-[color:var(--text-secondary)]">No audit events recorded yet. Events appear here as you use Skillayer.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1000px] border-collapse text-left text-[13px]">
            <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
              <tr>
                {["Timestamp", "Severity", "Event", "Actor", "Resource", "Summary"].map((heading) => (
                  <th className="border-b border-[color:var(--bg-border)] px-5 py-3 font-semibold" key={heading}>{heading}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((event) => (
                <Fragment key={event.id}>
                  <tr className="cursor-pointer border-b border-[color:var(--bg-elevated)] transition-colors hover:bg-white/5" onClick={() => setExpanded(expanded === event.id ? null : event.id)}>
                    <td className="px-5 py-4 font-mono text-[12px] text-[color:var(--text-secondary)]" title={event.created_at}>{relativeTime(event.created_at)}</td>
                    <td className="px-5 py-4"><Severity severity={event.severity} /></td>
                    <td className="px-5 py-4 font-mono text-[12px] text-[color:var(--text-primary)]">{event.event_type}</td>
                    <td className="px-5 py-4 font-mono text-[12px] text-[color:var(--text-secondary)]">{event.actor_login ?? "system"}</td>
                    <td className="px-5 py-4 text-[color:var(--text-secondary)]">{event.repo_name ?? event.skill_domain ?? event.resource_id ?? "—"}</td>
                    <td className="px-5 py-4 text-[color:var(--text-primary)]" title={event.summary}>{event.summary}</td>
                  </tr>
                  {expanded === event.id ? (
                    <tr className="border-b border-[color:var(--bg-elevated)]">
                      <td className="px-5 py-4" colSpan={6}>
                        <pre className="max-h-[260px] overflow-auto rounded-xl bg-black/40 px-4 py-3 font-mono text-[12px] leading-6 text-[color:var(--text-secondary)]">{JSON.stringify(event.metadata ?? {}, null, 2)}</pre>
                      </td>
                    </tr>
                  ) : null}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function Severity({ severity }: { severity: "info" | "warning" | "critical" }) {
  const dot = severity === "critical" ? "bg-red-400 animate-pulse" : severity === "warning" ? "bg-amber-400" : "bg-[color:var(--text-tertiary)]";
  const text = severity === "critical" ? "text-red-300" : severity === "warning" ? "text-amber-300" : "text-[color:var(--text-tertiary)]";
  return (
    <span className={`inline-flex items-center gap-2 text-[12px] ${text}`}>
      <span className={`h-2 w-2 rounded-full ${dot}`} />
      {severity}
    </span>
  );
}
