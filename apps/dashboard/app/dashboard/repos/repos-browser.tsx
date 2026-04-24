"use client";

import { useCallback, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

import { API_URL } from "../../../lib/data";
import { captureDashboardEvent } from "@/lib/posthog";

type Score = {
  total: number;
  groundedness: number;
  coverage: number;
  freshness: number;
  structure: number;
};

export type RepoListItem = {
  id: string;
  name: string;
  full_name: string;
  language: string | null;
  last_analysed_at: string | null;
  created_at?: string | null;
  score: Score | null;
  skill_count: number;
};

type SortMode = "score-desc" | "score-asc" | "name-asc" | "last-analysed";
type RowAnalyseState = "idle" | "loading" | "queued" | "error";

function scoreBadgeClass(score: number): string {
  if (score <= 40) return "bg-red-900/30 text-red-400";
  if (score <= 70) return "bg-amber-900/30 text-amber-400";
  return "bg-green-900/30 text-green-400";
}

function relativeTime(value: string | null): string {
  if (!value) return "Never";
  const timestamp = new Date(value).getTime();
  if (Number.isNaN(timestamp)) return "Never";

  const diff = Math.max(0, Date.now() - timestamp);
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (diff < hour) {
    const minutes = Math.max(1, Math.floor(diff / minute));
    return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  }
  if (diff < day) {
    const hours = Math.floor(diff / hour);
    return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  }
  if (diff < 7 * day) {
    const days = Math.floor(diff / day);
    return `${days} day${days === 1 ? "" : "s"} ago`;
  }
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(timestamp));
}

function isRecentlyConnected(createdAt: string | null | undefined, lastAnalysedAt: string | null): boolean {
  if (lastAnalysedAt !== null || !createdAt) return false;

  const createdTimestamp = new Date(createdAt).getTime();
  if (Number.isNaN(createdTimestamp)) return false;

  return Date.now() - createdTimestamp <= 5 * 60 * 1000;
}

function sortRepos(repos: RepoListItem[], sortMode: SortMode): RepoListItem[] {
  return [...repos].sort((left, right) => {
    if (sortMode === "name-asc") return left.full_name.localeCompare(right.full_name);
    if (sortMode === "last-analysed") {
      return new Date(right.last_analysed_at ?? 0).getTime() - new Date(left.last_analysed_at ?? 0).getTime();
    }

    const leftScore = left.score?.total ?? -1;
    const rightScore = right.score?.total ?? -1;
    return sortMode === "score-asc" ? leftScore - rightScore : rightScore - leftScore;
  });
}

type RepoAnalyseActionProps = {
  disabled: boolean;
  label: string;
  onAnalyse: () => Promise<void>;
};

function RepoAnalyseAction({ disabled, label, onAnalyse }: RepoAnalyseActionProps) {
  return (
    <button
      className="rounded-md border border-[rgb(var(--accent-primary-rgb)/0.45)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--accent-primary)] transition-colors hover:bg-[rgb(var(--accent-primary-rgb)/0.12)] disabled:cursor-not-allowed disabled:opacity-60"
      disabled={disabled}
      onClick={(event) => {
        event.stopPropagation();
        void onAnalyse();
      }}
      type="button"
    >
      {label}
    </button>
  );
}

