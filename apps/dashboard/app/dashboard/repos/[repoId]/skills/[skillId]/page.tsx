import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft, FileText } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { SectionFallback } from "@/components/section-fallback";
import { SkillDetailViewer } from "@/components/skill-detail-viewer";
import { SkillViewTracker } from "@/components/skill-view-tracker";
import { getRepo, getRepoSkillUsageStats, getSkill, getSkillVersions, type Repo, type Score, type Skill, type SkillUsageStats, type SkillVersionSummary } from "../../../../../../lib/data";
import { PublishSkillButton } from "./publish-skill-button";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ repoId: string; skillId: string }>;
};

/** Return the score badge color class for the skill total. */
function scoreBadgeClass(score: number) {
  if (score <= 40) return "bg-red-900/50 text-red-400";
  if (score <= 70) return "bg-amber-900/50 text-amber-400";
  return "bg-green-900/50 text-green-400";
}

/** Render the total score badge for a skill. */
function ScoreBadge({ score }: { score: Score }) {
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-[12px] font-semibold ${scoreBadgeClass(score.total)}`}>{score.total}/100</span>;
}

/** Render the freshness state badge for a skill. */
function StaleBadge({ isStale }: { isStale: boolean }) {
  return (
    <span
      className={
        isStale
          ? "inline-flex rounded-full bg-red-900/40 px-2.5 py-1 text-[12px] font-semibold text-red-300"
          : "inline-flex rounded-full bg-[rgb(var(--accent-green-rgb)/0.14)] px-2.5 py-1 text-[12px] font-semibold text-[color:var(--accent-green)]"
      }
    >
      {isStale ? "Stale" : "Fresh"}
    </span>
  );
}

/** Render the latest skill version badge when version metadata exists. */
function VersionBadge({ versionNumber }: { versionNumber: number | null }) {
  if (!versionNumber) return null;
  return <span className="inline-flex rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-2.5 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">v{versionNumber}</span>;
}

function sourceDescription(sourceType: string | null | undefined): string {
  const labels: Record<string, string> = {
    code: "Generated from codebase analysis",
    openapi: "Generated from OpenAPI spec",
    graphql: "Generated from GraphQL schema",
    postman: "Generated from Postman collection",
    terraform: "Generated from Terraform modules",
    kubernetes: "Generated from Kubernetes manifests",
    helm: "Generated from Helm charts",
    dbt: "Generated from dbt project",
    sql_schema: "Generated from SQL schema",
    kafka: "Generated from Kafka schemas",
    sarif: "Generated from SARIF findings",
    sbom: "Generated from SBOM inventory",
    security_policy: "Generated from security policy",
    runbook: "Generated from runbooks",
    confluence: "Generated from Confluence export",
    notion: "Generated from Notion export",
    incident: "Generated from incident reports",
    pagerduty: "Generated from PagerDuty export",
  };
  const key = sourceType ?? "code";
  return labels[key] ?? `Generated from ${key}`;
}

/** Render one skill score dimension. */
function SubscoreCard({ label, value }: { label: string; value: number }) {
  return (
    <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-3 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
      <div className="text-[28px] font-bold leading-none text-[color:var(--text-primary)]">
        {value}
        <span className="ml-1 text-[14px] font-medium text-[color:var(--text-tertiary)]">/25</span>
      </div>
    </article>
  );
}

function ScoreRing({ score }: { score: number }) {
  const clamped = Math.max(0, Math.min(100, score));
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;
  const tone = clamped <= 40 ? "text-red-400" : clamped <= 70 ? "text-amber-400" : "text-[color:var(--accent-green)]";

  return (
    <div className="relative flex h-28 w-28 items-center justify-center">
      <svg className="-rotate-90 h-28 w-28" viewBox="0 0 120 120">
        <circle cx="60" cy="60" fill="none" r={radius} stroke="rgba(255,255,255,0.08)" strokeWidth="10" />
        <circle
          cx="60"
          cy="60"
          fill="none"
          r={radius}
          stroke="currentColor"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          strokeWidth="10"
          className={tone}
        />
      </svg>
      <div className="absolute text-center">
        <div className="text-2xl font-semibold text-[color:var(--text-primary)]">{clamped}</div>
        <div className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">Score</div>
      </div>
    </div>
  );
}

function formatRelativeTime(value: string | null): string {
  if (!value) return "Never";
  const date = new Date(value);
  const timestamp = date.getTime();
  if (Number.isNaN(timestamp)) return "Unknown";
  const diffMinutes = Math.max(0, Math.floor((Date.now() - timestamp) / 60000));
  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(date);
}

function categoryLabel(category: string | null): string | null {
  if (!category) return null;
  return category
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function UsageAlertBadge({ alert }: { alert: SkillUsageStats["alert"] }) {
  if (alert === "stale_but_active") {
    return (
      <span className="inline-flex items-center gap-2 rounded-full bg-red-500/12 px-3 py-1 text-[12px] font-semibold text-red-300">
        <span className="h-2 w-2 animate-pulse rounded-full bg-red-400" />
        Stale but active
      </span>
    );
  }
  if (alert === "dead_skill") {
    return (
      <span className="inline-flex items-center gap-2 rounded-full bg-white/8 px-3 py-1 text-[12px] font-semibold text-[color:var(--text-secondary)]">
        <span>💤</span>
        Never loaded
      </span>
    );
  }
  return null;
}

function UsageSparkline({ points }: { points: SkillUsageStats["daily_loads"] }) {
  const width = 420;
  const height = 92;
  const maxLoads = Math.max(1, ...points.map((point) => point.loads));
  const coordinates = points.map((point, index) => {
    const x = points.length <= 1 ? width / 2 : (index / (points.length - 1)) * width;
    const y = height - (point.loads / maxLoads) * (height - 12) - 6;
    return `${x},${y}`;
  });

  return (
    <svg aria-label="30-day skill activity" className="h-[92px] w-full" preserveAspectRatio="none" viewBox={`0 0 ${width} ${height}`}>
      <polyline fill="none" points={coordinates.join(" ")} stroke="#C9973A" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
    </svg>
  );
}

function RuntimeBreakdown({ runtimes }: { runtimes: SkillUsageStats["agent_runtimes"] }) {
  const entries = Object.entries(runtimes).sort((left, right) => right[1] - left[1]);
  const total = entries.reduce((sum, [, count]) => sum + count, 0);
  const labels: Record<string, string> = {
    claude_code: "Claude Code",
    cursor: "Cursor",
    codex: "Codex",
    copilot: "Copilot",
    unknown: "Other",
  };

  if (total === 0 || entries.length === 0) {
    return <div className="rounded-2xl border border-dashed border-[color:var(--bg-border)] p-4 text-[13px] text-[color:var(--text-secondary)]">No runtime activity recorded yet.</div>;
  }

  return (
    <div className="space-y-3">
      {entries.map(([runtime, count]) => {
        const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
        return (
          <div className="grid grid-cols-[110px_minmax(0,1fr)_72px] items-center gap-3 text-[13px]" key={runtime}>
            <span className="font-medium text-[color:var(--text-primary)]">{labels[runtime] ?? runtime}</span>
            <div className="h-2.5 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-[#C9973A]" style={{ width: `${Math.max(6, percentage)}%` }} />
            </div>
            <span className="text-right text-[color:var(--text-secondary)]">
              {count} ({percentage}%)
            </span>
          </div>
        );
      })}
    </div>
  );
}

function UsageIntelligencePanel({ usage }: { usage: SkillUsageStats | null }) {
  if (!usage) {
    return (
      <section className="mb-8 rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <div className="mb-2 text-[18px] font-semibold text-[color:var(--text-primary)]">Usage Intelligence</div>
        <p className="text-[14px] text-[color:var(--text-secondary)]">No usage data recorded yet.</p>
      </section>
    );
  }

  return (
    <section className="mb-8 rounded-[24px] border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-6">
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Usage Intelligence</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Live activity on this skill across the last 30 days.</p>
        </div>
        <UsageAlertBadge alert={usage.alert} />
      </div>

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <article className="rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Criticality Score</div>
          <div className="mt-3 text-[32px] font-semibold text-[color:var(--text-primary)]">{usage.criticality_score}/100</div>
        </article>
        <article className="rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Loads (30d)</div>
          <div className="mt-3 text-[32px] font-semibold text-[color:var(--text-primary)]">{usage.loads_30d}</div>
        </article>
        <article className="rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Last Loaded</div>
          <div className="mt-3 text-[32px] font-semibold text-[color:var(--text-primary)]">{formatRelativeTime(usage.last_loaded_at)}</div>
        </article>
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(280px,0.9fr)]">
        <div className="rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-5">
          <h3 className="text-[14px] font-semibold text-[color:var(--text-primary)]">30-day load activity</h3>
          <p className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">Daily load counts with missing days filled as zero.</p>
          <div className="mt-4">
            <UsageSparkline points={usage.daily_loads} />
          </div>
        </div>
        <div className="rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-5">
          <h3 className="text-[14px] font-semibold text-[color:var(--text-primary)]">Runtime breakdown</h3>
          <p className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">Which coding agents are loading this skill.</p>
          <div className="mt-4">
            <RuntimeBreakdown runtimes={usage.agent_runtimes} />
          </div>
        </div>
      </div>
    </section>
  );
}

export default async function SkillDetailPage({ params }: PageProps) {
  const { repoId, skillId } = await params;
  let accessToken = "";

  let skill: Skill | null = null;
  let repo: Repo | null = null;
  let versions: SkillVersionSummary[] = [];
  let usageStats: SkillUsageStats | null = null;
  let skillLoadFailed = false;

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session.accessToken || "";
  } catch (error) {
    console.error("Skill detail auth unavailable:", error);
  }

  try {
    const [repoPayload, skillPayload, versionsPayload] = await Promise.all([
      getRepo(accessToken, repoId),
      getSkill(accessToken, skillId),
      getSkillVersions(accessToken, skillId),
    ]);
    repo = repoPayload;
    skill = skillPayload;
    versions = versionsPayload ?? [];
    usageStats = await getRepoSkillUsageStats(accessToken, repoId, skillId);
  } catch (error) {
    skillLoadFailed = true;
    console.error("Failed to fetch skill detail:", error);
  }

  if (!skill) {
    return (
      <div>
        <Link className="mb-6 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}`}>
          <ArrowLeft className="h-4 w-4" />
          Back to repository
        </Link>
        {skillLoadFailed ? <SectionFallback section="skill" /> : (
          <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
            Skill not found.
          </section>
        )}
      </div>
    );
  }

  return (
    <div>
      <SkillViewTracker domain={skill.domain} repo={repo?.full_name ?? skill.repo_name} />
      <nav className="mb-6 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">
          Overview
        </Link>
        <span>/</span>
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard/repos">
          Repos
        </Link>
        <span>/</span>
        <Link className="hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}`}>
          {repo?.name ?? skill.repo_name}
        </Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">{skill.domain}</span>
      </nav>

      <SectionErrorBoundary section="skill header">
        <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:gap-6">
            <ScoreRing score={skill.score.total} />
            <div>
              <Link className="mb-4 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}`}>
                <ArrowLeft className="h-4 w-4" />
                Back to repository
              </Link>
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-[rgb(var(--accent-primary-rgb)/0.2)] bg-[rgb(var(--accent-primary-rgb)/0.1)]">
                  <FileText className="h-5 w-5 text-[color:var(--accent-primary)]" />
                </div>
                <div>
                  <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">{skill.domain}</h1>
                  <p className="mt-1 font-mono text-[12px] text-[color:var(--text-secondary)]">{skill.skill_path}</p>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <div className="inline-flex rounded-full border border-[rgb(var(--accent-primary-rgb)/0.28)] bg-[rgb(var(--accent-primary-rgb)/0.08)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
                  Source: {sourceDescription(skill.source_type)}
                </div>
                {categoryLabel(skill.skill_category) ? (
                  <div className="inline-flex rounded-full border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-1 text-[12px] font-semibold text-[color:var(--text-secondary)]">
                    Category: {categoryLabel(skill.skill_category)}
                  </div>
                ) : null}
              </div>
              <div className="mt-4 flex flex-wrap gap-4 text-[13px] text-[color:var(--text-secondary)]">
                <span>{skill.load_count_30d} loads in 30d</span>
                <span>Last loaded: {formatRelativeTime(skill.last_loaded_at)}</span>
                <span>{versions.length || skill.version_count} version{(versions.length || skill.version_count) === 1 ? "" : "s"}</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <ScoreBadge score={skill.score} />
            <PublishSkillButton accessToken={accessToken} domain={skill.domain} skillId={skill.id} />
            <StaleBadge isStale={skill.is_stale} />
            <VersionBadge versionNumber={skill.latest_version_number} />
          </div>
        </div>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="skill subscores">
        <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <SubscoreCard label="Groundedness" value={skill.score.groundedness} />
          <SubscoreCard label="Coverage" value={skill.score.coverage} />
          <SubscoreCard label="Freshness" value={skill.score.freshness} />
          <SubscoreCard label="Structure" value={skill.score.structure} />
        </div>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="skill usage intelligence">
        <UsageIntelligencePanel usage={usageStats} />
      </SectionErrorBoundary>

      <SectionErrorBoundary section="skill content">
        <SkillDetailViewer accessToken={accessToken} skill={skill} versions={versions} copyLabel="Copy skill path" copyValue={skill.skill_path} />
      </SectionErrorBoundary>
    </div>
  );
}
