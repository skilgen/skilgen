"use client";

import { AlertTriangle, CalendarDays, Code2, ExternalLink, FileText, GitPullRequest, RefreshCcw, Search, ShieldAlert, Sparkles, UserRound } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import type { ReactNode } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { cn } from "@skillayer/ui";
import type { MyCodeTodayPR, MyCodeTodayResponse, MyCodeTodaySession } from "../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type Props = {
  accessToken: string;
  orgId: string;
  initialData: MyCodeTodayResponse | null;
  initialDate: string;
  initialLogin: string;
};

const AGENT_LABELS: Record<string, string> = {
  claude_code: "Claude Code",
  codex: "Codex",
  cursor: "Cursor",
  copilot: "Copilot",
  devin: "Devin",
};

const AGENT_COLORS: Record<string, string> = {
  claude_code: "#D97706",
  codex: "#10B981",
  cursor: "#8B5CF6",
  copilot: "#24292F",
  devin: "#3B82F6",
};

function formatTime(value: string | null): string {
  if (!value) return "Open session";
  return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

function uniqueCount(values: string[]): number {
  return new Set(values).size;
}

function riskClass(tier: string | null | undefined): string {
  if (tier === "red") return "border-red-500/40 bg-red-500/12 text-red-200";
  if (tier === "yellow") return "border-amber-500/40 bg-amber-500/12 text-amber-200";
  return "border-[color:var(--accent-green)]/40 bg-[color:var(--accent-green)]/12 text-[color:var(--accent-green)]";
}

async function fetchMyCodeToday(accessToken: string, orgId: string, login: string, date: string): Promise<MyCodeTodayResponse> {
  const params = new URLSearchParams({ login, date });
  const response = await fetch(`${API_URL}/orgs/${orgId}/my-code-today?${params.toString()}`, {
    headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
    cache: "no-store",
  });
  if (!response.ok) throw new Error((await response.text()) || "Could not load My Code Today");
  return response.json() as Promise<MyCodeTodayResponse>;
}

function SummaryCard({ label, value, tone, icon }: { label: string; value: number | string; tone?: "red" | "amber" | "green"; icon: ReactNode }) {
  return (
    <div className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">{label}</span>
        <span className={cn("rounded-lg p-2", tone === "red" ? "bg-red-500/12 text-red-200" : tone === "amber" ? "bg-amber-500/12 text-amber-200" : tone === "green" ? "bg-[color:var(--accent-green)]/12 text-[color:var(--accent-green)]" : "bg-white/5 text-[color:var(--text-secondary)]")}>{icon}</span>
      </div>
      <div className="mt-3 text-2xl font-semibold text-[color:var(--text-primary)]">{value}</div>
    </div>
  );
}

function EmptyState({ date }: { date: string }) {
  return (
    <div className="rounded-[28px] border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-6 py-16 text-center">
      <CalendarDays className="mx-auto h-12 w-12 text-[color:var(--text-tertiary)]" />
      <h2 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">No agent activity on this date</h2>
      <p className="mx-auto mt-2 max-w-lg text-sm text-[color:var(--text-secondary)]">No attributed sessions were found for {date}. Pick another date or connect an agent to start tracking your work.</p>
      <Link className="mt-6 inline-flex rounded-lg bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-black transition-colors hover:bg-[color:var(--accent-bright)]" href="/dashboard/connect">
        Connect an agent
      </Link>
    </div>
  );
}

function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="rounded-[28px] border border-red-500/30 bg-red-500/10 px-6 py-12 text-center">
      <AlertTriangle className="mx-auto h-12 w-12 text-red-300" />
      <h2 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">Could not load your day</h2>
      <p className="mx-auto mt-2 max-w-2xl text-sm text-red-100/80">{error}</p>
      <button className="mt-6 rounded-lg border border-red-300/40 px-4 py-2 text-sm font-semibold text-red-100 transition-colors hover:bg-red-500/20" onClick={onRetry} type="button">
        Retry
      </button>
    </div>
  );
}

