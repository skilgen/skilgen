import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft, BookOpen, GitBranch } from "lucide-react";

import { getBootstrapOrg, getRegistrySkillDetail } from "../../../../lib/data";
import { CopyValueButton, SkillActions } from "./skill-actions";
import { ImportOwnButton } from "./import-own-button";

type PageProps = {
  params: Promise<{ registryId: string }>;
};

function scoreClass(score: number): string {
  if (score <= 40) return "bg-red-900/30 text-red-400";
  if (score <= 70) return "bg-amber-900/30 text-amber-400";
  return "bg-green-900/30 text-green-400";
}

export default async function RegistryDetailPage({ params }: PageProps) {
  const { registryId } = await params;
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Registry detail auth unavailable:", error);
  }

  const bootstrapOrg = await getBootstrapOrg();
  const orgId = bootstrapOrg?.id ?? "";
  const detail = await getRegistrySkillDetail(registryId);

  if (!detail) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center gap-6 text-center">
        <BookOpen className="h-16 w-16 text-[color:var(--text-tertiary)]" />
        <div>
          <h1 className="text-[28px] font-semibold text-[color:var(--text-primary)]">Skill not found</h1>
          <p className="mx-auto mt-3 max-w-sm text-[15px] text-[color:var(--text-secondary)]">
            This registry entry doesn&apos;t exist or has been unpublished.
          </p>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-3">
          <Link
            className="inline-flex h-11 items-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]"
            href="/dashboard/registry"
          >
            Browse Registry
          </Link>
          {orgId ? <ImportOwnButton accessToken={accessToken} orgId={orgId} /> : null}
        </div>
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
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard/registry">
          Registry
        </Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">{detail.name}</span>
      </nav>

      <Link className="mb-5 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href="/dashboard/registry">
        <ArrowLeft className="h-4 w-4" />
        Back to Registry
      </Link>

      <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-7">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            {detail.is_official ? (
              <div className="mb-3 inline-flex rounded-full bg-[rgb(var(--accent-primary-rgb)/0.14)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
                Official
              </div>
            ) : null}
            <h1 className="text-[28px] font-semibold text-[color:var(--text-primary)]">{detail.name}</h1>
            <p className="mt-1 font-mono text-[13px] text-[color:var(--text-tertiary)]">{detail.domain}</p>
            <p className="mt-3 max-w-2xl text-[14px] leading-6 text-[color:var(--text-secondary)]">{detail.description}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {detail.tags.map((tag) => (
                <span className="rounded-full bg-[color:var(--bg-elevated)] px-2 py-0.5 text-[11px] text-[color:var(--text-secondary)]" key={tag}>
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div className="flex flex-col items-start gap-3 lg:items-end">
            <span className={`rounded-full px-3 py-1 text-[14px] font-semibold ${scoreClass(detail.score_total)}`}>{detail.score_total}/100</span>
            <div className="text-[13px] text-[color:var(--text-tertiary)]">↓ {detail.import_count} imports</div>
            <div className="text-[13px] text-[color:var(--text-tertiary)]">
              Published: {new Intl.DateTimeFormat(undefined, { month: "short", year: "numeric" }).format(new Date(detail.created_at))}
            </div>
            <div className="inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)]">
              <GitBranch className="h-3.5 w-3.5" />
              {detail.repo_name}
            </div>
          </div>
        </div>

        <SkillActions accessToken={accessToken} registryId={detail.id} skillPath={detail.skill_path} />
      </section>

      <section className="mt-6 overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[color:var(--bg-border)] px-5 py-4">
          <div>
            <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">SKILL.md Content</h2>
            <p className="mt-1 max-w-[600px] truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{detail.content_hash}</p>
          </div>
          <CopyValueButton label="Copy" value={detail.content} />
        </div>
        <pre className="max-h-[600px] overflow-x-auto overflow-y-auto bg-[#08080d] p-6 font-mono text-[13px] leading-6 text-[color:var(--text-secondary)]">{detail.content}</pre>
      </section>
    </div>
  );
}
