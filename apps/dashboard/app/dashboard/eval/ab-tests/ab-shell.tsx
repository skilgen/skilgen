"use client";

import { FlaskConical, Plus } from "lucide-react";
import type { ReactElement } from "react";
import { useMemo, useState } from "react";
import useSWR from "swr";

import type { ABTest } from "../../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type SkillOption = {
  id: string;
  label: string;
  versions: Array<{ id: string; version_number: number; is_latest: boolean }>;
};

function pct(value: number | null | undefined): string {
  return typeof value === "number" ? `${Math.round(value * 100)}%` : "n/a";
}

export function ABShell({ accessToken, orgId, skills, tests }: { accessToken: string; orgId: string; skills: SkillOption[]; tests: ABTest[] }): ReactElement {
  const fetcher = async (url: string): Promise<ABTest[]> => {
    const response = await fetch(url, { headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {} });
    if (!response.ok) throw new Error("Could not load A/B tests");
    return response.json() as Promise<ABTest[]>;
  };
  const { data: liveTests = tests, mutate, isValidating } = useSWR(`${API_URL}/eval/orgs/${orgId}/ab-tests`, fetcher, {
    fallbackData: tests,
    refreshInterval: 10000,
  });
  const [open, setOpen] = useState(false);
  const [skillId, setSkillId] = useState(skills[0]?.id ?? "");
  const selected = skills.find((skill) => skill.id === skillId);
  const control = selected?.versions.find((version) => version.is_latest) ?? selected?.versions[0];
  const treatment = selected?.versions.find((version) => version.id !== control?.id);
  const defaultName = useMemo(() => `${selected?.label ?? "Skill"} v${control?.version_number ?? 1} vs v${treatment?.version_number ?? 2}`, [selected, control, treatment]);
  const [name, setName] = useState("");
  async function createTest(): Promise<void> {
    if (!skillId || !control || !treatment) return;
    await fetch(`${API_URL}/eval/orgs/${orgId}/ab-tests`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
      body: JSON.stringify({ skill_id: skillId, name: name || defaultName, control_version_id: control.id, treatment_version_id: treatment.id }),
    });
    await mutate();
    setOpen(false);
  }
  async function conclude(testId: string): Promise<void> {
    await fetch(`${API_URL}/eval/orgs/${orgId}/ab-tests/${testId}/conclude`, { method: "POST", headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {} });
    await mutate();
  }
  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">A/B Skill Tests</h1>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Compare skill versions against real agent tasks. {isValidating ? "Refreshing status..." : "Live status refreshes every 10 seconds."}</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-black" onClick={() => setOpen(true)} type="button"><Plus className="h-4 w-4" />New A/B Test</button>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {liveTests.map((test) => (
          <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={test.id}>
            <div className="flex items-center justify-between"><h2 className="font-semibold">{test.skill_name ?? test.name}</h2><span className="rounded-full border border-[color:var(--bg-border)] px-2 py-1 text-xs capitalize">{String(test.status).replace("_", " ")}</span></div>
            {test.status === "completed" ? (
              <div className="mt-5 rounded-lg border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 p-4 text-sm text-[color:var(--accent-green)]">Treatment wins? {test.winner === "treatment" ? `Yes (+${test.improvement_pct ?? 0}% success rate)` : test.winner}</div>
            ) : (
              <div className="mt-5 grid grid-cols-[1fr_auto_1fr] items-center gap-4 text-center">
                <div><div className="text-xs text-[color:var(--text-tertiary)]">Control</div><div className="mt-2 text-2xl font-semibold">{pct(test.control_success_rate)}</div><div className="text-xs text-[color:var(--text-tertiary)]">{test.control_task_count ?? 0} tasks</div></div>
                <div className="text-xs text-[color:var(--text-tertiary)]">vs</div>
                <div><div className="text-xs text-[color:var(--text-tertiary)]">Treatment</div><div className="mt-2 text-2xl font-semibold">{pct(test.treatment_success_rate)}</div><div className="text-xs text-[color:var(--text-tertiary)]">{test.treatment_task_count ?? 0} tasks</div></div>
              </div>
            )}
            <p className="mt-4 text-sm text-[color:var(--text-secondary)]">{test.recommendation ?? `Confidence: ${test.confidence ?? "Collecting data"}`}</p>
            {test.status === "running" ? <button className="mt-4 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs" onClick={() => conclude(test.id)} type="button">Conclude test</button> : null}
            {test.status === "needs_data" ? <button className="mt-4 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-xs font-semibold text-black" onClick={() => setOpen(true)} type="button">Start a fresh test</button> : null}
          </article>
        ))}
      </div>
      {open ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="w-full max-w-lg rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-5">
            <div className="mb-4 flex items-center gap-2"><FlaskConical className="h-5 w-5 text-[color:var(--accent-primary)]" /><h2 className="text-lg font-semibold">New A/B Test</h2></div>
            <label className="block text-sm">Skill<select className="mt-2 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-2" value={skillId} onChange={(event) => setSkillId(event.target.value)}>{skills.map((skill) => <option key={skill.id} value={skill.id}>{skill.label}</option>)}</select></label>
            <div className="mt-4 grid gap-3 md:grid-cols-2"><div className="rounded-md border border-[color:var(--bg-border)] p-3 text-sm">Control: v{control?.version_number ?? "n/a"}</div><div className="rounded-md border border-[color:var(--bg-border)] p-3 text-sm">Treatment: v{treatment?.version_number ?? "n/a"}</div></div>
            <label className="mt-4 block text-sm">Name<input className="mt-2 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-2" value={name || defaultName} onChange={(event) => setName(event.target.value)} /></label>
            <div className="mt-5 flex justify-end gap-2"><button className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm" onClick={() => setOpen(false)} type="button">Cancel</button><button className="rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-black" onClick={createTest} type="button">Create test</button></div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