function SessionCard({ session }: { session: MyCodeTodaySession }) {
  const agentColor = AGENT_COLORS[session.agent_runtime] ?? "var(--text-secondary)";
  const visibleSkills = session.skills_loaded.slice(0, 4);
  const moreSkills = Math.max(0, session.skills_loaded.length - visibleSkills.length);
  return (
    <article className="relative overflow-hidden rounded-[22px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5 transition-colors hover:border-[color:var(--accent-primary)]/60">
      <div className="absolute inset-y-0 left-0 w-1" style={{ backgroundColor: agentColor }} />
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-bold" style={{ borderColor: `${agentColor}66`, backgroundColor: `${agentColor}22`, color: agentColor }}>
              <Sparkles className="mr-1.5 h-3.5 w-3.5" />
              {AGENT_LABELS[session.agent_runtime] ?? session.agent_runtime}
            </span>
            <span className="text-xs text-[color:var(--text-tertiary)]">
              {formatTime(session.started_at)} → {formatTime(session.ended_at)}
            </span>
            {session.outcome ? <span className="rounded-full bg-white/5 px-2 py-1 text-xs text-[color:var(--text-secondary)]">{session.outcome}</span> : null}
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl border border-[color:var(--bg-border)] bg-black/15 p-3">
              <div className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Files touched</div>
              <div className="mt-2 text-lg font-semibold text-[color:var(--text-primary)]">{uniqueCount(session.files_touched)}</div>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {session.files_touched.slice(0, 3).map((file) => (
                  <span className="max-w-full truncate rounded-md bg-black/25 px-2 py-1 font-mono text-[11px] text-[color:var(--text-secondary)]" key={file}>{file}</span>
                ))}
                {session.files_touched.length > 3 ? <span className="rounded-md bg-white/5 px-2 py-1 text-[11px] text-[color:var(--text-tertiary)]">+{session.files_touched.length - 3}</span> : null}
              </div>
            </div>
            <div className="rounded-xl border border-[color:var(--bg-border)] bg-black/15 p-3">
              <div className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Skills loaded</div>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {visibleSkills.length ? visibleSkills.map((skill) => <span className="rounded-full border border-[color:var(--bg-border)] px-2 py-1 text-[11px] text-[color:var(--text-secondary)]" key={skill}>{skill}</span>) : <span className="text-sm text-[color:var(--text-tertiary)]">No skills recorded</span>}
                {moreSkills ? <span className="rounded-full bg-white/5 px-2 py-1 text-[11px] text-[color:var(--text-tertiary)]">+{moreSkills}</span> : null}
              </div>
            </div>
          </div>
        </div>
        <div className="w-full lg:w-[240px]">
          {session.pr ? (
            <Link className="block rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-4 transition-colors hover:border-[color:var(--accent-primary)]/70" href={`/dashboard/agent-prs?pr=${session.pr.id}`}>
              <div className="flex items-center justify-between gap-3">
                <span className="inline-flex items-center text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]"><GitPullRequest className="mr-1.5 h-3.5 w-3.5" />PR #{session.pr.github_pr_number}</span>
                <span className={cn("rounded-full border px-2 py-1 text-[11px] font-semibold capitalize", riskClass(session.pr.risk_tier))}>{session.pr.risk_tier}</span>
              </div>
              <div className="mt-3 line-clamp-2 text-sm font-semibold text-[color:var(--text-primary)]">{session.pr.title}</div>
              <div className="mt-3 inline-flex items-center text-xs font-semibold text-[color:var(--accent-primary)]">Open PR context <ExternalLink className="ml-1 h-3.5 w-3.5" /></div>
            </Link>
          ) : (
            <div className="rounded-2xl border border-dashed border-[color:var(--bg-border)] bg-black/10 p-4 text-sm text-[color:var(--text-secondary)]">No PR attributed to this session yet.</div>
          )}
        </div>
      </div>
    </article>
  );
}

function PrCard({ pr }: { pr: MyCodeTodayPR }) {
  return (
    <Link className="block rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 transition-colors hover:border-[color:var(--accent-primary)]/70" href={`/dashboard/agent-prs?pr=${pr.id}`}>
      <div className="flex items-center justify-between gap-3">
        <span className="inline-flex items-center text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]"><GitPullRequest className="mr-1.5 h-3.5 w-3.5" />PR #{pr.github_pr_number}</span>
        <span className={cn("rounded-full border px-2 py-1 text-[11px] font-semibold capitalize", riskClass(pr.risk_tier))}>{pr.risk_tier}</span>
      </div>
      <div className="mt-3 line-clamp-2 text-sm font-semibold text-[color:var(--text-primary)]">{pr.title}</div>
      <div className="mt-3 flex items-center justify-between gap-3 text-xs">
        <span className="capitalize text-[color:var(--text-secondary)]">{pr.state ?? "open"}</span>
        <span className="inline-flex items-center font-semibold text-[color:var(--accent-primary)]">Open PR context <ExternalLink className="ml-1 h-3.5 w-3.5" /></span>
      </div>
    </Link>
  );
}

