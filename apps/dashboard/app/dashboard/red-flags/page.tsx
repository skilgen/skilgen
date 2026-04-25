import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getOrgRedFlags, type OrgRedFlags, type RedFlag } from "../../../lib/data";

export const dynamic = "force-dynamic";

function flagTypeMeta(flag: RedFlag): { label: string; className: string } {
  if (flag.flag_type === "stale_but_active") return { label: "🔴 Stale & Active", className: "bg-red-500/20 text-red-300" };
  if (flag.flag_type === "freshness_critical") return { label: "🔴 Zero Freshness", className: "bg-red-500/20 text-red-300" };
  if (flag.flag_type === "conflict") return { label: "⚡ Conflict", className: "bg-orange-500/20 text-orange-300" };
  if (flag.flag_type === "missing_security") return { label: "🛡 Missing Security", className: "bg-amber-500/20 text-amber-300" };
  return { label: "💤 Dead Skill", className: "bg-blue-500/20 text-blue-300" };
}

function severityBar(severity: RedFlag["severity"]): string {
  if (severity === "critical") return "bg-red-500";
  if (severity === "high") return "bg-amber-500";
  return "bg-blue-500";
}

function StatCard({ label, count, description, className }: { label: string; count: number; description: string; className: string }) {
  return (
    <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className={`mt-3 text-[32px] font-semibold ${className}`}>{count}</div>
      <div className="mt-2 text-[12px] text-[color:var(--text-tertiary)]">{description}</div>
    </article>
  );
}

function FlagCard({ flag }: { flag: RedFlag }) {
  const meta = flagTypeMeta(flag);
  return (
    <article className="relative mb-2 overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-5 py-4">
      <div className={`absolute bottom-0 left-0 top-0 w-1 ${severityBar(flag.severity)}`} />
      <div className="flex flex-col gap-4 pl-4 md:flex-row md:items-start md:justify-between">
        <div>
          <span className={`rounded-full px-2.5 py-1 text-[12px] font-semibold ${meta.className}`}>{meta.label}</span>
          <h3 className="mt-2 text-[15px] font-semibold text-[color:var(--text-primary)]">{flag.title}</h3>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{flag.description}</p>
          <div className="mt-2 text-[12px] text-[color:var(--text-tertiary)]">{flag.repo_name} · {flag.loads_30d} loads (30d)</div>
          <div className="mt-2 text-[12px] italic text-[color:var(--text-secondary)]">{flag.action}</div>
        </div>
        {flag.action_url ? (
          <Link className="inline-flex shrink-0 rounded-full border border-[color:var(--bg-border)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--accent-primary)]" href={flag.action_url}>
            Fix →
          </Link>
        ) : null}
      </div>
    </article>
  );
}

function FlagGroup({ title, flags }: { title: string; flags: RedFlag[] }) {
  if (flags.length === 0) return null;
  return (
    <section>
      <h2 className="mb-3 mt-6 text-[13px] font-semibold text-[color:var(--text-secondary)]">{title}</h2>
      {flags.map((flag, index) => <FlagCard flag={flag} key={`${flag.flag_type}-${flag.repo_id}-${flag.skill_id ?? index}`} />)}
    </section>
  );
}

export default async function RedFlagsPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Red flags auth unavailable:", error);
  }
  const org = await getBootstrapOrg();
  const response = org?.id ? await getOrgRedFlags(accessToken, org.id) : null;
  const redFlags: OrgRedFlags = response ?? { critical_count: 0, high_count: 0, medium_count: 0, flags: [] };
  const critical = redFlags.flags.filter((flag) => flag.severity === "critical");
  const high = redFlags.flags.filter((flag) => flag.severity === "high");
  const medium = redFlags.flags.filter((flag) => flag.severity === "medium");

  return (
    <div>
      <nav className="mb-6 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">Overview</Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">Red Flags</span>
      </nav>
      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Red Flags</h1>
          <p className="mt-1 max-w-3xl text-[14px] text-[color:var(--text-secondary)]">Skills actively used by agents that are stale, conflicting, or missing. These are your highest-urgency items.</p>
        </div>
        {redFlags.critical_count > 0 ? (
          <div className="inline-flex items-center gap-2 rounded-full bg-red-500/20 px-3 py-1 text-[13px] font-semibold text-red-300"><span className="h-2 w-2 animate-pulse rounded-full bg-red-400" />{redFlags.critical_count} critical</div>
        ) : redFlags.high_count > 0 ? (
          <div className="rounded-full bg-amber-500/20 px-3 py-1 text-[13px] font-semibold text-amber-300">{redFlags.high_count} high priority</div>
        ) : (
          <div className="rounded-full bg-[rgb(var(--accent-green-rgb)/0.15)] px-3 py-1 text-[13px] font-semibold text-[color:var(--accent-green)]">✓ No critical flags</div>
        )}
      </div>
      <section className="mb-8 grid gap-4 md:grid-cols-3">
        <StatCard className="text-red-400" count={redFlags.critical_count} description="Stale skills actively loaded by agents" label="Critical" />
        <StatCard className="text-amber-400" count={redFlags.high_count} description="Missing security skills or conflicts" label="High" />
        <StatCard className="text-blue-400" count={redFlags.medium_count} description="Dead high-quality skills" label="Medium" />
      </section>
      {redFlags.flags.length === 0 ? (
        <div className="rounded-xl border border-[rgb(var(--accent-green-rgb)/0.25)] bg-[rgb(var(--accent-green-rgb)/0.12)] px-5 py-4 text-[13px] font-semibold text-[color:var(--accent-green)]">✓ No red flags detected across your org.</div>
      ) : (
        <>
          <FlagGroup flags={critical} title="🔴 Critical" />
          <FlagGroup flags={high} title="🟡 High Priority" />
          <FlagGroup flags={medium} title="🔵 Medium" />
        </>
      )}
    </div>
  );
}
