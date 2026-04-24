import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft, ClipboardCopy, GitBranch } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { SectionFallback } from "@/components/section-fallback";
import {
  API_URL,
  getRepoDependencies,
  getRepo,
  getRepoScoreForecast,
  getRepoScoreHistory,
  getRepoSkillSources,
  getRepoSkills,
  type Dependency,
  type DependencyReport,
  type Repo,
  type RepoSkillSources,
  type ScoreForecast,
  type Score,
  type ScoreHistoryPoint,
  type SkillCategory,
  type Skill,
} from "../../../../lib/data";
import { AnalyseNowButton } from "./analyse-now-button";
import { CopyTextButton } from "../repos-browser";
import { RepoSkillsPanel } from "./skill-source-filter";

export const dynamic = "force-dynamic";

// RepoSkillsPanel renders href={`/dashboard/repos/${repoId}/skills/${skill.id}`}.

type PageProps = {
  params: Promise<{ repoId: string }>;
};

type RepoDetail = Repo & {
  default_branch?: string;
  installation_id?: number | null;
};

type RepoSkill = Skill & {
  last_updated_at?: string | null;
};

function ScoreRing({ score }: { score: number | null | undefined }) {
  const value = Math.max(0, Math.min(100, score ?? 0));
  return (
    <div className="flex items-center gap-4">
      <div
        aria-label={`Overall score ${value} out of 100`}
        className="grid h-24 w-24 place-items-center rounded-full"
        style={{ background: `conic-gradient(#C9973A ${value * 3.6}deg, rgba(255,255,255,0.08) 0deg)` }}
      >
        <div className="grid h-[74px] w-[74px] place-items-center rounded-full bg-[color:var(--bg-base)]">
          <div className="text-center">
            <div className="text-[24px] font-bold leading-none text-[color:var(--text-primary)]">{value}</div>
            <div className="mt-1 text-[11px] text-[color:var(--text-tertiary)]">/100</div>
          </div>
        </div>
      </div>
      <div>
        <p className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Overall score</p>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Latest completed analysis</p>
      </div>
    </div>
  );
}

