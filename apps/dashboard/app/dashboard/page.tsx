import { withAuth } from "@workos-inc/authkit-nextjs";
import { Github } from "lucide-react";

import { MetricCard } from "@/components/metric-card";
import { ReposTable } from "@/components/repos-table";
import { getMyOrg, getOrgRepos, getOrgStats, type OrgStats, type Repo } from "../../lib/data";

export const dynamic = "force-dynamic";

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

export default async function OverviewPage() {
  const session = await withAuth({ ensureSignedIn: true });
  const accessToken = session.accessToken || "";

  let stats: OrgStats | null = null;
  let repos: Repo[] = [];

  try {
    const org = await getMyOrg(accessToken);

    if (org?.id) {
      const [statsPayload, reposPayload] = await Promise.all([
        getOrgStats(accessToken, org.id),
        getOrgRepos(accessToken, org.id),
      ]);
      stats = statsPayload;
      repos = reposPayload ?? [];
    }
  } catch (error) {
    console.error("Failed to fetch dashboard data:", error);
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Overview</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Your org AI readiness at a glance</p>
      </div>

      <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Repos monitored" value={stats?.repo_count} sub="Connected repos" />
        <MetricCard label="Avg Skilgen Score" value={stats?.avg_score ? `${stats.avg_score}/100` : null} sub="Org readiness" />
        <MetricCard label="Skills generated" value={stats?.skill_count} sub="Published skills" />
        <MetricCard label="Active agents" value={stats?.active_agents} sub="Live sessions" />
      </div>

      {repos.length > 0 ? <ReposTable repos={repos} /> : <OnboardingCard />}
    </div>
  );
}
