"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ShieldAlert } from "lucide-react";

import type { Skill } from "../../../../lib/data";

type RepoSkill = Skill & {
  last_updated_at?: string | null;
};

type SourceFilter = "all" | "code" | "api" | "infrastructure" | "data" | "security" | "operational";

const sourceFilterLabels: Record<SourceFilter, string> = {
  all: "All",
  code: "Code",
  api: "API Specs",
  infrastructure: "Infrastructure",
  data: "Data",
  security: "Security",
  operational: "Operational",
};

const sourceGroups: Record<Exclude<SourceFilter, "all">, string[]> = {
  code: ["code"],
  api: ["openapi", "graphql", "postman"],
  infrastructure: ["terraform", "kubernetes", "helm"],
  data: ["dbt", "sql_schema", "kafka"],
  security: ["sarif", "sbom", "security_policy"],
  operational: ["runbook", "confluence", "notion", "incident", "pagerduty"],
};

function relativeTime(value: string | null | undefined): string {
  if (!value) return "—";
  const timestamp = new Date(value).getTime();
  if (Number.isNaN(timestamp)) return "—";
  const diff = Math.max(0, Date.now() - timestamp);
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;
  if (diff < hour) return `${Math.max(1, Math.floor(diff / minute))} minutes ago`;
  if (diff < day) return `${Math.floor(diff / hour)} hours ago`;
  if (diff < 7 * day) return `${Math.floor(diff / day)} days ago`;
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(timestamp));
}

function scoreBadgeClass(score: number): string {
  if (score <= 40) return "bg-red-900/30 text-red-400";
  if (score <= 70) return "bg-amber-900/30 text-amber-400";
  return "bg-green-900/30 text-green-400";
}

function ScoreBadge({ score }: { score: number | null | undefined }) {
  if (typeof score !== "number") return <span className="text-gray-600">Not analysed</span>;
  return <span className={`inline-flex rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreBadgeClass(score)}`}>{score}/100</span>;
}

function matchesFilter(skill: RepoSkill, filter: SourceFilter): boolean {
  if (filter === "all") return true;
  const sourceType = skill.source_type ?? "code";
  return sourceGroups[filter].includes(sourceType);
}

export function SkillSourceFilter({ repoId, skills }: { repoId: string; skills: RepoSkill[] }) {
  const [filter, setFilter] = useState<SourceFilter>("all");
  const sortedSkills = useMemo(
    () => [...skills].sort((left, right) => (right.score?.total ?? 0) - (left.score?.total ?? 0)),
    [skills],
  );
  const filteredSkills = useMemo(
    () => sortedSkills.filter((skill) => matchesFilter(skill, filter)),
    [filter, sortedSkills],
  );

  return (
    <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="flex flex-col gap-4 border-b border-[color:var(--bg-border)] px-5 py-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Skills</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{filteredSkills.length} generated skill files</p>
        </div>
        <label className="flex items-center gap-2 text-[12px] font-semibold text-[color:var(--text-secondary)]">
          Source
          <select
            className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] px-3 py-2 text-[13px] text-[color:var(--text-primary)]"
            onChange={(event) => setFilter(event.target.value as SourceFilter)}
            value={filter}
          >
            {Object.entries(sourceFilterLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] border-collapse text-left text-[13px]">
          <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
            <tr className="border-b border-[color:var(--bg-border)]">
              <th className="px-5 py-3 font-semibold">Domain</th>
              <th className="px-5 py-3 font-semibold">Source</th>
              <th className="px-5 py-3 font-semibold">Score</th>
              <th className="px-5 py-3 font-semibold">Stale?</th>
              <th className="px-5 py-3 font-semibold">Last updated</th>
              <th className="px-5 py-3 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredSkills.map((skill) => (
              <tr className="border-b border-[color:var(--bg-elevated)] last:border-b-0 hover:bg-white/5" key={skill.id}>
                <td className="px-5 py-4">
                  <div className="font-medium text-[color:var(--text-primary)]">{skill.domain}</div>
                  <div className="mt-0.5 font-mono text-[12px] text-[color:var(--text-tertiary)]">{skill.skill_path}</div>
                </td>
                <td className="px-5 py-4 text-[color:var(--text-secondary)]">{skill.source_type ?? "code"}</td>
                <td className="px-5 py-4"><ScoreBadge score={skill.score?.total} /></td>
                <td className="px-5 py-4">
                  {skill.is_stale ? (
                    <span className="inline-flex items-center rounded-full bg-red-900/30 px-2 py-0.5 text-[12px] font-semibold text-red-400">
                      <ShieldAlert className="mr-1 h-3 w-3" />
                      Stale
                    </span>
                  ) : (
                    <span className="text-[color:var(--text-secondary)]">Fresh</span>
                  )}
                </td>
                <td className="px-5 py-4 text-[color:var(--text-secondary)]">{relativeTime(skill.last_updated_at ?? skill.last_loaded_at)}</td>
                <td className="px-5 py-4">
                  <Link
                    className="inline-flex rounded-md border border-[rgb(var(--accent-primary-rgb)/0.45)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--accent-primary)] transition-colors hover:bg-[rgb(var(--accent-primary-rgb)/0.12)]"
                    href={`/dashboard/repos/${repoId}/skills/${skill.id}`}
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
            {filteredSkills.length === 0 ? (
              <tr>
                <td className="px-5 py-8 text-center text-[color:var(--text-secondary)]" colSpan={6}>
                  No skills match this source filter.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
