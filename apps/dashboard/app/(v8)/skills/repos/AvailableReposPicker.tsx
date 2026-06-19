"use client";

import Link from "next/link";
import { Github } from "lucide-react";
import { useMemo, useState } from "react";

type AvailableRepo = {
  id: string;
  full_name: string;
  name: string;
  language: string | null;
  private: boolean;
  connected: boolean;
  connected_repo_id: string | null;
  url: string | null;
  updated_at: string | null;
  source: string;
  providers?: string[];
  session_count?: number;
  last_activity_at?: string | null;
};

type AvailableReposPickerProps = {
  repos: AvailableRepo[];
  githubAvailable: boolean;
  nextAction: string | null;
};

export function AvailableReposPicker({ repos, githubAvailable, nextAction }: AvailableReposPickerProps) {
  const uniqueRepos = useMemo(() => {
    const byName = new Map<string, AvailableRepo>();
    for (const repo of repos) {
      const key = repo.full_name.toLowerCase();
      const existing = byName.get(key);
      if (!existing || (repo.session_count ?? 0) > (existing.session_count ?? 0)) {
        byName.set(key, repo);
      }
    }
    return Array.from(byName.values()).sort((a, b) => a.full_name.localeCompare(b.full_name));
  }, [repos]);
  const defaultRepo = useMemo(() => uniqueRepos.find((repo) => (repo.session_count ?? 0) > 0) ?? uniqueRepos[0] ?? null, [uniqueRepos]);
  const [selectedId, setSelectedId] = useState(defaultRepo?.id ?? "");
  const selectedRepo = uniqueRepos.find((repo) => repo.id === selectedId) ?? defaultRepo;
  const observedCount = uniqueRepos.filter((repo) => (repo.session_count ?? 0) > 0).length;
  const providerLabel = selectedRepo?.providers?.length ? selectedRepo.providers.map((provider) => provider.replaceAll("_", " ")).join(", ") : "No coding-agent runs yet";

  return (
    <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" id="available-repositories">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Coding-agent repositories</h2>
          <p className="mt-2 max-w-3xl text-[13px] leading-6 text-[color:var(--text-secondary)]">
            Repositories seen from Codex, Claude Code, and other coding-agent telemetry. Pick a repo to open its Skillayer evidence or inspect the agent activity behind it.
          </p>
        </div>
        <div className="inline-flex w-fit items-center justify-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-[12px] font-semibold text-[color:var(--text-secondary)]">
          <Github className="h-3.5 w-3.5" />
          {githubAvailable ? `${observedCount} repos with agent runs` : "No agent repos detected"}
        </div>
      </div>

      {!githubAvailable && nextAction ? (
        <div className="mt-4 rounded-md border border-[#f59e0b]/30 bg-[#f59e0b]/10 p-3 text-[13px] text-[#f8d78a]">{nextAction}</div>
      ) : null}

      {selectedRepo ? (
        <div className="mt-4 grid gap-3 lg:grid-cols-[minmax(260px,420px)_1fr]">
          <label className="block">
            <span className="mb-2 block text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Repository</span>
            <select
              className="h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] text-[color:var(--text-primary)] outline-none transition-colors focus:border-[color:var(--accent-primary)]"
              onChange={(event) => setSelectedId(event.target.value)}
              value={selectedRepo.id}
            >
              {uniqueRepos.map((repo) => (
                <option key={repo.id} value={repo.id}>
                  {repo.full_name}
                </option>
              ))}
            </select>
          </label>

          <article className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="font-semibold text-[color:var(--text-primary)]">{selectedRepo.full_name}</div>
                <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">
                  {selectedRepo.language ?? "Language unknown"} · {providerLabel} · {(selectedRepo.session_count ?? 0).toLocaleString()} runs
                </div>
              </div>
              {selectedRepo.connected && selectedRepo.connected_repo_id ? (
                <Link className="inline-flex w-fit items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-[12px] font-semibold text-[color:var(--bg-base)]" href={`/activity/live-feed?repo_id=${encodeURIComponent(selectedRepo.connected_repo_id)}&hours=24`}>
                  Open repo feed
                </Link>
              ) : (
                <span className="inline-flex w-fit items-center justify-center rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-[12px] font-semibold text-[color:var(--text-secondary)]">No Skillayer index yet</span>
              )}
            </div>
          </article>
        </div>
      ) : (
        <div className="mt-4 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 text-[13px] text-[color:var(--text-secondary)]">No coding-agent repositories are available yet.</div>
      )}
    </section>
  );
}
