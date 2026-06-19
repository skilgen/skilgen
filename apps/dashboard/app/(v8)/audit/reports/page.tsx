import Link from "next/link";

import { getV8AuditReport, getV8AuditReports } from "../../../../lib/data";
import { loadAuditOrg } from "../common";

export default async function AuditReportsPage() {
  const { accessToken, orgId } = await loadAuditOrg();
  const reports = orgId ? await getV8AuditReports(accessToken, orgId) : [];
  const active = reports?.[0];
  const report = active && orgId ? await getV8AuditReport(accessToken, orgId, active.id) : null;
  return (
    <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
      <div className="space-y-2">
        {(reports ?? []).map((item) => (
          <Link className="block rounded-md border border-[color:var(--bg-border)] px-3 py-3 text-sm hover:border-[color:var(--accent-primary)]" href={`/audit/reports?report=${item.id}`} key={item.id}>
            <div className="font-semibold text-[color:var(--text-primary)]">{item.title}</div>
            <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">{item.control_mapping}</div>
          </Link>
        ))}
      </div>
      <div className="overflow-x-auto border-y border-[color:var(--bg-border)]">
        <table className="w-full min-w-[900px] text-left text-[13px]">
          <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
            <tr>{["Time", "Event", "Actor", "Repo", "Decision", "Summary"].map((heading) => <th className="border-b border-[color:var(--bg-border)] px-3 py-3" key={heading}>{heading}</th>)}</tr>
          </thead>
          <tbody>
            {(report?.rows ?? []).map((row) => (
              <tr className="border-b border-[color:var(--bg-elevated)]" key={row.id}>
                <td className="whitespace-nowrap px-3 py-3 font-mono text-[12px]">{new Date(row.created_at).toLocaleString()}</td>
                <td className="px-3 py-3 font-mono text-[12px]">{row.event_type}</td>
                <td className="px-3 py-3">{row.actor_login ?? "system"}</td>
                <td className="px-3 py-3">{row.repo_name ?? "-"}</td>
                <td className="px-3 py-3">{row.policy_decision ?? "-"}</td>
                <td className="max-w-[420px] truncate px-3 py-3">{row.summary}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
