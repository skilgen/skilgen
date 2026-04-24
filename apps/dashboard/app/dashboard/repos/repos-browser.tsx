"use client";

import Link from "next/link";
import { useCallback, useDeferredValue, useMemo, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { Check, ClipboardCopy, Search, X } from "lucide-react";

import { captureDashboardEvent } from "@/lib/posthog";
import { relativeTime } from "../../../lib/relative-time";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

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
  installation_id?: number | null;
  language: string | null;
  display_language?: string;
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

function displayLanguage(repo: RepoListItem): string {
  if (repo.language) return repo.language;
  if (repo.display_language === "Multiple") return "Multi";
  return "—";
}

export function CopyTextButton({
  text,
  label = "Copy",
  title,
  children,
}: {
  text: string;
  label?: string;
  title?: string;
  children?: ReactNode;
}) {
  const [copied, setCopied] = useState(false);

  return (
    <button
      className="inline-flex items-center gap-1.5 rounded-md border border-[color:var(--bg-border)] bg-black/10 px-2.5 py-1.5 text-[12px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:bg-[color:var(--bg-elevated)] hover:text-[color:var(--text-primary)]"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text);
          setCopied(true);
          window.setTimeout(() => setCopied(false), 1400);
        } catch (error) {
          console.error("Failed to copy text:", error);
        }
      }}
      title={title}
      type="button"
    >
      {children ?? (copied ? <Check className="h-3.5 w-3.5 text-emerald-300" /> : <ClipboardCopy className="h-3.5 w-3.5" />)}
      {label ? (copied ? "Copied" : label) : null}
    </button>
  );
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
  const deferredQuery = useDeferredValue(query);
  const [sortMode, setSortMode] = useState<SortMode>("score-desc");
  const [langFilter, setLangFilter] = useState("All");
  const [rowStates, setRowStates] = useState<Record<string, RowAnalyseState>>({});

  const langs = useMemo(() => {
    const set = new Set<string>();
    repos.forEach((repo) => {
      if (repo.language) set.add(repo.language);
      else if (repo.display_language === "Multiple") set.add("Multi-language");
    });
    return ["All", ...Array.from(set).sort()];
  }, [repos]);

  const visibleRepos = useMemo(() => {
    const normalized = deferredQuery.trim().toLowerCase();
    const filteredByQuery = normalized
      ? repos.filter((repo) => `${repo.name} ${repo.full_name} ${repo.language ?? ""} ${repo.display_language ?? ""}`.toLowerCase().includes(normalized))
      : repos;

    const filteredByLanguage = filteredByQuery.filter((repo) => {
      if (langFilter === "All") return true;
      if (langFilter === "Multi-language") return repo.display_language === "Multiple";
      return repo.language === langFilter;
    });

    return sortRepos(filteredByLanguage, sortMode);
  }, [deferredQuery, langFilter, repos, sortMode]);

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

  const clearSearch = () => {
    setQuery("");
    setLangFilter("All");
  };

  const activeQuery = deferredQuery.trim();

  return (
    <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
            <input
              className="h-10 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] pl-9 pr-10 text-[14px] text-[color:var(--text-primary)] outline-none transition-colors placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)] xl:w-[340px]"
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search repositories…"
              type="search"
              value={query}
            />
            {query ? (
              <button
                aria-label="Clear search"
                className="absolute right-3 top-1/2 inline-flex h-5 w-5 -translate-y-1/2 items-center justify-center rounded-full text-[color:var(--text-tertiary)] hover:bg-white/10 hover:text-[color:var(--text-primary)]"
                onClick={() => setQuery("")}
                type="button"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            ) : null}
          </div>

          <div className="flex items-center gap-3">
            {activeQuery ? (
              <span className="text-[12px] font-semibold text-[color:var(--text-tertiary)]">
                {visibleRepos.length} result{visibleRepos.length === 1 ? "" : "s"}
              </span>
            ) : null}
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
        </div>

        {langs.length > 1 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {langs.map((lang) => (
              <button
                key={lang}
                onClick={() => setLangFilter(lang)}
                className={`rounded-full px-3 py-1 text-[12px] font-semibold transition-colors ${
                  langFilter === lang
                    ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]"
                    : "border border-[color:var(--bg-border)] text-[color:var(--text-secondary)] hover:bg-white/5"
                }`}
                type="button"
              >
                {lang}
              </button>
            ))}
          </div>
        ) : null}
      </div>

      {visibleRepos.length > 0 ? (
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
                    <td className="px-5 py-4 text-[color:var(--text-secondary)]">{displayLanguage(repo)}</td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        {typeof score === "number" ? (
                          <span className={`inline-flex rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreBadgeClass(score)}`}>
                            {score}/100
                          </span>
                        ) : (
                          <span className="text-gray-600">Not analysed</span>
                        )}
                        <Link
                          className="inline-flex h-8 items-center rounded-md border border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-secondary)] hover:bg-[color:var(--bg-elevated)]"
                          href={`/dashboard/repos/${repo.id}`}
                          onClick={(event) => event.stopPropagation()}
                        >
                          Analyse
                        </Link>
                      </div>
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
      ) : (
        <div className="border-t border-[color:var(--bg-border)] px-5 py-10 text-center text-[color:var(--text-secondary)]">
          <Search className="mx-auto h-6 w-6 text-[color:var(--text-tertiary)]" />
          <div className="mt-3 text-[16px] font-semibold text-[color:var(--text-primary)]">No repos match</div>
          <div className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Try a different search or clear the language filter</div>
          <button
            className="mt-4 inline-flex rounded-md border border-[color:var(--bg-border)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--text-secondary)] hover:bg-[color:var(--bg-elevated)]"
            onClick={clearSearch}
            type="button"
          >
            Clear search
          </button>
        </div>
      )}
    </section>
  );
}
