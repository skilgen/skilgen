import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft } from "lucide-react";

import { getRepo, getSkillVersionDiff } from "../../../../../../../../lib/data";

type PageProps = {
  params: Promise<{ repoId: string; skillId: string; versionId: string }>;
};

function lineClass(type: "meta" | "added" | "removed" | "context"): string {
  if (type === "added") return "border-l-2 border-green-500 bg-green-500/10 text-green-300";
  if (type === "removed") return "border-l-2 border-red-500 bg-red-500/10 text-red-300 line-through opacity-70";
  if (type === "meta") return "bg-white/3 py-1 pl-2 text-[11px] text-[color:var(--text-tertiary)]/50";
  return "pl-4 text-[color:var(--text-secondary)]/60";
}

export default async function SkillDiffPage({ params }: PageProps) {
  const { repoId, skillId, versionId } = await params;
  let accessToken = "";

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Skill diff auth unavailable:", error);
  }

  const [repo, diff] = await Promise.all([
    getRepo(accessToken, repoId),
    getSkillVersionDiff(accessToken, repoId, skillId, versionId),
  ]);

  if (!diff) {
    return (
      <div>
        <Link className="mb-6 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}/skills/${skillId}`}>
          <ArrowLeft className="h-4 w-4" />
          Back to skill
        </Link>
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
          Version not found.
        </section>
      </div>
    );
  }

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
          {repo?.name ?? repoId}
        </Link>
        <span>/</span>
        <Link className="hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}/skills/${skillId}`}>
          {diff.domain}
        </Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">Diff v{diff.version_number}</span>
      </nav>

      <Link className="mb-6 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}/skills/${skillId}`}>
        <ArrowLeft className="h-4 w-4" />
        Back to skill
      </Link>

      <section className="mb-6 rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">
              Skill diff — v{diff.prev_version_number ?? 0} → v{diff.version_number}
            </h1>
            <p className="mt-2 font-mono text-[13px] text-[color:var(--text-tertiary)]">{diff.domain}</p>
            {diff.is_first_version ? (
              <p className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-[13px] text-amber-200">
                First version — no previous content to compare
              </p>
            ) : null}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-green-900/30 px-3 py-1 text-[13px] font-semibold text-green-300">+{diff.added_count} added</span>
            <span className="rounded-full bg-red-900/30 px-3 py-1 text-[13px] font-semibold text-red-300">-{diff.removed_count} removed</span>
          </div>
        </div>
      </section>

      <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[#08080d]">
        <div className="flex items-center justify-between border-b border-[color:var(--bg-border)] px-5 py-4">
          <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">SKILL.md changes</h2>
          <span className="rounded-full bg-white/8 px-2.5 py-1 text-[12px] font-semibold text-[color:var(--text-secondary)]">v{diff.version_number}</span>
        </div>
        <div className="max-h-[70vh] overflow-auto">
          {diff.lines.map((line, index) => (
            <div className={`font-mono text-[13px] leading-6 ${lineClass(line.type)} ${line.type === "meta" ? "" : "pl-4"}`} key={`${line.type}-${index}`}>
              {line.type === "added" ? <span className="mr-2 text-green-500">+</span> : null}
              {line.type === "removed" ? <span className="mr-2 text-red-500">-</span> : null}
              {line.type === "context" ? <span className="mr-2 text-[color:var(--text-tertiary)]"> </span> : null}
              {line.text || "\u00A0"}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
