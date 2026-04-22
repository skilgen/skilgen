"use client";

import { useEffect, useState } from "react";
import { Github } from "lucide-react";

import type { Org, OrgStats, Repo } from "../../lib/data";
import { MetricCard } from "./metric-card";
import { ReposTable } from "./repos-table";

type OverviewLiveDataProps = {
  apiUrl: string;
  initialStats?: OrgStats | null;
  initialRepos?: Repo[];
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

export function OverviewLiveData({ apiUrl, initialStats = null, initialRepos = [] }: OverviewLiveDataProps) {
  const [stats, setStats] = useState<OrgStats | null>(initialStats);
  const [repos, setRepos] = useState<Repo[]>(initialRepos);
  const [loaded, setLoaded] = useState(Boolean(initialStats || initialRepos.length));

  useEffect(() => {
    let cancelled = false;

    async function loadOverviewData() {
      console.log("Overview API URL:", apiUrl);
      try {
        const bootstrapRes = await fetch(`${apiUrl}/orgs/bootstrap`);
        console.log("orgs/bootstrap browser status:", bootstrapRes.status);
        const bootstrapText = await bootstrapRes.text();
        console.log("orgs/bootstrap browser response:", bootstrapText);
        if (!bootstrapRes.ok) return;

        const org = JSON.parse(bootstrapText) as Org;
        const [statsRes, reposRes] = await Promise.all([
          fetch(`${apiUrl}/orgs/${org.id}/stats`),
          fetch(`${apiUrl}/orgs/${org.id}/repos`),
        ]);
        console.log("org stats browser status:", statsRes.status);
        console.log("org repos browser status:", reposRes.status);

        if (!cancelled && statsRes.ok) {
          setStats((await statsRes.json()) as OrgStats);
        }
        if (!cancelled && reposRes.ok) {
          setRepos(((await reposRes.json()) as Repo[]) ?? []);
        }
      } catch (error) {
        console.error("Overview browser fetch error:", error);
      } finally {
        if (!cancelled) {
          setLoaded(true);
        }
      }
    }

    loadOverviewData();

    return () => {
      cancelled = true;
    };
  }, [apiUrl]);

  return (
    <>
      <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Repos monitored" value={loaded ? stats?.repo_count : null} sub="Connected repos" />
        <MetricCard label="Avg Skilgen Score" value={loaded && stats?.avg_score ? `${stats.avg_score}/100` : null} sub="Org readiness" />
        <MetricCard label="Skills generated" value={loaded ? stats?.skill_count : null} sub="Published skills" />
        <MetricCard label="Active agents" value={loaded ? stats?.active_agents : null} sub="Live sessions" />
      </div>

      {repos.length > 0 ? <ReposTable repos={repos} /> : <OnboardingCard />}
    </>
  );
}
