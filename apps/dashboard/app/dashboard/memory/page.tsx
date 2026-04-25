import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getKnowledgeVelocity, getMemoryQueue, getOrgRedFlags, type KnowledgeVelocity, type MemoryQueueResponse, type OrgRedFlags } from "../../../lib/data";
import { MemoryQueueClient } from "./memory-queue-client";

export const dynamic = "force-dynamic";

function emptyQueue(): MemoryQueueResponse {
  return { total: 0, pending_count: 0, items: [] };
}

function emptyVelocity(): KnowledgeVelocity {
  return {
    weekly: Array.from({ length: 8 }, (_, index) => ({ week_start: `Wk ${index + 1}`, discovered: 0, approved: 0 })),
    total_discoveries_all_time: 0,
    approval_rate: null,
  };
}

function StatCard({ label, value, subtitle, valueClassName = "text-[color:var(--text-primary)]" }: { label: string; value: string | number; subtitle?: string; valueClassName?: string }) {
  return (
    <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className={`mt-3 text-[32px] font-semibold ${valueClassName}`}>{value}</div>
      {subtitle ? <div className="mt-2 text-[12px] text-[color:var(--text-tertiary)]">{subtitle}</div> : null}
    </article>
  );
}

function VelocityStrip({ velocity }: { velocity: KnowledgeVelocity }) {
  const weeks = velocity.weekly;
  const current = weeks[0]?.discovered ?? 0;
  const previous = weeks[1]?.discovered ?? 0;
  const delta = current - previous;
  const max = Math.max(1, ...weeks.map((week) => Math.max(week.discovered, week.approved)));
  const approval = velocity.approval_rate;
  const approvalClass = approval === null ? "text-[color:var(--text-tertiary)]" : approval >= 0.7 ? "text-[color:var(--accent-green)]" : approval >= 0.4 ? "text-amber-400" : "text-red-400";

  return (
    <section className="mb-8">
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="ALL TIME" value={velocity.total_discoveries_all_time} />
        <StatCard label="THIS WEEK" value={current} subtitle={delta === 0 ? "No change" : delta > 0 ? `↑ +${delta} vs last week` : `↓ ${delta} vs last week`} />
        <StatCard label="APPROVAL RATE" value={approval === null ? "—" : `${Math.round(approval * 100)}%`} valueClassName={approvalClass} />
      </div>
      <div className="mt-4 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-5 py-4">
        <div className="flex h-16 items-end gap-3">
          {weeks.map((week, index) => (
            <div className="flex flex-1 items-end gap-1" key={`${week.week_start}-${index}`}>
              <div className="w-full rounded-t bg-[color:var(--accent-primary)]" style={{ height: `${Math.max(4, (week.discovered / max) * 64)}px` }} />
              <div className="w-full rounded-t bg-green-400" style={{ height: `${Math.max(4, (week.approved / max) * 64)}px` }} />
            </div>
          ))}
        </div>
        <div className="mt-2 grid grid-cols-8 gap-3 text-center text-[11px] text-[color:var(--text-tertiary)]">
          {weeks.map((week, index) => <span key={`${week.week_start}-label`}>Wk {index + 1}</span>)}
        </div>
      </div>
    </section>
  );
}

export default async function MemoryPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Memory auth unavailable:", error);
  }
  const org = await getBootstrapOrg();
  const [queue, velocity, redFlags] = org?.id
    ? await Promise.all([
        getMemoryQueue(accessToken, org.id, { status: "pending" }),
        getKnowledgeVelocity(accessToken, org.id),
        getOrgRedFlags(accessToken, org.id, "critical"),
      ])
    : [null, null, null];
  const safeQueue = queue ?? emptyQueue();
  const safeVelocity = velocity ?? emptyVelocity();
  const safeRedFlags: OrgRedFlags = redFlags ?? { critical_count: 0, high_count: 0, medium_count: 0, flags: [] };

  return (
    <div>
      <nav className="mb-6 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">Overview</Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">Memory Capture</span>
      </nav>
      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Memory Capture</h1>
          <p className="mt-1 max-w-3xl text-[14px] text-[color:var(--text-secondary)]">Knowledge discovered by coding agents during real sessions, queued for your review. Approve to merge into your skill tree.</p>
        </div>
        {safeQueue.pending_count > 0 ? <div className="rounded-full bg-red-500/20 px-3 py-1 text-[13px] font-semibold text-red-300">{safeQueue.pending_count} pending</div> : null}
      </div>
      {safeRedFlags.critical_count > 0 ? <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-[13px] font-semibold text-red-300">{safeRedFlags.critical_count} critical red flag{safeRedFlags.critical_count === 1 ? "" : "s"} need attention before merging memory.</div> : null}
      <VelocityStrip velocity={safeVelocity} />
      <MemoryQueueClient accessToken={accessToken} initialQueue={safeQueue} orgId={org?.id ?? ""} />
    </div>
  );
}
