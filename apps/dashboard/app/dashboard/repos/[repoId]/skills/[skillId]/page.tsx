import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft } from "lucide-react";

import { SectionFallback } from "@/components/section-fallback";
import { SkillViewTracker } from "@/components/skill-view-tracker";
import { getRepo, getRepoSkillUsageStats, getSkill, getSkillVersions, type Repo, type Skill, type SkillUsageStats, type SkillVersionSummary } from "../../../../../../lib/data";
import { SkillDetailShell } from "./skill-detail-shell";

type PageProps = {
  params: Promise<{ repoId: string; skillId: string }>;
};

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
    accessToken = session?.accessToken || "";
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
        {skillLoadFailed ? (
          <SectionFallback section="skill" />
        ) : (
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
      <SkillDetailShell accessToken={accessToken} repo={repo} repoId={repoId} skill={skill} usageStats={usageStats} versions={versions} />
    </div>
  );
}
