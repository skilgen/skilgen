import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { AlertTriangle, ArrowRight, ChevronRight, Eye, GitBranch, PlusCircle, RefreshCw, Wrench } from "lucide-react";

import { mockOrg } from "@/lib/mock-data";
import {
  getOrgActionItems,
  getBootstrapOrg,
  getEvalROI,
  getEvalSkillGaps,
  getMyOrg,
  getOrgMemoryScore,
  getOverviewScoreTrend,
  getOrgRepos,
  getOrgSkillDebt,
  getOrgSetupStatus,
  getOrgSkillHeatmap,
  getOrgStats,
  type ActionItem,
  type MemoryScore,
  type Org,
  type Repo,
  type SetupStatus,
} from "../../lib/data";
import { isDashboardV8Enabled } from "../../lib/flags";
import { AgentSetupBanner } from "./agent-setup-banner";
import { AnalyseRepoButton, QuickActions as OverviewQuickActions } from "./overview-actions";
import { OverviewChart } from "./overview-chart";
import { ActivityHome } from "../(v8)/activity/ActivityHome";

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
    <article className="group relative cursor-pointer rounded-[24px] border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 shadow-[0_22px_60px_rgba(0,0,0,0.18)] transition-colors hover:border-[color:var(--accent-primary)]">
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
      <span className="absolute bottom-4 right-5 text-[16px] text-[color:var(--accent-primary)] opacity-0 transition-opacity group-hover:opacity-100">→</span>
    </article>
  );
  return href ? <Link href={href}>{content}</Link> : content;
}

