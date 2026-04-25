import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { AlertTriangle, ArrowRight, BookOpen, ChevronRight, Eye, GitBranch, Play, PlusCircle, RefreshCw, TrendingUp, Wrench } from "lucide-react";

import {
  getOrgActionItems,
  getBootstrapOrg,
  getEvalROI,
  getEvalSkillGaps,
  getMyOrg,
  getOrgRepos,
  getOrgSetupStatus,
  getOrgSkillHeatmap,
  getOrgStats,
  type ActionItem,
  type Org,
  type Repo,
} from "../../lib/data";
import { AgentSetupBanner } from "./agent-setup-banner";

export const dynamic = "force-dynamic";

function todayLabel(): string {
  return new Intl.DateTimeFormat("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" }).format(new Date());
}

function formatRelativeTime(value: string | null): string {
  if (!value) return "Never";
  const ts = new Date(value).getTime();
  if (Number.isNaN(ts)) return "Unknown";
  const diffHours = Math.max(0, Math.floor((Date.now() - ts) / 3600000));
  if (diffHours < 1) return "Just now";
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function scoreTone(score: number): string {
  if (score < 40) return "#ef4444";
  if (score < 70) return "#f59e0b";
  return "#22c55e";
}

function ScoreRing({ score }: { score: number }) {
  const radius = 30;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference - (clamped / 100) * circumference;
  return (
    <div className="relative h-20 w-20">
      <svg className="h-20 w-20 -rotate-90" viewBox="0 0 84 84">
        <circle cx="42" cy="42" fill="none" r={radius} stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
        <circle cx="42" cy="42" fill="none" r={radius} stroke={scoreTone(clamped)} strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" strokeWidth="8" />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center text-[18px] font-semibold text-[color:var(--text-primary)]">{clamped}</div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  sub,
  tone = "default",
  ringScore,
  href,
}: {
  label: string;
  value: string | number;
  sub: string;
  tone?: "default" | "danger" | "warning";
  ringScore?: number;
  href?: string;
}) {
  const content = (
    <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 shadow-[0_22px_60px_rgba(0,0,0,0.18)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
          <div
            className={`mt-3 text-[30px] font-semibold leading-none ${
              tone === "danger" ? "text-red-300" : tone === "warning" ? "text-amber-300" : "text-[color:var(--text-primary)]"
            }`}
          >
            {value}
          </div>
        </div>
        {typeof ringScore === "number" ? <ScoreRing score={ringScore} /> : null}
      </div>
      <div className="mt-5 border-t border-white/6 pt-3 text-[12px] text-[color:var(--text-secondary)]">{sub}</div>
    </article>
  );
  return href ? <Link href={href}>{content}</Link> : content;
}

function ScoreTrend({ points, avgScore, skillsBelowThreshold }: { points: { date: string; score: number }[]; avgScore: number; skillsBelowThreshold: number }) {
  const width = 920;
  const height = 210;
  const chartHeight = 176;
  const safe = points.length ? points : [{ date: "", score: 0 }];
  const coordinates = safe.map((point, index) => {
    const x = safe.length === 1 ? width / 2 : (index / (safe.length - 1)) * width;
    const y = chartHeight - (Math.max(0, Math.min(100, point.score)) / 100) * (chartHeight - 16) - 8;
    return `${x},${y}`;
  });
  const areaPoints = [`0,${chartHeight}`, ...coordinates, `${width},${chartHeight}`].join(" ");
  const targetY = chartHeight - 0.7 * (chartHeight - 16) - 8;
  const weekLabels = safe.map((_, index) => ({
    x: safe.length === 1 ? width / 2 : (index / (safe.length - 1)) * width,
    label: `Week ${index + 1}`,
  }));
  const caption =
    avgScore < 70
      ? `You're ${Math.max(0, 70 - avgScore)} points from the 70+ threshold where agents perform best.`
      : `Your skills are performing well. ${skillsBelowThreshold} skills still below threshold.`;

  return (
    <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[radial-gradient(circle_at_top,rgba(201,151,58,0.18),rgba(16,16,24,0.96)_50%)] p-6">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Score Trend</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">30-day average Skilgen score across your org.</p>
        </div>
        <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/20 px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
          <TrendingUp className="h-4 w-4" />
          {safe[safe.length - 1]?.score ?? 0}/100
        </div>
      </div>
      {points.some((point) => point.score > 0) ? (
        <svg aria-label="Org score trend" className="h-[210px] w-full" preserveAspectRatio="none" viewBox={`0 0 ${width} ${height}`}>
          <defs>
            <linearGradient id="overview-line" x1="0" x2="1" y1="0" y2="1">
              <stop offset="0%" stopColor="#f5d07a" />
              <stop offset="100%" stopColor="#C9973A" />
            </linearGradient>
            <linearGradient id="overview-fill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="rgba(201,151,58,0.28)" />
              <stop offset="100%" stopColor="rgba(201,151,58,0)" />
            </linearGradient>
          </defs>
          <line stroke="#f59e0b" strokeDasharray="8 8" strokeOpacity="0.7" strokeWidth="2" x1="0" x2={width} y1={targetY} y2={targetY} />
          <text fill="#f59e0b" fontSize="12" fontWeight="600" x={width - 58} y={targetY - 8}>
            Target
          </text>
          <polygon fill="url(#overview-fill)" points={areaPoints} />
          <polyline fill="none" points={coordinates.join(" ")} stroke="url(#overview-line)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" />
          {weekLabels.map((week) => (
            <text fill="rgba(238,238,245,0.48)" fontSize="11" key={`${week.label}-${week.x}`} textAnchor="middle" x={week.x} y={height - 8}>
              {week.label}
            </text>
          ))}
        </svg>
      ) : (
        <div className="rounded-2xl border border-dashed border-[color:var(--bg-border)] p-8 text-[14px] text-[color:var(--text-secondary)]">
          Analyse repos regularly to build score history.
        </div>
      )}
      <p className="mt-3 text-[13px] text-[color:var(--text-secondary)]">{caption}</p>
    </section>
  );
}

function actionIcon(type: string) {
  if (type === "improve") return Wrench;
  if (type === "generate") return PlusCircle;
  if (type === "refresh") return RefreshCw;
  return Eye;
}

function priorityClass(priority: string) {
  if (priority === "urgent") return "border-red-500/30 bg-red-500/10 text-red-200";
  if (priority === "recommended") return "border-amber-500/30 bg-amber-500/10 text-amber-200";
  return "border-white/10 bg-white/5 text-[color:var(--text-secondary)]";
}

function TodayActions({ items }: { items: ActionItem[] }) {
  if (items.length === 0) return null;

  return (
    <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <div className="mb-5">
        <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">What to do today</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Prioritised actions based on score, coverage, freshness, and agent activity.</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        {items.slice(0, 3).map((item) => {
          const Icon = actionIcon(item.type);
          return (
            <article className="rounded-lg border border-[color:var(--bg-border)] bg-black/15 p-4" key={item.id}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[rgb(var(--accent-primary-rgb)/0.08)] text-[color:var(--accent-primary)]">
                  <Icon className="h-5 w-5" />
                </div>
                <span className={`rounded-full border px-2.5 py-1 text-[11px] font-semibold capitalize ${priorityClass(item.priority)}`}>{item.priority}</span>
              </div>
              <h3 className="mt-4 text-[15px] font-semibold text-[color:var(--text-primary)]">{item.title}</h3>
              <p className="mt-2 min-h-[44px] text-[13px] leading-6 text-[color:var(--text-secondary)]">{item.description}</p>
              <Link className="mt-4 inline-flex items-center gap-2 rounded-md border border-[rgb(var(--accent-primary-rgb)/0.28)] px-3 py-2 text-[12px] font-semibold text-[color:var(--accent-primary)] hover:bg-[rgb(var(--accent-primary-rgb)/0.08)]" href={item.action_url}>
                Fix it
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function AttentionTable({ repos }: { repos: Repo[] }) {
  return (
    <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Repos Needing Attention</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">The lowest-scoring repositories in your workspace right now.</p>
        </div>
        <Link className="inline-flex items-center gap-2 text-[13px] font-semibold text-[color:var(--accent-primary)] hover:text-[color:var(--accent-bright)]" href="/dashboard/repos">
          View all repos
          <ChevronRight className="h-4 w-4" />
        </Link>
      </div>
      <div className="overflow-hidden rounded-2xl border border-[color:var(--bg-border)]">
        <div className="grid grid-cols-[minmax(0,1.3fr)_120px_140px_140px] bg-black/20 px-4 py-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">
          <span>Repository</span>
          <span>Score</span>
          <span>Last analysed</span>
          <span>Action</span>
        </div>
        {repos.map((repo) => (
          <div className="grid grid-cols-[minmax(0,1.3fr)_120px_140px_140px] items-center border-t border-[color:var(--bg-border)] px-4 py-4 text-[13px]" key={repo.id}>
            <div className="min-w-0">
              <div className="truncate font-semibold text-[color:var(--text-primary)]">{repo.name}</div>
              <div className="truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{repo.full_name}</div>
            </div>
            <div>
              <span className="inline-flex rounded-full bg-white/8 px-2.5 py-1 text-[12px] font-semibold text-[color:var(--text-primary)]">{repo.score?.total ?? 0}/100</span>
            </div>
            <div className="text-[color:var(--text-secondary)]">{formatRelativeTime(repo.last_analysed_at)}</div>
            <div>
              <Link className="inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.28)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--accent-primary)] hover:bg-[rgb(var(--accent-primary-rgb)/0.08)]" href={`/dashboard/repos/${repo.id}`}>
                Analyse now
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function QuickActions() {
  const actions = [
    { href: "/dashboard/repos", label: "Connect Repo", icon: GitBranch },
    { href: "/dashboard/repos", label: "New Analysis", icon: Play },
    { href: "/dashboard/skills", label: "View Skills", icon: BookOpen },
    { href: "/dashboard/analytics", label: "Analytics", icon: TrendingUp },
  ];
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {actions.map((action) => {
        const Icon = action.icon;
        return (
          <Link className="group rounded-[22px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5 transition-transform hover:-translate-y-0.5 hover:border-[rgb(var(--accent-primary-rgb)/0.32)]" href={action.href} key={action.label}>
            <div className="flex items-center justify-between gap-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-[rgb(var(--accent-primary-rgb)/0.22)] bg-[rgb(var(--accent-primary-rgb)/0.08)]">
                <Icon className="h-5 w-5 text-[color:var(--accent-primary)]" />
              </div>
              <ArrowRight className="h-4 w-4 text-[color:var(--text-tertiary)] transition-transform group-hover:translate-x-0.5" />
            </div>
            <div className="mt-5 text-[16px] font-semibold text-[color:var(--text-primary)]">{action.label}</div>
          </Link>
        );
      })}
    </section>
  );
}

function EmptyState() {
  return (
    <section className="rounded-[28px] border border-[rgb(var(--accent-primary-rgb)/0.22)] bg-[linear-gradient(135deg,rgba(201,151,58,0.12),rgba(13,13,20,0.98))] p-10">
      <div className="max-w-2xl">
        <div className="inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-black/20 px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
          <GitBranch className="h-4 w-4" />
          Ready for your first repo
        </div>
        <h2 className="mt-5 text-[32px] font-semibold text-[color:var(--text-primary)]">Connect your first repository to unlock live org intelligence.</h2>
        <p className="mt-3 max-w-xl text-[15px] leading-7 text-[color:var(--text-secondary)]">
          Once a repo is connected and analysed, this page turns into your command center for score health, stale skills, and the repositories that need action first.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link className="inline-flex items-center gap-2 rounded-full bg-[color:var(--accent-primary)] px-5 py-3 text-[14px] font-semibold text-black hover:bg-[color:var(--accent-bright)]" href="/dashboard/repos">
            Connect Repo
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link className="inline-flex items-center gap-2 rounded-full border border-[color:var(--bg-border)] px-5 py-3 text-[14px] font-semibold text-[color:var(--text-primary)] hover:bg-white/5" href="/dashboard/onboarding">
            View onboarding
          </Link>
        </div>
      </div>
    </section>
  );
}

async function resolveOrg(): Promise<{ accessToken: string; org: Org | null; firstName: string }> {
  let accessToken = "";
  let firstName = "there";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
    firstName = session?.user?.firstName || firstName;
  } catch {
    // Auth can be unavailable in local preview; continue with bootstrap data.
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  return { accessToken, org, firstName };
}

export default async function OverviewPage() {
  const { accessToken, org, firstName } = await resolveOrg();
  const [stats, heatmap, repos, setupStatus, actionItems, roi, skillGaps] = org
    ? await Promise.all([
        getOrgStats(accessToken, org.id),
        getOrgSkillHeatmap(accessToken, org.id),
        getOrgRepos(accessToken, org.id),
        getOrgSetupStatus(accessToken, org.id),
        getOrgActionItems(accessToken, org.id),
        getEvalROI(accessToken, org.id),
        getEvalSkillGaps(accessToken, org.id, "open"),
      ])
    : [null, null, null, null, null, null, null];

  const repoList = repos ?? [];
  const attentionRepos = [...repoList]
    .sort((left, right) => (left.score?.total ?? 0) - (right.score?.total ?? 0))
    .slice(0, 3);
  const staleActive = heatmap?.summary.stale_but_active ?? 0;
  const deadSkills = heatmap?.summary.dead_skills ?? 0;
  const skillsBelowThreshold = heatmap?.skills.filter((skill) => skill.score_total < 70).length ?? 0;
  const showSetupBanner = Boolean(setupStatus?.has_skills && !setupStatus.has_agent_loads);
  const showTodayActions = (actionItems?.items.length ?? 0) > 0;
  const showPerformance = (roi?.total_tasks ?? 0) >= 10 && roi?.multiplier;
  const gapDomains = (skillGaps ?? []).map((gap) => gap.domain).slice(0, 3);

  return (
    <div className="space-y-6">
      <section className="rounded-[30px] border border-[color:var(--bg-border)] bg-[radial-gradient(circle_at_top_left,rgba(201,151,58,0.2),rgba(13,13,20,0.98)_48%)] p-7">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="text-[12px] font-semibold uppercase tracking-[0.2em] text-[color:var(--text-tertiary)]">{todayLabel()}</div>
            <h1 className="mt-3 text-[34px] font-semibold tracking-[-0.02em] text-[color:var(--text-primary)]">Welcome back, {firstName}</h1>
            <p className="mt-2 max-w-2xl text-[15px] text-[color:var(--text-secondary)]">This is your live Skillayer command center for repo health, skill freshness, and the places your engineering org needs attention first.</p>
          </div>
          {staleActive > 0 ? (
            <Link className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-[13px] font-semibold text-red-200 hover:bg-red-500/15" href="/dashboard/analytics">
              <AlertTriangle className="h-4 w-4" />
              {staleActive} stale + active skills
            </Link>
          ) : null}
        </div>
      </section>

      {repoList.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          {showSetupBanner ? <AgentSetupBanner /> : null}
          {(skillGaps?.length ?? 0) > 0 ? (
            <Link className="flex items-center justify-between gap-4 rounded-xl border border-[#f59e0b]/30 bg-[#f59e0b]/10 p-4 text-sm text-amber-100" href="/dashboard/eval/gaps">
              <span>⚠ {skillGaps?.length} skill gaps — agents failing on {gapDomains.join(", ")}</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          ) : null}
          {showTodayActions ? <TodayActions items={actionItems?.items ?? []} /> : null}
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
            <MetricCard label="Repos Connected" value={stats?.repo_count ?? repoList.length} sub="Connected repositories" />
            <MetricCard label="Skills Generated" value={stats?.skill_count ?? heatmap?.summary.total_skills ?? 0} sub="Tracked skill inventory" />
            <MetricCard label="Avg Skilgen Score" value={`${stats?.avg_score ?? 0}/100`} sub="Org-wide average" ringScore={stats?.avg_score ?? 0} />
            {showPerformance ? <MetricCard label="Performance" value={`${roi?.multiplier}x`} sub="Agent task improvement" href="/dashboard/eval" /> : null}
            <MetricCard label="Dead Skills" value={deadSkills} sub="Skills with no recent usage" tone={deadSkills > 0 ? "danger" : "default"} href="/dashboard/analytics" />
            <MetricCard label="Stale + Active" value={staleActive} sub="Agents still loading outdated context" tone={staleActive > 0 ? "warning" : "default"} href="/dashboard/analytics" />
          </section>

          <ScoreTrend avgScore={stats?.avg_score ?? 0} points={stats?.score_trend ?? []} skillsBelowThreshold={skillsBelowThreshold} />
          <AttentionTable repos={attentionRepos} />
          <QuickActions />
        </>
      )}
    </div>
  );
}
