import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getOrgRedFlags, type OrgRedFlags } from "../../../lib/data";
import { RedFlagsShell } from "./red-flags-shell";

export const dynamic = "force-dynamic";

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
  const redFlags: OrgRedFlags = response ?? {
    critical_count: 0,
    high_count: 0,
    medium_count: 0,
    flags: [],
  };

  const totalFlags = redFlags.flags.length;
  const hasCritical = redFlags.critical_count > 0;
  const hasHigh = redFlags.high_count > 0;

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
          <p className="mt-1 max-w-2xl text-[14px] text-[color:var(--text-secondary)]">
            Skills your agents are using that are stale, conflicting, or missing. Click{" "}
            <span className="font-semibold text-[color:var(--text-primary)]">Fix</span> to see a recommended
            fix, or <span className="font-semibold text-[color:var(--text-primary)]">Not a risk</span> to
            dismiss flags you've already handled.
          </p>
        </div>

        <div className="shrink-0">
          {hasCritical ? (
            <div className="inline-flex items-center gap-2 rounded-full bg-red-500/20 px-3 py-1 text-[13px] font-semibold text-red-300">
              <span className="h-2 w-2 animate-pulse rounded-full bg-red-400" />
              {redFlags.critical_count} critical
            </div>
          ) : hasHigh ? (
            <div className="rounded-full bg-amber-500/20 px-3 py-1 text-[13px] font-semibold text-amber-300">
              {redFlags.high_count} high priority
            </div>
          ) : totalFlags > 0 ? (
            <div className="rounded-full bg-blue-500/20 px-3 py-1 text-[13px] font-semibold text-blue-300">
              {totalFlags} flags to review
            </div>
          ) : (
            <div className="rounded-full bg-[rgb(var(--accent-green-rgb)/0.15)] px-3 py-1 text-[13px] font-semibold text-[color:var(--accent-green)]">
              ✓ All clear
            </div>
          )}
        </div>
      </div>

      <RedFlagsShell accessToken={accessToken} orgId={org?.id ?? ""} redFlags={redFlags} />
    </div>
  );
}
