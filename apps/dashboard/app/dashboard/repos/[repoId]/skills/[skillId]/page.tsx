import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft, FileText } from "lucide-react";

import { CopySkillButton } from "@/components/copy-skill-button";
import { getRepo, getSkill, getSkillVersion, getSkillVersions, type Repo, type Score, type Skill, type SkillVersion, type SkillVersionSummary } from "../../../../../../lib/data";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ repoId: string; skillId: string }>;
  searchParams: Promise<{ version?: string | string[] }>;
};

function scoreBadgeClass(score: number) {
  if (score <= 40) return "bg-red-900/50 text-red-400";
  if (score <= 70) return "bg-amber-900/50 text-amber-400";
  return "bg-green-900/50 text-green-400";
}

function ScoreBadge({ score }: { score: Score }) {
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-[12px] font-semibold ${scoreBadgeClass(score.total)}`}>{score.total}/100</span>;
}

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

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown date";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function contentHashLabel(hash: string | null | undefined) {
  return hash ? hash.slice(0, 10) : "No hash";
}

function VersionHistory({
  repoId,
  selectedVersionId,
  skill,
  versions,
}: {
  repoId: string;
  selectedVersionId: string | null;
  skill: Skill;
  versions: SkillVersionSummary[];
}) {
  return (
    <aside className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
        <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Version history</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{versions.length || skill.version_count} stored version{(versions.length || skill.version_count) === 1 ? "" : "s"}</p>
      </div>

      <div className="divide-y divide-[color:var(--bg-elevated)]">
        <Link
          className={`block px-5 py-4 transition-colors hover:bg-white/5 ${
            selectedVersionId ? "text-[color:var(--text-secondary)]" : "bg-[rgb(var(--accent-primary-rgb)/0.08)] text-[color:var(--text-primary)]"
          }`}
          href={`/dashboard/repos/${repoId}/skills/${skill.id}`}
        >
          <div className="flex items-center justify-between gap-3">
            <span className="text-[13px] font-semibold">Current SKILL.md</span>
            {!selectedVersionId ? <span className="rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-2 py-0.5 text-[11px] font-semibold text-[color:var(--accent-primary)]">Viewing</span> : null}
          </div>
          <div className="mt-1 font-mono text-[11px] text-[color:var(--text-tertiary)]">{contentHashLabel(skill.content_hash)}</div>
        </Link>

        {versions.map((version) => {
          const isSelected = selectedVersionId === version.id;

          return (
            <Link
              className={`block px-5 py-4 transition-colors hover:bg-white/5 ${
                isSelected ? "bg-[rgb(var(--accent-primary-rgb)/0.08)] text-[color:var(--text-primary)]" : "text-[color:var(--text-secondary)]"
              }`}
              href={`/dashboard/repos/${repoId}/skills/${skill.id}?version=${version.id}`}
              key={version.id}
            >
              <div className="flex items-center justify-between gap-3">
                <span className="text-[13px] font-semibold">Version {version.version_number}</span>
                {version.is_latest ? <span className="rounded-full bg-[rgb(var(--accent-green-rgb)/0.12)] px-2 py-0.5 text-[11px] font-semibold text-[color:var(--accent-green)]">Latest</span> : null}
              </div>
              <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{formatDate(version.created_at)}</div>
              <div className="mt-1 font-mono text-[11px] text-[color:var(--text-tertiary)]">{contentHashLabel(version.content_hash)}</div>
            </Link>
          );
        })}
      </div>
    </aside>
  );
}

function SkillContentPanel({
  content,
  versionNumber,
  selectedVersion,
}: {
  content: string;
  versionNumber: number | null;
  selectedVersion: SkillVersion | null;
}) {
  return (
    <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="flex items-center justify-between gap-4 border-b border-[color:var(--bg-border)] px-5 py-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">SKILL.md content</h2>
            {versionNumber ? (
              <span className="rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-2 py-0.5 text-[11px] font-semibold text-[color:var(--accent-primary)]">
                v{versionNumber}
              </span>
            ) : null}
          </div>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">
            {selectedVersion ? `Viewing version ${selectedVersion.version_number} from ${formatDate(selectedVersion.created_at)}` : "Viewing current generated content"}
          </p>
        </div>
        <CopySkillButton content={content} />
      </div>

      <pre className="max-h-[680px] overflow-auto whitespace-pre-wrap break-words bg-[#07070c] p-5 font-mono text-[12px] leading-6 text-[color:var(--text-secondary)]">
        {content}
      </pre>
    </section>
  );
}

export default async function SkillDetailPage({ params, searchParams }: PageProps) {
  const { repoId, skillId } = await params;
  const resolvedSearchParams = await searchParams;
  const versionParam = Array.isArray(resolvedSearchParams.version) ? resolvedSearchParams.version[0] : resolvedSearchParams.version;
  const session = await withAuth({ ensureSignedIn: true });
  const accessToken = session.accessToken || "";

  let skill: Skill | null = null;
  let repo: Repo | null = null;
  let selectedVersion: SkillVersion | null = null;
  let versions: SkillVersionSummary[] = [];

  try {
    const [repoPayload, skillPayload, versionsPayload] = await Promise.all([
      getRepo(accessToken, repoId),
      getSkill(accessToken, skillId),
      getSkillVersions(accessToken, skillId),
    ]);
    repo = repoPayload;
    skill = skillPayload;
    versions = versionsPayload ?? [];

    if (versionParam) {
      selectedVersion = await getSkillVersion(accessToken, skillId, versionParam);
    }
  } catch (error) {
    console.error("Failed to fetch skill detail:", error);
  }

  if (!skill) {
    return (
      <div>
        <Link className="mb-6 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}`}>
          <ArrowLeft className="h-4 w-4" />
          Back to repository
        </Link>
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
          Skill not found.
        </section>
      </div>
    );
  }

  const displayContent = selectedVersion?.content ?? skill.content ?? "No SKILL.md content is available for this skill yet.";
  const displayedVersionNumber = selectedVersion?.version_number ?? skill.latest_version_number;
  const showVersionHistory = skill.version_count > 1 || versions.length > 1;

  return (
    <div>
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
          {repo?.name ?? "Repository"}
        </Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">{skill.domain}</span>
      </nav>

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
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <ScoreBadge score={skill.score} />
          <StaleBadge isStale={skill.is_stale} />
          {versionParam && !selectedVersion ? (
            <span className="rounded-full bg-amber-900/40 px-2.5 py-1 text-[12px] font-semibold text-amber-300">Version unavailable</span>
          ) : null}
        </div>
      </div>

      <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SubscoreCard label="Groundedness" value={skill.score.groundedness} />
        <SubscoreCard label="Coverage" value={skill.score.coverage} />
        <SubscoreCard label="Freshness" value={skill.score.freshness} />
        <SubscoreCard label="Structure" value={skill.score.structure} />
      </div>

      <div className={showVersionHistory ? "grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]" : "grid gap-6"}>
        <SkillContentPanel content={displayContent} versionNumber={displayedVersionNumber} selectedVersion={selectedVersion} />
        {showVersionHistory ? (
          <VersionHistory repoId={repoId} selectedVersionId={selectedVersion?.id ?? (versionParam || null)} skill={skill} versions={versions} />
        ) : null}
      </div>
    </div>
  );
}
