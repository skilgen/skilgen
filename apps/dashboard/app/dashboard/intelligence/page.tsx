import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getOrgIntelligence, type CategoryMatrixEntry, type OrgIntelligence, type OrgRepoSummary, type StaleAlert, type TopSkill } from "../../../lib/data";

export const dynamic = "force-dynamic";

const categoryLabels: Record<string, string> = {
  codebase_architecture: "Codebase Architecture",
  code_style: "Code Style",
  testing_conventions: "Testing Conventions",
  internal_tools: "Internal Tools",
  security_compliance: "Security Compliance",
  design_system: "Design System",
  data_schema: "Data Schema",
  operational_knowledge: "Operational Knowledge",
};

const categoryOrder = Object.keys(categoryLabels);

function scoreTextClass(score: number): string {
  if (score >= 70) return "text-[color:var(--accent-green)]";
  if (score >= 40) return "text-amber-400";
  return "text-red-400";
}

function scorePillClass(score: number): string {
  if (score >= 70) return "bg-[rgb(var(--accent-green-rgb)/0.15)] text-[color:var(--accent-green)]";
  if (score >= 40) return "bg-amber-500/15 text-amber-300";
  return "bg-red-500/15 text-red-400";
}

function formatRelativeTime(value: string | null): string {
  if (!value) return "Never";
  const date = new Date(value);
  const timestamp = date.getTime();
  if (Number.isNaN(timestamp)) return "Unknown";
  const diffMinutes = Math.max(0, Math.floor((Date.now() - timestamp) / 60000));
  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) return `${diffDays}d ago`;
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(date);
}

function formatTrend(value: number | null): { label: string; className: string } {
  if (value === null) return { label: "— No history", className: "text-[color:var(--text-tertiary)]" };
  const rounded = Math.round(value);
  if (rounded > 0) return { label: `↑ +${rounded} pts`, className: "text-green-400" };
  if (rounded < 0) return { label: `↓ ${rounded} pts`, className: "text-red-400" };
  return { label: "— No change", className: "text-[color:var(--text-tertiary)]" };
}

function formatTableTrend(value: number | null): { label: string; className: string } {
  if (value === null) return { label: "—", className: "text-[color:var(--text-tertiary)]" };
  const rounded = Math.round(value);
  if (rounded > 0) return { label: `↑ +${rounded}`, className: "text-green-400" };
  if (rounded < 0) return { label: `↓ ${rounded}`, className: "text-red-400" };
  return { label: "—", className: "text-[color:var(--text-tertiary)]" };
}

function StatCard({ label, value, valueClassName = "text-[color:var(--text-primary)]", subtitle }: { label: string; value: string | number; valueClassName?: string; subtitle?: string }) {
  return (
    <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className={`mt-3 text-[32px] font-semibold ${valueClassName}`}>{value}</div>
      {subtitle ? <div className="mt-2 text-[12px] text-[color:var(--text-tertiary)]">{subtitle}</div> : null}
    </article>
  );
}

function HeroMetrics({ intelligence }: { intelligence: OrgIntelligence }) {
  const trend = formatTrend(intelligence.org_health_trend);
  const dormantRepos = intelligence.repos.filter((repo) => repo.dormant).length;

  return (
    <section className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-5">
      <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">ORG HEALTH</div>
        <div className={`mt-3 text-[32px] font-semibold ${scoreTextClass(intelligence.org_health_score)}`}>{intelligence.org_health_score}</div>
        <div className={`mt-2 inline-flex rounded-full border border-[color:var(--bg-border)] px-2.5 py-1 text-[12px] font-semibold ${trend.className}`}>{trend.label}</div>
      </article>
      <StatCard label="REPOS" value={intelligence.total_repos} />
      <StatCard label="SKILLS" value={intelligence.total_skills} />
      <StatCard label="DORMANT REPOS" subtitle="No analysis in 30d" value={dormantRepos} valueClassName={dormantRepos > 0 ? "text-red-400" : "text-[color:var(--text-primary)]"} />
      <StatCard label="AGENT LOADS (30D)" value={intelligence.total_loads_30d.toLocaleString()} />
    </section>
  );
}

