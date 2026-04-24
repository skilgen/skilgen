"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { BookOpen, Zap } from "lucide-react";

import { relativeTime } from "../../../lib/relative-time";

type AlertFilter = "all" | "healthy" | "stale_but_active" | "dead_skill";
type SortMode = "criticality" | "loads" | "score" | "alpha";

type HeatmapClientProps = {
  skills: SkillHeatmapSkill[];
  summary: SkillHeatmapSummary;
  hasSkills: boolean;
};

type SkillHeatmapSkill = {
  skill_id: string;
  domain: string;
  repo_id: string;
  repo_name: string;
  skill_category: string | null;
  score_total: number;
  loads_30d: number;
  criticality_score: number;
  last_loaded_at: string | null;
  alert: "healthy" | "stale_but_active" | "dead_skill";
};

type SkillHeatmapSummary = {
  total_skills: number;
  dead_skills: number;
  stale_but_active: number;
  healthy: number;
  avg_criticality: number;
};

const categoryClasses: Record<string, string> = {
  codebase_architecture: "bg-blue-900/30 text-blue-300",
  code_style: "bg-purple-900/30 text-purple-300",
  testing_conventions: "bg-green-900/30 text-green-300",
  internal_tools: "bg-amber-900/30 text-amber-300",
  security_compliance: "bg-red-900/30 text-red-300",
  design_system: "bg-pink-900/30 text-pink-300",
  data_schema: "bg-cyan-900/30 text-cyan-300",
  operational_knowledge: "bg-orange-900/30 text-orange-300",
};

function scoreBadgeClass(score: number): string {
  if (score <= 40) return "bg-red-900/30 text-red-400";
  if (score <= 70) return "bg-amber-900/30 text-amber-400";
  return "bg-green-900/30 text-green-400";
}

