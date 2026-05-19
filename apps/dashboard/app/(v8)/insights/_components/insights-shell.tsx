import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { AlertTriangle, ArrowDownRight, ArrowUpRight, CheckCircle2, CircleSlash, Clock3, Code2, ExternalLink, KeyRound, RadioTower, ShieldAlert, Sparkles, UserRoundCheck } from "lucide-react";

import {
  getV8AgentComplianceMetrics,
  getBootstrapOrg,
  getMyOrg,
  getV8AccessGrants,
  getV8CodexRuns,
  getV8CoverageSla,
  getV8DeveloperTrack,
  getV8FleetKpis,
  getV8IntelligenceUsage,
  getV8PlatformOverview,
  getV8ProviderCoverage,
  getV8RiskyAgents,
  getV8RiskyRepos,
  type InsightsAccessGrants,
  type InsightsAgentComplianceMetricBreakdownRow,
  type InsightsAgentComplianceMetricItem,
  type InsightsAgentComplianceMetrics,
  type InsightsCodexRun,
  type InsightsCodexRuns,
  type InsightsCoverageSla,
  type InsightsDeveloperTrack,
  type InsightsDeveloperTrackRow,
  type InsightsFleetKpis,
  type InsightsIntelligenceUsage,
  type InsightsPlatformOverview,
  type InsightsPlatformOverviewRow,
  type InsightsProviderCoverage,
  type InsightsProviderCoverageRow,
  type InsightsRiskRanking,
  type InsightsRiskRow,
  type InsightsTrendMetric,
} from "../../../../lib/data";

type InsightsTab = "overview" | "fleet-kpis" | "developer-track" | "risky-agents" | "risky-repos" | "coverage-sla" | "agent-compliance-metrics" | "agent-runs" | "codex-runs" | "intelligence-usage" | "access-grants" | "provider-coverage";

const tabs: Array<{ id: InsightsTab; label: string; href: string }> = [
  { id: "overview", label: "Overview", href: "/insights" },
  { id: "fleet-kpis", label: "Fleet KPIs", href: "/insights/fleet-kpis" },
  { id: "developer-track", label: "Developer track", href: "/insights/developer-track" },
  { id: "risky-agents", label: "Risky agents", href: "/insights/risky-agents" },
  { id: "risky-repos", label: "Risky repos", href: "/insights/risky-repos" },
  { id: "coverage-sla", label: "Coverage SLA", href: "/insights/coverage-sla" },
  { id: "agent-compliance-metrics", label: "Agent metrics", href: "/insights/agent-compliance-metrics" },
  { id: "agent-runs", label: "Agent runs", href: "/insights/agent-runs" },
  { id: "intelligence-usage", label: "Intelligence usage", href: "/insights/intelligence-usage" },
  { id: "access-grants", label: "Access grants", href: "/insights/access-grants" },
  { id: "provider-coverage", label: "Provider coverage", href: "/insights/provider-coverage" },
];

async function resolveOrgAndToken() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  return { accessToken, org };
}

function TabNav({ active }: { active: InsightsTab }) {
  return (
    <div className="flex flex-wrap gap-2 border-b border-[color:var(--bg-border)] pb-2">
      {tabs.map((tab) => (
        <Link
          className={`whitespace-nowrap border-b-2 px-3 py-2 text-sm font-semibold ${tab.id === active ? "border-[color:var(--accent-primary)] text-[color:var(--text-primary)]" : "border-transparent text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]"}`}
          href={tab.href}
          key={tab.id}
        >
          {tab.label}
        </Link>
      ))}
    </div>
  );
}

function PageFrame({ active, children }: { active: InsightsTab; children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <header>
        <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Skillayer v8</div>
        <h1 className="mt-2 text-2xl font-semibold text-[color:var(--text-primary)]">Insights</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Cross-platform coding-agent spend, usage, risk, and provider coverage.</p>
      </header>
      <TabNav active={active} />
      {children}
    </div>
  );
}

function EmptyState({ label }: { label: string }) {
  return (
    <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center">
      <CircleSlash className="mx-auto h-8 w-8 text-[color:var(--text-tertiary)]" />
      <h2 className="mt-3 font-semibold text-[color:var(--text-primary)]">{label}</h2>
      <p className="mt-1 text-sm text-[color:var(--text-secondary)]">No matching v8 Insights data is available yet.</p>
    </section>
  );
}

function formatMetric(metric: InsightsTrendMetric): string {
  if (metric.current === null) return "N/A";
  if (metric.unit === "percent") return `${Math.round(metric.current * 1000) / 10}%`;
  if (metric.unit === "minutes") return `${Math.round(metric.current)}m`;
  if (metric.unit === "hours") return `${Math.round(metric.current * 10) / 10}h`;
  return new Intl.NumberFormat("en-US").format(metric.current);
}

function MetricTile({ metric }: { metric: InsightsTrendMetric }) {
  const isUnavailable = metric.status === "unavailable";
  const improving = (metric.delta ?? 0) >= 0;
  const TrendIcon = improving ? ArrowUpRight : ArrowDownRight;
  return (
    <article className="min-h-[132px] rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{metric.label}</div>
          <div className={`mt-3 text-[28px] font-semibold ${isUnavailable ? "text-[color:var(--text-tertiary)]" : "text-[color:var(--text-primary)]"}`}>{formatMetric(metric)}</div>
        </div>
        {isUnavailable ? <Clock3 className="h-4 w-4 text-[color:var(--text-tertiary)]" /> : <TrendIcon className="h-4 w-4 text-[color:var(--accent-primary)]" />}
      </div>
      <div className="mt-4 text-xs text-[color:var(--text-secondary)]">
        {isUnavailable ? "Not tracked by current v8 data model" : metric.previous === null ? "No prior-period baseline" : `${metric.delta && metric.delta > 0 ? "+" : ""}${metric.delta ?? 0} vs prior period`}
      </div>
    </article>
  );
}

function RiskTable({ ranking, noun }: { ranking: InsightsRiskRanking | null; noun: string }) {
  const rows = ranking?.rows ?? [];
  if (!rows.length) return <EmptyState label={`No risky ${noun} ranked`} />;
  return (
    <section className="overflow-hidden rounded-lg border border-[color:var(--bg-border)]">
      <div className="grid grid-cols-[1.4fr_90px_110px_130px_130px] gap-3 bg-black/20 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">
        <span>Name</span>
        <span>Volume</span>
        <span>Deny rate</span>
        <span>Sensitivity</span>
        <span>Risk</span>
      </div>
      {rows.map((row: InsightsRiskRow) => (
        <div className="grid grid-cols-[1.4fr_90px_110px_130px_130px] gap-3 border-t border-[color:var(--bg-border)] px-4 py-3 text-sm" key={row.id}>
          <span className="min-w-0 truncate font-semibold text-[color:var(--text-primary)]">{row.name}</span>
          <span>{row.volume}</span>
          <span>{Math.round(row.deny_rate * 1000) / 10}%</span>
          <span>{row.sensitivity_tier ?? row.scope_sensitivity}</span>
          <span className="font-semibold text-[color:var(--accent-primary)]">{Math.round(row.composite_risk * 100) / 100}</span>
        </div>
      ))}
    </section>
  );
}

