"use client";

import { AlertTriangle, BarChart3, RefreshCcw, ShieldCheck, Sparkles, TrendingUp } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import type { ReactNode } from "react";
import { useCallback, useMemo, useState } from "react";

import { cn } from "@skillayer/ui";
import type { AgentScorecardResponse, AgentScorecardRow } from "../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
const DAY_OPTIONS = [7, 30, 90] as const;

type Props = {
  accessToken: string;
  orgId: string;
  initialData: AgentScorecardResponse | null;
  initialDays: number;
};

const AGENT_LABELS: Record<string, string> = {
  claude_code: "Claude Code",
  codex: "Codex",
  codex_cli: "Codex CLI",
  cursor: "Cursor",
  copilot: "GitHub Copilot",
  github_copilot: "GitHub Copilot",
  gemini_cli: "Gemini CLI",
  devin: "Devin",
  human: "Human",
  mixed: "Mixed",
  unidentified_agent: "Codex CLI",
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

async function fetchAgentScorecard(accessToken: string, orgId: string, days: number): Promise<AgentScorecardResponse> {
  const params = new URLSearchParams({ days: String(days) });
  const response = await fetch(`${API_URL}/orgs/${orgId}/agent-scorecard?${params.toString()}`, {
    headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
    cache: "no-store",
  });
  if (!response.ok) throw new Error((await response.text()) || "Could not load agent scorecard");
  return response.json() as Promise<AgentScorecardResponse>;
}

function numberFormat(value: number): string {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value || 0);
}

function percentFormat(value: number): string {
  return `${Math.round(value || 0)}%`;
}

function riskTone(value: number): string {
  if (value >= 70) return "text-red-200";
  if (value >= 35) return "text-amber-200";
  return "text-[color:var(--accent-green)]";
}

function displayAgent(row: AgentScorecardRow): string {
  return row.agent_label || AGENT_LABELS[row.agent] || row.agent;
}

function SummaryCard({ label, value, icon, tone }: { label: string; value: string; icon: ReactNode; tone?: "green" | "amber" | "red" }) {
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

function RiskDistribution({ row }: { row: AgentScorecardRow }) {
  const green = row.risk_distribution?.green ?? 0;
  const yellow = row.risk_distribution?.yellow ?? 0;
  const red = row.risk_distribution?.red ?? 0;
  const total = Math.max(1, green + yellow + red);

  return (
    <div>
      <div className="flex h-2.5 w-24 overflow-hidden rounded-full bg-white/5" title={`${green} low · ${yellow} medium · ${red} high`}>
        <div className="bg-[color:var(--accent-green)]" style={{ width: `${(green / total) * 100}%` }} />
        <div className="bg-amber-400" style={{ width: `${(yellow / total) * 100}%` }} />
        <div className="bg-red-400" style={{ width: `${(red / total) * 100}%` }} />
      </div>
      <div className="mt-1 text-[11px] text-[color:var(--text-tertiary)]">{green}/{yellow}/{red}</div>
    </div>
  );
}

function SkillPills({ values, emptyLabel }: { values: string[]; emptyLabel: string }) {
  const visible = values.slice(0, 3);
  const more = Math.max(0, values.length - visible.length);

  if (!visible.length) {
    return <span className="text-sm text-[color:var(--text-tertiary)]">{emptyLabel}</span>;
  }

  return (
    <div className="flex flex-wrap gap-1.5">
      {visible.map((value) => (
        <span className="max-w-[170px] truncate rounded-full border border-[color:var(--bg-border)] px-2 py-1 text-[11px] text-[color:var(--text-secondary)]" key={value} title={value}>
          {value}
        </span>
      ))}
      {more > 0 ? <span className="rounded-full bg-white/5 px-2 py-1 text-[11px] text-[color:var(--text-tertiary)]">+{more}</span> : null}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-[28px] border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-6 py-16 text-center">
      <BarChart3 className="mx-auto h-12 w-12 text-[color:var(--text-tertiary)]" />
      <h2 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">No scorecard data yet</h2>
      <p className="mx-auto mt-2 max-w-lg text-sm text-[color:var(--text-secondary)]">Attributed PRs will roll up here once agents open or merge work in connected repositories.</p>
    </div>
  );
}

function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="rounded-[28px] border border-red-500/30 bg-red-500/10 px-6 py-12 text-center">
      <AlertTriangle className="mx-auto h-12 w-12 text-red-300" />
      <h2 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">Could not load agent scorecard</h2>
      <p className="mx-auto mt-2 max-w-2xl text-sm text-red-100/80">{error || "The API did not return a scorecard payload."}</p>
      <button className="mt-6 rounded-lg border border-red-300/40 px-4 py-2 text-sm font-semibold text-red-100 transition-colors hover:bg-red-500/20" onClick={onRetry} type="button">
        Retry
      </button>
    </div>
  );
}