function RepoLeaderboard({ repos }: { repos: OrgRepoSummary[] }) {
  return (
    <section className="mb-8 overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="flex flex-col gap-3 border-b border-[color:var(--bg-border)] px-6 py-5 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Repo Leaderboard</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">All repos ranked by skill quality score.</p>
        </div>
        <div className="text-[12px] text-[color:var(--text-tertiary)]">🟢 Healthy (&gt;70) 🟡 Warning (40-70) 🔴 At Risk (&lt;40)</div>
      </div>
      {repos.length === 0 ? (
        <div className="px-6 py-14 text-center">
          <p className="text-[14px] text-[color:var(--text-secondary)]">No repositories connected yet.</p>
          <Link className="mt-4 inline-flex rounded-full border border-[color:var(--bg-border)] px-4 py-2 text-[12px] font-semibold text-[color:var(--accent-primary)] hover:border-[color:var(--accent-primary)]" href="/dashboard">
            Connect a repo →
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse text-left text-[13px]">
            <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
              <tr className="border-b border-[color:var(--bg-border)]">
                {["Repo", "Score", "Trend", "Skills", "Dead", "Stale", "Last Analysed", "Action"].map((column) => (
                  <th className="px-5 py-3 font-semibold" key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {repos.map((repo) => {
                const trend = formatTableTrend(repo.score_trend);
                return (
                  <tr className="border-b border-[color:var(--bg-elevated)] transition-colors last:border-b-0 hover:bg-white/5" key={repo.id}>
                    <td className="px-5 py-4 font-medium text-[color:var(--text-primary)]">{repo.name}</td>
                    <td className={`px-5 py-4 font-semibold ${scoreTextClass(repo.score)}`}>{repo.score}/100</td>
                    <td className={`px-5 py-4 font-semibold ${trend.className}`}>{trend.label}</td>
                    <td className="px-5 py-4 text-[color:var(--text-secondary)]">{repo.skill_count}</td>
                    <td className={`px-5 py-4 font-semibold ${repo.dead_skill_count > 0 ? "text-red-400" : "text-[color:var(--text-secondary)]"}`}>{repo.dead_skill_count}</td>
                    <td className={`px-5 py-4 font-semibold ${repo.stale_skill_count > 0 ? "text-amber-400" : "text-[color:var(--text-secondary)]"}`}>{repo.stale_skill_count}</td>
                    <td className="px-5 py-4">
                      <span className={repo.dormant ? "text-amber-400" : "text-[color:var(--text-secondary)]"}>{repo.dormant ? "⚠ " : ""}{formatRelativeTime(repo.last_analysed_at)}</span>
                    </td>
                    <td className="px-5 py-4">
                      <Link className="inline-flex rounded-full border border-[color:var(--bg-border)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repo.id}`}>
                        View →
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function alertPillClass(alertType: StaleAlert["alert_type"]): string {
  if (alertType === "dead") return "bg-white/8 text-[color:var(--text-secondary)]";
  if (alertType === "stale_but_active") return "bg-amber-500/15 text-amber-300";
  return "bg-red-500/15 text-red-300";
}

function alertLabel(alertType: StaleAlert["alert_type"]): string {
  if (alertType === "dead") return "Dead";
  if (alertType === "stale_but_active") return "Stale & Active";
  return "Dormant Repo";
}

function SkillAlerts({ alerts }: { alerts: StaleAlert[] }) {
  return (
    <section className="mb-8 overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="border-b border-[color:var(--bg-border)] px-6 py-5">
        <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Skill Alerts</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Skills and repos that need attention.</p>
      </div>
      {alerts.length === 0 ? (
        <div className="m-5 rounded-xl border border-[rgb(var(--accent-green-rgb)/0.25)] bg-[rgb(var(--accent-green-rgb)/0.12)] px-5 py-4 text-[13px] font-semibold text-[color:var(--accent-green)]">✓ No alerts — all skills are fresh and active.</div>
      ) : (
        <div className="divide-y divide-[color:var(--bg-elevated)]">
          {alerts.map((alert) => (
            <div className="flex flex-col gap-4 px-5 py-4 md:flex-row md:items-start md:justify-between" key={`${alert.alert_type}-${alert.skill_id}`}>
              <div className="min-w-0">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <span className={`rounded-full px-2.5 py-1 text-[12px] font-semibold ${alertPillClass(alert.alert_type)}`}>{alertLabel(alert.alert_type)}</span>
                  <span className="text-[14px] font-semibold text-[color:var(--text-primary)]">{alert.domain}</span>
                </div>
                <div className="font-mono text-[12px] text-[color:var(--text-tertiary)]">{alert.skill_path}</div>
                <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">in {alert.repo_name}</div>
              </div>
              <div className="shrink-0 text-left md:text-right">
                <div className="text-[12px] text-[color:var(--text-tertiary)]">{alert.loads_30d} loads</div>
                <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">Last loaded: {alert.last_loaded_at ? formatRelativeTime(alert.last_loaded_at) : "Never"}</div>
                <Link className="mt-2 inline-flex text-[12px] font-semibold text-[color:var(--accent-primary)] hover:underline" href={`/dashboard/repos/${alert.repo_id}/skills/${alert.skill_id}`}>
                  Edit →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function truncateRepoName(value: string): string {
  return value.length > 12 ? `${value.slice(0, 11)}…` : value;
}

function CoverageCell({ entry }: { entry: CategoryMatrixEntry | undefined }) {
  if (!entry?.covered) return <span className="text-[color:var(--text-tertiary)]">—</span>;
  return <span className={`inline-flex min-w-10 justify-center rounded-full px-2 py-1 text-[12px] font-semibold ${scorePillClass(entry.avg_score)}`}>{entry.avg_score}</span>;
}

function CoverageMatrix({ intelligence }: { intelligence: OrgIntelligence }) {
  if (intelligence.repos.length === 0) return null;
  const visibleRepos = intelligence.repos.slice(0, 8);
  const hiddenRepoCount = Math.max(0, intelligence.repos.length - visibleRepos.length);

  return (
    <section className="mb-8 overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="border-b border-[color:var(--bg-border)] px-6 py-5">
        <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Category Coverage Matrix</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Which skill categories are covered across each repo.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] border-collapse text-left text-[13px]">
          <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
            <tr className="border-b border-[color:var(--bg-border)]">
              <th className="w-[200px] px-5 py-3 font-semibold">Category</th>
              {visibleRepos.map((repo) => (
                <th className="w-20 px-3 py-3 text-center font-semibold" key={repo.id}>{truncateRepoName(repo.name)}</th>
              ))}
              {hiddenRepoCount > 0 ? <th className="w-24 px-3 py-3 text-center font-semibold">…and {hiddenRepoCount} more</th> : null}
            </tr>
          </thead>
          <tbody>
            {categoryOrder.map((category) => {
              const entries = intelligence.category_matrix[category] ?? [];
              return (
                <tr className="border-b border-[color:var(--bg-elevated)] last:border-b-0" key={category}>
                  <td className="px-5 py-4 font-medium text-[color:var(--text-primary)]">{categoryLabels[category]}</td>
                  {visibleRepos.map((repo) => (
                    <td className="px-3 py-4 text-center" key={repo.id}>
                      <CoverageCell entry={entries.find((entry) => entry.repo_id === repo.id)} />
                    </td>
                  ))}
                  {hiddenRepoCount > 0 ? <td className="px-3 py-4 text-center text-[color:var(--text-tertiary)]">—</td> : null}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap gap-4 border-t border-[color:var(--bg-border)] px-5 py-4 text-[12px] text-[color:var(--text-tertiary)]">
        <span>🟢 ≥70 Healthy</span>
        <span>🟡 40-69 Needs work</span>
        <span>🔴 &lt;40 At risk</span>
        <span>— Not covered</span>
      </div>
    </section>
  );
}

function TopSkills({ totalLoads, skills }: { totalLoads: number; skills: TopSkill[] }) {
  return (
    <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="border-b border-[color:var(--bg-border)] px-6 py-5">
        <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Most-Used Skills</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Skills loaded most frequently by agents in the last 30 days.</p>
      </div>
      {totalLoads === 0 ? (
        <div className="px-6 py-14 text-center">
          <p className="text-[14px] text-[color:var(--text-secondary)]">No agent activity recorded yet. See the Heatmap for setup instructions.</p>
          <Link className="mt-4 inline-flex rounded-full border border-[color:var(--bg-border)] px-4 py-2 text-[12px] font-semibold text-[color:var(--accent-primary)] hover:border-[color:var(--accent-primary)]" href="/dashboard/heatmap">
            Go to Heatmap
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] border-collapse text-left text-[13px]">
            <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
              <tr className="border-b border-[color:var(--bg-border)]">
                {["#", "Skill", "Repo", "Score", "Loads (30d)"].map((column) => (
                  <th className="px-5 py-3 font-semibold" key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {skills.slice(0, 10).map((skill, index) => (
                <tr className="border-b border-[color:var(--bg-elevated)] transition-colors last:border-b-0 hover:bg-white/5" key={skill.skill_id}>
                  <td className="px-5 py-4 text-[color:var(--text-tertiary)]">{index + 1}</td>
                  <td className="px-5 py-4">
                    <Link className="font-medium text-[color:var(--text-primary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${skill.repo_id}/skills/${skill.skill_id}`}>
                      {skill.domain}
                    </Link>
                  </td>
                  <td className="px-5 py-4 text-[12px] text-[color:var(--text-secondary)]">{skill.repo_name}</td>
                  <td className={`px-5 py-4 font-semibold ${scoreTextClass(skill.score)}`}>{skill.score}/100</td>
                  <td className="px-5 py-4 font-semibold text-[color:var(--text-primary)]">{skill.loads_30d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default async function IntelligencePage() {
  let accessToken = "";

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Intelligence auth unavailable:", error);
  }

  const org = await getBootstrapOrg();
  const intelligence = org?.id ? await getOrgIntelligence(accessToken, org.id) : null;
  const safeIntelligence: OrgIntelligence = intelligence ?? {
    org_health_score: 0,
    org_health_trend: null,
    total_repos: 0,
    total_skills: 0,
    total_loads_30d: 0,
    repos: [],
    category_matrix: Object.fromEntries(categoryOrder.map((category) => [category, []])),
    stale_alerts: [],
    top_skills: [],
  };

  return (
    <div>
      <nav className="mb-6 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">
          Overview
        </Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">Intelligence</span>
      </nav>

      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Org Intelligence</h1>
        <p className="mt-1 text-[14px] text-[color:var(--text-secondary)]">Cross-repo skill health, coverage gaps, and agent activity across your organisation.</p>
      </div>

      <HeroMetrics intelligence={safeIntelligence} />
      <RepoLeaderboard repos={safeIntelligence.repos} />
      <SkillAlerts alerts={safeIntelligence.stale_alerts} />
      <CoverageMatrix intelligence={safeIntelligence} />
      <TopSkills skills={safeIntelligence.top_skills} totalLoads={safeIntelligence.total_loads_30d} />
    </div>
  );
}
