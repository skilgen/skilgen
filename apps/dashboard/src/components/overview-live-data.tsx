import { Github } from "lucide-react";

import type { OrgStats, Repo } from "../../lib/data";
import { MetricCard } from "./metric-card";
import { ReposTable } from "./repos-table";
import { SectionFallback } from "./section-fallback";

type OverviewLiveDataProps = {
  initialStats?: OrgStats | null;
  initialRepos?: Repo[];
  orgError?: string | null;
  statsError?: string | null;
  reposError?: string | null;
};

function OnboardingCard() {
  return (
    <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
      <div className="mx-auto max-w-[480px]">
        <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-xl border border-[rgb(var(--accent-primary-rgb)/0.2)] bg-[rgb(var(--accent-primary-rgb)/0.1)]">
          <Github className="h-[26px] w-[26px] text-[color:var(--accent-primary)]" />
        </div>
        <h2 className="mb-2 text-[18px] font-semibold text-[color:var(--text-primary)]">Connect your GitHub organization</h2>
        <p className="mb-6 text-[14px] leading-[1.6] text-[color:var(--text-secondary)]">
          Install the Skillayer GitHub App to start analysing repos and generating skills. Takes under 2 minutes.
        </p>
        <a
          className="inline-flex items-center rounded-md bg-[color:var(--accent-primary)] px-5 py-2.5 text-[14px] font-semibold text-[color:var(--bg-base)] shadow-[0_0_20px_rgb(var(--accent-primary-rgb)/0.15)] transition-colors hover:bg-[color:var(--accent-bright)]"
          href="#"
        >
          <Github className="mr-2 h-4 w-4" />
          Install GitHub App
        </a>
        <p className="mt-3 text-[12px] text-[color:var(--text-tertiary)]">Free tier includes 3 private repos</p>
      </div>
    </section>
  );
}

function MetricSkeleton() {
  return (
    <article className="animate-pulse rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-3 h-3 w-28 rounded bg-white/10" />
      <div className="h-8 w-20 rounded bg-white/10" />
      <div className="mt-4 border-t border-[color:var(--bg-elevated)] pt-3">
        <div className="h-3 w-24 rounded bg-white/10" />
      </div>
    </article>
  );
}

function ScoreSparkline({ points }: { points: OrgStats["score_trend"] }) {
  if (points.length === 0) return null;
  const width = 240;
  const height = 56;
  const coordinates = points.map((point, index) => {
    const x = points.length === 1 ? width : (index / (points.length - 1)) * width;
    const y = height - (Math.max(0, Math.min(100, point.score)) / 100) * height;
    return `${x},${y}`;
  });

  return (
    <section className="mb-8 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-5 py-4">
      <div className="mb-3 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-[14px] font-semibold text-[color:var(--text-primary)]">Score trend</h2>
          <p className="text-[12px] text-[color:var(--text-tertiary)]">Latest {points.length} data point{points.length === 1 ? "" : "s"}</p>
        </div>
        <span className="text-[18px] font-bold text-white">{points[points.length - 1]?.score ?? 0}/100</span>
      </div>
      <svg aria-label="Score trend" className="h-14 w-full" preserveAspectRatio="none" viewBox={`0 0 ${width} ${height}`}>
        <polyline fill="none" points={coordinates.join(" ")} stroke="#C9973A" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
      </svg>
    </section>
  );
}

export function OverviewLiveData({
  initialStats = null,
  initialRepos = [],
  orgError = null,
  statsError = null,
  reposError = null,
}: OverviewLiveDataProps) {
  const stats = initialStats;
  const repos = initialRepos;
  const showMetricSkeletons = stats === null;
  const statsErrorDetail = statsError ?? orgError;
  const reposErrorDetail = reposError ?? orgError;

  return (
    <>
      {statsErrorDetail ? (
        <div className="mb-8">
          <SectionFallback section="overview metrics" />
        </div>
      ) : (
        <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {showMetricSkeletons ? (
            <>
              <MetricSkeleton />
              <MetricSkeleton />
              <MetricSkeleton />
              <MetricSkeleton />
            </>
          ) : (
            <>
              <MetricCard label="Repos monitored" value={stats.repo_count} sub="Connected repos" />
              <MetricCard label="Avg Skilgen Score" value={`${stats.avg_score}/100`} sub="Org readiness" />
              <MetricCard label="Skills generated" value={stats.skill_count} sub="Published skills" />
              <MetricCard label="Active agents" value={stats.active_agents} sub="Live sessions" />
            </>
          )}
        </div>
      )}

      {stats ? <ScoreSparkline points={stats.score_trend} /> : null}

      {repos.length > 0 ? (
        <ReposTable repos={repos} />
      ) : reposErrorDetail ? (
        <SectionFallback section="repositories" />
      ) : (
        <OnboardingCard />
      )}
    </>
  );
}
