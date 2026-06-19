"use client";

import { Loader2, Search, Square, SquareCheckBig, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useDeferredValue, useEffect, useMemo, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type AvailableRepo = {
  github_repo_id: number;
  full_name: string;
  name: string;
  language: string | null;
  default_branch: string;
  private: boolean;
  installation_id: number;
};

export function AddReposModal({
  orgId,
  accessToken,
  onClose,
}: {
  orgId: string;
  accessToken: string;
  onClose: () => void;
}) {
  const router = useRouter();
  const [repos, setRepos] = useState<AvailableRepo[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [installationIdInput, setInstallationIdInput] = useState("");
  const [requestedInstallationId, setRequestedInstallationId] = useState("");
  const [query, setQuery] = useState("");
  const [fetchTrigger, setFetchTrigger] = useState(0);
  const deferredQuery = useDeferredValue(query);

  const headers = useMemo(
    () => ({
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    }),
    [accessToken],
  );

  useEffect(() => {
    let cancelled = false;
    async function loadRepos() {
      setLoading(true);
      setError(null);
      try {
        const url = requestedInstallationId
          ? `${API_URL}/orgs/${orgId}/available-repos?installation_id=${requestedInstallationId}`
          : `${API_URL}/orgs/${orgId}/available-repos`;
        const response = await fetch(url, {
          headers,
        });
        const body = await response.json().catch(() => ([]));
        if (!response.ok) throw new Error(body.detail || "Unable to load repositories");
        if (!cancelled) {
          setRepos(body as AvailableRepo[]);
          setSelectedIds([]);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Unable to load repositories");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void loadRepos();
    return () => {
      cancelled = true;
    };
  }, [fetchTrigger, headers, orgId, requestedInstallationId]);

  useEffect(() => {
    if (!success) return;
    const timer = window.setTimeout(() => {
      router.refresh();
      onClose();
    }, 800);
    return () => window.clearTimeout(timer);
  }, [onClose, router, success]);

  const selectedRepos = repos.filter((repo) => selectedIds.includes(repo.github_repo_id));
  const visibleRepos = useMemo(() => {
    const normalized = deferredQuery.trim().toLowerCase();
    if (!normalized) return repos;
    return repos.filter((repo) => `${repo.full_name} ${repo.language ?? ""} ${repo.default_branch}`.toLowerCase().includes(normalized));
  }, [deferredQuery, repos]);
  const allVisibleSelected = visibleRepos.length > 0 && visibleRepos.every((repo) => selectedIds.includes(repo.github_repo_id));

  function toggleRepo(id: number) {
    setSelectedIds((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]));
  }

  async function connectSelectedRepos() {
    if (!selectedRepos.length) return;
    setConnecting(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/orgs/${orgId}/connect-repos`, {
        method: "POST",
        headers,
        body: JSON.stringify({ repos: selectedRepos }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Unable to connect repositories");
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to connect repositories");
    } finally {
      setConnecting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] shadow-[0_32px_90px_rgba(0,0,0,0.45)]" data-testid="add-repos-modal">
        <div className="flex items-start justify-between gap-4 border-b border-[color:var(--bg-border)] px-6 py-5">
          <div>
            <h2 className="text-[22px] font-semibold text-[color:var(--text-primary)]">Add repositories</h2>
            <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">From your existing GitHub installation</p>
          </div>
          <button className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-[color:var(--bg-border)] text-[color:var(--text-secondary)] hover:bg-[color:var(--bg-elevated)]" onClick={onClose} type="button">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="px-6 py-5">
          {loading ? (
            <div className="flex min-h-[220px] flex-col items-center justify-center gap-3 text-[color:var(--text-secondary)]">
              <Loader2 className="h-6 w-6 animate-spin" />
              <p className="text-[14px]">Loading your repositories…</p>
            </div>
          ) : error ? (
            <div className="space-y-4">
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-[14px] text-red-200">{error}</div>
              {error.toLowerCase().includes("installation") ? (
                <div className="space-y-3">
                  <p className="text-[13px] text-[color:var(--text-secondary)]">
                    Paste your GitHub App installation ID to continue. Find it in your GitHub URL:{" "}
                    <span className="font-mono text-[color:var(--text-tertiary)]">
                      github.com/settings/installations/<strong>125707663</strong>
                    </span>
                  </p>
                  <div className="flex gap-2">
                    <input
                      className="h-10 flex-1 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 font-mono text-[14px] text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]"
                      onChange={(e) => setInstallationIdInput(e.target.value)}
                      placeholder="e.g. 125707663"
                      type="text"
                      value={installationIdInput}
                    />
                    <button
                      className="inline-flex h-10 items-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] disabled:opacity-50"
                      disabled={!installationIdInput.trim()}
                      onClick={() => {
                        setError(null);
                        setRequestedInstallationId(installationIdInput.trim());
                        setFetchTrigger((n) => n + 1);
                      }}
                      type="button"
                    >
                      Retry
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          ) : repos.length === 0 ? (
            <div className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] px-4 py-8 text-center text-[14px] text-[color:var(--text-secondary)]">
              All repos are already connected
            </div>
          ) : (
            <>
              <label className="relative mb-4 block">
                <span className="sr-only">Search available repositories</span>
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
                <input
                  className="h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] pl-10 pr-10 text-[14px] text-[color:var(--text-primary)] outline-none transition-colors placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]"
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Search available repos"
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
              </label>
              <div className="mb-4 flex items-center justify-between gap-4">
                <div className="text-[12px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">
                  {visibleRepos.length} shown
                  <span className="ml-2 normal-case tracking-normal text-[color:var(--text-secondary)]">{repos.length} available total</span>
                </div>
                <button
                  className="text-[12px] font-semibold text-[color:var(--accent-primary)] hover:text-[color:var(--accent-bright)]"
                  onClick={() =>
                    setSelectedIds(allVisibleSelected ? selectedIds.filter((id) => !visibleRepos.some((repo) => repo.github_repo_id === id)) : [...new Set([...selectedIds, ...visibleRepos.map((repo) => repo.github_repo_id)])])
                  }
                  type="button"
                >
                  {allVisibleSelected ? "Deselect shown" : "Select shown"}
                </button>
              </div>
              <div className="max-h-[360px] space-y-3 overflow-y-auto pr-1">
                {visibleRepos.map((repo) => {
                  const selected = selectedIds.includes(repo.github_repo_id);
                  return (
                    <button
                      className={`flex w-full items-start justify-between gap-4 rounded-2xl border px-4 py-4 text-left transition-colors ${
                        selected
                          ? "border-[rgb(var(--accent-primary-rgb)/0.48)] bg-[rgb(var(--accent-primary-rgb)/0.12)]"
                          : "border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] hover:bg-[color:var(--bg-elevated)]"
                      }`}
                      data-testid="available-repo-row"
                      key={repo.github_repo_id}
                      onClick={() => toggleRepo(repo.github_repo_id)}
                      type="button"
                    >
                      <div className="min-w-0">
                        <div className="truncate text-[15px] font-semibold text-[color:var(--text-primary)]">{repo.full_name}</div>
                        <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">
                          {repo.language || "Unknown"} · {repo.private ? "Private" : "Public"} · {repo.default_branch}
                        </div>
                      </div>
                      <div className="shrink-0 text-[color:var(--accent-primary)]">{selected ? <SquareCheckBig className="h-5 w-5" /> : <Square className="h-5 w-5 text-[color:var(--text-tertiary)]" />}</div>
                    </button>
                  );
                })}
                {visibleRepos.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-[color:var(--bg-border)] px-4 py-8 text-center text-[14px] text-[color:var(--text-secondary)]">
                    No repositories match that search.
                  </div>
                ) : null}
              </div>
            </>
          )}
        </div>

        {repos.length > 0 ? (
          <div className="flex items-center justify-between gap-4 border-t border-[color:var(--bg-border)] px-6 py-4">
            <button className="text-[14px] font-semibold text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]" onClick={onClose} type="button">
              Cancel
            </button>
            <button
              className="inline-flex h-11 items-center justify-center rounded-full bg-[color:var(--accent-primary)] px-5 text-[14px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-60"
              data-testid="connect-selected-repos"
              disabled={selectedIds.length === 0 || connecting || success}
              onClick={() => void connectSelectedRepos()}
              type="button"
            >
              {connecting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              {success ? "Connected!" : connecting ? "Connecting…" : `Connect ${selectedIds.length} repos`}
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
