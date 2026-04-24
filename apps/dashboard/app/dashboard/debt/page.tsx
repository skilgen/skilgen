import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getOrgSkillDebt } from "../../../lib/data";
import { DebtClient } from "./debt-client";

export const dynamic = "force-dynamic";

function debtTone(score: number): string {
  if (score < 40) return "text-green-300";
  if (score < 70) return "text-amber-300";
  return "text-red-300";
}

export default async function SkillDebtPage() {
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
        <span className="text-[color:var(--text-secondary)]">Skill Debt</span>
      </nav>

      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Skill Debt</h1>
        <p className="mt-1 text-[14px] text-[color:var(--text-secondary)]">
          Uncovered domains, stale skills, and missing evidence — your AI readiness tech debt.
        </p>
      </div>

      <section className="mb-8 rounded-[28px] border border-[rgb(var(--accent-primary-rgb)/0.18)] bg-[linear-gradient(135deg,rgba(201,151,58,0.12),rgba(255,255,255,0.03))] p-6">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
          <div>
            <div className={`text-[56px] font-semibold leading-none ${debtTone(safeDebt.debt_score)}`}>{safeDebt.debt_score}</div>
            <div className="mt-2 text-[14px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Debt Score</div>
            <p className="mt-4 max-w-xl text-[14px] text-[color:var(--text-secondary)]">
              Lower is better. Resolve stale skills, improve low scores, and cover missing domains.
            </p>
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

      <DebtClient debt={safeDebt} />
    </div>
  );
}
