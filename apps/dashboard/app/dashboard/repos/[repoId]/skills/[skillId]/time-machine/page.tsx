import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft } from "lucide-react";

import { SectionFallback } from "@/components/section-fallback";
import { getRepo, getSkill, getSkillSnapshot, getSkillSnapshotDiff, getSkillSnapshots, type Repo, type Skill, type SkillSnapshot } from "../../../../../../../lib/data";
import { TimeMachineClient } from "./time-machine-client";

type PageProps = {
  params: Promise<{ repoId: string; skillId: string }>;
};

export default async function SkillTimeMachinePage({ params }: PageProps) {
  const { repoId, skillId } = await params;
  let accessToken = "";
  let repo: Repo | null = null;
  let skill: Skill | null = null;
  let snapshots: SkillSnapshot[] = [];
  let selectedSnapshot: SkillSnapshot | null = null;
  let selectedDiff: string | null = null;
  let loadFailed = false;

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Time Machine auth unavailable:", error);
  }

  try {
    const [repoPayload, skillPayload, snapshotsPayload] = await Promise.all([
      getRepo(accessToken, repoId),
      getSkill(accessToken, skillId),
      getSkillSnapshots(accessToken, repoId, skillId),
    ]);
    repo = repoPayload;
    skill = skillPayload;
    snapshots = snapshotsPayload ?? [];
    if (snapshots[0]) {
      selectedSnapshot = await getSkillSnapshot(accessToken, repoId, skillId, snapshots[0].id);
      selectedDiff = await getSkillSnapshotDiff(accessToken, repoId, skillId, snapshots[0].id);
    }
  } catch (error) {
    loadFailed = true;
    console.error("Failed to load skill time machine:", error);
  }

  if (!skill) {
    return (
      <div>
        <Link className="mb-6 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}/skills/${skillId}`}>
          <ArrowLeft className="h-4 w-4" />
          Back to skill
        </Link>
        {loadFailed ? (
          <SectionFallback section="skill time machine" />
        ) : (
          <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
            Skill not found.
          </section>
        )}
      </div>
    );
  }

  return (
    <TimeMachineClient
      accessToken={accessToken}
      currentContent={skill.content ?? ""}
      initialDiff={selectedDiff ?? ""}
      initialSelectedSnapshot={selectedSnapshot}
      initialSnapshots={snapshots}
      repo={repo}
      repoId={repoId}
      skill={skill}
      skillId={skillId}
    />
  );
}
