import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { AlertTriangle, ArrowDownRight, ArrowUpRight, CheckCircle2, CircleSlash, Clock3, Code2, GitPullRequest, KeyRound, ShieldAlert, Sparkles, UserRoundCheck } from "lucide-react";

import {
  getDeveloperLeaderboard,
  getBootstrapOrg,
  getMyOrg,
  getV8AccessGrants,
  getV8CoverageSla,
  getV8FleetKpis,
  getV8IntelligenceUsage,
  getV8RiskyAgents,
  getV8RiskyRepos,
  type InsightsAccessGrants,
  type InsightsCoverageSla,
  type InsightsFleetKpis,
  type InsightsIntelligenceUsage,
  type InsightsRiskRanking,
  type InsightsRiskRow,
  type InsightsTrendMetric,
  type DeveloperLeaderboardEntry,
  type DeveloperLeaderboardResponse,
} from "../../../../lib/data";

type InsightsTab = "fleet-kpis" | "developer-track" | "risky-agents" | "risky-repos" | "coverage-sla" | "intelligence-usage" | "access-grants";

const tabs: Array<{ id: InsightsTab; label: string; href: string }> = [
  { id: "fleet-kpis", label: "Fleet KPIs", href: "/insights/fleet-kpis" },
  { id: "developer-track", label: "Developer track", href: "/insights/developer-track" },
  { id: "risky-agents", label: "Risky agents", href: "/insights/risky-agents" },
  { id: "risky-repos", label: "Risky repos", href: "/insights/risky-repos" },
  { id: "coverage-sla", label: "Coverage SLA", href: "/insights/coverage-sla" },
  { id: "intelligence-usage", label: "Intelligence usage", href: "/insights/intelligence-usage" },
  { id: "access-grants", label: "Access grants", href: "/insights/access-grants" },
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
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Fleet risk trends, ranked governance attention, and coverage depth.</p>
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

function percent(value: number): string {
  return `${Math.round(value * 10) / 10}%`;
}

function compactNumber(value: number): string {
  return new Intl.NumberFormat("en-US", { notation: value >= 10000 ? "compact" : "standard" }).format(value);
}

function TrendPill({ row }: { row: DeveloperLeaderboardEntry }) {
  if (!row.trend) return <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-tertiary)]">trend unavailable</span>;
  const tone = row.trend.direction === "up" ? "text-[color:var(--accent-green)]" : row.trend.direction === "down" ? "text-[color:var(--accent-red)]" : "text-[color:var(--text-secondary)]";
  return (
    <span className={`rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs font-semibold ${tone}`}>
      {row.trend.direction} {row.trend.compliance_delta > 0 ? "+" : ""}{row.trend.compliance_delta}% compliance · {row.trend.violations_delta > 0 ? "+" : ""}{row.trend.violations_delta} violations
    </span>
  );
}