function compactNumber(value: number): string {
  return new Intl.NumberFormat("en-US", { notation: value >= 10000 ? "compact" : "standard" }).format(value);
}

function formatMoney(value: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: value >= 1000 ? 0 : 2 }).format(value);
}

function MiniBars({ values }: { values: number[] }) {
  const max = Math.max(...values, 1);
  return (
    <div className="flex h-8 items-end gap-1" aria-label="developer compliance volume bars">
      {values.map((value, index) => (
        <span className="w-2 rounded-full bg-[color:var(--accent-primary)]" key={`${value}-${index}`} style={{ height: Math.max(4, Math.round((value / max) * 28)) }} />
      ))}
    </div>
  );
}

function OverviewStat({ label, value, detail, icon }: { label: string; value: string | number; detail: string; icon: React.ReactNode }) {
  return (
    <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
        <div className="text-[color:var(--accent-primary)]">{icon}</div>
      </div>
      <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{value}</div>
      <p className="mt-2 text-xs leading-5 text-[color:var(--text-secondary)]">{detail}</p>
    </article>
  );
}

function PlatformSpendRow({ row, totalCost }: { row: InsightsPlatformOverviewRow; totalCost: number }) {
  const percent = totalCost > 0 ? Math.round((row.cost_usd / totalCost) * 100) : 0;
  return (
    <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(280px,0.9fr)]">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="font-semibold text-[color:var(--text-primary)]">{row.provider}</h2>
            <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]">{row.sessions} sessions</span>
            <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]">{row.users} users</span>
          </div>
          <p className="mt-2 text-sm text-[color:var(--text-secondary)]">
            {compactNumber(row.tokens_total)} tokens across {row.models.length} model{row.models.length === 1 ? "" : "s"}{row.top_model ? `; top model ${row.top_model}` : ""}.
          </p>
          <div className="mt-4 h-2 overflow-hidden rounded-full bg-black/40">
            <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${Math.max(4, percent)}%` }} />
          </div>
          <div className="mt-3 grid gap-2 text-xs text-[color:var(--text-secondary)] sm:grid-cols-3">
            <span>{row.edited_files} edited · {row.explored_files} explored</span>
            <span>{row.searches} searches · {row.commands} commands</span>
            <span>{row.tool_calls} tools · {row.mcp_tool_calls} MCP</span>
          </div>
        </div>
        <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Spend</div>
              <div className="mt-2 text-2xl font-semibold text-[color:var(--text-primary)]">{formatMoney(row.cost_usd)}</div>
            </div>
            <span className="rounded-md bg-[color:var(--accent-primary)]/15 px-2 py-1 text-xs font-semibold text-[color:var(--accent-primary)]">{percent}%</span>
          </div>
          <div className="mt-3 space-y-1 text-xs text-[color:var(--text-secondary)]">
            <div>Provider reported: {formatMoney(row.provider_reported_cost_usd)}</div>
            <div>Skillayer estimated: {formatMoney(row.skillayer_estimated_cost_usd)}</div>
            {row.unknown_cost_usd ? <div>Unknown source: {formatMoney(row.unknown_cost_usd)}</div> : null}
            <div>Full access: {row.full_access_events} · risk signals: {row.risk_signals}</div>
          </div>
        </div>
      </div>
    </article>
  );
}

function DeveloperMetric({ label, value, detail, icon }: { label: string; value: string | number; detail: string; icon: React.ReactNode }) {
  return (
    <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
        <div className="text-[color:var(--accent-primary)]">{icon}</div>
      </div>
      <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{value}</div>
      <p className="mt-2 text-xs leading-5 text-[color:var(--text-secondary)]">{detail}</p>
    </article>
  );
}

function ItemPills({ empty, items }: { empty: string; items: Array<InsightsAgentComplianceMetricItem | string> }) {
  if (!items.length) return <span className="text-xs text-[color:var(--text-tertiary)]">{empty}</span>;
  return (
    <div className="flex flex-wrap gap-2">
      {items.slice(0, 6).map((item) => {
        const key = typeof item === "string" ? item : item.key;
        const label = typeof item === "string" ? item : `${item.label} (${item.count})`;
        return <span className="max-w-full break-words rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={key}>{label}</span>;
      })}
    </div>
  );
}

function DeveloperRow({ row }: { row: InsightsDeveloperTrackRow }) {
  const riskTone = row.risk_band === "high" ? "text-[color:var(--accent-red)]" : row.risk_band === "medium" ? "text-amber-200" : "text-[color:var(--accent-green)]";
  return (
    <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-md bg-[color:var(--accent-primary)]/15 px-2 py-1 text-xs font-semibold text-[color:var(--accent-primary)]">#{row.rank}</span>
            <h2 className="font-semibold text-[color:var(--text-primary)]">{row.actor_login}</h2>
            <span className={`rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs font-semibold ${riskTone}`}>{row.risk_band} risk</span>
          </div>
          <p className="mt-2 text-sm text-[color:var(--text-secondary)]">Last active {row.last_active_at ? new Date(row.last_active_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) : "unknown"}</p>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Events</div>
              <div className="mt-2 font-mono text-lg">{row.events}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Sessions</div>
              <div className="mt-2 font-mono text-lg">{row.sessions}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Tools</div>
              <div className="mt-2 font-mono text-lg">{row.tool_calls}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Risk</div>
              <div className="mt-2 font-mono text-lg">{row.risk_score}</div>
            </div>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Files</div>
              <div className="mt-2 font-mono text-lg">{row.file_targets}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Tokens</div>
              <div className="mt-2 font-mono text-lg">{compactNumber(row.tokens_total)}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Cost</div>
              <div className="mt-2 font-mono text-lg">${row.cost_usd.toFixed(4)}</div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Policy decisions</div>
                <div className="mt-2 text-[30px] font-semibold text-[color:var(--text-primary)]">{row.approvals + row.denials}</div>
              </div>
              <MiniBars values={[row.approvals, row.denials, row.warnings, row.violations, row.errors]} />
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div>
                <div className="font-mono text-lg text-[color:var(--text-primary)]">{row.approvals}</div>
                <div className="text-xs text-[color:var(--text-tertiary)]">approvals</div>
              </div>
              <div>
                <div className="font-mono text-lg text-[color:var(--text-primary)]">{row.denials}</div>
                <div className="text-xs text-[color:var(--text-tertiary)]">denials</div>
              </div>
            </div>
          </div>

          <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
            <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Exposure</div>
            <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
              <span>{row.full_access_events} full access</span>
              <span>{row.autonomous_events} autonomous</span>
              <span>{row.warnings} warnings</span>
              <span>{row.errors} errors</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-3">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Providers</div>
          <div className="mt-2"><ItemPills empty="none" items={row.providers} /></div>
        </div>
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Models</div>
          <div className="mt-2"><ItemPills empty="none" items={row.models} /></div>
        </div>
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Top tools</div>
          <div className="mt-2"><ItemPills empty="none" items={[...row.top_tools, ...row.top_mcp_tools]} /></div>
        </div>
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Repos</div>
          <div className="mt-2"><ItemPills empty="none" items={row.repos} /></div>
        </div>
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Files</div>
          <div className="mt-2"><ItemPills empty="none" items={row.top_files} /></div>
        </div>
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Source records</div>
          <div className="mt-2"><ItemPills empty="none" items={row.source_record_types} /></div>
        </div>
      </div>
    </article>
  );
}

export async function OverviewView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: InsightsPlatformOverview | null = org ? await getV8PlatformOverview(accessToken, org.id) : null;
  const summary = data?.summary;
  const platforms = data?.platforms ?? [];
  return (
    <PageFrame active="overview">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <OverviewStat detail={`${summary?.providers ?? 0} platforms and ${summary?.users ?? 0} developers represented.`} icon={<RadioTower className="h-4 w-4" />} label="Coding platforms" value={summary?.providers ?? 0} />
        <OverviewStat detail={`${compactNumber(summary?.tokens_total ?? 0)} tokens from ${summary?.sessions ?? 0} sessions.`} icon={<Sparkles className="h-4 w-4" />} label="Total tokens" value={compactNumber(summary?.tokens_total ?? 0)} />
        <OverviewStat detail={`${formatMoney(summary?.provider_reported_cost_usd ?? 0)} provider reported · ${formatMoney(summary?.skillayer_estimated_cost_usd ?? 0)} Skillayer estimated.`} icon={<KeyRound className="h-4 w-4" />} label="Total spend" value={formatMoney(summary?.cost_usd ?? 0)} />
        <OverviewStat detail={`${summary?.full_access_events ?? 0} full-access events and ${summary?.risk_signals ?? 0} risk signals.`} icon={<ShieldAlert className="h-4 w-4" />} label="Governance signals" value={(summary?.full_access_events ?? 0) + (summary?.risk_signals ?? 0)} />
      </section>

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(300px,0.8fr)]">
        <div className="space-y-3">
          <div>
            <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">Platform spend and activity</h2>
            <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Compare Codex, Claude Code, and other coding platforms by spend, tokens, files, tools, and risk.</p>
          </div>
          {!data ? <EmptyState label="Coding platform overview unavailable" /> : null}
          {data && !platforms.length ? <EmptyState label="No coding platform telemetry yet" /> : null}
          {platforms.map((row) => <PlatformSpendRow key={row.provider} row={row} totalCost={summary?.cost_usd ?? 0} />)}
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
            <h2 className="font-semibold text-[color:var(--text-primary)]">Cost source</h2>
            <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">
              Spend is split by provenance so provider-reported billing data is not mixed up with Skillayer estimates from token metadata.
            </p>
            <div className="mt-4 space-y-2 text-sm text-[color:var(--text-secondary)]">
              <div className="flex justify-between gap-3"><span>Provider reported</span><span className="font-semibold text-[color:var(--text-primary)]">{formatMoney(summary?.provider_reported_cost_usd ?? 0)}</span></div>
              <div className="flex justify-between gap-3"><span>Skillayer estimated</span><span className="font-semibold text-[color:var(--text-primary)]">{formatMoney(summary?.skillayer_estimated_cost_usd ?? 0)}</span></div>
              <div className="flex justify-between gap-3"><span>Unknown source</span><span className="font-semibold text-[color:var(--text-primary)]">{formatMoney(summary?.unknown_cost_usd ?? 0)}</span></div>
            </div>
          </section>

          <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
            <h2 className="font-semibold text-[color:var(--text-primary)]">What is happening</h2>
            <div className="mt-4 space-y-3">
              {(data?.insights ?? []).map((insight) => (
                <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3" key={insight.title}>
                  <div className={`text-sm font-semibold ${insight.severity === "high" ? "text-[color:var(--accent-red)]" : insight.severity === "medium" ? "text-amber-200" : "text-[color:var(--text-primary)]"}`}>{insight.title}</div>
                  <p className="mt-1 text-xs leading-5 text-[color:var(--text-secondary)]">{insight.detail}</p>
                </div>
              ))}
              {data && !data.insights.length ? <p className="text-sm text-[color:var(--text-secondary)]">No platform insight yet.</p> : null}
            </div>
          </section>
        </aside>
      </section>
    </PageFrame>
  );
}

export async function DeveloperTrackView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: InsightsDeveloperTrack | null = org ? await getV8DeveloperTrack(accessToken, org.id) : null;
  const developers = data?.developers ?? [];
  const summary = data?.summary;
  return (
    <PageFrame active="developer-track">
      <section className="grid gap-4 md:grid-cols-4">
        <DeveloperMetric detail="Developers represented by metadata-only compliance telemetry." icon={<UserRoundCheck className="h-4 w-4" />} label="Developers" value={summary?.developers ?? 0} />
        <DeveloperMetric detail="Provider sessions attributed across coding agents." icon={<Code2 className="h-4 w-4" />} label="Sessions" value={summary?.sessions ?? 0} />
        <DeveloperMetric detail="Tool and MCP activity captured by provider metadata." icon={<RadioTower className="h-4 w-4" />} label="Tool calls" value={summary?.tool_calls ?? 0} />
        <DeveloperMetric detail={`${summary?.violations ?? 0} violations, ${summary?.warnings ?? 0} warnings, ${summary?.errors ?? 0} errors.`} icon={<ShieldAlert className="h-4 w-4" />} label="Risk signals" value={(summary?.violations ?? 0) + (summary?.warnings ?? 0) + (summary?.errors ?? 0)} />
      </section>

      <section className="rounded-lg border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
        <p className="text-sm leading-6 text-[color:var(--text-secondary)]">
          Consolidated from v8 compliance API metadata: developers, providers, repos, models, sessions, tools, MCP tools, files, policy decisions, access exposure, tokens, cost, latency, warnings, violations, errors, risk, source record types, and last activity are shown without raw prompts, chat, diffs, file content, or tool parameters.
        </p>
      </section>

      {!data ? <EmptyState label="Developer compliance metrics unavailable" /> : null}
      {data && !developers.length ? <EmptyState label="No developer compliance rows yet" /> : null}
      <section className="space-y-4">
        {developers.map((row) => <DeveloperRow key={row.actor_login} row={row} />)}
      </section>
    </PageFrame>
  );
}

export async function FleetKpisView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: InsightsFleetKpis | null = org ? await getV8FleetKpis(accessToken, org.id) : null;
  return (
    <PageFrame active="fleet-kpis">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {(data?.metrics ?? []).map((metric) => <MetricTile key={metric.key} metric={metric} />)}
      </section>
      {!data ? <EmptyState label="Fleet KPIs unavailable" /> : null}
    </PageFrame>
  );
}

export async function RiskyAgentsView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data = org ? await getV8RiskyAgents(accessToken, org.id) : null;
  return (
    <PageFrame active="risky-agents">
      <RiskTable ranking={data} noun="agents" />
    </PageFrame>
  );
}

export async function RiskyReposView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data = org ? await getV8RiskyRepos(accessToken, org.id) : null;
  return (
    <PageFrame active="risky-repos">
      <RiskTable ranking={data} noun="repos" />
    </PageFrame>
  );
}

export async function CoverageSlaView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: InsightsCoverageSla | null = org ? await getV8CoverageSla(accessToken, org.id) : null;
  const repos = data?.repos ?? [];
  return (
    <PageFrame active="coverage-sla">
      {data?.product_review_required ? (
        <div className="flex items-start gap-3 rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-100">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{data.product_review_note || "Coverage SLA is running with a placeholder critical-operations taxonomy."}</span>
        </div>
      ) : null}
      {!repos.length ? <EmptyState label="No internal-or-higher repos in SLA scope" /> : null}
      <section className="grid gap-4">
        {repos.map((repo) => {
          const allCovered = repo.critical_operations.length > 0 && repo.critical_operations.every((operation) => operation.covered);
          return (
            <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={repo.repo_id}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="font-semibold text-[color:var(--text-primary)]">{repo.repo_name}</h2>
                  <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Tier: {repo.sensitivity_tier ?? "unknown"} · Policies: {repo.policy_bindings.length}</p>
                </div>
                <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold ${allCovered ? "bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : "bg-red-500/10 text-red-200"}`}>
                  {allCovered ? <CheckCircle2 className="h-3.5 w-3.5" /> : <ShieldAlert className="h-3.5 w-3.5" />}
                  {allCovered ? "Covered" : "Gap"}
                </span>
              </div>
              <div className="mt-4 grid gap-3">
                {repo.critical_operations.map((operation) => (
                  <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4" key={operation.operation_id}>
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="text-sm font-semibold">{operation.label}</h3>
                      <div className="flex flex-wrap gap-2 text-xs text-[color:var(--text-secondary)]">
                        {operation.sla_hours ? <span>{operation.sla_hours}h SLA</span> : null}
                        <span>{operation.skills.length} covering skills</span>
                      </div>
                    </div>
                    {operation.description ? <p className="mt-2 text-xs leading-5 text-[color:var(--text-secondary)]">{operation.description}</p> : null}
                    {operation.required_skill_categories.length ? (
                      <p className="mt-1 text-xs text-[color:var(--text-tertiary)]">Requires: {operation.required_skill_categories.join(", ")}</p>
                    ) : null}
                    {operation.evidence_requirements.length ? (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {operation.evidence_requirements.map((requirement) => (
                          <span className="rounded-md border border-[color:var(--bg-border)] bg-black/15 px-2 py-1 text-[11px] text-[color:var(--text-tertiary)]" key={requirement}>{requirement}</span>
                        ))}
                      </div>
                    ) : null}
                    <div className="mt-3 flex flex-wrap gap-2">
                      {operation.skills.length ? operation.skills.map((skill) => (
                        <span className="rounded-md bg-white/5 px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={skill.id}>{skill.domain} · {skill.score_total}</span>
                      )) : <span className="text-xs text-[color:var(--text-tertiary)]">No covering skill found</span>}
                    </div>
                  </div>
                ))}
              </div>
            </article>
          );
        })}
      </section>
    </PageFrame>
  );
}

