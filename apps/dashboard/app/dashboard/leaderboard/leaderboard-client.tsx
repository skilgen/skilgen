"use client";

import { AlertTriangle, ChevronDown, FileText, GitPullRequest, RefreshCcw, ShieldCheck, Trophy, UsersRound } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { cn } from "@skillayer/ui";
import type { DeveloperLeaderboardEntry, DeveloperLeaderboardResponse } from "../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
const DAY_OPTIONS = [7, 30, 90] as const;
const SORT_OPTIONS = [
  { value: "compliance", label: "Compliance %" },
  { value: "prs", label: "PRs Merged" },
  { value: "sessions", label: "Sessions" },
  { value: "violations", label: "Violations" },
  { value: "lines", label: "Lines Changed" },
] as const;

const AGENT_LABELS: Record<string, string> = {
  claude_code: "Claude",
  codex: "Codex",
  cursor: "Cursor",
  copilot: "Copilot",
  devin: "Devin",
  human: "Human",
  mixed: "Mixed",
};

const AGENT_COLORS: Record<string, string> = {
  claude_code: "#D97706",
  codex: "#10B981",
  cursor: "#8B5CF6",
  copilot: "#24292F",
  devin: "#3B82F6",
  human: "var(--text-secondary)",
  mixed: "var(--accent-primary)",
};

type Props = {
  accessToken: string;
  orgId: string;
  initialDays: number;
  initialSortBy: string;
};

async function fetchLeaderboard(accessToken: string, orgId: string, days: number, sortBy: string): Promise<DeveloperLeaderboardResponse> {
  const params = new URLSearchParams({ days: String(days), sort_by: sortBy });
  const response = await fetch(`${API_URL}/orgs/${orgId}/developer-leaderboard?${params.toString()}`, {
    headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
    cache: "no-store",
  });
  if (!response.ok) throw new Error((await response.text()) || "Could not load leaderboard");
  return response.json() as Promise<DeveloperLeaderboardResponse>;
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value || 0);
}

function relativeTime(value: string | null): string {
  if (!value) return "No activity";
  const deltaMs = Date.now() - new Date(value).getTime();
  const absMs = Math.abs(deltaMs);
  const units: Array<[Intl.RelativeTimeFormatUnit, number]> = [
    ["day", 86400000],
    ["hour", 3600000],
    ["minute", 60000],
  ];
  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
  for (const [unit, size] of units) {
    if (absMs >= size || unit === "minute") {
      return formatter.format(Math.round(-deltaMs / size), unit);
    }
  }
  return "just now";
}

function complianceTone(value: number): string {
  if (value >= 80) return "bg-[color:var(--accent-green)] text-[color:var(--accent-green)]";
  if (value >= 50) return "bg-amber-400 text-amber-200";
  return "bg-red-400 text-red-200";
}

function riskTone(value: number): string {
  if (value >= 70) return "bg-red-400 text-red-200";
  if (value >= 30) return "bg-amber-400 text-amber-200";
  return "bg-[color:var(--accent-green)] text-[color:var(--accent-green)]";
}

function mergedTone(row: DeveloperLeaderboardEntry): string {
  if (row.prs_opened === 0) return "text-[color:var(--text-secondary)]";
  if (row.prs_merged === row.prs_opened) return "text-[color:var(--accent-green)]";
  if (row.prs_merged > 0) return "text-amber-200";
  return "text-red-200";
}

function SkillPills({ values, variant = "default" }: { values: string[]; variant?: "default" | "danger" }) {
  const visible = values.slice(0, 2);
  const hidden = values.length - visible.length;
  if (!visible.length) return <span className="text-xs text-[color:var(--text-tertiary)]">None</span>;
  return (
    <div className="flex flex-wrap gap-1.5">
      {visible.map((value) => (
        <span
          className={cn(
            "whitespace-nowrap rounded-full border px-2 py-1 text-[11px]",
            variant === "danger"
              ? "border-red-500/30 bg-red-500/10 text-red-100"
              : "border-[color:var(--bg-border)] bg-white/5 text-[color:var(--text-secondary)]",
          )}
          key={value}
        >
          {value}
        </span>
      ))}
      {hidden > 0 ? <span className="whitespace-nowrap rounded-full bg-white/5 px-2 py-1 text-[11px] text-[color:var(--text-tertiary)]">+{hidden} more</span> : null}
    </div>
  );
}

