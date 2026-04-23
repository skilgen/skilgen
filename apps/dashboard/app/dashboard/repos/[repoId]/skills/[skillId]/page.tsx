import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft, FileText } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { SectionFallback } from "@/components/section-fallback";
import { SkillDetailViewer } from "@/components/skill-detail-viewer";
import { SkillViewTracker } from "@/components/skill-view-tracker";
import { getRepo, getSkill, getSkillVersions, type Repo, type Score, type Skill, type SkillVersionSummary } from "../../../../../../lib/data";

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

export default async function SkillDetailPage({ params }: PageProps) {
  const { repoId, skillId } = await params;
  let accessToken = "";

  let skill: Skill | null = null;
  let repo: Repo | null = null;
  let versions: SkillVersionSummary[] = [];
  let skillLoadFailed = false;

  try {
    const session = await withAuth({ ensureSignedIn: true });
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
            <div className="mt-4 inline-flex rounded-full border border-[rgb(var(--accent-primary-rgb)/0.28)] bg-[rgb(var(--accent-primary-rgb)/0.08)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
              Source: {sourceDescription(skill.source_type)}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <ScoreBadge score={skill.score} />
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

      <SectionErrorBoundary section="skill content">
        <SkillDetailViewer accessToken={accessToken} skill={skill} versions={versions} />
      </SectionErrorBoundary>
    </div>
  );
}
