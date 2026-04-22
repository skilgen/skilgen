import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft } from "lucide-react";

import { getRepo, getRepoScoreHistory, getRepoSkills, type Repo, type Score, type ScoreHistoryPoint, type Skill } from "../../../../lib/data";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ repoId: string }>;
};

function ScoreCard({ label, value, max }: { label: string; value: number | null | undefined; max: number }) {
  return (
    <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-3 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
      <div className="text-[28px] font-bold leading-none text-[color:var(--text-primary)]">
        {typeof value === "number" ? value : "—"}
        <span className="ml-1 text-[14px] font-medium text-[color:var(--text-tertiary)]">/{max}</span>
      </div>
    </article>
  );
}

function SkillScore({ score }: { score: Score }) {
  return (
    <span className="inline-flex rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-2 py-0.5 text-[12px] font-semibold text-[color:var(--accent-primary)]">
      {score.total}/100
    </span>
  );
}

function SkillsTable({ repoId, skills }: { repoId: string; skills: Skill[] }) {
  return (
    <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
        <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Skills</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Generated SKILL.md files for this repository.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-left text-[13px]">
          <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
            <tr className="border-b border-[color:var(--bg-border)]">
              <th className="px-5 py-3 font-semibold">Domain</th>
              <th className="px-5 py-3 font-semibold">Skill path</th>
              <th className="px-5 py-3 font-semibold">Score</th>
              <th className="px-5 py-3 font-semibold">Stale?</th>
            </tr>
          </thead>
          <tbody>
            {skills.map((skill) => (
              <tr key={skill.id} className="cursor-pointer border-b border-[color:var(--bg-elevated)] transition-colors last:border-b-0 hover:bg-white/5">
                <td className="px-5 py-4 font-medium text-[color:var(--text-primary)]">
                  <Link className="block" href={`/dashboard/repos/${repoId}/skills/${skill.id}`}>
                    {skill.domain}
                  </Link>
                </td>
                <td className="px-5 py-4 font-mono text-[12px] text-[color:var(--text-secondary)]">
                  <Link className="block" href={`/dashboard/repos/${repoId}/skills/${skill.id}`}>
                    {skill.skill_path}
                  </Link>
                </td>
                <td className="px-5 py-4">
                  <Link className="block" href={`/dashboard/repos/${repoId}/skills/${skill.id}`}>
                    <SkillScore score={skill.score} />
                    <div className="mt-1 text-[11px] text-[color:var(--text-tertiary)]">
                      G {skill.score.groundedness}/25 · C {skill.score.coverage}/25 · F {skill.score.freshness}/25 · S {skill.score.structure}/25
                    </div>
                  </Link>
                </td>
                <td className="px-5 py-4 text-[color:var(--text-secondary)]">
                  <Link className="block" href={`/dashboard/repos/${repoId}/skills/${skill.id}`}>
                    {skill.is_stale ? "Yes" : "No"}
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default async function RepoDetailPage({ params }: PageProps) {
  const { repoId } = await params;
  const session = await withAuth({ ensureSignedIn: true });
  const accessToken = session.accessToken || "";

  let repo: Repo | null = null;
  let skills: Skill[] = [];
  let scoreHistory: ScoreHistoryPoint[] = [];

  try {
    const [repoPayload, skillsPayload, historyPayload] = await Promise.all([
      getRepo(accessToken, repoId),
      getRepoSkills(accessToken, repoId),
      getRepoScoreHistory(accessToken, repoId),
    ]);
    repo = repoPayload;
    skills = skillsPayload ?? [];
    scoreHistory = historyPayload ?? [];
  } catch (error) {
    console.error("Failed to fetch repo detail:", error);
  }

  if (!repo) {
    return (
      <div>
        <Link className="mb-6 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href="/dashboard/repos">
          <ArrowLeft className="h-4 w-4" />
          Back to repos
        </Link>
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
          Repository not found.
        </section>
      </div>
    );
  }

  return (
    <div>
      <Link className="mb-6 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href="/dashboard/repos">
        <ArrowLeft className="h-4 w-4" />
        Back to repos
      </Link>

      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">{repo.name}</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{repo.full_name}</p>
        <p className="mt-2 text-[12px] text-[color:var(--text-tertiary)]">Score history: {scoreHistory.length} point{scoreHistory.length === 1 ? "" : "s"}</p>
      </div>

      <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <ScoreCard label="Total score" value={repo.score?.total} max={100} />
        <ScoreCard label="Groundedness" value={repo.score?.groundedness} max={25} />
        <ScoreCard label="Coverage" value={repo.score?.coverage} max={25} />
        <ScoreCard label="Freshness" value={repo.score?.freshness} max={25} />
        <ScoreCard label="Structure" value={repo.score?.structure} max={25} />
      </div>

      {skills.length > 0 ? (
        <SkillsTable repoId={repoId} skills={skills} />
      ) : (
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
          No skills found for this repository.
        </section>
      )}
    </div>
  );
}