export function MyCodeTodayClient({ accessToken, orgId, initialData, initialDate, initialLogin }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const loginInputRef = useRef<HTMLInputElement>(null);
  const [data, setData] = useState<MyCodeTodayResponse | null>(initialData);
  const [date, setDate] = useState(initialDate);
  const [login, setLogin] = useState(initialLogin);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const summary = data?.summary ?? { total_sessions: 0, total_files: 0, skills_used: [], prs_opened: 0, prs_merged: 0, violations: 0, warnings: 0 };
  const sessions = useMemo(() => data?.sessions ?? [], [data?.sessions]);
  const prs = useMemo(() => data?.prs ?? [], [data?.prs]);

  const refresh = useCallback(async (nextLogin = login, nextDate = date) => {
    if (!orgId || !nextLogin) return;
    setLoading(true);
    setError("");
    try {
      setData(await fetchMyCodeToday(accessToken, orgId, nextLogin, nextDate));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown API error");
    } finally {
      setLoading(false);
    }
  }, [accessToken, date, login, orgId]);

  const setUrlState = useCallback((nextLogin: string, nextDate: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("login", nextLogin);
    params.set("date", nextDate);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }, [pathname, router, searchParams]);

  function applyFilters(nextLogin = login, nextDate = date) {
    setUrlState(nextLogin, nextDate);
    void refresh(nextLogin, nextDate);
  }

  useEffect(() => {
    const interval = window.setInterval(() => void refresh(), 60000);
    return () => window.clearInterval(interval);
  }, [refresh]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") {
        event.preventDefault();
        loginInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-1 text-xs font-semibold text-[color:var(--text-secondary)]">
            <UserRound className="h-3.5 w-3.5" /> Personal agent activity
          </div>
          <h1 className="mt-3 text-[32px] font-semibold tracking-[-0.02em] text-[color:var(--text-primary)]">My Code Today</h1>
          <p className="mt-2 max-w-2xl text-sm text-[color:var(--text-secondary)]">A daily view of the agent sessions, skills, files, and PRs attributed to this developer.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)] disabled:cursor-wait disabled:opacity-60" disabled={loading} onClick={() => void refresh()} type="button">
          <RefreshCcw className={cn("h-4 w-4", loading && "animate-spin")} /> Refresh
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
        <SummaryCard icon={<Code2 className="h-4 w-4" />} label="Sessions" value={summary.total_sessions} />
        <SummaryCard icon={<FileText className="h-4 w-4" />} label="Files" value={summary.total_files} />
        <SummaryCard icon={<GitPullRequest className="h-4 w-4" />} label="PRs Opened" value={summary.prs_opened} />
        <SummaryCard icon={<GitPullRequest className="h-4 w-4" />} label="PRs Merged" tone={summary.prs_merged > 0 ? "green" : undefined} value={summary.prs_merged} />
        <SummaryCard icon={<ShieldAlert className="h-4 w-4" />} label="Violations" tone={summary.violations > 0 ? "red" : "green"} value={summary.violations} />
        <SummaryCard icon={<AlertTriangle className="h-4 w-4" />} label="Warnings" tone={summary.warnings > 0 ? "amber" : "green"} value={summary.warnings} />
      </div>

      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="grid gap-3 md:grid-cols-[180px_1fr_150px]">
          <label>
            <span className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Date</span>
            <input className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm text-[color:var(--text-primary)] outline-none transition-colors focus:border-[color:var(--accent-primary)]" onChange={(event) => { setDate(event.target.value); applyFilters(login, event.target.value); }} type="date" value={date} />
          </label>
          <label>
            <span className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">GitHub login</span>
            <div className="relative mt-2">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
              <input className="h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-black/15 pl-9 pr-3 text-sm text-[color:var(--text-primary)] outline-none transition-colors focus:border-[color:var(--accent-primary)]" onChange={(event) => setLogin(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") applyFilters(event.currentTarget.value, date); }} ref={loginInputRef} value={login} />
            </div>
          </label>
          <button className="mt-6 h-11 rounded-xl bg-[color:var(--accent-primary)] px-4 text-sm font-semibold text-black transition-colors hover:bg-[color:var(--accent-bright)]" onClick={() => applyFilters()} type="button">
            Apply
          </button>
        </div>
      </section>

      {summary.skills_used.length ? (
        <div className="flex flex-wrap gap-2 rounded-2xl border border-[color:var(--bg-border)] bg-black/10 p-3">
          <span className="px-1 py-1 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Skills used</span>
          {summary.skills_used.slice(0, 12).map((skill) => <span className="rounded-full border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={skill}>{skill}</span>)}
        </div>
      ) : null}

      {error ? <ErrorState error={error} onRetry={() => void refresh()} /> : sessions.length || prs.length ? (
        <div className="space-y-5">
          {prs.length ? (
            <section className="space-y-3">
              <div>
                <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">PR activity</h2>
                <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Pull requests authored by this developer on the selected date.</p>
              </div>
              <div className="grid gap-3 lg:grid-cols-2">
                {prs.map((pr) => <PrCard key={pr.id} pr={pr} />)}
              </div>
            </section>
          ) : null}
          {sessions.length ? (
            <section className="space-y-3">
              <div>
                <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">Agent sessions</h2>
                <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Sessions with loaded skills and file touch data.</p>
              </div>
              {sessions.map((session) => <SessionCard key={session.session_id} session={session} />)}
            </section>
          ) : null}
        </div>
      ) : <EmptyState date={date} />}
    </div>
  );
}