function MemoryScoreHero({ score }: { score: MemoryScore | null }) {
  const safe = score ?? {
    score: 0,
    grade: "F" as const,
    trend_7d: 0,
    trend_30d: 0,
    computed_at: "",
    breakdown: { coverage: 0, load_frequency: 0, compliance: 0, freshness: 0 },
  };
  const tone = safe.score >= 80 ? "text-[color:var(--accent-green)]" : safe.score >= 50 ? "text-amber-300" : "text-red-300";
  const compliance = safe.breakdown.compliance ?? safe.breakdown.quality ?? 0;
  const trendLabel = `${safe.trend_7d >= 0 ? "+" : ""}${safe.trend_7d} this week`;
  const sparkY = 30 - Math.min(24, Math.max(0, safe.score) / 4);
  const subScores = [
    ["Coverage", safe.breakdown.coverage],
    ["Load frequency", safe.breakdown.load_frequency],
    ["Compliance", compliance],
    ["Freshness", safe.breakdown.freshness],
  ];
  return (
    <Link className="block rounded-[28px] border border-[color:var(--bg-border)] bg-[linear-gradient(135deg,rgba(16,185,129,0.10),rgba(13,13,20,0.98)_48%)] p-6 transition-colors hover:border-[color:var(--accent-primary)]" href="/dashboard/ai-readiness">
      <div className="grid gap-6 xl:grid-cols-[260px_minmax(0,1fr)_360px] xl:items-center">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Org Memory Score</div>
          <div className={`mt-3 text-[54px] font-semibold leading-none ${tone}`}>{safe.score}</div>
          <div className="mt-2 text-sm text-[color:var(--text-secondary)]">Coverage, load frequency, compliance, and freshness.</div>
        </div>
        <div>
          <div className="flex items-center gap-3">
            <span className={`rounded-full border px-3 py-1 text-sm font-semibold ${safe.trend_7d >= 0 ? "border-[color:var(--accent-green)]/30 text-[color:var(--accent-green)]" : "border-red-500/30 text-red-300"}`}>{trendLabel}</span>
            <span className="text-sm text-[color:var(--text-secondary)]">{safe.trend_30d >= 0 ? "+" : ""}{safe.trend_30d} in 30d</span>
          </div>
          <svg className="mt-5 h-16 w-full max-w-[420px]" viewBox="0 0 240 64" role="img" aria-label="Flat memory score sparkline">
            <path d={`M4 ${sparkY} H236`} fill="none" stroke="var(--accent-primary)" strokeLinecap="round" strokeWidth="3" />
            <circle cx="236" cy={sparkY} fill="var(--accent-primary)" r="4" />
          </svg>
          <p className="mt-2 text-xs text-[color:var(--text-tertiary)]">Flat sparkline reflects the current score only; historical Memory Score trend is planned for Phase 3.</p>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {subScores.map(([label, value]) => (
            <div className="rounded-xl border border-[color:var(--bg-border)] bg-black/15 p-3" key={label as string}>
              <div className="text-xs text-[color:var(--text-secondary)]">{label as string}</div>
              <div className="mt-2 flex items-center gap-3">
                <ScoreRing score={Math.round(Number(value) * 100)} />
                <span className="text-lg font-semibold">{Math.round(Number(value) * 100)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Link>
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

function SetupProgressCard({ setupStatus }: { setupStatus: SetupStatus | null }) {
  if (!setupStatus || setupStatus.completion_percent >= 100) return null;
  const nextStepTitle = setupStatus.next_step_title ?? "Finish setup";
  const nextActionUrl = setupStatus.next_action_url ?? "/dashboard/connect";
  const guidance = setupStatus.next_step_guidance ?? "Complete the next setup step to unlock live Skillayer recommendations.";
  return (
    <section className="rounded-[8px] border border-[rgb(var(--accent-primary-rgb)/0.28)] bg-[linear-gradient(135deg,rgba(201,151,58,0.12),rgba(16,185,129,0.08),rgba(13,13,20,0.98))] p-5">
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_260px] lg:items-center">
        <div className="min-w-0">
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--accent-primary)]">Setup readiness</div>
          <h2 className="mt-2 text-[22px] font-semibold text-[color:var(--text-primary)]">{nextStepTitle}</h2>
          <p className="mt-2 max-w-3xl text-[14px] leading-6 text-[color:var(--text-secondary)]">{guidance}</p>
        </div>
        <div className="space-y-3 rounded-[8px] border border-[color:var(--bg-border)] bg-black/20 p-4">
          <div className="flex items-center justify-between gap-3 text-sm">
            <span className="font-medium text-[color:var(--text-secondary)]">{setupStatus.completion_label}</span>
            <span className="font-semibold text-[color:var(--text-primary)]">{setupStatus.completion_percent}%</span>
          </div>
          <div
            aria-label="Setup completion"
            aria-valuemax={100}
            aria-valuemin={0}
            aria-valuenow={setupStatus.completion_percent}
            className="h-2 overflow-hidden rounded-full bg-white/10"
            role="progressbar"
          >
            <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${Math.max(0, Math.min(100, setupStatus.completion_percent))}%` }} />
          </div>
          <Link className="inline-flex w-full items-center justify-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-4 py-2.5 text-[13px] font-semibold text-black hover:bg-[color:var(--accent-bright)]" href={nextActionUrl}>
            Continue setup
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </section>
  );
}

function AttentionTable({ accessToken, orgId, repos }: { accessToken: string; orgId: string; repos: Repo[] }) {
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
              <Link className="truncate font-semibold text-[color:var(--text-primary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repo.id}`}>{repo.name}</Link>
              <div className="truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{repo.full_name}</div>
            </div>
            <div>
              <span className="inline-flex rounded-full bg-white/8 px-2.5 py-1 text-[12px] font-semibold text-[color:var(--text-primary)]">{repo.score?.total ?? 0}/100</span>
            </div>
            <div className="text-[color:var(--text-secondary)]">{formatRelativeTime(repo.last_analysed_at)}</div>
            <div>
              <AnalyseRepoButton accessToken={accessToken} orgId={orgId} repo={repo} />
            </div>
          </div>
        ))}
      </div>
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
  const fallbackOrg: Org = {
    id: mockOrg.id,
    login: "skillayer",
    name: mockOrg.name,
    plan: mockOrg.plan,
  };
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg()) ?? fallbackOrg;
  return { accessToken, org, firstName };
}

