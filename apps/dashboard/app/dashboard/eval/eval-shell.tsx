"use client";

import Link from "next/link";
import { BarChart2, Clipboard, TrendingUp } from "lucide-react";
import type { ReactElement } from "react";

import type { EvalROI } from "../../../lib/data";

function pct(value: number | null | undefined): string {
  return typeof value === "number" ? `${Math.round(value * 100)}%` : "n/a";
}

function rateColor(value: number | null | undefined): string {
  if (typeof value !== "number") return "text-[color:var(--text-tertiary)]";
  if (value >= 0.7) return "text-[color:var(--accent-green)]";
  if (value >= 0.4) return "text-[#f59e0b]";
  return "text-[#ef4444]";
}

function SetupGuide({ orgId }: { orgId: string }): ReactElement {
  const cli = "skilgen eval record --outcome success --repo-id <repo-id>";
  const api = `POST https://api.skillayer.com/eval/orgs/${orgId}/tasks\n{ "outcome": "success", "skills_loaded": [...] }`;
  return (
    <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center">
      <BarChart2 className="mx-auto h-12 w-12 text-[color:var(--accent-primary)]" />
      <h2 className="mt-5 text-2xl font-semibold text-[color:var(--text-primary)]">Start measuring agent performance</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-[color:var(--text-secondary)]">Record task outcomes to see how skill quality affects your agents&apos; success rate.</p>
      <div className="mx-auto mt-7 grid max-w-3xl gap-4 text-left">
        {[["Option 1 - CLI", cli], ["Option 2 - API", api]].map(([title, code]) => (
          <div className="rounded-lg border border-[color:var(--bg-border)] bg-black/20 p-4" key={title}>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-[color:var(--text-primary)]">{title}</h3>
              <button className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-1.5 text-xs text-[color:var(--text-secondary)]" onClick={() => navigator.clipboard.writeText(code)} type="button">
                <Clipboard className="h-3.5 w-3.5" />
                Copy
              </button>
            </div>
            <pre className="whitespace-pre-wrap break-all font-mono text-xs leading-6 text-[color:var(--text-secondary)]">{code}</pre>
          </div>
        ))}
      </div>
      <div className="mt-6 text-sm text-[color:var(--text-secondary)]">
        Claude Code hook setup lives in <Link className="font-semibold text-[color:var(--accent-primary)]" href="/dashboard/connect">Connect Agent</Link>.
      </div>
    </section>
  );
}

function TrendChart({ roi }: { roi: EvalROI }): ReactElement {
  const points = roi.trend.length ? roi.trend : [];
  const width = 720;
  const height = 220;
  const x = (index: number) => (points.length <= 1 ? width / 2 : (index / (points.length - 1)) * width);
  const yRate = (value: number | null) => height - 28 - ((value ?? 0) * (height - 52));
  const yScore = (value: number | null) => height - 28 - (((value ?? 0) / 100) * (height - 52));
  const success = points.map((point, index) => `${x(index)},${yRate(point.success_rate)}`).join(" ");
  const score = points.map((point, index) => `${x(index)},${yScore(point.avg_skill_score)}`).join(" ");
  return (
    <svg className="h-[220px] w-full" preserveAspectRatio="none" viewBox={`0 0 ${width} ${height}`}>
      <polyline fill="none" points={success} stroke="var(--accent-green)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" />
      <polyline fill="none" points={score} stroke="var(--accent-primary)" strokeDasharray="8 8" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
      {points.map((point, index) => (
        <text fill="rgba(238,238,245,0.5)" fontSize="11" key={point.week} textAnchor="middle" x={x(index)} y={height - 6}>
          {`W${index + 1}`}
        </text>
      ))}
    </svg>
  );
}

