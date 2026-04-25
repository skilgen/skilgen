import { withAuth } from "@workos-inc/authkit-nextjs";
import Link from "next/link";

import { AuditClient } from "./audit-client";
import { exportAuditLogCsvUrl, getAuditLogStats, getBootstrapOrg, getMyOrg, getOrgAuditLog } from "../../../lib/data";

export const dynamic = "force-dynamic";

export default async function AuditPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Audit auth unavailable:", error);
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const orgId = org?.id ?? "";
  const params = new URLSearchParams({ limit: "50" });
  const [audit, stats] = orgId
    ? await Promise.all([getOrgAuditLog(accessToken, orgId, params), getAuditLogStats(accessToken, orgId)])
    : [null, null];

  return (
    <div className="space-y-6">
      <nav className="text-[12px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--text-primary)]" href="/dashboard">
          Overview
        </Link>
        <span className="px-2">/</span>
        <span>Audit Log</span>
      </nav>

      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Audit Log</h1>
          <p className="mt-2 max-w-[760px] text-[15px] text-[color:var(--text-secondary)]">
            Every analysis run, skill edit, gate result, and config change across your org. 1-year retention.
          </p>
        </div>
        {orgId ? (
          <a
            className="inline-flex items-center justify-center rounded-full border border-[color:var(--bg-border)] px-4 py-2 text-[13px] font-semibold text-[color:var(--text-primary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--accent-primary)]"
            href={exportAuditLogCsvUrl(orgId)}
            target="_blank"
          >
            Export CSV
          </a>
        ) : null}
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Metric label="TOTAL EVENTS (30D)" value={stats?.total_events ?? 0} />
        <Metric label="ANALYSIS RUNS (30D)" value={stats?.analysis_runs_30d ?? 0} />
        <Metric
          label="GATE PASS RATE"
          value={stats?.gate_pass_rate == null ? "—" : `${Math.round((stats.gate_pass_rate ?? 0) * 100)}%`}
          tone={(stats?.gate_pass_rate ?? 1) >= 0.8 ? "green" : (stats?.gate_pass_rate ?? 1) >= 0.5 ? "amber" : "red"}
        />
        <Metric label="CRITICAL EVENTS (7D)" value={stats?.critical_events_7d ?? 0} tone={(stats?.critical_events_7d ?? 0) > 0 ? "red" : "default"} />
      </div>

      <AuditClient accessToken={accessToken} initialAudit={audit} orgId={orgId} />
    </div>
  );
}

function Metric({ label, value, tone = "default" }: { label: string; value: string | number; tone?: "default" | "green" | "amber" | "red" }) {
  const toneClass =
    tone === "green"
      ? "text-[color:var(--accent-green)]"
      : tone === "amber"
        ? "text-amber-400"
        : tone === "red"
          ? "text-red-400"
          : "text-[color:var(--text-primary)]";
  return (
    <div className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className={`mt-3 text-[32px] font-semibold ${toneClass}`}>{value}</div>
    </div>
  );
}
