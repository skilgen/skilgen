import { Github } from "lucide-react";

import { mockOrgStats } from "@/lib/mock-data";
import { OverviewMetricCards } from "@/components/overview-metric-cards";

export default function DashboardOverviewPage() {
  const hasConnectedRepos = false;

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-[22px] font-semibold text-[color:var(--text-primary)]">Overview</h1>
          <p className="mt-0.5 text-[14px] text-[color:var(--text-secondary)]">Your org&apos;s AI readiness at a glance</p>
        </div>
        <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-1.5 text-[13px] text-[color:var(--text-secondary)]">
          Last 30 days
        </div>
      </div>

      <OverviewMetricCards stats={hasConnectedRepos ? mockOrgStats : null} />

      {!hasConnectedRepos ? (
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
          <div className="mx-auto max-w-[480px] text-center">
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
      ) : null}
    </div>
  );
}
