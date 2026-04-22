import Link from "next/link";
import { Github, Plus } from "lucide-react";

import { API_URL, type Org, type Repo } from "../../../lib/data";
import { ReposBrowser, type RepoListItem } from "./repos-browser";

export const dynamic = "force-dynamic";

export default async function ReposPage() {
  let repos: RepoListItem[] = [];

  try {
    const bootstrapRes = await fetch(`${API_URL}/orgs/bootstrap`, {
      next: { revalidate: 60 },
    });
    if (bootstrapRes.ok) {
      const org = (await bootstrapRes.json()) as Org;
      const reposRes = await fetch(`${API_URL}/orgs/${org.id}/repos`, {
        next: { revalidate: 60 },
      });
      if (reposRes.ok) {
        repos = (((await reposRes.json()) as Repo[]) ?? []) as RepoListItem[];
      }
    }
  } catch (error) {
    console.error("Failed to fetch repos:", error);
  }

  return (
    <div>
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="mb-3 flex items-center gap-2 text-[12px] text-[color:var(--text-tertiary)]">
            <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">
              Overview
            </Link>
            <span>/</span>
            <span className="text-[color:var(--text-secondary)]">Repos</span>
          </div>
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Repositories</h1>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{repos.length} repos connected</p>
        </div>

        <Link
          className="inline-flex h-10 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]"
          href="https://github.com/apps/skillayer/installations/new"
          target="_blank"
        >
          <Github className="mr-2 h-4 w-4" />
          Connect repo
        </Link>
      </div>

      {repos.length > 0 ? (
        <ReposBrowser repos={repos} />
      ) : (
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[color:var(--accent-primary)]">
            <Plus className="h-5 w-5" />
          </div>
          <h2 className="text-[17px] font-semibold text-[color:var(--text-primary)]">Connect your first repository</h2>
          <p className="mx-auto mt-2 max-w-md text-[14px] text-[color:var(--text-secondary)]">
            Install the Skillayer GitHub App to analyse repositories, generate skills, and track score history.
          </p>
          <Link
            className="mt-6 inline-flex h-10 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]"
            href="https://github.com/apps/skillayer/installations/new"
            target="_blank"
          >
            <Github className="mr-2 h-4 w-4" />
            Connect repo
          </Link>
        </section>
      )}
    </div>
  );
}
