import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft, GitBranch } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { SectionFallback } from "@/components/section-fallback";
import {
  API_URL,
  getRepoDependencies,
  getRepo,
  getRepoScoreHistory,
  getRepoSkillSources,
  getRepoSkills,
  type Dependency,
  type DependencyReport,
  type Repo,
  type RepoSkillSources,
  type Score,
  type ScoreHistoryPoint,
  type SkillCategory,
  type Skill,
} from "../../../../lib/data";
import { AnalyseNowButton } from "./analyse-now-button";
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
                {dependency.upgrade_command ? (
                  <code className="mt-3 block rounded-md bg-black/30 px-3 py-2 font-mono text-[12px] text-[color:var(--accent-primary)]">{dependency.upgrade_command}</code>
                ) : null}
              </div>
            ))}
          </div>
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
    const [repoPayload, skillsPayload, historyPayload, dependencyPayload, sourcePayload] = await Promise.all([
      getRepo(accessToken, repoId),
      getRepoSkills(accessToken, repoId),
      getRepoScoreHistory(accessToken, repoId),
      getRepoDependencies(accessToken, repoId),
      getRepoSkillSources(accessToken, repoId),
    ]);
    repo = repoPayload as RepoDetail | null;
    skills = ((skillsPayload ?? []) as RepoSkill[]) ?? [];
    scoreHistory = historyPayload ?? [];
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
              <span className="inline-flex rounded-full border border-[color:var(--bg-border)] px-2.5 py-1 text-[12px] text-[color:var(--text-secondary)]">
                {repo.language || "—"}
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
        <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <SubscoreCard label="Groundedness" value={score?.groundedness} />
          <SubscoreCard label="Coverage" value={score?.coverage} />
          <SubscoreCard label="Freshness" value={score?.freshness} />
          <SubscoreCard label="Structure" value={score?.structure} />
        </div>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="score history">
        <div className="mb-8">
          <ScoreHistoryChart points={scoreHistory} />
        </div>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="dependencies">
        <DependenciesSection report={dependencies} />
      </SectionErrorBoundary>

      <SectionErrorBoundary section="coverage map">
        <CoverageMap coverage={skillSources} />
      </SectionErrorBoundary>

      <SectionErrorBoundary section="skills">
        {skills.length > 0 ? (
          <RepoSkillsPanel repoId={repoId} skills={skills} />
        ) : (
          <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
            No skills found for this repository.
          </section>
        )}
      </SectionErrorBoundary>
    </div>
  );
}