function IntelligenceUsageEmpty() {
  return (
    <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center">
      <Sparkles className="mx-auto h-8 w-8 text-[color:var(--text-tertiary)]" />
      <h2 className="mt-3 font-semibold text-[color:var(--text-primary)]">No intelligence telemetry yet</h2>
      <p className="mx-auto mt-1 max-w-2xl text-sm text-[color:var(--text-secondary)]">
        Connect OpenAI Compliance Platform, Anthropic Compliance API, Claude Cowork OTel, Codex CLI, or Cursor sources to populate metadata-only model tier and access exposure rollups.
      </p>
    </section>
  );
}

function ComplianceMetricStat({ label, value, detail }: { label: string; value: string | number; detail: string }) {
  return (
    <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{value}</div>
      <p className="mt-2 text-xs leading-5 text-[color:var(--text-secondary)]">{detail}</p>
    </article>
  );
}

function ComplianceBreakdownTable({ title, rows }: { title: string; rows: InsightsAgentComplianceMetricBreakdownRow[] }) {
  if (!rows.length) return null;
  return (
    <section className="space-y-3">
      <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">{title}</h2>
      <div className="overflow-hidden rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="grid grid-cols-[1.5fr_80px_80px_90px_90px_90px_90px] gap-3 bg-black/20 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] max-xl:hidden">
          <span>Name</span>
          <span>Events</span>
          <span>Users</span>
          <span>Tools</span>
          <span>Files</span>
          <span>Risk</span>
          <span>Cost</span>
        </div>
        {rows.map((row) => (
          <div className="grid gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm first:border-t-0 xl:grid-cols-[1.5fr_80px_80px_90px_90px_90px_90px]" key={row.key}>
            <div>
              <div className="font-semibold text-[color:var(--text-primary)]">{row.label}</div>
              <div className="mt-1 text-xs text-[color:var(--text-tertiary)]">{row.sessions} sessions · {row.tokens_total.toLocaleString("en-US")} tokens</div>
            </div>
            <div className="flex justify-between gap-3 xl:block"><span className="text-xs uppercase text-[color:var(--text-tertiary)] xl:hidden">Events</span>{row.events}</div>
            <div className="flex justify-between gap-3 xl:block"><span className="text-xs uppercase text-[color:var(--text-tertiary)] xl:hidden">Users</span>{row.users}</div>
            <div className="flex justify-between gap-3 xl:block"><span className="text-xs uppercase text-[color:var(--text-tertiary)] xl:hidden">Tools</span>{row.tool_permission_events + row.mcp_tool_events}</div>
            <div className="flex justify-between gap-3 xl:block"><span className="text-xs uppercase text-[color:var(--text-tertiary)] xl:hidden">Files</span>{row.file_targets}</div>
            <div className="flex justify-between gap-3 font-semibold text-[color:var(--accent-primary)] xl:block"><span className="text-xs uppercase text-[color:var(--text-tertiary)] xl:hidden">Risk</span>{row.full_access_events + row.autonomous_events + row.violations + row.errors}</div>
            <div className="flex justify-between gap-3 xl:block"><span className="text-xs uppercase text-[color:var(--text-tertiary)] xl:hidden">Cost</span>${row.cost_usd.toFixed(2)}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function ComplianceMetricChips({ title, items }: { title: string; items: InsightsAgentComplianceMetricItem[] }) {
  if (!items.length) return null;
  return (
    <section className="min-w-0 overflow-hidden rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">{title}</h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {items.map((item) => (
          <span className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={`${title}-${item.key}`}>
            {item.label}: <strong className="text-[color:var(--text-primary)]">{item.count}</strong>
          </span>
        ))}
      </div>
    </section>
  );
}

export async function AgentComplianceMetricsView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: InsightsAgentComplianceMetrics | null = org ? await getV8AgentComplianceMetrics(accessToken, org.id) : null;
  const summary = data?.summary;
  return (
    <PageFrame active="agent-compliance-metrics">
      {!data || !summary ? <EmptyState label="Agent compliance metrics unavailable" /> : null}
      {summary ? (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <ComplianceMetricStat label="Events" value={summary.events} detail={`${summary.users} users across ${summary.providers} providers and ${summary.sessions} sessions.`} />
            <ComplianceMetricStat label="Access risk" value={summary.full_access_events + summary.autonomous_events} detail={`${summary.full_access_events} full-access and ${summary.autonomous_events} autonomous grants.`} />
            <ComplianceMetricStat label="Tools and files" value={summary.tool_permission_events + summary.mcp_tool_events + summary.file_targets} detail={`${summary.tool_permission_events} tool permissions, ${summary.mcp_tool_events} MCP tools, ${summary.file_targets} file targets.`} />
            <ComplianceMetricStat label="Policy outcomes" value={summary.violations + summary.warnings + summary.errors} detail={`${summary.violations} violations, ${summary.warnings} warnings, ${summary.errors} errors.`} />
            <ComplianceMetricStat label="Tokens" value={summary.tokens_total.toLocaleString("en-US")} detail={`${summary.tokens_input.toLocaleString("en-US")} input and ${summary.tokens_output.toLocaleString("en-US")} output tokens.`} />
            <ComplianceMetricStat label="Cost" value={`$${summary.cost_usd.toFixed(2)}`} detail={`${summary.avg_latency_ms ?? "N/A"} ms average latency from compliance metadata.`} />
            <ComplianceMetricStat label="Approvals" value={summary.approvals} detail={`${summary.denials} denial signals from policy decisions and approvals.`} />
            <ComplianceMetricStat label="Repos" value={summary.repos} detail="Repositories observed in normalized metadata-only events." />
          </section>

          <section className="rounded-lg border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
            <p className="text-sm leading-6 text-[color:var(--text-secondary)]">
              Consolidated from normalized `agent.compliance` and coding-agent telemetry records: provider, user, session, model tier, full/autonomous access, tools, MCP calls, file targets, policy decisions, approvals, tokens, cost, latency, warnings, violations, errors, source type, and retention state.
            </p>
          </section>

          <ComplianceBreakdownTable title="By Provider" rows={data.by_provider} />
          <ComplianceBreakdownTable title="By Developer" rows={data.by_actor} />
          <ComplianceBreakdownTable title="By Model" rows={data.by_model} />
          <ComplianceBreakdownTable title="By Repository" rows={data.by_repo} />

          <section className="grid gap-4 xl:grid-cols-2">
            <ComplianceMetricChips title="Tool permissions" items={data.top_tools} />
            <ComplianceMetricChips title="MCP tools" items={data.top_mcp_tools} />
            <ComplianceMetricChips title="File targets" items={data.top_files} />
            <ComplianceMetricChips title="Policy decisions" items={data.policy_decisions} />
            <ComplianceMetricChips title="Approval statuses" items={data.approval_statuses} />
            <ComplianceMetricChips title="Source record types" items={data.source_record_types} />
            <ComplianceMetricChips title="Retention states" items={data.retention_states} />
          </section>
        </>
      ) : null}
    </PageFrame>
  );
}

function CodexRunCard({ run }: { run: InsightsCodexRun }) {
  const metrics = run.activity_metrics;
  return (
    <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="font-semibold text-[color:var(--text-primary)]">{run.provider} background flow</h2>
          <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{run.timestamp ? new Date(run.timestamp).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) : "time unknown"} · {run.actor_login} · {run.repo_name ?? "repo unknown"}</p>
          <p className="mt-2 text-xs text-[color:var(--text-tertiary)]">{run.model ?? "model unknown"}{run.reasoning_tier ? ` · ${run.reasoning_tier}` : ""} · {compactNumber(run.tokens_total)} tokens · ${run.cost_usd.toFixed(2)}</p>
        </div>
        {run.replay_url ? <Link className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs font-semibold text-[color:var(--accent-primary)]" href={run.replay_url}>Replay</Link> : null}
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-6">
        {[
          ["Edited", metrics.edited_files],
          ["Explored", metrics.explored_files],
          ["Searches", metrics.searches],
          ["Lists", metrics.lists],
          ["Commands", metrics.commands],
          ["Tools", metrics.tool_calls],
        ].map(([label, value]) => (
          <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3" key={label}>
            <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
            <div className="mt-2 font-mono text-lg text-[color:var(--text-primary)]">{value}</div>
          </div>
        ))}
      </div>
    </article>
  );
}

export async function CodexRunsView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: InsightsCodexRuns | null = org ? await getV8CodexRuns(accessToken, org.id) : null;
  const summary = data?.summary;
  const runs = data?.runs ?? [];
  return (
    <PageFrame active="agent-runs">
      <section className="grid gap-4 md:grid-cols-4">
        <DeveloperMetric detail="Coding-agent runs captured from metadata-only local/provider telemetry." icon={<Code2 className="h-4 w-4" />} label="Runs" value={summary?.runs ?? 0} />
        <DeveloperMetric detail={`${summary?.edited_files ?? 0} edited files and ${summary?.explored_files ?? 0} explored files.`} icon={<Sparkles className="h-4 w-4" />} label="File activity" value={(summary?.edited_files ?? 0) + (summary?.explored_files ?? 0)} />
        <DeveloperMetric detail={`${summary?.searches ?? 0} searches, ${summary?.lists ?? 0} lists, ${summary?.commands ?? 0} shell commands.`} icon={<RadioTower className="h-4 w-4" />} label="Background ops" value={(summary?.searches ?? 0) + (summary?.lists ?? 0) + (summary?.commands ?? 0)} />
        <DeveloperMetric detail={`${compactNumber(summary?.tokens_total ?? 0)} tokens and $${(summary?.cost_usd ?? 0).toFixed(2)} in this window.`} icon={<KeyRound className="h-4 w-4" />} label="Full access" value={summary?.full_access_runs ?? 0} />
      </section>
      {!data ? <EmptyState label="Agent run telemetry unavailable" /> : null}
      {data && !runs.length ? <EmptyState label="No coding-agent runs captured yet" /> : null}
      <section className="space-y-4">
        {runs.map((run) => <CodexRunCard key={run.id} run={run} />)}
      </section>
    </PageFrame>
  );
}

export async function IntelligenceUsageView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: InsightsIntelligenceUsage | null = org ? await getV8IntelligenceUsage(accessToken, org.id) : null;
  const tierUsage = data?.tier_usage ?? [];
  const accessGrants = data?.access_grants ?? [];
  const peakUsage = data?.peak_usage ?? [];
  const taskModelUsage = data?.task_model_usage ?? [];
  const prPushUsage = data?.pr_push_usage ?? [];
  const recommendations = data?.recommendations ?? [];
  const totalEvents = tierUsage.reduce((total, row) => total + row.events, 0);
  const exposedActors = new Set(accessGrants.map((row) => row.actor_login)).size;
  const peak = peakUsage[0];
  return (
    <PageFrame active="intelligence-usage">
      <section className="grid gap-4 md:grid-cols-3 xl:grid-cols-5">
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Model tier events</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{totalEvents}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">Very-high, high, medium, and low intelligence tier usage.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Access exposures</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{accessGrants.length}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{exposedActors} actors with full-access, autonomous, or tool-permission evidence.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Retention</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">Metadata</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{data?.source ?? "audit_events.metadata"} · raw content disabled by default.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Tokens</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{compactNumber(data?.tokens_total ?? 0)}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">Total model tokens across coding-agent events.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Peak usage</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{peak ? `${peak.hour}:00` : "-"}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{peak ? `${compactNumber(peak.tokens_total)} tokens · ${peak.events} events` : "No hourly usage yet."}</p>
        </article>
      </section>

      {!tierUsage.length && !accessGrants.length ? <IntelligenceUsageEmpty /> : null}

      {recommendations.length ? (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-[color:var(--accent-primary)]" />
            <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Model Routing Recommendations</h2>
          </div>
          <div className="grid gap-3 lg:grid-cols-2">
            {recommendations.map((item) => (
              <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={item.id}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-[color:var(--text-primary)]">{item.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">{item.reason}</p>
                  </div>
                  <span className="rounded-md border border-[color:var(--accent-primary)]/40 px-2 py-1 text-xs font-semibold capitalize text-[color:var(--accent-primary)]">{item.severity}</span>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  <div>
                    <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Current</div>
                    <div className="mt-1 text-sm text-[color:var(--text-primary)]">{item.current_model ?? "unknown"}</div>
                  </div>
                  <div>
                    <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Recommend</div>
                    <div className="mt-1 text-sm text-[color:var(--text-primary)]">{item.recommended_model ?? "review"}</div>
                  </div>
                  <div>
                    <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Token savings</div>
                    <div className="mt-1 text-sm text-[color:var(--text-primary)]">{compactNumber(item.estimated_token_savings)}</div>
                  </div>
                </div>
                <p className="mt-3 text-xs text-[color:var(--text-tertiary)]">{item.evidence}</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {taskModelUsage.length ? (
        <section className="space-y-3">
          <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Task Type by Model</h2>
          <div className="overflow-hidden rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
            <div className="grid grid-cols-[1.2fr_1.2fr_90px_120px_100px_1.5fr] gap-3 bg-black/20 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] max-xl:hidden">
              <span>Task</span>
              <span>Model</span>
              <span>Events</span>
              <span>Tokens</span>
              <span>Cost</span>
              <span>Recommendation</span>
            </div>
            {taskModelUsage.map((row) => (
              <div className="grid gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm first:border-t-0 xl:grid-cols-[1.2fr_1.2fr_90px_120px_100px_1.5fr]" key={`${row.task_type}-${row.provider}-${row.model}-${row.intelligence_tier}`}>
                <div className="font-semibold text-[color:var(--text-primary)]">{row.task_type}</div>
                <div>
                  <div className="text-[color:var(--text-primary)]">{row.model ?? "unknown model"}</div>
                  <div className="mt-1 text-xs text-[color:var(--text-tertiary)]">{row.provider} · {row.intelligence_tier ?? "tier unknown"}</div>
                </div>
                <div>{row.events}</div>
                <div>{compactNumber(row.tokens_total)}</div>
                <div>${row.cost_usd.toFixed(2)}</div>
                <div className="text-[color:var(--text-secondary)]">{row.recommendation_reason ?? "Current route looks reasonable."}</div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {prPushUsage.length ? (
        <section className="space-y-3">
          <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Tokens by PR / Code Push</h2>
          <div className="grid gap-3 lg:grid-cols-2">
            {prPushUsage.map((row) => (
              <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={row.id}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-[color:var(--text-primary)]">{row.label}</h3>
                    <p className="mt-1 text-xs text-[color:var(--text-tertiary)]">{row.repo_name ?? "unknown repo"} · {row.actor_login} · {row.task_type}</p>
                    {row.git_url ? (
                      <a className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-[color:var(--accent-primary)] hover:text-[color:var(--accent-bright)]" href={row.git_url} rel="noreferrer" target="_blank">
                        Open Git evidence <ExternalLink className="h-3 w-3" />
                      </a>
                    ) : null}
                  </div>
                  <span className="rounded-md bg-[color:var(--accent-primary)]/15 px-2 py-1 text-xs font-semibold text-[color:var(--accent-primary)]">{compactNumber(row.tokens_total)} tokens</span>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  <div>
                    <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Model</div>
                    <div className="mt-1 text-sm text-[color:var(--text-primary)]">{row.model ?? "unknown"}</div>
                  </div>
                  <div>
                    <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Cost</div>
                    <div className="mt-1 text-sm text-[color:var(--text-primary)]">${row.cost_usd.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Git / run</div>
                    <div className="mt-1 break-all text-sm text-[color:var(--text-primary)]">{row.pr_number ? `#${row.pr_number}` : row.commit_sha?.slice(0, 12) ?? row.session_id ?? "session"}</div>
                  </div>
                </div>
                {row.recommendation ? <p className="mt-3 text-xs leading-5 text-[color:var(--text-secondary)]">{row.recommendation}</p> : null}
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {tierUsage.length ? (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-[color:var(--accent-primary)]" />
            <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Intelligence Tier Usage</h2>
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {tierUsage.map((row) => (
              <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={`${row.provider}-${row.model}-${row.intelligence_tier}-${row.reasoning_mode}`}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-[color:var(--text-primary)]">{row.provider}</h3>
                    <p className="mt-1 text-xs text-[color:var(--text-secondary)]">{row.model ?? "model unknown"}</p>
                    <p className="mt-1 text-xs text-[color:var(--text-tertiary)]">{row.reasoning_mode ?? "normal"} mode{row.last_seen_at ? ` · last ${new Date(row.last_seen_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}` : ""}</p>
                  </div>
                  <span className="rounded-full bg-[color:var(--accent-primary)]/15 px-2 py-1 text-xs font-semibold text-[color:var(--accent-primary)]">{row.intelligence_tier}</span>
                </div>
                <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <div className="text-[22px] font-semibold text-[color:var(--text-primary)]">{row.events}</div>
                    <div className="text-xs text-[color:var(--text-tertiary)]">events</div>
                  </div>
                  <div>
                    <div className="text-[22px] font-semibold text-[color:var(--text-primary)]">{row.users}</div>
                    <div className="text-xs text-[color:var(--text-tertiary)]">users</div>
                  </div>
                  <div>
                    <div className="text-[22px] font-semibold text-[color:var(--text-primary)]">{compactNumber(row.tokens_total)}</div>
                    <div className="text-xs text-[color:var(--text-tertiary)]">tokens</div>
                  </div>
                  <div>
                    <div className="text-[22px] font-semibold text-[color:var(--text-primary)]">${row.cost_usd.toFixed(2)}</div>
                    <div className="text-xs text-[color:var(--text-tertiary)]">est. cost</div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {accessGrants.length ? (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <KeyRound className="h-4 w-4 text-[color:var(--accent-primary)]" />
            <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Access Grant Exposure</h2>
          </div>
          <div className="overflow-hidden rounded-lg border border-[color:var(--bg-border)]">
            <div className="grid grid-cols-[1fr_1fr_1fr_120px_120px_1.4fr] gap-3 bg-black/20 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] max-md:hidden">
              <span>Actor</span>
              <span>Provider</span>
              <span>Scope</span>
              <span>Full</span>
              <span>Tools</span>
              <span>Top tools</span>
            </div>
            {accessGrants.map((row) => (
              <div className="grid gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm first:border-t-0 md:grid-cols-[1fr_1fr_1fr_120px_120px_1.4fr]" key={`${row.actor_login}-${row.provider}-${row.repo_name}-${row.access_scope}`}>
                <div>
                  <div className="font-semibold text-[color:var(--text-primary)]">{row.actor_login}</div>
                  <div className="mt-1 text-xs text-[color:var(--text-tertiary)]">{row.repo_name ?? "repo unknown"}</div>
                </div>
                <div className="flex items-center justify-between gap-3 text-[color:var(--text-secondary)] md:block">
                  <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] md:hidden">Provider</span>
                  <span>{row.provider}</span>
                </div>
                <div className="flex items-center justify-between gap-3 text-[color:var(--text-secondary)] md:block">
                  <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] md:hidden">Scope</span>
                  <span>{row.access_scope}</span>
                </div>
                <div className="flex items-center justify-between gap-3 font-semibold text-[color:var(--text-primary)] md:block">
                  <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] md:hidden">Full or autonomous</span>
                  <span>{row.full_access_events + row.autonomous_events}</span>
                </div>
                <div className="flex items-center justify-between gap-3 font-semibold text-[color:var(--accent-primary)] md:block">
                  <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] md:hidden">Tool permissions</span>
                  <span>{row.tool_permission_events}</span>
                </div>
                <div className="flex flex-wrap justify-end gap-1 md:justify-start">
                  {(row.tools ?? []).slice(0, 4).map((tool) => (
                    <span className="rounded-sm border border-[color:var(--bg-border)] px-1.5 py-0.5 text-[11px] text-[color:var(--text-secondary)]" key={`${row.actor_login}-${row.provider}-${tool}`}>{tool}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </PageFrame>
  );
}

function AccessGrantsEmpty() {
  return (
    <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center">
      <KeyRound className="mx-auto h-8 w-8 text-[color:var(--text-tertiary)]" />
      <h2 className="mt-3 font-semibold text-[color:var(--text-primary)]">No access grants observed</h2>
      <p className="mx-auto mt-1 max-w-2xl text-sm text-[color:var(--text-secondary)]">
        Full-access, autonomous access, and tool-permission exposure rows appear here after metadata-only agent compliance events are ingested.
      </p>
    </section>
  );
}

export async function AccessGrantsView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: InsightsAccessGrants | null = org ? await getV8AccessGrants(accessToken, org.id) : null;
  const grants = data?.grants ?? [];
  const exposedActors = new Set(grants.map((row) => row.actor_login)).size;
  const fullOrAutonomous = grants.reduce((total, row) => total + row.full_access_events + row.autonomous_events, 0);
  const toolPermissions = grants.reduce((total, row) => total + row.tool_permission_events, 0);

  return (
    <PageFrame active="access-grants">
      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Exposed actors</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{exposedActors}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">Users with full-access, autonomous, or tool-permission evidence.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Full or autonomous</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{fullOrAutonomous}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">Grant events that can change files, repos, or workflow state.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Tool permissions</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{toolPermissions}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{data?.source ?? "audit_events.metadata"} · raw content disabled by default.</p>
        </article>
      </section>

      {!grants.length ? <AccessGrantsEmpty /> : null}

      {grants.length ? (
        <section className="overflow-hidden rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
            <div className="grid grid-cols-[1.2fr_1fr_1fr_100px_100px_1.4fr_150px] gap-3 bg-black/20 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] max-lg:hidden">
            <span>Actor</span>
            <span>Provider</span>
            <span>Scope</span>
            <span>Full</span>
            <span>Tools</span>
            <span>Tool evidence</span>
            <span>Last seen</span>
          </div>
          {grants.map((row) => (
            <div className="grid gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm first:border-t-0 lg:grid-cols-[1.2fr_1fr_1fr_100px_100px_1.4fr_150px]" key={`${row.actor_login}-${row.provider}-${row.repo_name}-${row.access_scope}`}>
              <div>
                <div className="font-semibold text-[color:var(--text-primary)]">{row.actor_login}</div>
                <div className="mt-1 text-xs text-[color:var(--text-tertiary)]">{row.repo_name ?? "repo unknown"}</div>
              </div>
              <div className="flex items-center justify-between gap-3 text-[color:var(--text-secondary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Provider</span>
                <span>{row.provider}</span>
              </div>
              <div className="flex items-center justify-between gap-3 text-[color:var(--text-secondary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Scope</span>
                <span>{row.access_scope}</span>
              </div>
              <div className="flex items-center justify-between gap-3 font-semibold text-[color:var(--text-primary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Full or autonomous</span>
                <span>{row.full_access_events + row.autonomous_events}</span>
              </div>
              <div className="flex items-center justify-between gap-3 font-semibold text-[color:var(--accent-primary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Tool permissions</span>
                <span>{row.tool_permission_events}</span>
              </div>
              <div className="flex flex-wrap justify-end gap-1 lg:justify-start">
                {(row.tools ?? []).slice(0, 5).map((tool) => (
                  <span className="rounded-sm border border-[color:var(--bg-border)] px-1.5 py-0.5 text-[11px] text-[color:var(--text-secondary)]" key={`${row.actor_login}-${row.provider}-${tool}`}>{tool}</span>
                ))}
              </div>
              <div className="flex items-center justify-between gap-3 text-[color:var(--text-secondary)] lg:block">
                <span className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] lg:hidden">Last seen</span>
                <span>{row.last_seen_at ? new Date(row.last_seen_at).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "Unknown"}</span>
              </div>
            </div>
          ))}
        </section>
      ) : null}
    </PageFrame>
  );
}

function providerStatusClass(status: InsightsProviderCoverageRow["status"]): string {
  if (status === "active") return "bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]";
  if (status === "retention-risk") return "bg-red-500/15 text-red-200";
  if (status === "stale" || status === "silent") return "bg-amber-500/15 text-amber-100";
  return "bg-[color:var(--bg-base)] text-[color:var(--text-tertiary)]";
}

function ProviderCoverageRowCard({ row }: { row: InsightsProviderCoverageRow }) {
  const tierEntries = Object.entries(row.intelligence_tiers);
  return (
    <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-semibold text-[color:var(--text-primary)]">{row.label}</h2>
          <p className="mt-1 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{row.category}</p>
        </div>
        <span className={`rounded-full px-2 py-1 text-xs font-semibold ${providerStatusClass(row.status)}`}>{row.status}</span>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2">
        <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <div className="text-[10px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Events</div>
          <div className="mt-2 text-xl font-semibold text-[color:var(--text-primary)]">{row.events}</div>
        </div>
        <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <div className="text-[10px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Users</div>
          <div className="mt-2 text-xl font-semibold text-[color:var(--text-primary)]">{row.users}</div>
        </div>
        <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <div className="text-[10px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Retention</div>
          <div className="mt-2 text-xl font-semibold text-[color:var(--accent-primary)]">{row.retention_days_remaining ?? "N/A"}</div>
        </div>
      </div>

      <div className="mt-4 space-y-2 text-sm text-[color:var(--text-secondary)]">
        <div className="flex justify-between gap-3">
          <span>Connector</span>
          <span className="font-semibold text-[color:var(--text-primary)]">{row.enabled ? "enabled" : row.configured ? "configured" : "unconfigured"}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span>Sync</span>
          <span className="font-semibold text-[color:var(--text-primary)]">{row.last_sync_status ?? "not started"}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span>Last event</span>
          <span className="font-semibold text-[color:var(--text-primary)]">{row.last_event_at ? new Date(row.last_event_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) : "none"}</span>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {row.models.slice(0, 4).map((model) => (
          <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={`${row.connector_id}-${model}`}>{model}</span>
        ))}
        {tierEntries.map(([tier, count]) => (
          <span className="rounded-md bg-[color:var(--accent-primary)]/10 px-2 py-1 text-xs font-semibold text-[color:var(--accent-primary)]" key={`${row.connector_id}-${tier}`}>{tier}: {count}</span>
        ))}
      </div>
    </article>
  );
}

export async function ProviderCoverageView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: InsightsProviderCoverage | null = org ? await getV8ProviderCoverage(accessToken, org.id) : null;
  const rows = data?.rows ?? [];
  const active = rows.filter((row) => row.status === "active").length;
  const atRisk = rows.filter((row) => row.status === "retention-risk" || row.status === "stale" || row.status === "silent").length;
  const configured = rows.filter((row) => row.configured).length;
  return (
    <PageFrame active="provider-coverage">
      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="flex items-center justify-between gap-3">
            <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Active providers</div>
            <RadioTower className="h-4 w-4 text-[color:var(--accent-primary)]" />
          </div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{active}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">Configured providers with recent metadata-only events.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Coverage risk</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{atRisk}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">Silent, stale, or close to the compliance retention window.</p>
        </article>
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Configured</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{configured}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{data?.retention_window_days ?? 30}-day retention window · metadata-only.</p>
        </article>
      </section>

      <section className="rounded-lg border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
        <p className="text-sm leading-6 text-[color:var(--text-secondary)]">
          Provider coverage compares configured compliance connectors with recent `agent.compliance` events so teams can see silent sources before 30-day provider log retention becomes unrecoverable.
        </p>
      </section>

      {!data ? <EmptyState label="Provider coverage unavailable" /> : null}
      {data && !rows.length ? <EmptyState label="No provider connectors in coverage scope" /> : null}
      <section className="grid gap-4 lg:grid-cols-2">
        {rows.map((row) => <ProviderCoverageRowCard key={row.connector_id} row={row} />)}
      </section>
    </PageFrame>
  );
}
