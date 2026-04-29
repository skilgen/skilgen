"use client";

import Link from "next/link";
import { Clipboard } from "lucide-react";
import type { ReactElement } from "react";
import { useMemo, useState } from "react";

import type { EvalSkillGap, EvalSkillGapsResponse } from "../../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

function severityClass(severity: string): string {
  if (severity === "critical") return "border-red-500/45";
  if (severity === "high") return "border-amber-500/45";
  return "border-blue-500/35";
}

function severityText(severity: string): string {
  if (severity === "critical") return "text-red-300";
  if (severity === "high") return "text-amber-300";
  return "text-blue-300";
}

function EmptyState({ response }: { response: EvalSkillGapsResponse }) {
  return (
    <section className="rounded-xl border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 p-8 text-center">
      <h2 className="text-xl font-semibold text-[color:var(--accent-green)]">✓ No skill gaps detected across all repos — your agents are well-guided.</h2>
      <p className="mt-3 text-sm text-[color:var(--text-secondary)]">Checked {response.checked_repos} repos, {response.checked_skills} skills, {response.checked_domains} domains · Last scan: {new Date(response.last_scan).toLocaleString()}</p>
    </section>
  );
}

export function GapsShell({ accessToken, orgId, response, status }: { accessToken: string; orgId: string; response: EvalSkillGapsResponse | null; status: string }): ReactElement {
  const [gaps, setGaps] = useState(response?.gaps ?? []);
  const counts = useMemo(() => ({
    all: response?.total_gaps ?? gaps.length,
    critical: gaps.filter((gap) => gap.severity === "critical").length,
    high: gaps.filter((gap) => gap.severity === "high").length,
    acknowledged: gaps.filter((gap) => gap.status === "acknowledged").length,
    resolved: gaps.filter((gap) => gap.status === "resolved").length,
  }), [gaps, response?.total_gaps]);

  async function updateGap(gapId: string, action: "acknowledge" | "resolve") {
    const nextStatus = action === "acknowledge" ? "acknowledged" : "resolved";
    setGaps((current) => current.map((gap) => gap.id === gapId ? { ...gap, status: nextStatus } : gap));
    await fetch(`${API_URL}/eval/orgs/${orgId}/skill-gaps/${gapId}/${action}`, {
      method: "POST",
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
    });
  }

  const safeResponse = response ?? { total_gaps: 0, critical_gap_count: 0, high_gap_count: 0, medium_gap_count: 0, checked_repos: 0, checked_skills: 0, checked_domains: 8, last_scan: new Date().toISOString(), gaps: [] };
  const tabs = [["all", `All (${counts.all})`], ["critical", `Critical (${counts.critical})`], ["high", `High (${counts.high})`], ["acknowledged", `Acknowledged (${counts.acknowledged})`], ["resolved", `Resolved (${counts.resolved})`]];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Skill Gaps</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Domains where your agents lack reliable guidance — and exactly how to fix them.</p>
        <Link className="mt-2 inline-flex text-[13px] font-semibold text-[color:var(--accent-primary)] hover:underline" href="/dashboard/sources?tab=finder">Not sure what skill to create first? → Find the right skill for your problem</Link>
      </header>
      {safeResponse.total_gaps === 0 ? <EmptyState response={safeResponse} /> : (
        <>
          <section className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
            <span className="mr-2 inline-flex h-2.5 w-2.5 animate-pulse rounded-full bg-red-400" />
            {safeResponse.critical_gap_count} critical · {safeResponse.high_gap_count} high priority · {safeResponse.medium_gap_count} to review
          </section>
          <nav className="flex flex-wrap gap-2">
            {tabs.map(([key, label]) => <Link className={key === status ? "rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-black" : "rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm text-[color:var(--text-secondary)]"} href={`/dashboard/eval/gaps?status=${key}`} key={key}>{label}</Link>)}
          </nav>
          {safeResponse.critical_gap_count > 0 ? (
            <details className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
              <summary className="cursor-pointer font-semibold text-[color:var(--text-primary)]">Your 3-step fix plan</summary>
              <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm text-[color:var(--text-secondary)]">
                <li>Run <code className="text-[color:var(--accent-primary)]">skilgen analyse --project-root .</code> to generate all missing skills.</li>
                <li>Open each low-score skill and improve the weakest sub-section shown below.</li>
                <li>Add <code className="text-[color:var(--accent-primary)]">## Last verified</code> dates to stale skills to reset freshness score.</li>
              </ol>
              <Link className="mt-4 inline-flex text-sm font-semibold text-[color:var(--accent-primary)]" href="/dashboard/autopilot">Open Autopilot to auto-fix →</Link>
            </details>
          ) : null}
          <div className="grid gap-4">
            {gaps.map((gap: EvalSkillGap) => (
              <article className={`rounded-xl border bg-[color:var(--bg-surface)] p-5 ${severityClass(gap.severity)}`} key={gap.id}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className={`text-xs font-semibold uppercase tracking-widest ${severityText(gap.severity)}`}>● {gap.severity} · {gap.gap_type.replaceAll("_", " ")}</div>
                    <h2 className="mt-1 text-xl font-semibold">{gap.domain} · {gap.repo_name}</h2>
                  </div>
                  <span className="rounded-full bg-white/10 px-2 py-1 text-xs capitalize text-[color:var(--text-secondary)]">{gap.status}</span>
                </div>
                <p className="mt-4 text-sm text-[color:var(--text-secondary)]"><b>Evidence:</b> {gap.evidence}</p>
                <p className="mt-3 text-sm text-[color:var(--text-secondary)]"><b>Impact:</b> {gap.estimated_impact}</p>
                <p className="mt-3 text-sm text-[color:var(--text-secondary)]"><b>Recommendation:</b> {gap.recommendation}</p>
                {gap.fix_command ? <div className="mt-4 flex flex-wrap items-center gap-3 rounded-md border border-[color:var(--bg-border)] bg-black/20 p-3"><code className="font-mono text-xs text-[color:var(--accent-primary)]">{gap.fix_command}</code><button className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-1.5 text-xs" onClick={() => navigator.clipboard.writeText(gap.fix_command ?? "")} type="button"><Clipboard className="h-3.5 w-3.5" />Copy</button></div> : null}
                <div className="mt-5 flex flex-wrap gap-2">
                  <button className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs" onClick={() => void updateGap(gap.id, "acknowledge")} type="button">Acknowledge — I&apos;ll handle this later</button>
                  <button className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs" onClick={() => void updateGap(gap.id, "resolve")} type="button">Mark resolved</button>
                </div>
              </article>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
