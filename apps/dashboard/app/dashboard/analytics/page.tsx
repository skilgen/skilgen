import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import {
  API_URL,
  getAnalyticsCriticality,
  getBootstrapOrg,
  getMyOrg,
  getOrgAnalytics,
  getOrgApiKey,
  getOrgRuntimeBreakdown,
  type AnalyticsSkill,
  type CriticalityItem,
  type RuntimeBreakdownItem,
} from "../../../lib/data";
import { AnalyticsRiskWorkbench, type ColoadTree } from "./coload-tree";
import { LiveFeed } from "./LiveFeed";

export const dynamic = "force-dynamic";

const riskClass = {
  critical: "bg-red-900/30 text-red-300",
  high: "bg-amber-900/30 text-amber-300",
  medium: "bg-blue-900/30 text-blue-300",
  low: "bg-green-900/30 text-green-300",
};

function MetricPanel({ label, value, sub }: { label: string; value: string | number; sub: string }) {
  return (
    <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-2 text-[32px] font-semibold text-[color:var(--text-primary)]">{value}</div>
      <div className="mt-3 text-[12px] text-[color:var(--text-secondary)]">{sub}</div>
    </article>
  );
}

function RiskBadge({ risk }: { risk: CriticalityItem["risk_level"] }) {
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${riskClass[risk]}`}>{risk}</span>;
}

async function getSkillColoadTree(accessToken: string | null, orgId: string): Promise<ColoadTree | null> {
  try {
    const response = await fetch(`${API_URL}/orgs/${orgId}/analytics/skill-coload-tree`, {
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as ColoadTree;
  } catch {
    return null;
  }
}

function SkillRiskRegister({ items }: { items: CriticalityItem[] }) {
  const allLow = items.length > 0 && items.every((item) => item.risk_level === "low");
  return (
    <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <div className="mb-5">
        <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Skill Risk Register</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Skills your agents depend on most — sorted by risk, not score.</p>
      </div>
      {allLow ? <div className="mb-4 rounded-xl border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 p-4 text-sm text-[color:var(--accent-green)]">✓ All skills your agents depend on are high quality — no urgent action needed.</div> : null}
      <div className="overflow-hidden rounded-xl border border-[color:var(--bg-border)]">
        <div className="grid grid-cols-[70px_1.1fr_1fr_110px_2fr_80px] gap-3 bg-black/20 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">
          <span>Rank</span><span>Domain</span><span>Repo</span><span>Risk</span><span>Why</span><span>Action</span>
        </div>
        {items.slice(0, 12).map((item) => (
          <div className="grid grid-cols-[70px_1.1fr_1fr_110px_2fr_80px] gap-3 border-t border-[color:var(--bg-border)] px-4 py-3 text-sm" key={item.skill_id}>
            <span className="font-semibold text-[color:var(--text-secondary)]">#{item.dependency_rank}</span>
            <span className="font-medium text-[color:var(--text-primary)]">{item.domain}</span>
            <span className="text-[color:var(--text-secondary)]">{item.repo_name}</span>
            <RiskBadge risk={item.risk_level} />
            <span className="text-[color:var(--text-secondary)]">{item.risk_reason}</span>
            <Link className="font-semibold text-[color:var(--accent-primary)]" href={`/dashboard/repos/${item.repo_id}/skills/${item.skill_id}${item.risk_level === "critical" || item.risk_level === "high" ? "?tab=edit" : ""}`}>
              {item.risk_level === "critical" ? "Fix →" : item.risk_level === "high" ? "Update →" : "OK"}
            </Link>
          </div>
        ))}
      </div>
    </section>
  );
}

function TopSkillsActionPanels({ criticality, neverLoaded }: { criticality: CriticalityItem[]; neverLoaded: AnalyticsSkill[] }) {
  const loaded = criticality.filter((item) => item.load_count_30d > 0).sort((a, b) => b.load_count_30d - a.load_count_30d).slice(0, 8);
  const max = Math.max(1, ...loaded.map((item) => item.load_count_30d));
  const uniform = loaded.length > 1 && loaded.every((item) => item.load_count_30d === loaded[0].load_count_30d);
  return (
    <section className="grid gap-4 lg:grid-cols-2">
      <article className="rounded-[24px] border border-[color:var(--accent-primary)]/35 bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Most relied on</h2>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">These skills shape the most agent output. Fix high-risk rows first.</p>
        {uniform ? <div className="mt-4 rounded-lg border border-[color:var(--bg-border)] bg-black/20 p-3 text-sm text-[color:var(--text-secondary)]">Codex loaded all skills uniformly in setup — real differentiation will appear after more agent sessions.</div> : null}
        <div className="mt-4 space-y-4">
          {loaded.map((item) => (
            <div key={item.skill_id}>
              <div className="mb-1 flex items-center justify-between gap-3 text-sm">
                <div><span className="font-semibold">{item.domain}</span><span className="text-[color:var(--text-tertiary)]"> · {item.repo_name}</span></div>
                <div className="flex items-center gap-2"><span>{item.load_count_30d} loads</span>{item.is_every_session ? <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs">every session</span> : null}{item.risk_level === "critical" || item.risk_level === "high" ? <RiskBadge risk={item.risk_level} /> : null}</div>
              </div>
              <div className="h-2 rounded-full bg-white/10"><div className="h-2 rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${Math.max(4, (item.load_count_30d / max) * 100)}%` }} /></div>
            </div>
          ))}
        </div>
      </article>
      <article className="rounded-[24px] border border-red-500/35 bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Loaded but never used</h2>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Skills with zero loads are generating zero value. Check agent references.</p>
        <div className="mt-4 space-y-3">
          {neverLoaded.length ? neverLoaded.slice(0, 8).map((skill) => (
            <Link className="block rounded-lg border border-[color:var(--bg-border)] bg-black/15 p-3 text-sm" href={`/dashboard/repos/${skill.repo_id}/skills/${skill.id}`} key={skill.id}>
              <span className="font-semibold">{skill.domain}</span><span className="text-[color:var(--text-tertiary)]"> · {skill.repo_name}</span>
              <div className="mt-1 text-xs text-[color:var(--text-secondary)]">Not referenced in CLAUDE.md?</div>
            </Link>
          )) : <div className="rounded-lg border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 p-4 text-sm text-[color:var(--accent-green)]">✓ All skills are being referenced by agents.</div>}
        </div>
      </article>
    </section>
  );
}

