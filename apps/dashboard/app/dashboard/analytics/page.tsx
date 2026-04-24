import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { AlertTriangle, ArrowRight, BarChart3 } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import {
  getBootstrapOrg,
  getMyOrg,
  getOrgAnalytics,
  getOrgRuntimeBreakdown,
  getOrgSkillHeatmap,
  type AnalyticsSkill,
  type OrgAnalytics,
  type RuntimeBreakdownItem,
  type RuntimeBreakdownResponse,
  type SkillHeatmapResponse,
  type SkillHeatmapSkill,
} from "../../../lib/data";

export const dynamic = "force-dynamic";

const runtimeTheme: Record<string, { label: string; color: string; pill: string; initial: string }> = {
  claude_code: { label: "Claude Code", color: "#7C3AED", pill: "bg-violet-500/15 text-violet-200 ring-1 ring-violet-400/30", initial: "C" },
  cursor: { label: "Cursor", color: "#2563EB", pill: "bg-blue-500/15 text-blue-200 ring-1 ring-blue-400/30", initial: "C" },
  codex: { label: "Codex", color: "#16A34A", pill: "bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-400/30", initial: "O" },
  copilot: { label: "Copilot", color: "#1D4ED8", pill: "bg-indigo-500/15 text-indigo-200 ring-1 ring-indigo-400/30", initial: "G" },
  unknown: { label: "Other", color: "#6B7280", pill: "bg-white/10 text-[color:var(--text-secondary)] ring-1 ring-white/10", initial: "O" },
};

function toneForScore(score: number): string {
  if (score < 40) return "#ef4444";
  if (score < 70) return "#f59e0b";
  return "#22c55e";
}

function formatRelativeTime(value: string | null): string {
  if (!value) return "Never";
  const timestamp = new Date(value).getTime();
  if (Number.isNaN(timestamp)) return "Unknown";
  const diffMinutes = Math.max(0, Math.floor((Date.now() - timestamp) / 60000));
  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(new Date(value));
}

function formatCategory(value: string | null): string {
  if (!value) return "General";
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function MetricPanel({ label, value, sub }: { label: string; value: string | number; sub: string }) {
  return (
    <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02))] p-5 shadow-[0_24px_60px_rgba(0,0,0,0.18)]">
      <div className="mb-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className="text-[32px] font-semibold leading-none text-[color:var(--text-primary)]">{value}</div>
      <div className="mt-4 border-t border-white/6 pt-3 text-[12px] text-[color:var(--text-secondary)]">{sub}</div>
    </article>
  );
}

function Sparkline({ points }: { points: OrgAnalytics["daily_loads"] }) {
  const width = 720;
  const height = 180;
  const maxLoads = Math.max(1, ...points.map((point) => point.loads));
  const coordinates = points.map((point, index) => {
    const x = points.length <= 1 ? width / 2 : (index / (points.length - 1)) * width;
    const y = height - (point.loads / maxLoads) * (height - 18) - 9;
    return `${x},${y}`;
  });
  const areaPoints = [`0,${height}`, ...coordinates, `${width},${height}`].join(" ");

  return (
    <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[radial-gradient(circle_at_top,rgba(201,151,58,0.18),rgba(16,16,24,0.96)_52%)] p-6 shadow-[0_28px_80px_rgba(0,0,0,0.22)]">
      <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">30-day activity</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Daily skill loads recorded by connected agents across your org.</p>
        </div>
        <div className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
          {points.reduce((sum, point) => sum + point.loads, 0)} total loads
        </div>
      </div>
      <svg aria-label="30-day skill usage sparkline" className="h-[180px] w-full" preserveAspectRatio="none" viewBox={`0 0 ${width} ${height}`}>
        <defs>
          <linearGradient id="analytics-line" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stopColor="#f5d07a" />
            <stop offset="100%" stopColor="#C9973A" />
          </linearGradient>
          <linearGradient id="analytics-fill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="rgba(201,151,58,0.28)" />
            <stop offset="100%" stopColor="rgba(201,151,58,0)" />
          </linearGradient>
        </defs>
        <polygon fill="url(#analytics-fill)" points={areaPoints} />
        <polyline fill="none" points={coordinates.join(" ")} stroke="url(#analytics-line)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" />
      </svg>
    </section>
  );
}

