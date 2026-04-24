import { withAuth } from "@workos-inc/authkit-nextjs";
import { CheckCircle2, Clock3, Filter, XCircle } from "lucide-react";

import { getBootstrapOrg, getMyOrg, getOrgAuditLog, type AuditLogEvent, type AuditLogResponse } from "../../../lib/data";

export const dynamic = "force-dynamic";

type AuditPageProps = {
  searchParams: Promise<{ event_type?: string; repo_id?: string; limit?: string; offset?: string }>;
};

function relativeTime(value: string | null): string {
  if (!value) return "Unknown";
  const diffHours = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 3600000));
  if (diffHours < 1) return "Just now";
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${Math.floor(diffHours / 24)}d ago`;
}

function statusIcon(status: string | null) {
  if (status === "complete") return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
  if (status === "failed") return <XCircle className="h-4 w-4 text-red-400" />;
  return <Clock3 className="h-4 w-4 text-amber-400" />;
}

function scoreChange(event: AuditLogEvent): string {
  if (event.score_before == null || event.score_after == null) return "—";
  const delta = event.score_after - event.score_before;
  const prefix = delta > 0 ? "+" : "";
  return `${event.score_before} → ${event.score_after} (${prefix}${delta})`;
}

async function loadAudit(params: URLSearchParams): Promise<AuditLogResponse | null> {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Audit auth unavailable:", error);
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  if (!org) return null;
  return getOrgAuditLog(accessToken, org.id, params);
}

export default async function AuditPage({ searchParams }: AuditPageProps) {
  const resolved = await searchParams;
  const params = new URLSearchParams();
  if (resolved.event_type) params.set("event_type", resolved.event_type);
  if (resolved.repo_id) params.set("repo_id", resolved.repo_id);
  params.set("limit", resolved.limit || "50");
  params.set("offset", resolved.offset || "0");

  const audit = await loadAudit(params);
  const limit = Number(resolved.limit || "50");
  const offset = Number(resolved.offset || "0");
  const nextParams = new URLSearchParams(params);
  nextParams.set("offset", String(offset + limit));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Audit</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Filterable event history for analyses, automation, and governance signals.</p>
      </div>

      <form className="grid gap-3 rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5 md:grid-cols-4" method="get">
        <label className="text-[12px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">
          Event type
          <input className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-black/20 px-3 text-[14px] text-[color:var(--text-primary)]" defaultValue={resolved.event_type || ""} name="event_type" placeholder="analysis_complete" />
        </label>
        <label className="text-[12px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">
          Repository
          <input className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-black/20 px-3 text-[14px] text-[color:var(--text-primary)]" defaultValue={resolved.repo_id || ""} name="repo_id" placeholder="repo id" />
        </label>
        <label className="text-[12px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">
          Limit
          <select className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-black/20 px-3 text-[14px] text-[color:var(--text-primary)]" defaultValue={resolved.limit || "50"} name="limit">
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </label>
        <div className="flex items-end">
          <button className="inline-flex h-11 items-center gap-2 rounded-xl bg-[color:var(--accent-primary)] px-4 text-[14px] font-semibold text-black hover:bg-[color:var(--accent-bright)]" type="submit">
            <Filter className="h-4 w-4" />
            Apply
          </button>
        </div>
      </form>

      {!audit || audit.events.length === 0 ? (
        <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[14px] text-[color:var(--text-secondary)]">
          No events recorded yet. Events appear after your first analysis run.
        </section>
      ) : (
        <section className="overflow-hidden rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="grid grid-cols-[120px_180px_minmax(0,1fr)_110px_110px_160px] bg-black/20 px-4 py-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">
            <span>Time</span>
            <span>Event</span>
            <span>Repository</span>
            <span>Actor</span>
            <span>Status</span>
            <span>Score change</span>
          </div>
          {audit.events.map((event) => (
            <details className="border-t border-[color:var(--bg-border)]" key={event.id}>
              <summary className="grid cursor-pointer grid-cols-[120px_180px_minmax(0,1fr)_110px_110px_160px] items-center px-4 py-4 text-[13px] marker:content-none">
                <span className="text-[color:var(--text-secondary)]">{relativeTime(event.created_at)}</span>
                <span className="font-medium text-[color:var(--text-primary)]">{event.event_type.replaceAll("_", " ")}</span>
                <span className="truncate text-[color:var(--text-primary)]">{event.repo_name ?? "—"}</span>
                <span className="text-[color:var(--text-secondary)]">{event.actor ?? "—"}</span>
                <span className="inline-flex items-center gap-2 text-[color:var(--text-secondary)]">
                  {statusIcon(event.status)}
                  {event.status ?? "—"}
                </span>
                <span className="text-[color:var(--text-secondary)]">{scoreChange(event)}</span>
              </summary>
              <div className="bg-black/10 px-4 py-4 text-[13px] text-[color:var(--text-secondary)]">
                <div>ID: {event.id}</div>
                <div>Repo ID: {event.repo_id ?? "—"}</div>
                <div>Created: {event.created_at ? new Date(event.created_at).toLocaleString() : "Unknown"}</div>
                <div>Skill count: {event.skill_count ?? "—"}</div>
              </div>
            </details>
          ))}
        </section>
      )}

      {audit && audit.events.length >= limit ? (
        <a className="inline-flex items-center gap-2 rounded-full border border-[color:var(--bg-border)] px-4 py-2 text-[13px] font-semibold text-[color:var(--text-primary)] hover:bg-white/5" href={`/dashboard/audit?${nextParams.toString()}`}>
          Load more
        </a>
      ) : null}
    </div>
  );
}
