"use client";

import { useMemo, useState } from "react";

import type { HalfLifeSkill, HalfLifeSummary } from "../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

export function HalfLifeShell({ accessToken, orgId, summary }: { accessToken: string; orgId: string; summary: HalfLifeSummary | null }) {
  const [status, setStatus] = useState("");
  const rows = useMemo(() => [...(summary?.critical ?? []), ...(summary?.warning ?? []), ...(summary?.healthy ?? [])], [summary]);
  async function refresh() {
    setStatus("Refreshing...");
    const response = await fetch(`${API_URL}/registry/orgs/${orgId}/half-life/refresh`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` } });
    setStatus(response.ok ? "Refresh queued ✓" : "Could not refresh predictions");
  }
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Skill Half-life Engine</h1>
          <p className="mt-2 text-[15px] text-[color:var(--text-secondary)]">Predicted decay dates based on domain commit velocity.</p>
        </div>
        <button className="rounded-full bg-[color:var(--accent-primary)] px-5 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)]" onClick={refresh} type="button">Refresh Predictions</button>
      </div>
      {status ? <div className="text-[12px] text-[color:var(--text-tertiary)]">{status}</div> : null}
      <div className="grid gap-4 md:grid-cols-4">
        <Metric label="CRITICAL" tone="red" value={summary?.critical.length ?? 0} />
        <Metric label="WARNING" tone="amber" value={summary?.warning.length ?? 0} />
        <Metric label="HEALTHY" tone="green" value={summary?.healthy.length ?? 0} />
        <Metric label="REGEN QUEUED" value={summary?.regen_queued_count ?? 0} />
      </div>
      <Timeline rows={rows} />
      <div className="overflow-x-auto rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <table className="w-full min-w-[1000px] text-left text-[13px]">
          <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]"><tr>{["Skill Name", "Domain", "Repo", "Current Freshness", "Commit Velocity", "Predicted Decay", "Days Left", "Confidence", "Regen Status"].map((head) => <th className="px-5 py-3" key={head}>{head}</th>)}</tr></thead>
          <tbody>{rows.map((row) => <SkillRow key={row.skill_id} row={row} />)}</tbody>
        </table>
      </div>
      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <h2 className="text-[18px] font-semibold">Regeneration Buffer</h2>
        <p className="mt-2 text-[13px] text-[color:var(--text-secondary)]">Skills will be queued for regeneration before their predicted decay date.</p>
        <div className="mt-4 flex flex-wrap gap-2">{["6h", "12h", "24h", "48h", "72h"].map((value) => <button className="rounded-full border border-[color:var(--bg-border)] px-3 py-1.5 text-[12px]" key={value} type="button">{value}</button>)}</div>
      </section>
    </div>
  );
}

function Metric({ label, value, tone = "default" }: { label: string; value: number; tone?: "red" | "amber" | "green" | "default" }) {
  const cls = tone === "red" ? "text-[#ef4444]" : tone === "amber" ? "text-[#f59e0b]" : tone === "green" ? "text-[color:var(--accent-green)]" : "text-[color:var(--text-primary)]";
  return <div className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div><div className={`mt-3 text-[32px] font-semibold ${cls}`}>{value}</div></div>;
}

function Timeline({ rows }: { rows: HalfLifeSkill[] }) {
  return <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><div className="relative h-[92px] border-b border-[color:var(--bg-border)]">{rows.slice(0, 30).map((row, index) => { const left = `${Math.min(96, Math.max(2, (row.predicted_decay_days / 30) * 100))}%`; const color = row.predicted_decay_days < 3 ? "bg-[#ef4444]" : row.predicted_decay_days <= 7 ? "bg-[#f59e0b]" : "bg-[color:var(--accent-green)]"; return <button className={`absolute h-3 w-3 rounded-full ${color}`} key={row.skill_id} style={{ left, top: 16 + (index % 3) * 16 }} title={row.domain} type="button" />; })}</div><div className="mt-3 flex justify-between text-[11px] text-[color:var(--text-tertiary)]"><span>Today</span><span>30 days</span></div></section>;
}

function SkillRow({ row }: { row: HalfLifeSkill }) {
  const velocity = row.commits_30d / 30;
  const velocityLabel = velocity > 2 ? "High" : velocity > 0.5 ? "Moderate" : "Stable";
  const dayTone = row.predicted_decay_days < 3 ? "text-[#ef4444]" : row.predicted_decay_days <= 7 ? "text-[#f59e0b]" : "text-[color:var(--accent-green)]";
  return <tr className="border-t border-[color:var(--bg-border)]"><td className="px-5 py-4 font-medium">{row.name}</td><td className="px-5 py-4">{row.domain}</td><td className="px-5 py-4 text-[color:var(--text-secondary)]">{row.repo_name}</td><td className="px-5 py-4">{row.freshness}/25</td><td className="px-5 py-4">{velocityLabel}</td><td className="px-5 py-4">{row.predicted_decay_date ? new Date(row.predicted_decay_date).toLocaleDateString() : "—"}</td><td className={`px-5 py-4 font-semibold ${dayTone}`}>{Math.round(row.predicted_decay_days)}d</td><td className="px-5 py-4">{Math.round(row.decay_confidence * 100)}%</td><td className="px-5 py-4">{row.regen_queued ? <span className="text-[color:var(--accent-green)]">Queued ⚡</span> : row.freshness <= 20 ? <span className="text-[#f59e0b]">Already stale ⚠</span> : <span className="text-[color:var(--text-tertiary)]">Not queued</span>}</td></tr>;
}