function RuntimeComparison({ runtimes }: { runtimes: RuntimeBreakdownItem[] }) {
  const low = runtimes.find((item) => item.avg_skill_score < 60);
  const narrow = runtimes.find((item) => item.unique_domains <= 2 && item.loads_30d > 0);
  const insight = low
    ? `⚠️ ${low.display_name} is loading low-quality skills on average. Improving skill scores will directly improve ${low.display_name}'s code output quality.`
    : narrow
      ? `💡 ${narrow.display_name} only loads ${narrow.unique_domains} domain(s) — it may be missing context from other areas. Check that CLAUDE.md references all relevant skills.`
      : "✓ All agents are loading broad, high-quality skill sets.";
  return (
    <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Agent Runtimes</h2>
      <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Which agents are getting the most value from your skills?</p>
      <div className="mt-5 overflow-hidden rounded-xl border border-[color:var(--bg-border)]">
        <div className="grid grid-cols-[1fr_90px_150px_140px_150px_1.4fr] gap-3 bg-black/20 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]"><span>Agent</span><span>Sessions</span><span>Unique skills loaded</span><span>Domains covered</span><span>Avg skill quality</span><span>Pattern</span></div>
        {runtimes.map((item) => (
          <div className="grid grid-cols-[1fr_90px_150px_140px_150px_1.4fr] gap-3 border-t border-[color:var(--bg-border)] px-4 py-3 text-sm" key={item.runtime}>
            <span className="font-semibold">{item.display_name}</span><span>{item.loads_30d}</span><span>{item.unique_skills}</span><span>{item.unique_domains}</span><span>{item.avg_skill_score}/100</span><span className="text-[color:var(--text-secondary)]">{item.pattern}</span>
          </div>
        ))}
      </div>
      <div className="mt-4 rounded-xl border border-[color:var(--bg-border)] bg-black/20 p-4 text-sm text-[color:var(--text-secondary)]">{insight}</div>
    </section>
  );
}

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

export default async function AnalyticsPage() {
  const { accessToken, org } = await resolveOrgAndToken();
  const [analytics, criticality, runtimeBreakdown, orgApiKey, coloadTree] = org
    ? await Promise.all([
        getOrgAnalytics(accessToken, org.id),
        getAnalyticsCriticality(accessToken, org.id),
        getOrgRuntimeBreakdown(accessToken, org.id),
        getOrgApiKey(accessToken, org.id),
        getSkillColoadTree(accessToken, org.id),
      ])
    : [null, null, null, null, null];
  const hasActivity = (analytics?.total_loads_30d ?? 0) > 0;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Analytics</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Usage intelligence that explains which skills matter and what to fix next.</p>
      </header>
      <SectionErrorBoundary section="analytics metrics">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricPanel label="Total loads" value={analytics?.total_loads_30d ?? 0} sub="Observed in the last 30 days" />
          <MetricPanel label="Skills loaded" value={analytics?.unique_skills_loaded ?? 0} sub={`${analytics?.total_skills ?? 0} skills available`} />
          <MetricPanel label="Most active repo" value={analytics?.most_active_repo?.name ?? "—"} sub={analytics?.most_active_repo ? `${analytics.most_active_repo.loads} loads this month` : "No repo activity yet"} />
          <MetricPanel label="Most loaded skill" value={analytics?.most_loaded_skill?.domain ?? "—"} sub={analytics?.most_loaded_skill ? `${analytics.most_loaded_skill.loads ?? 0} loads in 30d` : "No dominant skill yet"} />
        </div>
      </SectionErrorBoundary>
      {!hasActivity ? (
        <div className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center text-[color:var(--text-secondary)]">No agent activity yet. Connect Claude Code or Codex so Skillayer can show which skills agents depend on.</div>
      ) : null}
      {org?.id ? <AnalyticsRiskWorkbench accessToken={accessToken} criticality={criticality ?? []} orgId={org.id} tree={coloadTree} /> : <SkillRiskRegister items={criticality ?? []} />}
      <TopSkillsActionPanels criticality={criticality ?? []} neverLoaded={analytics?.never_loaded ?? []} />
      <RuntimeComparison runtimes={runtimeBreakdown?.runtimes ?? []} />
      {org?.id && orgApiKey?.api_key ? <LiveFeed apiKey={orgApiKey.api_key} orgId={org.id} /> : null}
    </div>
  );
}
