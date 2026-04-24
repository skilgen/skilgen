import Link from "next/link";
import { AlertTriangle } from "lucide-react";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getOrgSkillHeatmap } from "../../../lib/data";
import { HeatmapClient } from "./heatmap-client";

export const dynamic = "force-dynamic";

export default async function HeatmapPage() {
  let accessToken = "";
  let orgId = "";

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Heatmap auth unavailable:", error);
  }

  const org = await getBootstrapOrg();
  orgId = org?.id ?? "";
  const heatmap = orgId ? await getOrgSkillHeatmap(accessToken, orgId) : null;
  const summary = heatmap?.summary ?? { total_skills: 0, dead_skills: 0, stale_but_active: 0, healthy: 0, avg_criticality: 0 };
  const skills = heatmap?.skills ?? [];

  return (
    <div>
      <nav className="mb-6 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">
          Overview
        </Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">Heatmap</span>
      </nav>

      <div className="mb-8 flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Heatmap</h1>
          <p className="mt-1 text-[14px] text-[color:var(--text-secondary)]">Live view of skill criticality, decay, and agent usage across your org.</p>
        </div>
      </div>

      <section className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          <div className="text-[12px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Total Skills</div>
          <div className="mt-3 text-[32px] font-semibold text-[color:var(--text-primary)]">{summary.total_skills}</div>
        </article>
        <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          <div className="text-[12px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Healthy</div>
          <div className="mt-3 text-[32px] font-semibold text-green-400">{summary.healthy}</div>
        </article>
        <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          <div className="flex items-center gap-2 text-[12px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">
            <AlertTriangle className="h-4 w-4 text-amber-400" />
            Stale &amp; Active
          </div>
          <div className="mt-3 text-[32px] font-semibold text-amber-400">{summary.stale_but_active}</div>
        </article>
        <Link className="rounded-[24px] border border-red-500/25 bg-[color:var(--bg-surface)] p-5 transition-colors hover:border-red-500/40" href="/dashboard/heatmap">
          <div className="text-[12px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Dead Skills</div>
          <div className="mt-3 text-[32px] font-semibold text-red-400">{summary.dead_skills}</div>
        </Link>
      </section>

      {summary.dead_skills > 0 ? (
        <section className="mb-6 rounded-xl border border-amber-500/30 bg-amber-500/10 px-5 py-4 text-[14px] text-amber-200">
          ⚠ {summary.dead_skills} skill{summary.dead_skills === 1 ? "" : "s"} haven&apos;t been loaded in 30+ days. Consider pruning or re-analysing.
        </section>
      ) : null}

      <HeatmapClient skills={skills} summary={summary} />
    </div>
  );
}
