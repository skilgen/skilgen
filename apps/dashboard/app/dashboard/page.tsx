import { withAuth } from "@workos-inc/authkit-nextjs";

import { OverviewLiveData } from "@/components/overview-live-data";
import { API_URL, type Org, type OrgStats, type Repo } from "../../lib/data";

export const dynamic = "force-dynamic";

type OverviewLogDetails = Record<string, boolean | number | string | null | undefined | object>;

function logOverviewEvent(event: string, details: OverviewLogDetails = {}): void {
  console.info(
    JSON.stringify({
      scope: "dashboard.overview",
      event,
      timestamp: new Date().toISOString(),
      ...details,
    }),
  );
}

function logOverviewError(event: string, error: unknown, details: OverviewLogDetails = {}): void {
  const message = error instanceof Error ? error.message : "Unknown error";
  console.error(
    JSON.stringify({
      scope: "dashboard.overview",
      event,
      timestamp: new Date().toISOString(),
      message,
      ...details,
    }),
  );
}

function repoLogSummary(repos: Repo[]): object {
  return {
    count: repos.length,
    repos: repos.slice(0, 5).map((repo) => ({
      id: repo.id,
      name: repo.name,
      full_name: repo.full_name,
      score_total: repo.score?.total ?? null,
      skill_count: repo.skill_count,
      last_analysed_at: repo.last_analysed_at,
    })),
  };
}

function safeApiHost(apiUrl: string): string {
  try {
    return new URL(apiUrl).host;
  } catch {
    return "invalid-api-url";
  }
}

export default async function OverviewPage() {
  let accessToken = "";
  let org: Org | null = null;
  let stats: OrgStats | null = null;
  let repos: Repo[] = [];
  let orgError: string | null = null;
  let statsError: string | null = null;
  let reposError: string | null = null;

  try {
    const session = await withAuth({ ensureSignedIn: true });
    accessToken = session?.accessToken || "";
    logOverviewEvent("auth_session_loaded", {
      hasToken: !!accessToken,
    });
  } catch (error) {
    logOverviewError("auth_session_error", error);
  }

  logOverviewEvent("server_preload_started", {
    apiHost: safeApiHost(API_URL),
    hasToken: !!accessToken,
  });

  try {
    const bootstrapRes = await fetch(`${API_URL}/orgs/bootstrap`, {
      next: { revalidate: 60 },
    });
    logOverviewEvent("org_fetch_completed", {
      status: bootstrapRes.status,
      ok: bootstrapRes.ok,
    });

    if (!bootstrapRes.ok) {
      orgError = `Unable to load organization (${bootstrapRes.status}).`;
    } else {
      org = (await bootstrapRes.json()) as Org;
      logOverviewEvent("org_loaded", {
        orgId: org.id,
        login: org.login,
        name: org.name,
        plan: org.plan,
      });
    }
  } catch (error) {
    orgError = "Unable to load organization.";
    logOverviewError("org_fetch_error", error);
  }

  if (org) {
    try {
      const statsRes = await fetch(`${API_URL}/orgs/${org.id}/stats`, {
        next: { revalidate: 60 },
      });
      logOverviewEvent("stats_fetch_completed", {
        status: statsRes.status,
        ok: statsRes.ok,
        orgId: org.id,
      });

      if (!statsRes.ok) {
        statsError = `Unable to load metrics (${statsRes.status}).`;
      } else {
        stats = (await statsRes.json()) as OrgStats;
        logOverviewEvent("stats_loaded", {
          orgId: org.id,
          repo_count: stats.repo_count,
          avg_score: stats.avg_score,
          skill_count: stats.skill_count,
          active_agents: stats.active_agents,
          score_trend_points: stats.score_trend.length,
        });
      }
    } catch (error) {
      statsError = "Unable to load metrics.";
      logOverviewError("stats_fetch_error", error, { orgId: org.id });
    }

    try {
      const reposRes = await fetch(`${API_URL}/orgs/${org.id}/repos`, {
        next: { revalidate: 60 },
      });
      logOverviewEvent("repos_fetch_completed", {
        status: reposRes.status,
        ok: reposRes.ok,
        orgId: org.id,
      });

      if (!reposRes.ok) {
        reposError = `Unable to load repositories (${reposRes.status}).`;
      } else {
        repos = ((await reposRes.json()) as Repo[]) ?? [];
        logOverviewEvent("repos_loaded", {
          orgId: org.id,
          ...repoLogSummary(repos),
        });
      }
    } catch (error) {
      reposError = "Unable to load repositories.";
      logOverviewError("repos_fetch_error", error, { orgId: org.id });
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Overview</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Your org AI readiness at a glance</p>
      </div>

      <OverviewLiveData
        initialRepos={repos}
        initialStats={stats}
        orgError={orgError}
        reposError={reposError}
        statsError={statsError}
      />
    </div>
  );
}
