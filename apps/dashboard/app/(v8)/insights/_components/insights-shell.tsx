import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { AlertTriangle, ArrowDownRight, ArrowUpRight, CheckCircle2, CircleSlash, Clock3, ShieldAlert } from "lucide-react";

import {
  getBootstrapOrg,
  getMyOrg,
  getV8CoverageSla,
  getV8FleetKpis,
  getV8RiskyAgents,
  getV8RiskyRepos,
  type InsightsCoverageSla,
  type InsightsFleetKpis,
  type InsightsRiskRanking,
  type InsightsRiskRow,
  type InsightsTrendMetric,
} from "../../../../lib/data";

type InsightsTab = "fleet-kpis" | "risky-agents" | "risky-repos" | "coverage-sla";

const tabs: Array<{ id: InsightsTab; label: string; href: string }> = [
  { id: "fleet-kpis", label: "Fleet KPIs", href: "/insights/fleet-kpis" },
  { id: "risky-agents", label: "Risky agents", href: "/insights/risky-agents" },
  { id: "risky-repos", label: "Risky repos", href: "/insights/risky-repos" },
  { id: "coverage-sla", label: "Coverage SLA", href: "/insights/coverage-sla" },
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
    <div className="flex gap-1 overflow-x-auto border-b border-[color:var(--bg-border)]">
      {tabs.map((tab) => (
        <Link
          className={`border-b-2 px-3 py-2 text-sm font-semibold ${tab.id === active ? "border-[color:var(--accent-primary)] text-[color:var(--text-primary)]" : "border-transparent text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]"}`}
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
          <span>{data.product_review_note}</span>
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