export function EvalShell({ orgId, roi }: { orgId: string; roi: EvalROI }): ReactElement {
  if (roi.total_tasks === 0) return <SetupGuide orgId={orgId} />;
  const openGaps = roi.skill_gaps.length;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Agent Performance</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Measure how skill quality affects your agents&apos; success rate.</p>
      </div>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center">
        {roi.multiplier ? (
          <>
            <div className="text-7xl font-semibold text-[color:var(--accent-primary)]">{roi.multiplier}x</div>
            <p className="mt-3 text-lg font-semibold text-[color:var(--text-primary)]">better task success with high-quality skills</p>
            <p className="mt-4 text-sm text-[color:var(--text-secondary)]">Skilgen Score &gt;=70 -&gt; {pct(roi.high_skill_success_rate)} agent success rate</p>
            <p className="text-sm text-[color:var(--text-secondary)]">Skilgen Score &lt;40 -&gt; {pct(roi.low_skill_success_rate)} agent success rate</p>
          </>
        ) : (
          <>
            <div className="text-4xl font-semibold text-[color:var(--text-primary)]">Collect more task data</div>
            <p className="mt-3 text-sm text-[color:var(--text-secondary)]">At least 5 high-score and 5 low-score tasks are needed to show the ROI multiplier.</p>
          </>
        )}
      </section>
      <section className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4"><div className="text-xs text-[color:var(--text-tertiary)]">Total tasks</div><div className="mt-2 text-2xl font-semibold">{roi.total_tasks}</div></div>
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4"><div className="text-xs text-[color:var(--text-tertiary)]">Success rate</div><div className={`mt-2 text-2xl font-semibold ${rateColor(roi.success_rate)}`}>{pct(roi.success_rate)}</div></div>
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4"><div className="text-xs text-[color:var(--text-tertiary)]">Open skill gaps</div><div className={openGaps ? "mt-2 text-2xl font-semibold text-[#ef4444]" : "mt-2 text-2xl font-semibold text-[color:var(--accent-green)]"}>{openGaps}</div></div>
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4"><div className="text-xs text-[color:var(--text-tertiary)]">A/B tests</div><div className="mt-2 text-2xl font-semibold">Active</div></div>
      </section>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-lg font-semibold">Success rate by skill score</h2>
        <div className="mt-5 space-y-4">
          {roi.by_skill_score_bucket.map((bucket) => (
            <div className="grid grid-cols-[70px_1fr_54px] items-center gap-3" key={bucket.bucket}>
              <span className="text-sm text-[color:var(--text-secondary)]">{bucket.bucket}</span>
              <div className="h-3 rounded-full bg-black/30"><div className="h-3 rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${Math.round((bucket.success_rate ?? 0) * 100)}%` }} /></div>
              <span className="text-right text-sm font-semibold">{pct(bucket.success_rate)}</span>
            </div>
          ))}
        </div>
        <p className="mt-4 text-xs text-[color:var(--text-tertiary)]">Tasks are grouped by the average score of skills loaded during that task.</p>
      </section>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="mb-3 flex items-center gap-2"><TrendingUp className="h-4 w-4 text-[color:var(--accent-primary)]" /><h2 className="text-lg font-semibold">8-week trend</h2></div>
        <TrendChart roi={roi} />
        <p className="text-xs text-[color:var(--text-tertiary)]">As skill quality improves, task success rate follows.</p>
      </section>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-lg font-semibold">By agent runtime</h2>
        <div className="mt-4 overflow-hidden rounded-lg border border-[color:var(--bg-border)]">
          <div className="grid grid-cols-4 bg-black/20 px-4 py-3 text-xs text-[color:var(--text-tertiary)]"><span>Agent</span><span>Tasks</span><span>Success</span><span>Avg tokens</span></div>
          {roi.by_agent_runtime.map((row) => (
            <div className="grid grid-cols-4 border-t border-[color:var(--bg-border)] px-4 py-3 text-sm" key={row.runtime}><span>{row.runtime}</span><span>{row.task_count}</span><span>{pct(row.success_rate)}</span><span>{row.avg_token_count ?? "n/a"}</span></div>
          ))}
        </div>
      </section>
    </div>
  );
}
