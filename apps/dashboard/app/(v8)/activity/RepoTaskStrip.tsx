import Link from "next/link";

import type { ActivityRepoOption } from "./activity-data";

function hrefFor(basePath: string, current: URLSearchParams, repoId: string | null): string {
  const params = new URLSearchParams(current);
  params.delete("offset");
  if (repoId) {
    params.set("repo_id", repoId);
  } else {
    params.delete("repo_id");
  }
  if (!params.get("limit")) params.set("limit", "25");
  const query = params.toString();
  return `${basePath}${query ? `?${query}` : ""}`;
}

export function RepoTaskStrip({
  basePath,
  currentParams,
  repos,
  selectedRepoId,
  title = "Repository task feed",
}: {
  basePath: string;
  currentParams: URLSearchParams;
  repos: ActivityRepoOption[];
  selectedRepoId: string | null;
  title?: string;
}) {
  const taskRepos = repos.filter((repo) => (repo.session_count ?? 0) > 0);
  const selectedRepo = selectedRepoId ? taskRepos.find((repo) => repo.id === selectedRepoId) : null;
  if (!taskRepos.length) return null;

  return (
    <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">{title}</h2>
          <p className="mt-1 text-xs leading-5 text-[color:var(--text-secondary)]">
            Click a repository to show only the runs, replay candidates, and tasks tied to that repo.
          </p>
        </div>
        {selectedRepo ? (
          <Link className="w-fit rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href={hrefFor(basePath, currentParams, null)}>
            Show all repositories
          </Link>
        ) : null}
      </div>
      <div className="mt-4 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
        <Link
          className={`rounded-md border px-3 py-3 text-sm transition-colors ${!selectedRepoId ? "border-[color:var(--accent-primary)] bg-[color:var(--accent-primary)]/10 text-[color:var(--text-primary)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-base)] text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]"}`}
          href={hrefFor(basePath, currentParams, null)}
        >
          <span className="block font-semibold">All repositories</span>
          <span className="mt-1 block text-xs text-[color:var(--text-tertiary)]">{selectedRepoId ? "Clear repo filter" : "Cross-repo view"}</span>
        </Link>
        {taskRepos.map((repo) => {
          const isActive = selectedRepoId === repo.id;
          return (
            <Link
              className={`rounded-md border px-3 py-3 text-sm transition-colors ${isActive ? "border-[color:var(--accent-primary)] bg-[color:var(--accent-primary)]/10 text-[color:var(--text-primary)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-base)] text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]"}`}
              href={hrefFor(basePath, currentParams, repo.id)}
              key={repo.id}
            >
              <span className="block truncate font-semibold">{repo.full_name}</span>
              <span className="mt-1 block text-xs text-[color:var(--text-tertiary)]">{(repo.session_count ?? 0).toLocaleString()} total runs</span>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
