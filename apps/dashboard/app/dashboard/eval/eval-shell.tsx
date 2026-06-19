"use client";

import Link from "next/link";
import { BarChart2, Clipboard } from "lucide-react";
import type { ReactElement } from "react";
import { useState } from "react";

import type { EvalSessionQuality, EvalSummary } from "../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

function qualityClass(signal: string): string {
  if (signal === "strong") return "bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]";
  if (signal === "mixed") return "bg-amber-500/15 text-amber-300";
  return "bg-red-500/15 text-red-300";
}

function agentDisplayName(row: EvalSessionQuality): string {
  if (row.agent_runtime === "unidentified_agent" || row.agent_display_name === "Unidentified Agent") return "Codex CLI";
  return row.agent_display_name ?? row.agent_runtime;
}

function TrendChart({ points }: { points: EvalSummary["weekly_trend"] }): ReactElement {
  if (points.filter((point) => point.sessions > 0).length < 2) {
    return <div className="rounded-lg border border-dashed border-[color:var(--bg-border)] p-8 text-center text-sm text-[color:var(--text-secondary)]">📊 Trend appears after 2 weeks of sessions.</div>;
  }
  const width = 720;
  const height = 220;
  const x = (index: number) => (points.length <= 1 ? width / 2 : (index / (points.length - 1)) * width);
  const y = (value: number) => height - 28 - (Math.max(0, Math.min(100, value)) / 100) * (height - 52);
  const strong = points.map((point, index) => `${x(index)},${y(point.strong_pct)}`).join(" ");
  const weak = points.map((point, index) => `${x(index)},${y(point.weak_pct)}`).join(" ");
  return (
    <svg className="h-[220px] w-full" preserveAspectRatio="none" viewBox={`0 0 ${width} ${height}`}>
      <polyline fill="none" points={strong} stroke="var(--accent-green)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" />
      <polyline fill="none" points={weak} stroke="#ef4444" strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" />
      {points.map((point, index) => <text fill="rgba(238,238,245,0.55)" fontSize="11" key={point.week} textAnchor="middle" x={x(index)} y={height - 6}>{`W${index + 1}`}</text>)}
    </svg>
  );
}

function SetupGuide({ orgId }: { orgId: string }): ReactElement {
  const cli = "SKILLAYER_API_KEY=sk-... skilgen analytics --upload --repo-id <repo-id>";
  const api = `POST https://api.skillayer.com/eval/orgs/${orgId}/tasks\n{ "outcome": "success", "skills_loaded": [...] }`;
  return (
    <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">Connect session quality data</h2>
      <p className="mt-2 text-sm text-[color:var(--text-secondary)]">Once your agents start loading skills, Skillayer will show whether each session had strong, mixed, or weak guidance. Use this setup only if sessions are not appearing automatically.</p>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        {[["CLI", cli], ["API", api]].map(([title, code]) => (
          <div className="rounded-lg border border-[color:var(--bg-border)] bg-black/20 p-4" key={title}>
            <div className="mb-3 flex items-center justify-between"><h3 className="text-sm font-semibold">{title}</h3><button className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-1.5 text-xs" onClick={() => navigator.clipboard.writeText(code)} type="button"><Clipboard className="h-3.5 w-3.5" />Copy</button></div>
            <pre className="whitespace-pre-wrap break-all font-mono text-xs leading-6 text-[color:var(--text-secondary)]">{code}</pre>
          </div>
        ))}
      </div>
    </section>
  );
}

