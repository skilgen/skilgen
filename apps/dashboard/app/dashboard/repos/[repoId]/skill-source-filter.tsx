"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ShieldAlert } from "lucide-react";

import type { Skill } from "../../../../lib/data";

type RepoSkill = Skill & {
  last_updated_at?: string | null;
};

type SourceGroup = "All" | "Code" | "API Specs" | "Infrastructure" | "Data" | "Security" | "Operational";

const SOURCE_GROUPS: Record<SourceGroup, Array<string | null | undefined>> = {
  All: [],
  Code: ["code", null, undefined],
  "API Specs": ["openapi", "graphql", "postman"],
  Infrastructure: ["terraform", "kubernetes", "helm"],
  Data: ["dbt", "sql_schema", "kafka"],
  Security: ["sarif", "sbom", "security_policy"],
  Operational: ["runbook", "confluence", "notion", "incident"],
};

const SOURCE_LABELS: Record<string, string> = {
  code: "Code",
  openapi: "OpenAPI",
  graphql: "GraphQL",
  postman: "Postman",
  terraform: "Terraform",
  kubernetes: "Kubernetes",
  helm: "Helm",
  dbt: "dbt",
  sql_schema: "SQL Schema",
  kafka: "Kafka",
  sarif: "SARIF",
  sbom: "SBOM",
  security_policy: "Security Policy",
  runbook: "Runbook",
  confluence: "Confluence",
  notion: "Notion",
  incident: "Incident",
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

function matchesGroup(skill: RepoSkill, group: SourceGroup): boolean {
  if (group === "All") return true;
  const sourceType = skill.source_type ?? "code";
  return SOURCE_GROUPS[group].includes(sourceType);
}

export function SkillSourceFilter({
  skills,
  onChange,
}: {
  skills: RepoSkill[];
  onChange: (filtered: RepoSkill[]) => void;
}) {
  const [activeGroup, setActiveGroup] = useState<SourceGroup>("All");

  function selectGroup(group: SourceGroup): void {
    setActiveGroup(group);
    const filtered = group === "All" ? skills : skills.filter((skill) => matchesGroup(skill, group));
    onChange(filtered);
  }

  return (
    <div className="flex flex-wrap gap-2">
      {(Object.keys(SOURCE_GROUPS) as SourceGroup[]).map((group) => (
        <button
          className={`rounded-full px-3 py-1.5 text-[12px] font-semibold transition-colors ${
            activeGroup === group
              ? "bg-yellow-400 text-black"
              : "border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]"
          }`}
          key={group}
          onClick={() => selectGroup(group)}
          type="button"
        >
          {group}
        </button>
      ))}
    </div>
  );
}

export function RepoSkillsPanel({ repoId, skills }: { repoId: string; skills: RepoSkill[] }) {
  const sortedSkills = useMemo(() => [...skills].sort((left, right) => (right.score?.total ?? 0) - (left.score?.total ?? 0)), [skills]);
  const [filteredSkills, setFilteredSkills] = useState<RepoSkill[]>(sortedSkills);

  return (
    <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="flex flex-col gap-4 border-b border-[color:var(--bg-border)] px-5 py-4">
        <div>
          <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Skills</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{filteredSkills.length} generated skill files</p>
        </div>
        <SkillSourceFilter onChange={setFilteredSkills} skills={sortedSkills} />
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
                <td className="px-5 py-4 text-[color:var(--text-secondary)]">{SOURCE_LABELS[skill.source_type ?? "code"] ?? (skill.source_type ?? "Code")}</td>
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