export function AgentScorecardClient({ accessToken, orgId, initialData, initialDays }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [data, setData] = useState<AgentScorecardResponse | null>(initialData);
  const [days, setDays] = useState(initialDays);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const rows = useMemo(() => data?.agents ?? [], [data?.agents]);
  const summary = data?.summary ?? {
    total_prs: rows.reduce((sum, row) => sum + (row.prs || 0), 0),
    total_merged: rows.reduce((sum, row) => sum + (row.merged || 0), 0),
    total_violations: rows.reduce((sum, row) => sum + (row.violations || 0), 0),
    avg_compliance_percent: rows.length ? rows.reduce((sum, row) => sum + (row.compliance_percent || 0), 0) / rows.length : 0,
    avg_risk: rows.length ? rows.reduce((sum, row) => sum + (row.avg_risk || 0), 0) / rows.length : 0,
  };

  const refresh = useCallback(async (nextDays = days) => {
    if (!orgId) {
      setError("No organization is available for this dashboard session.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      setData(await fetchAgentScorecard(accessToken, orgId, nextDays));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown API error");
    } finally {
      setLoading(false);
    }
  }, [accessToken, days, orgId]);

  function selectDays(nextDays: number) {
    setDays(nextDays);
    const params = new URLSearchParams(searchParams.toString());
    params.set("days", String(nextDays));
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    void refresh(nextDays);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-1 text-xs font-semibold text-[color:var(--text-secondary)]">
            <BarChart3 className="h-3.5 w-3.5" /> Agent quality rollup
          </div>
          <h1 className="mt-3 text-[32px] font-semibold tracking-[-0.02em] text-[color:var(--text-primary)]">Agent Scorecard</h1>
          <p className="mt-2 max-w-2xl text-sm text-[color:var(--text-secondary)]">Compare PR volume, merge outcomes, skill compliance, and risk by agent over the selected window.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)] disabled:cursor-wait disabled:opacity-60" disabled={loading} onClick={() => void refresh()} type="button">
          <RefreshCcw className={cn("h-4 w-4", loading && "animate-spin")} /> Refresh
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <SummaryCard icon={<Sparkles className="h-4 w-4" />} label="PRs" value={numberFormat(summary.total_prs)} />
        <SummaryCard icon={<ShieldCheck className="h-4 w-4" />} label="Merged" tone="green" value={numberFormat(summary.total_merged)} />
        <SummaryCard icon={<AlertTriangle className="h-4 w-4" />} label="Violations" tone={summary.total_violations > 0 ? "red" : "green"} value={numberFormat(summary.total_violations)} />
        <SummaryCard icon={<TrendingUp className="h-4 w-4" />} label="Compliance" tone={summary.avg_compliance_percent >= 90 ? "green" : summary.avg_compliance_percent >= 70 ? "amber" : "red"} value={percentFormat(summary.avg_compliance_percent)} />
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
          <div className="text-xs text-[color:var(--text-tertiary)]">
            {data?.generated_at ? `Updated ${new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(data.generated_at))}` : `Last ${days} days`}
          </div>
        </div>
      </section>

      {error ? <ErrorState error={error} onRetry={() => void refresh()} /> : rows.length ? (
        <div className="overflow-hidden rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="hidden grid-cols-[1.1fr_.55fr_.65fr_.75fr_.85fr_.9fr_1.25fr_1.35fr] gap-4 border-b border-[color:var(--bg-border)] bg-black/15 px-5 py-3 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:grid">
            <div>Agent</div>
            <div>PRs</div>
            <div>Merged</div>
            <div>Violations</div>
            <div>Compliance %</div>
            <div>Avg Risk</div>
            <div>Top Skills</div>
            <div>Top Violations</div>
          </div>
          <div className={cn("divide-y divide-[color:var(--bg-border)]", loading && "opacity-60")}>
            {rows.map((row) => {
              const color = AGENT_COLORS[row.agent] ?? "var(--text-secondary)";
              return (
                <article className="relative grid gap-4 px-5 py-5 lg:grid-cols-[1.1fr_.55fr_.65fr_.75fr_.85fr_.9fr_1.25fr_1.35fr] lg:items-center" key={row.agent}>
                  <div className="absolute inset-y-0 left-0 w-1" style={{ backgroundColor: color }} />
                  <div className="min-w-0">
                    <div className="inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-bold" style={{ borderColor: `${color}66`, backgroundColor: `${color}22`, color }}>
                      {displayAgent(row)}
                    </div>
                  </div>
                  <div>
                    <div className="lg:hidden text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">PRs</div>
                    <div className="text-sm font-semibold text-[color:var(--text-primary)]">{numberFormat(row.prs)}</div>
                  </div>
                  <div>
                    <div className="lg:hidden text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Merged</div>
                    <div className="text-sm font-semibold text-[color:var(--text-primary)]">{numberFormat(row.merged)}</div>
                  </div>
                  <div>
                    <div className="lg:hidden text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Violations</div>
                    <div className={cn("text-sm font-semibold", row.violations > 0 ? "text-red-200" : "text-[color:var(--accent-green)]")}>{numberFormat(row.violations)}</div>
                  </div>
                  <div>
                    <div className="lg:hidden text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Compliance %</div>
                    <div className="text-sm font-semibold text-[color:var(--text-primary)]">{percentFormat(row.compliance_percent)}</div>
                  </div>
                  <div>
                    <div className="lg:hidden text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Avg Risk</div>
                    <div className={cn("text-sm font-semibold", riskTone(row.avg_risk))}>{Math.round(row.avg_risk || 0)}</div>
                    <RiskDistribution row={row} />
                  </div>
                  <div>
                    <div className="mb-1 lg:hidden text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Top Skills</div>
                    <SkillPills emptyLabel="No skills" values={row.top_skills ?? []} />
                  </div>
                  <div>
                    <div className="mb-1 lg:hidden text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Top Violations</div>
                    <SkillPills emptyLabel="No violations" values={row.top_violations ?? []} />
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      ) : <EmptyState />}
    </div>
  );
}