function TopSkillsChart({ skills }: { skills: AnalyticsSkill[] }) {
  const maxLoads = Math.max(1, ...skills.map((skill) => skill.loads ?? 0));

  return (
    <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-5">
        <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">Top skills</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Most loaded skills in the last 30 days.</p>
      </div>
      <div className="space-y-4">
        {skills.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[color:var(--bg-border)] p-6 text-[13px] text-[color:var(--text-secondary)]">No skill loads recorded yet.</div>
        ) : (
          skills.map((skill) => {
            const loads = skill.loads ?? 0;
            const width = `${Math.max(4, (loads / maxLoads) * 100)}%`;
            return (
              <div key={skill.id}>
                <div className="mb-1 flex items-center justify-between gap-4 text-[13px]">
                  <div className="min-w-0">
                    <div className="truncate font-medium text-[color:var(--text-primary)]">{skill.domain}</div>
                    <div className="truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{skill.repo_full_name}</div>
                  </div>
                  <span className="font-semibold text-[color:var(--accent-primary)]">{loads}</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white/10">
                  <div className="h-full rounded-full bg-[#C9973A]" style={{ width }} />
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}

function ScoreRing({ score }: { score: number }) {
  const radius = 34;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference - (clamped / 100) * circumference;
  const stroke = toneForScore(clamped);

  return (
    <div className="relative h-20 w-20">
      <svg className="h-20 w-20 -rotate-90" viewBox="0 0 96 96">
        <circle cx="48" cy="48" fill="none" r={radius} stroke="rgba(255,255,255,0.08)" strokeWidth="10" />
        <circle cx="48" cy="48" fill="none" r={radius} stroke={stroke} strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" strokeWidth="10" />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center text-[22px] font-semibold text-[color:var(--text-primary)]">{clamped}</div>
    </div>
  );
}

function RuntimeBadge({ runtime }: { runtime: string }) {
  const theme = runtimeTheme[runtime] ?? runtimeTheme.unknown;
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold ${theme.pill}`}>{theme.label}</span>;
}

function CriticalityCard({ skill }: { skill: SkillHeatmapSkill }) {
  return (
    <Link
      className="group relative overflow-hidden rounded-[24px] border border-[color:var(--bg-border)] bg-[linear-gradient(160deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 transition-transform duration-200 hover:-translate-y-0.5 hover:border-[rgb(var(--accent-primary-rgb)/0.32)]"
      href={`/dashboard/repos/${skill.repo_id}/skills/${skill.skill_id}`}
    >
      <div className="absolute inset-x-0 top-0 h-px bg-[linear-gradient(90deg,transparent,rgba(201,151,58,0.7),transparent)] opacity-70" />
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="truncate text-[18px] font-semibold text-[color:var(--text-primary)]">{skill.domain}</div>
          <div className="mt-1 truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{skill.repo_name}</div>
        </div>
        <ScoreRing score={skill.criticality_score} />
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {skill.agent_runtimes.length ? skill.agent_runtimes.map((runtime) => <RuntimeBadge key={runtime} runtime={runtime} />) : <RuntimeBadge runtime="unknown" />}
      </div>

      <div className="mt-5 flex items-center justify-between gap-4 text-[13px] text-[color:var(--text-secondary)]">
        <span>
          {skill.loads_30d} loads · 7d: {skill.loads_7d}
        </span>
        <span>{formatRelativeTime(skill.last_loaded_at)}</span>
      </div>

      <div className="mt-4 flex items-center justify-between gap-3">
        <div className="text-[12px] font-medium text-[color:var(--text-tertiary)]">{formatCategory(skill.skill_category)}</div>
        {skill.alert === "stale_but_active" ? (
          <span className="inline-flex items-center gap-2 rounded-full bg-red-500/12 px-3 py-1 text-[12px] font-semibold text-red-300">
            <span className="h-2 w-2 animate-pulse rounded-full bg-red-400" />
            Stale but active
          </span>
        ) : null}
        {skill.alert === "dead_skill" ? (
          <span className="inline-flex items-center gap-2 rounded-full bg-white/8 px-3 py-1 text-[12px] font-semibold text-[color:var(--text-secondary)]">
            <span className="text-[11px]">💤</span>
            Never loaded
          </span>
        ) : null}
      </div>
    </Link>
  );
}

function CriticalityHeatmap({ heatmap }: { heatmap: SkillHeatmapResponse }) {
  const skills = [...heatmap.skills].sort((left, right) => right.criticality_score - left.criticality_score).slice(0, 12);

  return (
    <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Skill Criticality</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Which skills are most critical to your agents right now.</p>
        </div>
        <Link className="inline-flex items-center gap-2 text-[13px] font-semibold text-[color:var(--accent-primary)] hover:text-[color:var(--accent-bright)]" href="/dashboard/skills?sort=criticality">
          View all
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {skills.length === 0 ? (
          <div className="col-span-full rounded-2xl border border-dashed border-[color:var(--bg-border)] p-8 text-[13px] text-[color:var(--text-secondary)]">
            No skill usage has been recorded yet.
          </div>
        ) : (
          skills.map((skill) => <CriticalityCard key={skill.skill_id} skill={skill} />)
        )}
      </div>
    </section>
  );
}

function RuntimeRow({ item, total }: { item: RuntimeBreakdownItem; total: number }) {
  const theme = runtimeTheme[item.runtime] ?? runtimeTheme.unknown;
  const width = total > 0 ? `${Math.max(6, (item.loads_30d / total) * 100)}%` : "0%";

  return (
    <div className="grid gap-3 rounded-2xl border border-white/6 bg-black/10 p-4 md:grid-cols-[220px_minmax(0,1fr)_170px] md:items-center">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full text-[13px] font-semibold text-white" style={{ backgroundColor: theme.color }}>
          {theme.initial}
        </div>
        <div>
          <div className="font-semibold text-[color:var(--text-primary)]">{item.display_name || theme.label}</div>
          <div className="text-[12px] text-[color:var(--text-tertiary)]">{item.top_skill_domain ? `Top domain: ${item.top_skill_domain}` : "No dominant skill yet"}</div>
        </div>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-white/10">
        <div className="h-full rounded-full" style={{ width, backgroundColor: theme.color }} />
      </div>
      <div className="text-right text-[13px] text-[color:var(--text-secondary)]">
        <div className="font-semibold text-[color:var(--text-primary)]">{item.loads_30d} loads</div>
        <div>{item.unique_skills} unique skills</div>
      </div>
    </div>
  );
}

function RuntimeBreakdownSection({ runtimeBreakdown }: { runtimeBreakdown: RuntimeBreakdownResponse | null }) {
  return (
    <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <div className="mb-6">
        <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Agent Runtimes</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Which coding agents are loading your skills.</p>
      </div>
      {!runtimeBreakdown || runtimeBreakdown.total_loads_30d === 0 || runtimeBreakdown.runtimes.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-[color:var(--bg-border)] p-8 text-[14px] text-[color:var(--text-secondary)]">
          No agent activity recorded yet. Skills are loaded automatically when agents run in repos with Skilgen installed.
        </div>
      ) : (
        <div className="space-y-3">
          {runtimeBreakdown.runtimes.map((item) => (
            <RuntimeRow item={item} key={item.runtime} total={runtimeBreakdown.total_loads_30d} />
          ))}
        </div>
      )}
    </section>
  );
}

function EmptyAnalyticsState() {
  return (
    <div className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-12 text-center">
      <BarChart3 className="mx-auto mb-4 h-10 w-10 text-[color:var(--text-tertiary)]" />
      <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">No activity yet</h2>
      <p className="mx-auto mt-2 max-w-md text-[14px] text-[color:var(--text-secondary)]">
        Analytics appear once agents start loading skills from your repositories. Run your first analysis to get started.
      </p>
      <Link
        className="mt-6 inline-flex h-10 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]"
        href="/dashboard/repos"
      >
        Go to Repos
      </Link>
    </div>
  );
}

async function resolveOrgAndToken() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Unable to load analytics auth:", error);
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  return { accessToken, org };
}

export default async function AnalyticsPage() {
  const { accessToken, org } = await resolveOrgAndToken();
  const [analytics, heatmap, runtimeBreakdown] = org
    ? await Promise.all([
        getOrgAnalytics(accessToken, org.id),
        getOrgSkillHeatmap(accessToken, org.id),
        getOrgRuntimeBreakdown(accessToken, org.id),
      ])
    : [null, null, null];

  const summary = heatmap?.summary;
  const showAlertBar = (summary?.stale_but_active ?? 0) > 0;

  return (
    <div className="space-y-6">
      <div className="mb-2">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Analytics</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Live usage intelligence for the skills your agents rely on.</p>
      </div>

      {showAlertBar ? (
        <div className="flex flex-col gap-3 rounded-[24px] border border-red-500/30 bg-[linear-gradient(135deg,rgba(127,29,29,0.88),rgba(69,10,10,0.88))] p-5 shadow-[0_24px_60px_rgba(69,10,10,0.3)] md:flex-row md:items-center md:justify-between">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-red-200" />
            <p className="text-[14px] font-medium text-red-50">
              {summary?.stale_but_active} skills are stale but still being loaded by agents. Agents are acting on outdated context right now.
            </p>
          </div>
          <Link className="inline-flex items-center gap-2 text-[13px] font-semibold text-red-100 hover:text-white" href="/dashboard/skills?alert=stale_but_active">
            View affected skills
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      ) : null}

      <SectionErrorBoundary section="analytics metrics">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricPanel label="Total loads" value={analytics?.total_loads_30d ?? 0} sub="Observed in the last 30 days" />
          <MetricPanel label="Critical skills" value={summary?.total_skills ?? 0} sub={`${summary?.healthy ?? 0} healthy, ${summary?.dead_skills ?? 0} dead`} />
          <MetricPanel label="Most active repo" value={analytics?.most_active_repo?.name ?? "—"} sub={analytics?.most_active_repo ? `${analytics.most_active_repo.loads} loads this month` : "No repo activity yet"} />
          <MetricPanel
            label="Most loaded skill"
            value={analytics?.most_loaded_skill?.domain ?? "—"}
            sub={analytics?.most_loaded_skill ? `${analytics.most_loaded_skill.loads ?? 0} loads in 30d` : "No dominant skill yet"}
          />
        </div>
      </SectionErrorBoundary>

      {analytics ? (
        <>
          <SectionErrorBoundary section="analytics activity">
            <Sparkline points={analytics.daily_loads} />
          </SectionErrorBoundary>

          <SectionErrorBoundary section="analytics heatmap">
            {heatmap ? <CriticalityHeatmap heatmap={heatmap} /> : <EmptyAnalyticsState />}
          </SectionErrorBoundary>

          <SectionErrorBoundary section="analytics runtimes">
            <RuntimeBreakdownSection runtimeBreakdown={runtimeBreakdown} />
          </SectionErrorBoundary>

          <SectionErrorBoundary section="analytics top skills">
            <TopSkillsChart skills={analytics.top_skills} />
          </SectionErrorBoundary>
        </>
      ) : (
        <EmptyAnalyticsState />
      )}
    </div>
  );
}