function titleize(value: string | null): string {
  if (!value) return "Unknown";
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function HeatmapClient({ skills, summary: _summary, hasSkills }: HeatmapClientProps) {
  void _summary;
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [alert, setAlert] = useState<AlertFilter>("all");
  const [sortMode, setSortMode] = useState<SortMode>("criticality");

  const filteredSkills = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    const visible = skills.filter((skill) => {
      const matchesQuery =
        !normalized || `${skill.domain} ${skill.repo_name}`.toLowerCase().includes(normalized);
      const matchesAlert = alert === "all" || skill.alert === alert;
      return matchesQuery && matchesAlert;
    });

    return [...visible].sort((left, right) => {
      if (sortMode === "loads") return right.loads_30d - left.loads_30d;
      if (sortMode === "score") return right.score_total - left.score_total;
      if (sortMode === "alpha") return left.domain.localeCompare(right.domain);
      return right.criticality_score - left.criticality_score;
    });
  }, [alert, query, skills, sortMode]);

  return (
    <div className="space-y-5">
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <input
            className="h-10 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] text-[color:var(--text-primary)] outline-none transition-colors placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)] xl:w-[300px]"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by domain or repo"
            type="search"
            value={query}
          />
          <div className="flex flex-col gap-3 md:flex-row md:items-center">
            <div className="flex flex-wrap gap-2">
              {[
                { label: "All", value: "all" },
                { label: "Healthy", value: "healthy" },
                { label: "Stale & active", value: "stale_but_active" },
                { label: "Dead skills", value: "dead_skill" },
              ].map((option) => (
                <button
                  className={`rounded-full px-3 py-1.5 text-[13px] font-semibold ${
                    alert === option.value
                      ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]"
                      : "border border-[color:var(--bg-border)] text-[color:var(--text-secondary)]"
                  }`}
                  key={option.value}
                  onClick={() => setAlert(option.value as AlertFilter)}
                  type="button"
                >
                  {option.label}
                </button>
              ))}
            </div>
            <select
              className="h-10 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]"
              onChange={(event) => setSortMode(event.target.value as SortMode)}
              value={sortMode}
            >
              <option value="criticality">Criticality ↓</option>
              <option value="loads">Loads 30d ↓</option>
              <option value="score">Score ↓</option>
              <option value="alpha">A–Z</option>
            </select>
          </div>
        </div>
      </section>

      <section className="overflow-x-auto rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        {filteredSkills.length > 0 ? (
          <table className="w-full min-w-[980px] border-collapse text-left text-[13px]">
            <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
              <tr className="border-b border-[color:var(--bg-border)]">
                <th className="px-5 py-3 font-semibold">Domain</th>
                <th className="px-5 py-3 font-semibold">Repo</th>
                <th className="px-5 py-3 font-semibold">Category</th>
                <th className="px-5 py-3 font-semibold">Score</th>
                <th className="px-5 py-3 font-semibold">Criticality</th>
                <th className="px-5 py-3 font-semibold">Loads 30d</th>
                <th className="px-5 py-3 font-semibold">Alert</th>
                <th className="px-5 py-3 font-semibold">Last loaded</th>
              </tr>
            </thead>
            <tbody>
              {filteredSkills.map((skill) => (
                <tr className="border-b border-[color:var(--bg-elevated)] transition-colors last:border-b-0 hover:bg-white/5" key={skill.skill_id}>
                  <td className="px-5 py-4">
                    <button
                      className="font-medium text-[color:var(--text-primary)] hover:text-[color:var(--accent-primary)]"
                      onClick={() => router.push(`/dashboard/repos/${skill.repo_id}`)}
                      type="button"
                    >
                      {skill.domain}
                    </button>
                  </td>
                  <td className="px-5 py-4 font-mono text-[12px] text-[color:var(--text-tertiary)]">{skill.repo_name}</td>
                  <td className="px-5 py-4">
                    <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${categoryClasses[skill.skill_category ?? ""] ?? "bg-white/10 text-[color:var(--text-secondary)]"}`}>
                      {titleize(skill.skill_category)}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <span className={`rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreBadgeClass(skill.score_total)}`}>{skill.score_total}/100</span>
                  </td>
                  <td className="px-5 py-4">
                    <div className="font-semibold text-[color:var(--text-primary)]">{skill.criticality_score}</div>
                    <div className="mt-2 h-1 w-full rounded-full bg-white/8">
                      <div className={`h-full rounded-full ${skill.criticality_score <= 40 ? "bg-red-400" : skill.criticality_score <= 70 ? "bg-amber-400" : "bg-green-400"}`} style={{ width: `${Math.max(6, skill.criticality_score)}%` }} />
                    </div>
                  </td>
                  <td className={`px-5 py-4 ${skill.loads_30d === 0 ? "text-[color:var(--text-tertiary)]" : "text-[color:var(--text-primary)]"}`}>{skill.loads_30d}</td>
                  <td className="px-5 py-4">
                    {skill.alert === "healthy" ? (
                      <span className="text-green-400">• Healthy</span>
                    ) : skill.alert === "stale_but_active" ? (
                      <span className="text-amber-400">⚠ Stale &amp; active</span>
                    ) : (
                      <span className="text-red-400">✕ Dead skill</span>
                    )}
                  </td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{relativeTime(skill.last_loaded_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : !hasSkills ? (
          <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
            <Zap className="h-10 w-10 text-[color:var(--text-tertiary)]" />
            <h2 className="mt-4 text-[18px] font-semibold text-[color:var(--text-primary)]">No agent usage recorded yet</h2>
            <p className="mt-2 max-w-xl text-[14px] text-[color:var(--text-secondary)]">
              Once agents start loading your skills via Claude Code, Codex, or Cursor, their activity will appear here.
            </p>
            <Link
              className="mt-5 inline-flex h-10 items-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]"
              href="/dashboard/repos"
            >
              Go to Repos
            </Link>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
            <BookOpen className="h-9 w-9 text-[color:var(--text-tertiary)]" />
            <h2 className="mt-4 text-[18px] font-semibold text-[color:var(--text-primary)]">No skills match your filters</h2>
            <p className="mt-2 text-[14px] text-[color:var(--text-secondary)]">Try a different search or clear the current filters.</p>
            <button
              className="mt-5 inline-flex h-10 items-center rounded-md border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-primary)] transition-colors hover:bg-[color:var(--bg-elevated)]"
              onClick={() => {
                setQuery("");
                setAlert("all");
              }}
              type="button"
            >
              Clear filters
            </button>
          </div>
        )}
      </section>
    </div>
  );
}