function SubscoreCard({ label, value }: { label: string; value: number | null | undefined }) {
  const score = Math.max(0, Math.min(25, value ?? 0));
  return (
    <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-3 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
      <div className="text-[28px] font-bold leading-none text-[color:var(--text-primary)]">
        {typeof value === "number" ? value : "—"}
        <span className="ml-1 text-[14px] font-medium text-[color:var(--text-tertiary)]">/25</span>
      </div>
      <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/10">
        <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${(score / 25) * 100}%` }} />
      </div>
    </article>
  );
}

function ScoreHistoryChart({ points }: { points: ScoreHistoryPoint[] }) {
  const width = 640;
  const height = 180;
  const padding = 24;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;

  const coordinates = points.map((point, index) => {
    const x = padding + (points.length <= 1 ? chartWidth : (index / (points.length - 1)) * chartWidth);
    const y = padding + chartHeight - (Math.max(0, Math.min(100, point.score_total)) / 100) * chartHeight;
    return `${x},${y}`;
  });

  return (
    <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Score history</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Last {points.length} completed run{points.length === 1 ? "" : "s"}</p>
        </div>
      </div>
      {points.length > 0 ? (
        <svg className="h-[180px] w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
          <title>Score history chart</title>
          <line stroke="rgba(255,255,255,0.08)" x1={padding} x2={width - padding} y1={padding} y2={padding} />
          <line stroke="rgba(255,255,255,0.08)" x1={padding} x2={width - padding} y1={height / 2} y2={height / 2} />
          <line stroke="rgba(255,255,255,0.08)" x1={padding} x2={width - padding} y1={height - padding} y2={height - padding} />
          <polyline fill="none" points={coordinates.join(" ")} stroke="#C9973A" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
          {coordinates.map((coordinate, index) => {
            const [x, y] = coordinate.split(",");
            return <circle cx={x} cy={y} fill="#C9973A" key={`${points[index].date}-${index}`} r="4" />;
          })}
        </svg>
      ) : (
        <div className="grid h-[180px] place-items-center rounded-lg border border-dashed border-[color:var(--bg-border)] text-[13px] text-[color:var(--text-secondary)]">
          No score history yet.
        </div>
      )}
    </section>
  );
}

function scoreTone(value: number): string {
  if (value < 40) return "bg-red-900/30 text-red-300";
  if (value < 70) return "bg-amber-900/30 text-amber-300";
  return "bg-green-900/30 text-green-300";
}

function ForecastCard({ label, value, delta }: { label: string; value: number; delta?: number }) {
  return (
    <article className="rounded-xl border border-[color:var(--bg-border)] bg-black/10 p-4">
      <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-3 flex items-center gap-3">
        <span className={`rounded-full px-2.5 py-1 text-[14px] font-semibold ${scoreTone(value)}`}>{value}/100</span>
        {typeof delta === "number" ? (
          <span className={`text-[13px] font-semibold ${delta > 0 ? "text-green-300" : delta < 0 ? "text-red-300" : "text-[color:var(--text-tertiary)]"}`}>
            {delta > 0 ? `+${delta}` : `${delta}`}
          </span>
        ) : null}
      </div>
    </article>
  );
}

function ForecastSection({ forecast }: { forecast: ScoreForecast | null }) {
  if (!forecast?.has_forecast || forecast.current_score === null || forecast.forecast_30d === null || forecast.forecast_90d === null) {
    return null;
  }

  const directionCopy =
    forecast.trend === "improving" ? "↑ Improving" : forecast.trend === "declining" ? "↓ Declining" : "→ Stable";
  const directionTone =
    forecast.trend === "improving" ? "bg-green-900/30 text-green-300" : forecast.trend === "declining" ? "bg-red-900/30 text-red-300" : "bg-white/10 text-[color:var(--text-secondary)]";
  const delta30 = forecast.forecast_30d - forecast.current_score;
  const delta90 = forecast.forecast_90d - forecast.current_score;

  return (
    <section className="mb-8 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Score Forecast</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">
            Based on {forecast.data_points} analysis runs. Re-analyse regularly to improve forecast accuracy.
          </p>
        </div>
        <span className={`inline-flex rounded-full px-3 py-1 text-[12px] font-semibold ${directionTone}`}>{directionCopy}</span>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <ForecastCard label="Current" value={forecast.current_score} />
        <ForecastCard delta={delta30} label="In 30 days" value={forecast.forecast_30d} />
        <ForecastCard delta={delta90} label="In 90 days" value={forecast.forecast_90d} />
      </div>
    </section>
  );
}

function riskBadgeClass(riskLevel: Dependency["risk_level"]): string {
  if (riskLevel === "high") return "bg-red-900/40 text-red-300";
  if (riskLevel === "medium") return "bg-amber-900/30 text-amber-300";
  if (riskLevel === "low") return "bg-blue-900/30 text-blue-300";
  return "bg-green-900/25 text-green-300";
}

function RiskBadge({ riskLevel }: { riskLevel: Dependency["risk_level"] }) {
  return <span className={`inline-flex rounded-full px-2 py-0.5 text-[12px] font-semibold ${riskBadgeClass(riskLevel)}`}>{riskLevel}</span>;
}

function DependencyMetric({ label, value, suffix = "" }: { label: string; value: number; suffix?: string }) {
  return (
    <article className="rounded-xl border border-[color:var(--bg-border)] bg-black/10 p-4">
      <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-2 text-[24px] font-bold text-[color:var(--text-primary)]">
        {value}
        {suffix ? <span className="ml-1 text-[13px] font-medium text-[color:var(--text-tertiary)]">{suffix}</span> : null}
      </div>
    </article>
  );
}

function DependenciesSection({ report }: { report: DependencyReport | null }) {
  const dependencies = [
    ...(report?.high_risk ?? []),
    ...(report?.medium_risk ?? []),
    ...(report?.healthy ?? []),
  ];

  return (
    <section className="mb-8 overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
        <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Dependencies</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Dependency risk summary for the latest analysis run</p>
      </div>
      <div className="grid gap-3 border-b border-[color:var(--bg-border)] p-5 md:grid-cols-4">
        <DependencyMetric label="Risk score" suffix="/100" value={report?.risk_score ?? 0} />
        <DependencyMetric label="High risk" value={report?.high_risk.length ?? 0} />
        <DependencyMetric label="Medium risk" value={report?.medium_risk.length ?? 0} />
        <DependencyMetric label="Total deps" value={report?.total_count ?? 0} />
      </div>
      {report && report.high_risk.length > 0 ? (
        <div className="border-b border-[color:var(--bg-border)] p-5">
          <h3 className="mb-3 text-[13px] font-semibold uppercase tracking-wide text-red-300">High risk CVEs</h3>
          <div className="space-y-3">
            {report.high_risk.map((dependency) => (
              <div className="rounded-lg border border-red-900/40 bg-red-950/20 p-4" key={dependency.id}>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-[color:var(--text-primary)]">{dependency.name}</span>
                  <RiskBadge riskLevel={dependency.risk_level} />
                  <span className="font-mono text-[12px] text-[color:var(--text-tertiary)]">{dependency.ecosystem}</span>
                </div>
                <p className="mt-2 text-[13px] text-[color:var(--text-secondary)]">CVEs: {dependency.cves.join(", ") || "OSV advisory found"}</p>
                <p className="mt-2 text-[12px] text-[color:var(--text-secondary)]">
                  Found in your {dependency.ecosystem} dependencies with version constraint {dependency.version || "unknown"}. This version range includes the reported vulnerability.
                </p>
                {dependency.upgrade_command ? (
                  <div className="mt-3 flex items-start justify-between gap-2">
                    <code className="block rounded-md bg-black/30 px-3 py-2 font-mono text-[12px] text-[color:var(--accent-primary)]">{dependency.upgrade_command}</code>
                    <CopyTextButton label="" text={dependency.upgrade_command} title="Copy to clipboard">
                      <ClipboardCopy className="h-3.5 w-3.5 text-[color:var(--text-tertiary)]" />
                    </CopyTextButton>
                  </div>
                ) : null}
              </div>
            ))}
          </div>
          <p className="mt-4 text-[12px] italic text-[color:var(--text-tertiary)]">
            CVEs are matched against declared dependency version ranges, not the exact installed version. Verify with your package manager.
          </p>
        </div>
      ) : null}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] border-collapse text-left text-[13px]">
          <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
            <tr className="border-b border-[color:var(--bg-border)]">
              <th className="px-5 py-3 font-semibold">Package</th>
              <th className="px-5 py-3 font-semibold">Ecosystem</th>
              <th className="px-5 py-3 font-semibold">Version</th>
              <th className="px-5 py-3 font-semibold">Risk</th>
              <th className="px-5 py-3 font-semibold">CVEs</th>
            </tr>
          </thead>
          <tbody>
            {dependencies.length > 0 ? (
              dependencies.map((dependency) => (
                <tr className="border-b border-[color:var(--bg-elevated)] last:border-b-0" key={dependency.id}>
                  <td className="px-5 py-4 font-medium text-[color:var(--text-primary)]">{dependency.name}</td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{dependency.ecosystem}</td>
                  <td className="px-5 py-4 font-mono text-[12px] text-[color:var(--text-tertiary)]">{dependency.version || "—"}</td>
                  <td className="px-5 py-4"><RiskBadge riskLevel={dependency.risk_level} /></td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{dependency.cves.join(", ") || "—"}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-5 py-8 text-center text-[color:var(--text-secondary)]" colSpan={5}>No supported dependency manifests were found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ZeroScoreBanner({ score }: { score: Score | null }) {
  if (score && score.total > 0) return null;

  return (
    <section className="mb-8 rounded-xl border border-amber-500/30 bg-amber-900/20 px-5 py-4 text-[13px] text-amber-200">
      Analysis is still running or no skills have been generated yet. Click &quot;Analyse again&quot; to trigger a fresh analysis.
    </section>
  );
}

function ScoreInsight({ score, coverage }: { score: Score | null; coverage: RepoSkillSources | null }) {
  const subscoreEntries: Array<{ label: string; value: number }> = [
    { label: "Groundedness", value: score?.groundedness ?? 0 },
    { label: "Coverage", value: score?.coverage ?? 0 },
    { label: "Freshness", value: score?.freshness ?? 0 },
    { label: "Structure", value: score?.structure ?? 0 },
  ];
  const weakest = [...subscoreEntries].sort((left, right) => left.value - right.value)[0];
  const coveredCategories = coverage ? Object.values(coverage.coverage_map).filter((item) => item.covered).length : 0;
  const missingCount = Math.max(0, 8 - coveredCategories);
  const missingCategories = coverage
    ? Object.entries(coverage.coverage_map)
        .filter(([, item]) => !item.covered)
        .map(([category]) => category.replaceAll("_", " "))
    : [];

  let text = "Skilgen found very few verified patterns to build skills from.";
  if (score) {
    if (score.total < 30) {
      text =
        "Skilgen found very few verified patterns to build skills from. The most common reasons: the repo has no SKILL.md files yet, the codebase is small or newly connected, or the analysis run is still in progress.";
    } else if (score.total < 60) {
      text = `Skills exist but coverage is narrow. ${missingCount} of 8 knowledge areas have no skill yet. Running 'Analyse again' adds more domains as Skilgen reads more of the codebase.${missingCategories.length > 0 ? ` Missing: ${missingCategories.join(", ")}.` : ""}`;
    } else if (score.total < 80) {
      text = `Good foundation. Score is held back by ${weakest.label} (${weakest.value}/25). See the subscore breakdown below.`;
    } else {
      text = "Strong skill coverage. Focus on keeping skills fresh with regular re-analysis as the codebase evolves.";
    }
  }

  return (
    <section className="mb-8 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-5 py-4 text-[13px] leading-relaxed text-[color:var(--text-secondary)]">
      {text}
    </section>
  );
}

const categoryMeta: Record<SkillCategory, { label: string; icon: string }> = {
  codebase_architecture: { label: "Codebase Architecture", icon: "🏗️" },
  code_style: { label: "Code Style", icon: "🎨" },
  testing_conventions: { label: "Testing", icon: "🧪" },
  internal_tools: { label: "Internal Tools", icon: "🔧" },
  security_compliance: { label: "Security", icon: "🔒" },
  design_system: { label: "Design System", icon: "🎯" },
  data_schema: { label: "Data Schema", icon: "🗄️" },
  operational_knowledge: { label: "Operational Knowledge", icon: "📋" },
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

function titleizeCategory(value: string | null | undefined): string {
  if (!value) return "Unknown";
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function scoreTextClass(score: number): string {
  if (score <= 40) return "text-red-400";
  if (score <= 70) return "text-amber-400";
  return "text-green-400";
}

function dimensionTextClass(score: number): string {
  if (score <= 6) return "text-red-300";
  if (score <= 12) return "text-amber-300";
  return "text-[color:var(--text-secondary)]";
}

function QualitySnapshotCard({ skills }: { skills: RepoSkill[] }) {
  if (skills.length === 0) return null;

  const averageScore = Math.round(skills.reduce((sum, skill) => sum + skill.score.total, 0) / skills.length);
  const highQualityCount = skills.filter((skill) => skill.score.total > 70).length;
  const needsWorkCount = skills.filter((skill) => skill.score.total <= 40).length;

  return (
    <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-4 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Quality snapshot</div>
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <span className="text-[13px] text-[color:var(--text-secondary)]">Avg skill quality</span>
          <span className={`text-[15px] font-semibold ${scoreTextClass(averageScore)}`}>{averageScore}/100</span>
        </div>
        <div className="flex items-center justify-between gap-3">
          <span className="text-[13px] text-[color:var(--text-secondary)]">High quality</span>
          <span className="text-[15px] font-semibold text-green-300">{highQualityCount}</span>
        </div>
        <div className="flex items-center justify-between gap-3">
          <span className="text-[13px] text-[color:var(--text-secondary)]">Needs work</span>
          <span className="text-[15px] font-semibold text-red-300">{needsWorkCount}</span>
        </div>
      </div>
      <div className="mt-4">
        <Link className="text-[12px] font-semibold text-[color:var(--accent-primary)] hover:text-[color:var(--accent-bright)]" href="#skill-quality">
          View quality table ↓
        </Link>
      </div>
    </article>
  );
}

function qualityTierDotClass(score: number): string {
  if (score <= 40) return "bg-red-400";
  if (score <= 70) return "bg-amber-400";
  return "bg-green-400";
}

function SkillQualityTable({ skills }: { skills: RepoSkill[] }) {
  const sortedSkills = [...skills].sort((left, right) => left.score.total - right.score.total);
  const allSkillsAboveThreshold = skills.length > 0 && skills.every((skill) => skill.score.total > 70);

  if (skills.length === 0) return null;

  return (
    <section className="mt-8" id="skill-quality">
      <div className="mb-4">
        <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Skill Quality</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Sorted by score — click any row to edit.</p>
      </div>
      {allSkillsAboveThreshold ? (
        <div className="rounded-xl border border-green-500/20 bg-green-900/20 px-5 py-4 text-[13px] font-medium text-green-300">
          🟢 All skills are high quality (score &gt; 70). Keep them fresh by re-analysing after major changes.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <table className="w-full min-w-[900px] border-collapse text-left text-[13px]">
            <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
              <tr>
                <th className="border-b border-[color:var(--bg-border)] px-5 py-3 font-semibold">Domain</th>
                <th className="border-b border-[color:var(--bg-border)] px-5 py-3 font-semibold">Category</th>
                <th className="border-b border-[color:var(--bg-border)] px-5 py-3 font-semibold">Score</th>
                <th className="border-b border-[color:var(--bg-border)] px-5 py-3 font-semibold">Groundedness</th>
                <th className="border-b border-[color:var(--bg-border)] px-5 py-3 font-semibold">Coverage</th>
                <th className="border-b border-[color:var(--bg-border)] px-5 py-3 font-semibold">Freshness</th>
                <th className="border-b border-[color:var(--bg-border)] px-5 py-3 font-semibold">Structure</th>
                <th className="border-b border-[color:var(--bg-border)] px-5 py-3 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedSkills.map((skill) => (
                <tr className="border-b border-[color:var(--bg-elevated)] transition-colors last:border-b-0 hover:bg-white/5" key={skill.id}>
                  <td className="px-5 py-4">
                    <Link className="inline-flex items-center font-medium text-[color:var(--text-primary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${skill.repo_id}/skills/${skill.id}`}>
                      <span className={`mr-2 inline-block h-2 w-2 rounded-full ${qualityTierDotClass(skill.score.total)}`} />
                      {skill.domain}
                    </Link>
                  </td>
                  <td className="px-5 py-4">
                    <span className={`rounded-full px-2 py-0.5 text-[12px] font-semibold ${categoryClasses[skill.skill_category ?? ""] ?? "bg-white/10 text-[color:var(--text-secondary)]"}`}>
                      {titleizeCategory(skill.skill_category)}
                    </span>
                  </td>
                  <td className={`px-5 py-4 text-[12px] font-semibold ${scoreTextClass(skill.score.total)}`}>{skill.score.total}/100</td>
                  <td className={`px-5 py-4 text-[12px] ${dimensionTextClass(skill.score.groundedness)}`}>{skill.score.groundedness}</td>
                  <td className={`px-5 py-4 text-[12px] ${dimensionTextClass(skill.score.coverage)}`}>{skill.score.coverage}</td>
                  <td className={`px-5 py-4 text-[12px] ${dimensionTextClass(skill.score.freshness)}`}>{skill.score.freshness}</td>
                  <td className={`px-5 py-4 text-[12px] ${dimensionTextClass(skill.score.structure)}`}>{skill.score.structure}</td>
                  <td className="px-5 py-4">
                    <Link className="inline-flex rounded-full border border-[color:var(--bg-border)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${skill.repo_id}/skills/${skill.id}`}>
                      Edit →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function CoverageMap({ coverage }: { coverage: RepoSkillSources | null }) {
  if (!coverage) {
    return (
      <section className="mb-8 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 text-[color:var(--text-secondary)]">
        Coverage data unavailable.
      </section>
    );
  }
  return (
    <section className="mb-8 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-5 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Knowledge Coverage</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Knowledge categories generated for this repository</p>
        </div>
        <span className="text-[18px] font-bold text-[color:var(--accent-primary)]">{coverage.coverage_score}%</span>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {(Object.keys(categoryMeta) as SkillCategory[]).map((category) => {
          const item = coverage.coverage_map[category];
          const meta = categoryMeta[category];
          return (
            <article className="rounded-lg border border-[color:var(--bg-border)] bg-black/10 p-4" key={category}>
              <div className="mb-3 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span aria-hidden="true">{meta.icon}</span>
                  <h3 className="text-[13px] font-semibold text-[color:var(--text-primary)]">{meta.label}</h3>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${item?.covered ? "bg-green-900/30 text-green-300" : "bg-red-900/30 text-red-300"}`}>
                  {item?.covered ? "Covered" : "Missing"}
                </span>
              </div>
              <p className="text-[12px] text-[color:var(--text-secondary)]">
                {item?.covered ? `${item.skill_count} skill${item.skill_count === 1 ? "" : "s"} · ${item.avg_score}/100 avg` : "0 skills · Add source to generate"}
              </p>
            </article>
          );
        })}
      </div>
    </section>
  );
}

export default async function RepoDetailPage({ params }: PageProps) {
  const { repoId } = await params;
  let accessToken = "";

  let repo: RepoDetail | null = null;
  let skills: RepoSkill[] = [];
  let scoreHistory: ScoreHistoryPoint[] = [];
  let scoreForecast: ScoreForecast | null = null;
  let dependencies: DependencyReport | null = null;
  let skillSources: RepoSkillSources | null = null;
  let repoLoadFailed = false;

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Repo detail auth unavailable:", error);
  }

  try {
    const [repoPayload, skillsPayload, historyPayload, forecastPayload, dependencyPayload, sourcePayload] = await Promise.all([
      getRepo(accessToken, repoId),
      getRepoSkills(accessToken, repoId),
      getRepoScoreHistory(accessToken, repoId),
      getRepoScoreForecast(accessToken, repoId),
      getRepoDependencies(accessToken, repoId),
      getRepoSkillSources(accessToken, repoId),
    ]);
    repo = repoPayload as RepoDetail | null;
    skills = ((skillsPayload ?? []) as RepoSkill[]) ?? [];
    scoreHistory = historyPayload ?? [];
    scoreForecast = forecastPayload;
    dependencies = dependencyPayload;
    skillSources = sourcePayload;
  } catch (error) {
    repoLoadFailed = true;
    console.error("Failed to fetch repo detail:", error);
  }

  if (!repo) {
    return (
      <div>
        <Link className="mb-6 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href="/dashboard/repos">
          <ArrowLeft className="h-4 w-4" />
          Back to repos
        </Link>
        {repoLoadFailed ? <SectionFallback section="repository" /> : (
          <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
            Repository not found.
          </section>
        )}
      </div>
    );
  }

  const score: Score | null = repo.score;
  const languageLabel = repo.language ? repo.language : skills.length > 0 ? "Multi-language" : "Unknown";
  const languageTone = repo.language
    ? "border-[color:var(--bg-border)] text-[color:var(--text-secondary)]"
    : skills.length > 0
      ? "border-blue-500/30 bg-blue-900/20 text-blue-300"
      : "border-[color:var(--bg-border)] text-[color:var(--text-tertiary)]";

  return (
    <div>
      <div className="mb-6 flex items-center gap-2 text-[12px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">
          Overview
        </Link>
        <span>/</span>
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard/repos">
          Repos
        </Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">{repo.name}</span>
      </div>

      <SectionErrorBoundary section="repository header">
        <section className="mb-8 flex flex-col gap-6 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <Link className="mb-5 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href="/dashboard/repos">
              <ArrowLeft className="h-4 w-4" />
              Back to repos
            </Link>
            <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">{repo.name}</h1>
            <p className="mt-2 font-mono text-sm text-[color:var(--text-secondary)]">{repo.full_name}</p>
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <span className={`inline-flex rounded-full border px-2.5 py-1 text-[12px] ${languageTone}`}>
                {languageLabel}
              </span>
              <span className="inline-flex items-center rounded-full border border-[color:var(--bg-border)] px-2.5 py-1 text-[12px] text-[color:var(--text-secondary)]">
                <GitBranch className="mr-1 h-3 w-3" />
                {repo.default_branch || "main"}
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-5 md:flex-row md:items-center">
            <AnalyseNowButton accessToken={accessToken} apiUrl={API_URL} lastAnalysedAt={repo.last_analysed_at} repoId={repoId} />
            <ScoreRing score={score?.total} />
          </div>
        </section>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="repository subscores">
        <ZeroScoreBanner score={score} />
        <ScoreInsight coverage={skillSources} score={score} />
        <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <SubscoreCard label="Groundedness" value={score?.groundedness} />
          <SubscoreCard label="Coverage" value={score?.coverage} />
          <SubscoreCard label="Freshness" value={score?.freshness} />
          <SubscoreCard label="Structure" value={score?.structure} />
          <QualitySnapshotCard skills={skills} />
        </div>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="score history">
        <div className="mb-8">
          <ScoreHistoryChart points={scoreHistory} />
        </div>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="score forecast">
        <ForecastSection forecast={scoreForecast} />
      </SectionErrorBoundary>

      <SectionErrorBoundary section="dependencies">
        <DependenciesSection report={dependencies} />
      </SectionErrorBoundary>

      <SectionErrorBoundary section="coverage map">
        <CoverageMap coverage={skillSources} />
      </SectionErrorBoundary>

      <SectionErrorBoundary section="skills">
        {skills.length > 0 ? (
          <>
            <RepoSkillsPanel repoId={repoId} skills={skills} />
            <SkillQualityTable skills={skills} />
          </>
        ) : (
          <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
            No skills found for this repository.
          </section>
        )}
      </SectionErrorBoundary>
    </div>
  );
}