function Sparkline({ values }: { values?: Array<number | null> }) {
  const points = values ?? [];
  return (
    <div className="flex h-8 items-end gap-1" aria-label="7 day compliance sparkline">
      {Array.from({ length: 7 }).map((_, index) => {
        const value = points[index];
        const height = value === null || value === undefined ? 3 : Math.max(4, Math.round(value / 5));
        return <span className={`w-2 rounded-full ${value === null || value === undefined ? "bg-[color:var(--bg-border)]" : "bg-[color:var(--accent-primary)]"}`} key={index} style={{ height }} />;
      })}
    </div>
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

function DeveloperRow({ row }: { row: DeveloperLeaderboardEntry }) {
  const riskTotal = row.risk_distribution.red + row.risk_distribution.yellow + row.risk_distribution.green;
  return (
    <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-md bg-[color:var(--accent-primary)]/15 px-2 py-1 text-xs font-semibold text-[color:var(--accent-primary)]">#{row.rank}</span>
            <h2 className="font-semibold text-[color:var(--text-primary)]">{row.login}</h2>
            <TrendPill row={row} />
          </div>
          <p className="mt-2 text-sm text-[color:var(--text-secondary)]">Last active {row.last_active ? new Date(row.last_active).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) : "unknown"}</p>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Sessions</div>
              <div className="mt-2 font-mono text-lg">{row.sessions_count}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Files</div>
              <div className="mt-2 font-mono text-lg">{row.files_touched}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Lines</div>
              <div className="mt-2 font-mono text-lg">{compactNumber(row.lines_changed)}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Risk</div>
              <div className="mt-2 font-mono text-lg">{row.avg_risk_score}</div>
            </div>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">PRs opened</div>
              <div className="mt-2 font-mono text-lg">{row.prs_opened}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">PRs merged</div>
              <div className="mt-2 font-mono text-lg">{row.prs_merged}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">PRs reverted</div>
              <div className="mt-2 font-mono text-lg">{row.prs_reverted}</div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Compliance</div>
                <div className={`mt-2 text-[30px] font-semibold ${row.compliance_pct >= 90 ? "text-[color:var(--accent-green)]" : row.compliance_pct >= 70 ? "text-amber-200" : "text-[color:var(--accent-red)]"}`}>{percent(row.compliance_pct)}</div>
              </div>
              <Sparkline values={row.sparkline} />
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div>
                <div className="font-mono text-lg text-[color:var(--text-primary)]">{row.violations_total}</div>
                <div className="text-xs text-[color:var(--text-tertiary)]">violations</div>
              </div>
              <div>
                <div className="font-mono text-lg text-[color:var(--text-primary)]">{row.warnings_total}</div>
                <div className="text-xs text-[color:var(--text-tertiary)]">warnings</div>
              </div>
            </div>
          </div>

          <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
            <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Risk distribution</div>
            <div className="mt-3 flex h-2 overflow-hidden rounded-full bg-black/40">
              <div className="bg-[color:var(--accent-red)]" style={{ width: riskTotal ? `${(row.risk_distribution.red / riskTotal) * 100}%` : "0%" }} />
              <div className="bg-amber-400" style={{ width: riskTotal ? `${(row.risk_distribution.yellow / riskTotal) * 100}%` : "0%" }} />
              <div className="bg-[color:var(--accent-green)]" style={{ width: riskTotal ? `${(row.risk_distribution.green / riskTotal) * 100}%` : "0%" }} />
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-[color:var(--text-secondary)]">
              <span>red {row.risk_distribution.red}</span>
              <span>yellow {row.risk_distribution.yellow}</span>
              <span>green {row.risk_distribution.green}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-3">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Agent runtimes</div>
          <div className="mt-2 flex flex-wrap gap-2">{row.agent_runtimes.length ? row.agent_runtimes.map((item) => <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={item}>{item}</span>) : <span className="text-xs text-[color:var(--text-tertiary)]">none</span>}</div>
        </div>
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Skills loaded</div>
          <div className="mt-2 flex flex-wrap gap-2">{row.skills_loaded.length ? row.skills_loaded.map((item) => <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={item}>{item}</span>) : <span className="text-xs text-[color:var(--text-tertiary)]">none</span>}</div>
        </div>
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Top violations</div>
          <div className="mt-2 flex flex-wrap gap-2">{row.top_violations.length ? row.top_violations.map((item) => <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={item}>{item}</span>) : <span className="text-xs text-[color:var(--text-tertiary)]">none</span>}</div>
        </div>
      </div>
    </article>
  );
}

export async function DeveloperTrackView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: DeveloperLeaderboardResponse | null = org ? await getDeveloperLeaderboard(accessToken, org.id, 30, "compliance", true) : null;
  const developers = data?.developers ?? [];
  const totalSessions = developers.reduce((total, row) => total + row.sessions_count, 0);
  const totalPrs = developers.reduce((total, row) => total + row.prs_opened, 0);
  const totalViolations = developers.reduce((total, row) => total + row.violations_total, 0);
  const avgCompliance = developers.length ? developers.reduce((total, row) => total + row.compliance_pct, 0) / developers.length : 0;
  return (
    <PageFrame active="developer-track">
      <section className="grid gap-4 md:grid-cols-4">
        <DeveloperMetric detail="Developers represented by the compliance API." icon={<UserRoundCheck className="h-4 w-4" />} label="Developers" value={developers.length} />
        <DeveloperMetric detail="Coding-agent sessions attributed to developers." icon={<Code2 className="h-4 w-4" />} label="Sessions" value={totalSessions} />
        <DeveloperMetric detail="Opened PRs tracked with merge/revert outcomes." icon={<GitPullRequest className="h-4 w-4" />} label="PRs opened" value={totalPrs} />
        <DeveloperMetric detail={`${totalViolations} violations across the window.`} icon={<ShieldAlert className="h-4 w-4" />} label="Avg compliance" value={percent(avgCompliance)} />
      </section>

      <section className="rounded-lg border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
        <p className="text-sm leading-6 text-[color:var(--text-secondary)]">
          Consolidated from the compliance API with `include_trend=true`: rank, sessions, files, lines, PR lifecycle, runtimes, skills, violations, warnings, compliance, risk distribution, top violations, trend, sparkline, and last activity are all shown here.
        </p>
      </section>

      {!data ? <EmptyState label="Developer compliance metrics unavailable" /> : null}
      {data && !developers.length ? <EmptyState label="No developer compliance rows yet" /> : null}
      <section className="space-y-4">
        {developers.map((row) => <DeveloperRow key={row.login} row={row} />)}
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
          const allCovered = repo.critical_operations.every((operation) => operation.covered);
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
                      <span className="text-xs text-[color:var(--text-secondary)]">{operation.skills.length} covering skills</span>
                    </div>
                    {operation.required_skill_categories.length ? (
                      <p className="mt-1 text-xs text-[color:var(--text-tertiary)]">Requires: {operation.required_skill_categories.join(", ")}</p>
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

export async function IntelligenceUsageView() {
  const { accessToken, org } = await resolveOrgAndToken();
  const data: InsightsIntelligenceUsage | null = org ? await getV8IntelligenceUsage(accessToken, org.id) : null;
  const tierUsage = data?.tier_usage ?? [];
  const accessGrants = data?.access_grants ?? [];
  const totalEvents = tierUsage.reduce((total, row) => total + row.events, 0);
  const exposedActors = new Set(accessGrants.map((row) => row.actor_login)).size;
  return (
    <PageFrame active="intelligence-usage">
      <section className="grid gap-4 md:grid-cols-3">
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
      </section>

      {!tierUsage.length && !accessGrants.length ? <IntelligenceUsageEmpty /> : null}

      {tierUsage.length ? (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-[color:var(--accent-primary)]" />
            <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Intelligence Tier Usage</h2>
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {tierUsage.map((row) => (
              <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={`${row.provider}-${row.model}-${row.intelligence_tier}`}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-[color:var(--text-primary)]">{row.provider}</h3>
                    <p className="mt-1 text-xs text-[color:var(--text-secondary)]">{row.model ?? "model unknown"}</p>
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
            <div className="grid grid-cols-[1fr_1fr_1fr_120px_120px] gap-3 bg-black/20 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] max-md:hidden">
              <span>Actor</span>
              <span>Provider</span>
              <span>Scope</span>
              <span>Full</span>
              <span>Tools</span>
            </div>
            {accessGrants.map((row) => (
              <div className="grid gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm first:border-t-0 md:grid-cols-[1fr_1fr_1fr_120px_120px]" key={`${row.actor_login}-${row.provider}-${row.repo_name}-${row.access_scope}`}>
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
          <div className="grid grid-cols-[1.2fr_1fr_1fr_120px_120px_150px] gap-3 bg-black/20 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)] max-lg:hidden">
            <span>Actor</span>
            <span>Provider</span>
            <span>Scope</span>
            <span>Full</span>
            <span>Tools</span>
            <span>Last seen</span>
          </div>
          {grants.map((row) => (
            <div className="grid gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm first:border-t-0 lg:grid-cols-[1.2fr_1fr_1fr_120px_120px_150px]" key={`${row.actor_login}-${row.provider}-${row.repo_name}-${row.access_scope}`}>
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