export default async function OverviewPage() {
  const { accessToken, org, firstName } = await resolveOrg();
  if (org?.id && (await isDashboardV8Enabled(org.id))) {
    return <ActivityHome />;
  }

  const [stats, scoreTrend, heatmap, repos, setupStatus, actionItems, roi, skillGaps, memoryScore, skillDebt] = org
    ? await Promise.all([
        getOrgStats(accessToken, org.id),
        getOverviewScoreTrend(accessToken, org.id, 30),
        getOrgSkillHeatmap(accessToken, org.id),
        getOrgRepos(accessToken, org.id),
        getOrgSetupStatus(accessToken, org.id),
        getOrgActionItems(accessToken, org.id),
        getEvalROI(accessToken, org.id),
        getEvalSkillGaps(accessToken, org.id, "open"),
        getOrgMemoryScore(accessToken, org.id),
        getOrgSkillDebt(accessToken, org.id),
      ])
    : [null, null, null, null, null, null, null, null, null, null];

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
          <SetupProgressCard setupStatus={setupStatus} />
          <MemoryScoreHero score={memoryScore} />
          {(skillGaps?.length ?? 0) > 0 ? (
            <Link className="flex items-center justify-between gap-4 rounded-xl border border-[#f59e0b]/30 bg-[#f59e0b]/10 p-4 text-sm text-amber-100" href="/dashboard/eval/gaps">
              <span>⚠ {skillGaps?.length} skill gaps — agents failing on {gapDomains.join(", ")}</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          ) : null}
          {showTodayActions ? <TodayActions items={actionItems?.items ?? []} /> : null}
          <Link className="block rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 hover:border-[color:var(--accent-primary)]" href="/dashboard/skills">
            <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Skills Health</div>
                <div className="mt-3 flex flex-wrap items-end gap-4">
                  <span className="text-5xl font-semibold text-[color:var(--text-primary)]">{stats?.skill_count ?? heatmap?.summary.total_skills ?? 0}</span>
                  <span className="rounded-full bg-[color:var(--accent-primary)]/15 px-3 py-1 text-sm font-semibold text-[color:var(--accent-primary)]">Avg {stats?.avg_score ?? 0}/100</span>
                  <span className="text-sm text-[color:var(--text-secondary)]">{skillsBelowThreshold} skills need attention</span>
                </div>
              </div>
              <svg className="h-20 w-full max-w-[360px]" viewBox="0 0 360 80" role="img" aria-label="Skill score trend">
                {(stats?.score_trend ?? []).slice(-5).map((point, index) => {
                  const height = Math.max(8, Math.min(70, point.score));
                  return <rect fill={scoreTone(point.score)} height={height} key={`${point.date}-${index}`} rx="4" width="46" x={index * 70 + 8} y={76 - height} />;
                })}
              </svg>
            </div>
          </Link>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
            <MetricCard href="/dashboard/repos" label="Repos Connected" value={stats?.repo_count ?? repoList.length} sub="Connected repositories" />
            <MetricCard href="/dashboard/skills" label="Skills Generated" value={stats?.skill_count ?? heatmap?.summary.total_skills ?? 0} sub="Tracked skill inventory" />
            <MetricCard href="/dashboard/ai-readiness" label="Avg Skilgen Score" value={`${stats?.avg_score ?? 0}/100`} sub="Org-wide average" ringScore={stats?.avg_score ?? 0} />
            <MetricCard label="Skill Health" value={`${skillDebt?.health_score ?? Math.max(0, 100 - (skillDebt?.debt_score ?? 100))}/100`} sub="Higher is better" ringScore={skillDebt?.health_score ?? Math.max(0, 100 - (skillDebt?.debt_score ?? 100))} href="/dashboard/debt" />
            <MetricCard label="AI Readiness" value={`${memoryScore?.score ?? 0}`} sub={`Grade ${memoryScore?.grade ?? "F"} · ${memoryScore?.trend ?? "Stable"}`} ringScore={memoryScore?.score ?? 0} href="/dashboard/ai-readiness" />
            {showPerformance ? <MetricCard label="Performance" value={`${roi?.multiplier}x`} sub="Agent task improvement" href="/dashboard/eval" /> : null}
            <MetricCard label="Dead Skills" value={deadSkills} sub="Skills with no recent usage" tone={deadSkills > 0 ? "danger" : "default"} href="/dashboard/analytics?view=never-loaded" />
            <MetricCard label="Stale + Active" value={staleActive} sub="Agents still loading outdated context" tone={staleActive > 0 ? "warning" : "default"} href="/dashboard/red-flags" />
          </section>

          <OverviewChart points={scoreTrend ?? []} />
          <AttentionTable accessToken={accessToken} orgId={org?.id ?? ""} repos={attentionRepos} />
          <OverviewQuickActions accessToken={accessToken} orgId={org?.id ?? ""} repos={repoList} />
        </>
      )}
    </div>
  );
}