function AgentPills({ values }: { values: string[] }) {
  const visible = values.slice(0, 2);
  const hidden = values.length - visible.length;
  if (!visible.length) return <span className="text-xs text-[color:var(--text-tertiary)]">None</span>;
  return (
    <div className="flex flex-wrap gap-1.5">
      {visible.map((value) => {
        const color = AGENT_COLORS[value] ?? "var(--text-secondary)";
        return (
          <span className="whitespace-nowrap rounded-full border px-2 py-1 text-[11px] font-semibold" key={value} style={{ borderColor: `${color}66`, backgroundColor: `${color}1F`, color }}>
            {AGENT_LABELS[value] ?? value}
          </span>
        );
      })}
      {hidden > 0 ? <span className="whitespace-nowrap rounded-full bg-white/5 px-2 py-1 text-[11px] text-[color:var(--text-tertiary)]">+{hidden}</span> : null}
    </div>
  );
}

function PodiumCard({ row, index }: { row: DeveloperLeaderboardEntry; index: number }) {
  const medals = ["🥇", "🥈", "🥉"];
  const tones = ["border-amber-300/45 bg-amber-300/10", "border-slate-300/35 bg-slate-300/10", "border-orange-300/35 bg-orange-300/10"];
  return (
    <button
      className={cn("min-h-[150px] rounded-[22px] border p-5 text-left transition-colors hover:border-[color:var(--accent-primary)]", tones[index] ?? "border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]")}
      onClick={() => { window.location.href = `/dashboard/my-code-today?login=${encodeURIComponent(row.login)}`; }}
      type="button"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-3xl" aria-hidden>{medals[index]}</span>
        <span className="rounded-full bg-black/20 px-2 py-1 text-[11px] font-semibold text-[color:var(--text-secondary)]">#{row.rank}</span>
      </div>
      <div className="mt-4 text-lg font-semibold text-[color:var(--text-primary)]">@{row.login}</div>
      <div className="mt-2 text-3xl font-semibold text-[color:var(--text-primary)]">{Math.round(row.compliance_pct)}%</div>
      <div className="mt-3 flex flex-wrap gap-2 text-xs text-[color:var(--text-secondary)]">
        <span>{formatNumber(row.sessions_count)} sessions</span>
        <span>{formatNumber(row.prs_merged)} merged</span>
      </div>
    </button>
  );
}

function EmptyState({ days }: { days: number }) {
  return (
    <div className="rounded-[28px] border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-6 py-16 text-center">
      <Trophy className="mx-auto h-12 w-12 text-[color:var(--text-tertiary)]" />
      <h2 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">No developer activity in the last {days} days</h2>
      <p className="mx-auto mt-2 max-w-lg text-sm text-[color:var(--text-secondary)]">Agent sessions and attributed PRs will appear here once developers start shipping through connected repos.</p>
      <a className="mt-6 inline-flex rounded-lg bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-black transition-colors hover:bg-[color:var(--accent-bright)]" href="/dashboard/connect">
        Connect agents
      </a>
    </div>
  );
}

function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="rounded-[28px] border border-red-500/30 bg-red-500/10 px-6 py-12 text-center">
      <AlertTriangle className="mx-auto h-12 w-12 text-red-300" />
      <h2 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">Could not load leaderboard</h2>
      <p className="mx-auto mt-2 max-w-2xl text-sm text-red-100/80">{error || "The leaderboard API did not return a usable response."}</p>
      <button className="mt-6 rounded-lg border border-red-300/40 px-4 py-2 text-sm font-semibold text-red-100 transition-colors hover:bg-red-500/20" onClick={onRetry} type="button">
        Retry
      </button>
    </div>
  );
}

