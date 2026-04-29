import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getOrgSkillDebt } from "../../../lib/data";
import { DebtClient } from "./debt-client";

type PageProps = {
  searchParams?: Promise<{ domain?: string | string[]; tab?: string | string[] }>;
};

function initialTab(value: string | string[] | undefined): "gaps" | "stale" | "low" | "never" {
  const raw = Array.isArray(value) ? value[0] : value;
  if (raw === "coverage" || raw === "coverage-gaps") return "gaps";
  return raw === "stale" || raw === "low" || raw === "never" || raw === "gaps" ? raw : "gaps";
}

function firstParam(value: string | string[] | undefined): string {
  return Array.isArray(value) ? value[0] ?? "" : value ?? "";
}

function healthTone(score: number): string {
  if (score >= 70) return "text-green-300";
  if (score >= 40) return "text-amber-300";
  return "text-red-300";
}

function healthLabel(score: number): string {
  if (score >= 70) return "Healthy - your skill library is in good shape";
  if (score >= 40) return "Needs attention - several skills are blocking agent quality";
  return "Critical - agents are working with poor or missing guidance";
}

export default async function SkillDebtPage({ searchParams }: PageProps) {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Skill debt auth unavailable:", error);
  }

  const org = await getBootstrapOrg();
  const orgId = org?.id ?? "";
  const debt = orgId ? await getOrgSkillDebt(accessToken, orgId) : null;
  const safeDebt = debt ?? {
    debt_score: 0,
    health_score: 0,
    estimated_if_fixed: 0,
    total_skills: 0,
    stale_skills: [],
    low_score_skills: [],
    never_loaded_skills: [],
    zero_subscore_skills: [],
    repo_coverage_gaps: [],
    summary: {
      stale_count: 0,
      low_score_count: 0,
      never_loaded_count: 0,
      zero_subscore_count: 0,
      repos_with_gaps: 0,
    },
  };

  return (
    <div>
      <nav className="mb-6 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">
          Overview
        </Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">Skill Health</span>
      </nav>

      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Skill Health Score</h1>
        <p className="mt-1 text-[14px] text-[color:var(--text-secondary)]">
          Higher is better. See stale, weak, or missing skills and let Skillayer generate fixes from the dashboard.
        </p>
      </div>

      <section className="mb-8 rounded-[28px] border border-[rgb(var(--accent-primary-rgb)/0.18)] bg-[linear-gradient(135deg,rgba(201,151,58,0.12),rgba(255,255,255,0.03))] p-6">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
          <div>
            <div className={`text-[56px] font-semibold leading-none ${healthTone(safeDebt.health_score ?? Math.max(0, 100 - safeDebt.debt_score))}`}>{safeDebt.health_score ?? Math.max(0, 100 - safeDebt.debt_score)}</div>
            <div className="mt-2 text-[14px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Skill Health Score</div>
            <p className="mt-4 max-w-xl text-[14px] text-[color:var(--text-secondary)]">
              {healthLabel(safeDebt.health_score ?? Math.max(0, 100 - safeDebt.debt_score))}
            </p>
            <p className="mt-3 max-w-xl text-[14px] text-[color:var(--text-secondary)]">You have {safeDebt.summary.low_score_count} skills scoring below 50/100, {safeDebt.summary.stale_count} stale skills, and {safeDebt.summary.never_loaded_count} skills agents have never loaded. Fixing low-score skills brings your health score to about {safeDebt.estimated_if_fixed ?? safeDebt.health_score ?? 0}.</p>
            <Link className="mt-5 inline-flex rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]" href="/dashboard/autopilot">Open Autopilot ↗</Link>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <article className="rounded-xl border border-[color:var(--bg-border)] bg-black/10 p-4">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Stale Skills</div>
              <div className="mt-2 text-[24px] font-semibold text-[color:var(--text-primary)]">{safeDebt.summary.stale_count}</div>
            </article>
            <article className="rounded-xl border border-[color:var(--bg-border)] bg-black/10 p-4">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Low Score</div>
              <div className="mt-2 text-[24px] font-semibold text-[color:var(--text-primary)]">{safeDebt.summary.low_score_count}</div>
            </article>
            <article className="rounded-xl border border-[color:var(--bg-border)] bg-black/10 p-4">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Never Loaded</div>
              <div className="mt-2 text-[24px] font-semibold text-[color:var(--text-primary)]">{safeDebt.summary.never_loaded_count}</div>
            </article>
            <article className="rounded-xl border border-[color:var(--bg-border)] bg-black/10 p-4">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Repos With Gaps</div>
              <div className="mt-2 text-[24px] font-semibold text-[color:var(--text-primary)]">{safeDebt.summary.repos_with_gaps}</div>
            </article>
          </div>
        </div>
      </section>

      <DebtClient accessToken={accessToken} debt={safeDebt} initialDomain={firstParam((await searchParams)?.domain)} initialTab={initialTab((await searchParams)?.tab)} orgId={orgId} />
    </div>
  );
}
