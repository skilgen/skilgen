import { getV8AuditLog } from "../../../../lib/data";
import { loadAuditOrg } from "../common";

export default async function AuditEventLogPage() {
  const { accessToken, orgId } = await loadAuditOrg();
  const audit = orgId ? await getV8AuditLog(accessToken, orgId, new URLSearchParams({ limit: "50" })) : null;
  const events = audit?.events ?? [];
  if (audit === null) {
    return (
      <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-sm text-[color:var(--text-secondary)]">
        <p className="text-[15px] font-semibold text-[color:var(--text-primary)]">Audit could not reach the API.</p>
        <p className="mx-auto mt-2 max-w-xl leading-6">Refresh after sign-in. Existing audit events will appear here once the authenticated API call succeeds.</p>
      </div>
    );
  }
  return (
    <div className="overflow-x-auto border-y border-[color:var(--bg-border)]">
      <table className="w-full min-w-[980px] border-collapse text-left text-[13px]">
        <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
          <tr>
            {["Time", "Event", "Actor", "Repo", "Severity", "Chain", "Summary"].map((heading) => (
              <th className="border-b border-[color:var(--bg-border)] px-3 py-3 font-semibold" key={heading}>{heading}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr className="border-b border-[color:var(--bg-elevated)]" key={event.id}>
              <td className="whitespace-nowrap px-3 py-3 font-mono text-[12px] text-[color:var(--text-secondary)]">{new Date(event.created_at).toLocaleString()}</td>
              <td className="px-3 py-3 font-mono text-[12px]">{event.event_type}</td>
              <td className="px-3 py-3">{event.actor_login ?? "system"}</td>
              <td className="px-3 py-3">{event.repo_name ?? event.repo_id ?? "-"}</td>
              <td className="px-3 py-3 capitalize">{event.severity}</td>
              <td className="px-3 py-3 font-mono text-[11px] text-[color:var(--text-secondary)]">{event.chain ? event.chain.root_hash.slice(0, 12) : "pending"}</td>
              <td className="max-w-[420px] truncate px-3 py-3">{event.summary}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {events.length === 0 ? <div className="py-12 text-center text-sm text-[color:var(--text-secondary)]">No audit events recorded yet.</div> : null}
    </div>
  );
}
