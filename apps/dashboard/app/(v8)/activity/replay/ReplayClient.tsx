"use client";

import { Download } from "lucide-react";
import { useMemo, useState } from "react";

import type { ActivitySession, ReplayStep } from "../activity-data";

function riskClass(band: ReplayStep["risk_band"]): string {
  if (band === "high") return "text-red-200";
  if (band === "medium") return "text-amber-200";
  return "text-[color:var(--accent-green)]";
}

export function ReplayClient({ exportHtml, session, timeline }: { exportHtml: string; session: ActivitySession; timeline: ReplayStep[] }) {
  const [index, setIndex] = useState(0);
  const active = timeline[Math.min(index, Math.max(0, timeline.length - 1))];
  const exportHref = useMemo(() => `data:text/html;charset=utf-8,${encodeURIComponent(exportHtml)}`, [exportHtml]);

  if (!active) {
    return <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-sm text-[color:var(--text-secondary)]">No replay timeline is available for this session.</div>;
  }

  return (
    <section className="space-y-4">
      <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">{session.agent} - {session.repo_name}</h2>
            <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{session.session_id} - {session.user}</p>
          </div>
          <a className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)]" download={`skillayer-replay-${session.session_id}.html`} href={exportHref}>
            <Download className="h-4 w-4" />
            Export HTML
          </a>
        </div>
        <input
          aria-label="Replay step"
          className="mt-5 w-full accent-[color:var(--accent-primary)]"
          max={timeline.length - 1}
          min={0}
          onChange={(event) => setIndex(Number(event.target.value))}
          type="range"
          value={index}
        />
        <div className="mt-2 flex justify-between text-xs text-[color:var(--text-tertiary)]">
          <span>Step {active.index + 1}</span>
          <span>{timeline.length} steps</span>
        </div>
      </div>

      <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-xs text-[color:var(--text-tertiary)]">{active.timestamp}</div>
            <h3 className="mt-1 text-xl font-semibold capitalize text-[color:var(--text-primary)]">{active.action}</h3>
          </div>
          <span className={`text-sm font-semibold capitalize ${riskClass(active.risk_band)}`}>{active.risk_band} risk - {active.risk_score}</span>
        </div>
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <div className="rounded-md border border-[color:var(--bg-border)] p-3">
            <div className="text-xs font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Policy</div>
            <div className="mt-2 text-sm capitalize text-[color:var(--text-primary)]">{active.policy_decision}</div>
          </div>
          <div className="rounded-md border border-[color:var(--bg-border)] p-3">
            <div className="text-xs font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Action</div>
            <div className="mt-2 text-sm capitalize text-[color:var(--text-primary)]">{active.action_class}</div>
          </div>
          <div className="rounded-md border border-[color:var(--bg-border)] p-3">
            <div className="text-xs font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Result</div>
            <div className="mt-2 truncate text-sm text-[color:var(--text-primary)]">{JSON.stringify(active.result)}</div>
          </div>
        </div>
        {active.reasoning ? <p className="mt-4 text-sm text-[color:var(--text-secondary)]">{active.reasoning}</p> : null}
        <pre className="mt-4 max-h-[420px] overflow-auto rounded-md bg-black/30 p-4 text-xs leading-5 text-[color:var(--text-secondary)]">{active.file_diff || JSON.stringify(active.tool_call, null, 2)}</pre>
      </article>
    </section>
  );
}
