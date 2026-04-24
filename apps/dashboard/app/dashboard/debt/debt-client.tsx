"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

import type { SkillDebtResponse } from "../../../lib/data";

type TabKey = "gaps" | "stale" | "low" | "never";

function scoreBadgeClass(score: number): string {
  if (score < 40) return "bg-red-900/30 text-red-300";
  if (score < 70) return "bg-amber-900/30 text-amber-300";
  return "bg-green-900/30 text-green-300";
}

export function DebtClient({ debt }: { debt: SkillDebtResponse }) {
  const [tab, setTab] = useState<TabKey>("gaps");

  const repoNames = useMemo(() => {
    const map = new Map<string, string>();
    for (const gap of debt.repo_coverage_gaps) map.set(gap.repo_id, gap.repo_name);
    return map;
  }, [debt.repo_coverage_gaps]);

  const tabs: Array<{ key: TabKey; label: string }> = [
    { key: "gaps", label: "Coverage Gaps" },
    { key: "stale", label: "Stale Skills" },
    { key: "low", label: "Low Score" },
    { key: "never", label: "Never Loaded" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {tabs.map((item) => (
          <button
            className={`rounded-full px-3 py-1.5 text-[13px] font-semibold ${tab === item.key ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "border border-[color:var(--bg-border)] text-[color:var(--text-secondary)]"}`}
            key={item.key}
            onClick={() => setTab(item.key)}
            type="button"
          >
            {item.label}
          </button>
        ))}
      </div>

      {tab === "gaps" ? (
        <section className="grid gap-4">
          {debt.repo_coverage_gaps.length > 0 ? (
            debt.repo_coverage_gaps.map((gap) => (
              <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={gap.repo_id}>
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">{gap.repo_name}</h2>
                    <div className="mt-3 h-2 w-full max-w-sm overflow-hidden rounded-full bg-white/8">
                      <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${gap.coverage_score}%` }} />
                    </div>
                    <p className="mt-2 text-[13px] text-[color:var(--text-secondary)]">Coverage score: {gap.coverage_score}%</p>
                  </div>
                  <Link className="text-[13px] font-semibold text-[color:var(--accent-primary)] hover:underline" href={`/dashboard/repos/${gap.repo_id}`}>
                    Go to repo
                  </Link>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {gap.missing_categories.map((category) => (
                    <span className="rounded-full bg-red-900/30 px-2 py-0.5 text-[11px] font-semibold text-red-300" key={category}>
                      {category}
                    </span>
                  ))}
                </div>
              </article>
            ))
          ) : (
            <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center text-[color:var(--text-secondary)]">
              No coverage gaps detected.
            </section>
          )}
        </section>
      ) : null}

      {tab === "stale" ? (
        <section className="overflow-x-auto rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <table className="w-full min-w-[720px] border-collapse text-left text-[13px]">
            <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
              <tr className="border-b border-[color:var(--bg-border)]">
                <th className="px-5 py-3 font-semibold">Domain</th>
                <th className="px-5 py-3 font-semibold">Repo</th>
                <th className="px-5 py-3 font-semibold">Score</th>
                <th className="px-5 py-3 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody>
              {debt.stale_skills.map((skill) => (
                <tr className="border-b border-[color:var(--bg-elevated)] last:border-b-0" key={skill.id}>
                  <td className="px-5 py-4 text-[color:var(--text-primary)]">{skill.domain}</td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{repoNames.get(skill.repo_id) ?? "Repo"}</td>
                  <td className="px-5 py-4"><span className={`rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreBadgeClass(skill.score_total)}`}>{skill.score_total}/100</span></td>
                  <td className="px-5 py-4"><Link className="text-[12px] font-semibold text-[color:var(--accent-primary)] hover:underline" href={`/dashboard/repos/${skill.repo_id}`}>Re-analyse</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}

      {tab === "low" ? (
        <section className="overflow-x-auto rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <table className="w-full min-w-[720px] border-collapse text-left text-[13px]">
            <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
              <tr className="border-b border-[color:var(--bg-border)]">
                <th className="px-5 py-3 font-semibold">Domain</th>
                <th className="px-5 py-3 font-semibold">Repo</th>
                <th className="px-5 py-3 font-semibold">Score</th>
                <th className="px-5 py-3 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody>
              {debt.low_score_skills.map((skill) => (
                <tr className="border-b border-[color:var(--bg-elevated)] last:border-b-0" key={skill.id}>
                  <td className="px-5 py-4 text-[color:var(--text-primary)]">{skill.domain}</td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{repoNames.get(skill.repo_id) ?? "Repo"}</td>
                  <td className="px-5 py-4"><span className="rounded-full bg-red-900/30 px-2 py-0.5 text-[12px] font-semibold text-red-300">{skill.score_total}/100</span></td>
                  <td className="px-5 py-4"><Link className="text-[12px] font-semibold text-[color:var(--accent-primary)] hover:underline" href={`/dashboard/repos/${skill.repo_id}/skills/${skill.id}`}>View skill →</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}

      {tab === "never" ? (
        <section className="overflow-x-auto rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="border-b border-[color:var(--bg-border)] px-5 py-4 text-[13px] text-[color:var(--text-secondary)]">
            These skills were generated but no agent has ever loaded them. Improve their metadata so agents can discover them.
          </div>
          <table className="w-full min-w-[720px] border-collapse text-left text-[13px]">
            <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
              <tr className="border-b border-[color:var(--bg-border)]">
                <th className="px-5 py-3 font-semibold">Domain</th>
                <th className="px-5 py-3 font-semibold">Repo</th>
                <th className="px-5 py-3 font-semibold">Score</th>
                <th className="px-5 py-3 font-semibold">Info</th>
              </tr>
            </thead>
            <tbody>
              {debt.never_loaded_skills.map((skill) => (
                <tr className="border-b border-[color:var(--bg-elevated)] last:border-b-0" key={skill.id}>
                  <td className="px-5 py-4 text-[color:var(--text-primary)]">{skill.domain}</td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{repoNames.get(skill.repo_id) ?? "Repo"}</td>
                  <td className="px-5 py-4"><span className={`rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreBadgeClass(skill.score_total)}`}>{skill.score_total}/100</span></td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">Never loaded in 30d</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}
    </div>
  );
}