export function ReposBrowser({ accessToken, repos }: { accessToken: string; repos: RepoListItem[] }) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [sortMode, setSortMode] = useState<SortMode>("score-desc");
  const [rowStates, setRowStates] = useState<Record<string, RowAnalyseState>>({});

  const visibleRepos = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    const filtered = normalized
      ? repos.filter((repo) => `${repo.name} ${repo.full_name} ${repo.language ?? ""}`.toLowerCase().includes(normalized))
      : repos;
    return sortRepos(filtered, sortMode);
  }, [query, repos, sortMode]);

  const handleAnalyse = useCallback(
    async (repoId: string) => {
      if (!accessToken) {
        router.push("/sign-in");
        return;
      }

      setRowStates((current) => ({ ...current, [repoId]: "loading" }));
      captureDashboardEvent({ name: "repo_analyse_triggered", properties: {} });

      try {
        const response = await fetch(`${API_URL}/repos/${repoId}/analyse`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({}),
        });
        const data = (await response.json().catch(() => ({}))) as { detail?: string };
        if (!response.ok) {
          throw new Error(data.detail || `Request failed with ${response.status}`);
        }
        setRowStates((current) => ({ ...current, [repoId]: "queued" }));
      } catch (error) {
        console.error("Failed to queue analysis:", error);
        setRowStates((current) => ({ ...current, [repoId]: "error" }));
      }
    },
    [accessToken, router],
  );

  return (
    <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="flex flex-col gap-3 border-b border-[color:var(--bg-border)] px-5 py-4 md:flex-row md:items-center md:justify-between">
        <label className="relative block w-full md:max-w-sm">
          <span className="sr-only">Search repositories</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
          <input
            className="h-10 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] pl-9 pr-3 text-[14px] text-[color:var(--text-primary)] outline-none transition-colors placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search repositories"
            type="search"
            value={query}
          />
        </label>

        <label className="flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)]">
          Sort
          <select
            className="h-10 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]"
            onChange={(event) => setSortMode(event.target.value as SortMode)}
            value={sortMode}
          >
            <option value="score-desc">Score ↓</option>
            <option value="score-asc">Score ↑</option>
            <option value="name-asc">Name A-Z</option>
            <option value="last-analysed">Last analysed</option>
          </select>
        </label>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[800px] border-collapse text-left text-[13px]">
          <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
            <tr className="border-b border-[color:var(--bg-border)]">
              <th className="px-5 py-3 font-semibold">Repository</th>
              <th className="px-5 py-3 font-semibold">Language</th>
              <th className="px-5 py-3 font-semibold">Score</th>
              <th className="px-5 py-3 font-semibold">Skills</th>
              <th className="px-5 py-3 font-semibold">Last analysed</th>
              <th className="px-5 py-3 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {visibleRepos.map((repo) => {
              const score = repo.score?.total ?? null;
              const analyseState = rowStates[repo.id] ?? "idle";
              const recentlyConnected = isRecentlyConnected(repo.created_at, repo.last_analysed_at);
              const analyseLabel =
                analyseState === "loading"
                  ? "Queueing..."
                  : analyseState === "queued"
                    ? "Queued"
                    : analyseState === "error"
                      ? "Retry analyse"
                      : score === null
                        ? "Analyse"
                        : "Analyse again";
              return (
                <tr
                  className="cursor-pointer border-b border-[color:var(--bg-elevated)] transition-colors last:border-b-0 hover:bg-white/5"
                  key={repo.id}
                  onClick={() => router.push(`/dashboard/repos/${repo.id}`)}
                >
                  <td className="px-5 py-4">
                    <span className="flex flex-wrap items-center gap-2 font-medium text-[color:var(--text-primary)]">
                      <span>{repo.name}</span>
                      {recentlyConnected ? (
                        <span className="inline-flex rounded-full bg-[rgb(var(--accent-primary-rgb)/0.14)] px-2 py-0.5 text-[11px] font-semibold text-[color:var(--accent-primary)]">
                          Recently connected
                        </span>
                      ) : null}
                    </span>
                    <span className="mt-0.5 block font-mono text-[12px] text-[color:var(--text-tertiary)]">{repo.full_name}</span>
                  </td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{repo.language || "—"}</td>
                  <td className="px-5 py-4">
                    {typeof score === "number" ? (
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreBadgeClass(score)}`}>
                        {score}/100
                      </span>
                    ) : (
                      <span className="text-gray-600">Not analysed</span>
                    )}
                  </td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{repo.skill_count || "—"}</td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{relativeTime(repo.last_analysed_at)}</td>
                  <td className="px-5 py-4">
                    <RepoAnalyseAction
                      disabled={analyseState === "loading" || analyseState === "queued"}
                      label={analyseLabel}
                      onAnalyse={() => handleAnalyse(repo.id)}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {visibleRepos.length === 0 ? (
        <div className="border-t border-[color:var(--bg-border)] px-5 py-10 text-center text-[color:var(--text-secondary)]">
          No repositories match your search.
        </div>
      ) : null}
    </section>
  );
}
