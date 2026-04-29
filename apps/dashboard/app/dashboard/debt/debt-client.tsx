"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { AlertTriangle, Clock, Eye, TrendingDown, ChevronRight } from "lucide-react";

import type { SkillDebtResponse } from "../../../lib/data";

type TabKey = "gaps" | "stale" | "low" | "never";

const categoryLabelMap: Record<string, string> = {
  codebase_architecture: "Architecture",
  code_style: "Code Style",
  testing_conventions: "Testing",
  internal_tools: "Internal Tools",
  security_compliance: "Security",
  design_system: "Design System",
  data_schema: "Data Schema",
  operational_knowledge: "Operations",
};

function scoreBadgeClass(score: number): string {
  if (score < 40) return "bg-red-900/30 text-red-300";
  if (score < 70) return "bg-amber-900/30 text-amber-300";
  return "bg-green-900/30 text-green-300";
}

function titleize(category: string): string {
  return categoryLabelMap[category] ?? category.replaceAll("_", " ");
}

/** Human-readable WHY for a low-score skill based on sub-scores */
function whyLowScore(skill: { score_total: number; score_groundedness?: number | null; score_coverage?: number | null; score_freshness?: number | null; score_structure?: number | null }): { why: string; fix: string } {
  const scores = [
    { name: "Groundedness", val: skill.score_groundedness ?? 0, max: 25, fix: "Add more file references and concrete code examples" },
    { name: "Coverage", val: skill.score_coverage ?? 0, max: 25, fix: "Add an Anti-patterns or Common Mistakes section" },
    { name: "Freshness", val: skill.score_freshness ?? 0, max: 25, fix: "Add a '## Last verified — Month Year' line at the bottom" },
    { name: "Structure", val: skill.score_structure ?? 0, max: 25, fix: "Add a Domain summary, Key patterns, and Anti-patterns section" },
  ];

  const weakest = scores.reduce((a, b) => (a.val / a.max < b.val / b.max ? a : b));
  return {
    why: `${weakest.name} score is only ${weakest.val}/${weakest.max}`,
    fix: weakest.fix,
  };
}

function whyNeverLoaded(domain: string): string {
  return `No agent has referenced "${domain}" in their session — verify it's listed in your CLAUDE.md or AGENTS.md`;
}

function whyStale(): string {
  return `The skill content hasn't been refreshed after recent codebase changes`;
}

// ─── reusable table ─────────────────────────────────────────────────────────

type SkillRow = {
  id: string;
  domain: string;
  repo_id: string;
  score_total: number;
  score_groundedness?: number | null;
  score_coverage?: number | null;
  score_freshness?: number | null;
  score_structure?: number | null;
};