export function LeaderboardClient({ accessToken, orgId, initialDays, initialSortBy }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [days, setDays] = useState(initialDays);
  const [sortBy, setSortBy] = useState(initialSortBy);
  const [data, setData] = useState<DeveloperLeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const developers = useMemo(() => data?.developers ?? [], [data?.developers]);

  const refresh = useCallback(async (nextDays = days, nextSortBy = sortBy) => {
    if (!orgId) {
      setError("No organization is available for this dashboard session.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError("");
    try {
      setData(await fetchLeaderboard(accessToken, orgId, nextDays, nextSortBy));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown API error");
    } finally {
      setLoading(false);
    }
  }, [accessToken, days, orgId, sortBy]);

  const setUrlState = useCallback((nextDays: number, nextSortBy: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("days", String(nextDays));
    params.set("sort_by", nextSortBy);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }, [pathname, router, searchParams]);

  function selectDays(nextDays: number) {
    setDays(nextDays);
    setUrlState(nextDays, sortBy);
    void refresh(nextDays, sortBy);
  }

  function selectSort(nextSortBy: string) {
    setSortBy(nextSortBy);
    setUrlState(days, nextSortBy);
    void refresh(days, nextSortBy);
  }

  useEffect(() => {
    void refresh(initialDays, initialSortBy);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const interval = window.setInterval(() => void refresh(), 60000);
    return () => window.clearInterval(interval);
  }, [refresh]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-1 text-xs font-semibold text-[color:var(--text-secondary)]">
            <Trophy className="h-3.5 w-3.5" /> Developer quality rollup
          </div>
          <h1 className="mt-3 text-[32px] font-semibold tracking-[-0.02em] text-[color:var(--text-primary)]">Developer Leaderboard</h1>
          <p className="mt-2 max-w-2xl text-sm text-[color:var(--text-secondary)]">Rank developers by agent sessions, PR outcomes, skill compliance, risk, and shipped code volume.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)] disabled:cursor-wait disabled:opacity-60" disabled={loading} onClick={() => void refresh()} type="button">
          <RefreshCcw className={cn("h-4 w-4", loading && "animate-spin")} /> Refresh
        </button>
      </div>

      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex rounded-xl border border-[color:var(--bg-border)] bg-black/15 p-1">
            {DAY_OPTIONS.map((option) => (
              <button
                className={cn("h-9 rounded-lg px-4 text-sm font-semibold transition-colors", days === option ? "bg-[color:var(--accent-primary)] text-black" : "text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]")}
                disabled={loading}
                key={option}
                onClick={() => selectDays(option)}
                type="button"
              >
                {option}d
              </button>
            ))}
          </div>
          <label className="relative">
            <span className="sr-only">Sort leaderboard</span>
            <select className="h-10 appearance-none rounded-xl border border-[color:var(--bg-border)] bg-black/15 pl-3 pr-9 text-sm font-semibold text-[color:var(--text-primary)] outline-none transition-colors hover:border-[color:var(--accent-primary)] focus:border-[color:var(--accent-primary)]" onChange={(event) => selectSort(event.target.value)} value={sortBy}>
              {SORT_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
          </label>
        </div>
      </section>

      {loading && !data ? <LeaderboardSkeletonInline /> : error ? <ErrorState error={error} onRetry={() => void refresh()} /> : developers.length === 0 ? <EmptyState days={days} /> : (
        <>
          <div className="grid gap-4 lg:grid-cols-3">
            {developers.slice(0, 3).map((row, index) => <PodiumCard index={index} key={row.login} row={row} />)}
          </div>

          <div className={cn("overflow-x-auto rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]", loading && "opacity-70")}>
            <table className="min-w-[1680px] w-full border-collapse text-left">
              <thead className="border-b border-[color:var(--bg-border)] bg-black/15 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">
                <tr>
                  {["#", "Developer", "Sessions", "Files", "Lines", "PRs", "Merged", "Violations", "Warnings", "Compliance", "Avg Risk", "Agents", "Top Skills", "Top Violations", "Last Active"].map((heading) => (
                    <th className="px-4 py-3" key={heading}>{heading}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[color:var(--bg-border)]">
                {developers.map((row) => {
                  const complianceClass = complianceTone(row.compliance_pct);
                  const riskClass = riskTone(row.avg_risk_score);
                  return (
                    <tr className="cursor-pointer transition-colors hover:bg-white/[0.03]" key={row.login} onClick={() => router.push(`/dashboard/my-code-today?login=${encodeURIComponent(row.login)}`)}>
                      <td className="px-4 py-4 text-sm font-semibold text-[color:var(--text-secondary)]">{row.rank}</td>
                      <td className="px-4 py-4">
                        <a className="font-semibold text-[color:var(--text-primary)] transition-colors hover:text-[color:var(--accent-primary)]" href={`/dashboard/my-code-today?login=${encodeURIComponent(row.login)}`} onClick={(event) => event.stopPropagation()}>
                          @{row.login}
                        </a>
                      </td>
                      <td className="px-4 py-4 text-sm text-[color:var(--text-secondary)]">{formatNumber(row.sessions_count)}</td>
                      <td className="px-4 py-4 text-sm text-[color:var(--text-secondary)]">{formatNumber(row.files_touched)}</td>
                      <td className="px-4 py-4 font-mono text-sm text-[color:var(--text-secondary)]">{formatNumber(row.lines_changed)}</td>
                      <td className="px-4 py-4 text-sm text-[color:var(--text-secondary)]">{formatNumber(row.prs_opened)}</td>
                      <td className={cn("px-4 py-4 text-sm font-semibold", mergedTone(row))}>{formatNumber(row.prs_merged)}</td>
                      <td className="px-4 py-4">
                        <span className={cn("rounded-full px-2 py-1 text-xs font-semibold", row.violations_total > 0 ? "bg-red-500/15 text-red-200" : "bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]")}>{formatNumber(row.violations_total)}</span>
                      </td>
                      <td className="px-4 py-4">
                        <span className={cn("rounded-full px-2 py-1 text-xs font-semibold", row.warnings_total > 0 ? "bg-amber-500/15 text-amber-200" : "bg-white/5 text-[color:var(--text-secondary)]")}>{formatNumber(row.warnings_total)}</span>
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex min-w-[130px] items-center gap-2">
                          <div className="h-2 flex-1 overflow-hidden rounded-full bg-white/5">
                            <div className={cn("h-full rounded-full", complianceClass.split(" ")[0])} style={{ width: `${Math.max(0, Math.min(100, row.compliance_pct))}%` }} />
                          </div>
                          <span className={cn("w-10 text-right text-xs font-semibold", complianceClass.split(" ")[1])}>{Math.round(row.compliance_pct)}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2">
                          <span className={cn("h-2.5 w-2.5 rounded-full", riskClass.split(" ")[0])} />
                          <span className={cn("text-sm font-semibold", riskClass.split(" ")[1])}>{row.avg_risk_score.toFixed(1)}</span>
                        </div>
                      </td>
                      <td className="px-4 py-4"><AgentPills values={row.agent_runtimes} /></td>
                      <td className="px-4 py-4"><SkillPills values={row.skills_loaded} /></td>
                      <td className="px-4 py-4"><SkillPills values={row.top_violations} variant="danger" /></td>
                      <td className="px-4 py-4 text-sm text-[color:var(--text-secondary)]">{relativeTime(row.last_active)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <div className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
              <UsersRound className="h-4 w-4 text-[color:var(--text-tertiary)]" />
              <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">{formatNumber(developers.length)}</div>
              <div className="text-xs uppercase tracking-wide text-[color:var(--text-tertiary)]">Developers</div>
            </div>
            <div className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
              <GitPullRequest className="h-4 w-4 text-[color:var(--text-tertiary)]" />
              <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">{formatNumber(developers.reduce((sum, row) => sum + row.prs_opened, 0))}</div>
              <div className="text-xs uppercase tracking-wide text-[color:var(--text-tertiary)]">PRs Opened</div>
            </div>
            <div className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
              <FileText className="h-4 w-4 text-[color:var(--text-tertiary)]" />
              <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">{formatNumber(developers.reduce((sum, row) => sum + row.lines_changed, 0))}</div>
              <div className="text-xs uppercase tracking-wide text-[color:var(--text-tertiary)]">Lines Changed</div>
            </div>
            <div className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
              <ShieldCheck className="h-4 w-4 text-[color:var(--text-tertiary)]" />
              <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">{Math.round(developers.reduce((sum, row) => sum + row.compliance_pct, 0) / Math.max(1, developers.length))}%</div>
              <div className="text-xs uppercase tracking-wide text-[color:var(--text-tertiary)]">Avg Compliance</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function LeaderboardSkeletonInline() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-3">
        {[...Array(3)].map((_, index) => (
          <div className="min-h-[150px] rounded-[22px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={index}>
            <div className="h-8 w-12 animate-pulse rounded bg-white/5" />
            <div className="mt-5 h-5 w-32 animate-pulse rounded bg-white/5" />
            <div className="mt-3 h-9 w-24 animate-pulse rounded bg-white/5" />
          </div>
        ))}
      </div>
      <div className="overflow-hidden rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        {[...Array(8)].map((_, row) => (
          <div className="grid min-w-[1680px] grid-cols-[60px_160px_repeat(13,100px)] gap-4 border-b border-[color:var(--bg-border)] p-4" key={row}>
            {[...Array(15)].map((__, cell) => <div className="h-5 animate-pulse rounded bg-white/5" key={cell} />)}
          </div>
        ))}
      </div>
    </div>
  );
}
