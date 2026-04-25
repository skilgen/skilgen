"use client";

import Link from "next/link";
import { AlertTriangle, CheckCircle2, Clipboard, ChevronDown } from "lucide-react";
import type { ReactElement } from "react";
import { useState } from "react";

import type { EvalSkillGap } from "../../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function tone(gapType: string): string {
  return gapType === "missing_skill" ? "border-[#ef4444]/40" : "border-[#f59e0b]/40";
}

function label(gapType: string): string {
  if (gapType === "missing_skill") return "MISSING SKILL";
  if (gapType === "stale_skill") return "STALE SKILL";
  return "WEAK SKILL";
}

export function GapsShell({ accessToken, gaps, orgId, status }: { accessToken: string; gaps: EvalSkillGap[]; orgId: string; status: string }): ReactElement {
  const [expanded, setExpanded] = useState<string | null>(null);
  async function updateGap(gapId: string, nextStatus: "acknowledged" | "resolved"): Promise<void> {
    await fetch(`${API_URL}/eval/orgs/${orgId}/skill-gaps/${gapId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
      body: JSON.stringify({ status: nextStatus }),
    });
    window.location.reload();
  }
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Skill Gaps</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Auto-detected from agent failures.</p>
      </div>
      <div className={gaps.length ? "rounded-xl border border-[#f59e0b]/30 bg-[#f59e0b]/10 p-4 text-sm text-amber-100" : "rounded-xl border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 p-4 text-sm text-[color:var(--accent-green)]"}>
        {gaps.length ? `Agents failed ${gaps.reduce((sum, gap) => sum + gap.failure_count, 0)} times on domains with weak or missing skills in the last 7 days.` : "✓ No skill gaps detected — all domains have sufficient coverage"}
      </div>
      <div className="flex gap-2">
        {["open", "acknowledged", "resolved"].map((item) => (
          <Link className={item === status ? "rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-black" : "rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm text-[color:var(--text-secondary)]"} href={`/dashboard/eval/gaps?status=${item}`} key={item}>
            {item[0].toUpperCase() + item.slice(1)}
          </Link>
        ))}
      </div>
      <div className="grid gap-4">
        {gaps.map((gap) => (
          <article className={`rounded-xl border bg-[color:var(--bg-surface)] p-5 ${tone(gap.gap_type)}`} key={gap.id ?? gap.domain}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="text-xs font-semibold tracking-widest text-[#f59e0b]">{label(gap.gap_type)}</div>
                <h2 className="mt-1 text-xl font-semibold">{gap.domain}</h2>
                <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{gap.failure_count} agent failures in last 7 days.</p>
              </div>
              <AlertTriangle className="h-5 w-5 text-[#f59e0b]" />
            </div>
            <p className="mt-4 text-sm text-[color:var(--text-secondary)]">
              {gap.gap_type === "missing_skill" ? "No skill exists for this domain." : `Existing skill score: ${gap.existing_skill_score ?? "unknown"}/100.`}
            </p>
            <div className="mt-4 rounded-md border border-[color:var(--bg-border)] bg-black/20 p-3 font-mono text-xs text-[color:var(--text-secondary)]">{gap.suggested_action}</div>
            <div className="mt-4 flex flex-wrap gap-2">
              <button className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs" onClick={() => navigator.clipboard.writeText(gap.suggested_action ?? "")} type="button"><Clipboard className="h-3.5 w-3.5" />Copy command</button>
              {gap.id ? <button className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs" onClick={() => updateGap(gap.id!, "acknowledged")} type="button"><CheckCircle2 className="h-3.5 w-3.5" />Mark acknowledged</button> : null}
              <button className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs" onClick={() => setExpanded(expanded === gap.id ? null : gap.id ?? gap.domain)} type="button"><ChevronDown className="h-3.5 w-3.5" />View failed tasks</button>
            </div>
            {expanded === (gap.id ?? gap.domain) ? (
              <div className="mt-4 overflow-hidden rounded-lg border border-[color:var(--bg-border)]">
                {(gap.failed_tasks ?? []).map((task) => (
                  <div className="grid grid-cols-[1fr_120px_1fr] gap-3 border-t border-[color:var(--bg-border)] px-3 py-2 text-xs" key={task.id}>
                    <span>{task.description ?? "Untitled task"}</span><span>{task.outcome}</span><span>{task.failure_reason ?? "No reason captured"}</span>
                  </div>
                ))}
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </div>
  );
}