function DebtTable({
  skills,
  repoNames,
  reasonFn,
  fixFn,
  actionLabel,
  actionHrefFn,
  emptyMessage,
}: {
  skills: SkillRow[];
  repoNames: Map<string, string>;
  reasonFn: (skill: SkillRow) => string;
  fixFn: (skill: SkillRow) => string;
  actionLabel: string;
  actionHrefFn: (skill: SkillRow) => string;
  emptyMessage: string;
}) {
  if (skills.length === 0) {
    return (
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center text-[13px] text-[color:var(--text-secondary)]">
        {emptyMessage}
      </section>
    );
  }

  return (
    <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="grid min-w-[860px] grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)_90px_minmax(0,2fr)_minmax(0,1.4fr)_80px] gap-4 border-b border-[color:var(--bg-border)] px-5 py-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">
        <div>Domain</div>
        <div>Repo</div>
        <div>Score</div>
        <div>Why it&apos;s debt</div>
        <div>Recommended fix</div>
        <div />
      </div>
      <div className="overflow-x-auto">
        <div className="min-w-[860px]">
          {skills.map((skill) => {
            const reason = reasonFn(skill);
            const fix = fixFn(skill);
            return (
              <div
                className="grid grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)_90px_minmax(0,2fr)_minmax(0,1.4fr)_80px] gap-4 border-b border-[color:var(--bg-elevated)] px-5 py-4 text-[13px] last:border-b-0"
                key={skill.id}
              >
                <div className="font-semibold text-[color:var(--text-primary)]">{skill.domain}</div>
                <div className="truncate text-[color:var(--text-secondary)]">{repoNames.get(skill.repo_id) ?? "Repo"}</div>
                <div>
                  <span className={`rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreBadgeClass(skill.score_total)}`}>
                    {skill.score_total}/100
                  </span>
                </div>
                <div className="text-[12px] text-[color:var(--text-secondary)]">
                  <span className="inline-flex items-start gap-1.5">
                    <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-400" />
                    {reason}
                  </span>
                </div>
                <div className="text-[12px] italic text-[color:var(--accent-primary)]">{fix}</div>
                <div className="flex items-center justify-end">
                  <Link
                    className="inline-flex items-center gap-1 text-[12px] font-semibold text-[color:var(--accent-primary)] hover:underline"
                    href={actionHrefFn(skill)}
                  >
                    {actionLabel}
                    <ChevronRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

// ─── main export ────────────────────────────────────────────────────────────

export function DebtClient({ debt }: { debt: SkillDebtResponse }) {
  const [tab, setTab] = useState<TabKey>("gaps");

  const repoNames = useMemo(() => {
    const map = new Map<string, string>();
    for (const gap of debt.repo_coverage_gaps) map.set(gap.repo_id, gap.repo_name);
    return map;
  }, [debt.repo_coverage_gaps]);

  const tabs: Array<{ key: TabKey; label: string; count: number; icon: React.ReactNode }> = [
    { key: "gaps", label: "Coverage Gaps", count: debt.summary.repos_with_gaps, icon: <Eye className="h-3.5 w-3.5" /> },
    { key: "stale", label: "Stale Skills", count: debt.summary.stale_count, icon: <Clock className="h-3.5 w-3.5" /> },
    { key: "low", label: "Low Score", count: debt.summary.low_score_count, icon: <TrendingDown className="h-3.5 w-3.5" /> },
    { key: "never", label: "Never Loaded", count: debt.summary.never_loaded_count, icon: <AlertTriangle className="h-3.5 w-3.5" /> },
  ];

  return (
    <div className="space-y-6">
      {/* Tab bar */}
      <div className="flex flex-wrap gap-2">
        {tabs.map((item) => (
          <button
            className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-[13px] font-semibold transition-colors ${
              tab === item.key
                ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]"
                : "border border-[color:var(--bg-border)] text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]"
            }`}
            key={item.key}
            onClick={() => setTab(item.key)}
            type="button"
          >
            {item.icon}
            {item.label}
            {item.count > 0 ? (
              <span className={`rounded-full px-1.5 py-0.5 text-[11px] font-bold ${tab === item.key ? "bg-white/20 text-white" : "bg-[color:var(--bg-elevated)] text-[color:var(--text-tertiary)]"}`}>
                {item.count}
              </span>
            ) : null}
          </button>
        ))}
      </div>

      {/* Coverage Gaps */}
      {tab === "gaps" ? (
        <section className="grid gap-4">
          {debt.repo_coverage_gaps.length > 0 ? (
            debt.repo_coverage_gaps.map((gap) => (
              <article className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={gap.repo_id}>
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">{gap.repo_name}</h2>
                      <span className="rounded-full bg-amber-500/15 px-2.5 py-0.5 text-[11px] font-semibold text-amber-300">
                        {gap.coverage_score}% covered
                      </span>
                    </div>
                    <p className="mt-1.5 text-[13px] text-[color:var(--text-secondary)]">
                      <AlertTriangle className="mr-1 inline h-3.5 w-3.5 text-amber-400" />
                      Missing {gap.missing_categories.length} of 8 knowledge areas — agents have no context for these domains
                    </p>

                    {/* Progress bar */}
                    <div className="mt-3 h-2 w-full max-w-sm overflow-hidden rounded-full bg-white/8">
                      <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${gap.coverage_score}%` }} />
                    </div>

                    {/* Covered */}
                    {gap.covered_categories && gap.covered_categories.length > 0 ? (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {gap.covered_categories.map((cat) => (
                          <span className="rounded-full bg-green-900/30 px-2 py-0.5 text-[11px] font-semibold text-green-300" key={cat}>
                            ✓ {titleize(cat)}
                          </span>
                        ))}
                      </div>
                    ) : null}

                    {/* Missing with WHY */}
                    <div className="mt-2 flex flex-wrap gap-2">
                      {gap.missing_categories.map((cat) => (
                        <span
                          className="rounded-full border border-red-500/20 bg-red-900/20 px-2 py-0.5 text-[11px] font-semibold text-red-300"
                          key={cat}
                          title={`Run: skilgen analyse --domain ${cat.replace("_", "-")} --project-root .`}
                        >
                          ✗ {titleize(cat)}
                        </span>
                      ))}
                    </div>

                    {gap.missing_categories.length > 0 ? (
                      <p className="mt-3 text-[12px] italic text-[color:var(--accent-primary)]">
                        → Run <code className="rounded bg-white/5 px-1 py-0.5 font-mono text-[11px]">skilgen analyse --project-root .</code> to generate missing skills
                      </p>
                    ) : null}
                  </div>

                  <Link
                    className="shrink-0 text-[13px] font-semibold text-[color:var(--accent-primary)] hover:underline"
                    href={`/dashboard/repos/${gap.repo_id}`}
                  >
                    Go to repo →
                  </Link>
                </div>
              </article>
            ))
          ) : (
            <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center text-[13px] text-[color:var(--text-secondary)]">
              No coverage gaps detected.
            </section>
          )}
        </section>
      ) : null}

      {/* Stale Skills */}
      {tab === "stale" ? (
        <DebtTable
          actionHrefFn={(s) => `/dashboard/repos/${s.repo_id}/skills/${s.id}`}
          actionLabel="Re-analyse"
          emptyMessage="No stale skills — everything is fresh!"
          fixFn={(s) => `Run: skilgen analyse --domain ${s.domain} --project-root .`}
          reasonFn={() => whyStale()}
          repoNames={repoNames}
          skills={debt.stale_skills}
        />
      ) : null}

      {/* Low Score Skills */}
      {tab === "low" ? (
        <DebtTable
          actionHrefFn={(s) => `/dashboard/repos/${s.repo_id}/skills/${s.id}`}
          actionLabel="View skill"
          emptyMessage="No low-score skills — great quality!"
          fixFn={(s) => whyLowScore(s).fix}
          reasonFn={(s) => whyLowScore(s).why}
          repoNames={repoNames}
          skills={debt.low_score_skills}
        />
      ) : null}

      {/* Never Loaded Skills */}
      {tab === "never" ? (
        <>
          <div className="rounded-xl border border-amber-500/20 bg-amber-950/20 px-4 py-3 text-[13px] text-amber-200">
            <strong className="font-semibold">Why does this matter?</strong> Skills agents never load deliver zero ROI — the knowledge is captured but not used. The fix is usually a missing reference in your CLAUDE.md or AGENTS.md.
          </div>
          <DebtTable
            actionHrefFn={(s) => `/dashboard/repos/${s.repo_id}/skills/${s.id}`}
            actionLabel="View skill"
            emptyMessage="All skills are being loaded by agents!"
            fixFn={() => `Add the skill path to your CLAUDE.md or AGENTS.md so agents discover it`}
            reasonFn={(s) => whyNeverLoaded(s.domain)}
            repoNames={repoNames}
            skills={debt.never_loaded_skills}
          />
        </>
      ) : null}
    </div>
  );
}