export function EvalShell({ accessToken, orgId, sessions, summary }: { accessToken: string; orgId: string; sessions: EvalSessionQuality[]; summary: EvalSummary | null }): ReactElement {
  const [rows, setRows] = useState(sessions);
  async function tagOutcome(sessionId: string, outcome: "success" | "needs_rework") {
    setRows((current) => current.map((row) => row.session_id === sessionId ? { ...row, outcome } : row));
    await fetch(`${API_URL}/orgs/${orgId}/sessions/${sessionId}/tag`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
      body: JSON.stringify({ outcome }),
    });
  }
  const safeSummary = summary ?? { total_sessions: 0, strong_sessions: 0, mixed_sessions: 0, weak_sessions: 0, strong_pct: 0, top_skill_impact: [], weekly_trend: [], insight: "No sessions recorded yet." };
  const hasImpactData = safeSummary.top_skill_impact.length > 0;
  if (safeSummary.total_sessions === 0) {
    return (
      <div className="space-y-6">
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
          <BarChart2 className="mx-auto h-12 w-12 text-[color:var(--accent-primary)]" />
          <h1 className="mt-5 text-2xl font-semibold text-[color:var(--text-primary)]">No agent sessions recorded yet</h1>
          <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-[color:var(--text-secondary)]">Once your agents start loading skills, you&apos;ll see session quality trends here.</p>
        </section>
        <SetupGuide orgId={orgId} />
      </div>
    );
  }
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Agent Performance</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">How well-guided were your agents? Skill quality during each session shapes code quality.</p>
      </header>
      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-[color:var(--accent-green)]/30 bg-[color:var(--bg-surface)] p-5"><div className="text-xs text-[color:var(--text-tertiary)]">Strong sessions</div><div className="mt-2 text-3xl font-semibold text-[color:var(--accent-green)]">{safeSummary.strong_sessions} ({safeSummary.strong_pct}%)</div></div>
        <div className="rounded-lg border border-amber-500/30 bg-[color:var(--bg-surface)] p-5"><div className="text-xs text-[color:var(--text-tertiary)]">Mixed sessions</div><div className="mt-2 text-3xl font-semibold text-amber-300">{safeSummary.mixed_sessions}</div></div>
        <div className="rounded-lg border border-red-500/30 bg-[color:var(--bg-surface)] p-5"><div className="text-xs text-[color:var(--text-tertiary)]">Weak sessions</div><div className="mt-2 text-3xl font-semibold text-red-300">{safeSummary.weak_sessions}</div><p className="mt-1 text-xs text-[color:var(--text-secondary)]">needs attention</p></div>
      </section>
      <div className="rounded-xl border border-[color:var(--bg-border)] bg-black/20 p-4 text-sm text-[color:var(--text-secondary)]">{safeSummary.insight}</div>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><h2 className="text-lg font-semibold">Weekly quality trend</h2><TrendChart points={safeSummary.weekly_trend} /></section>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-lg font-semibold">Session quality breakdown</h2>
        <div className="mt-4 overflow-x-auto rounded-lg border border-[color:var(--bg-border)]">
          <table className="w-full min-w-[980px] text-left text-sm">
            <thead className="bg-black/20 text-xs uppercase tracking-wide text-[color:var(--text-tertiary)]"><tr><th className="p-3">Date/Time</th><th>Agent</th><th>Repo</th><th>Context</th><th>Skills loaded</th><th>Guidance quality</th><th>Outcome</th><th>Tag</th></tr></thead>
            <tbody>{rows.map((row) => <tr className="border-t border-[color:var(--bg-border)]" key={row.session_id}><td className="p-3">{new Date(row.started_at).toLocaleString()}</td><td>{agentDisplayName(row)}</td><td>{row.repo_name}</td><td>{row.session_context}</td><td>{row.skills_loaded.slice(0, 4).join(", ")}</td><td><span className={`rounded-full px-2 py-1 text-xs font-semibold capitalize ${qualityClass(row.quality_signal)}`}>{row.quality_signal}</span></td><td>{row.outcome}</td><td><select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-2 py-1 text-xs" onChange={(event) => { if (event.target.value) void tagOutcome(row.session_id, event.target.value as "success" | "needs_rework"); }} value={row.outcome === "unknown" ? "" : row.outcome}><option value="">Tag outcome</option><option value="success">Success</option><option value="needs_rework">Needs rework</option></select></td></tr>)}</tbody>
          </table>
        </div>
      </section>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-lg font-semibold">Which skills make the biggest difference?</h2>
        <div className="mt-4 overflow-hidden rounded-lg border border-[color:var(--bg-border)]">
          <div className="grid grid-cols-4 bg-black/20 px-4 py-3 text-xs uppercase tracking-wide text-[color:var(--text-tertiary)]"><span>Domain</span><span>Times in strong sessions</span><span>Times in weak sessions</span><span>Net impact</span></div>
          {!hasImpactData ? (
            <div className="border-t border-[color:var(--bg-border)] px-4 py-8 text-center text-sm text-[color:var(--text-secondary)]">Skill impact rankings appear after at least 3 sessions with clear strong or weak guidance signals.</div>
          ) : safeSummary.top_skill_impact.map((item) => {
            const net = item.strong_appearances - item.weak_appearances;
            return <div className="grid grid-cols-4 border-t border-[color:var(--bg-border)] px-4 py-3 text-sm" key={item.domain}><span>{item.domain}</span><span>{item.strong_appearances}</span><span>{item.weak_appearances}</span><span className={net >= 0 ? "text-[color:var(--accent-green)]" : "text-red-300"}>{net >= 0 ? "+" : ""}{net}</span></div>;
          })}
        </div>
      </section>
      <Link className="text-sm font-semibold text-[color:var(--accent-primary)]" href="/dashboard/eval/gaps">Review skill gaps →</Link>
    </div>
  );
}
