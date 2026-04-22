import { withAuth } from "@workos-inc/authkit-nextjs";

import { OverviewLiveData } from "@/components/overview-live-data";
import { API_URL, type Org, type OrgStats, type Repo } from "../../lib/data";

export const dynamic = "force-dynamic";

export default async function OverviewPage() {
  let accessToken = "";
  let userId = "";
  let stats: OrgStats | null = null;
  let repos: Repo[] = [];

  try {
    const session = await withAuth({ ensureSignedIn: true });
    accessToken = session?.accessToken || "";
    userId = session?.user?.id || "";
    console.log("Auth session:", {
      hasToken: !!accessToken,
      userId,
    });
  } catch (error) {
    console.error("Auth error:", error);
  }

  console.log("API URL:", API_URL);
  console.log("Has access token:", !!accessToken);

  try {
    const bootstrapRes = await fetch(`${API_URL}/orgs/bootstrap`, {
      next: { revalidate: 60 },
    });
    console.log("orgs/bootstrap server status:", bootstrapRes.status);
    if (bootstrapRes.ok) {
      const org = (await bootstrapRes.json()) as Org;
      const [statsRes, reposRes] = await Promise.all([
        fetch(`${API_URL}/orgs/${org.id}/stats`, { next: { revalidate: 60 } }),
        fetch(`${API_URL}/orgs/${org.id}/repos`, { next: { revalidate: 60 } }),
      ]);
      console.log("org stats server status:", statsRes.status);
      console.log("org repos server status:", reposRes.status);
      if (statsRes.ok) {
        stats = (await statsRes.json()) as OrgStats;
      }
      if (reposRes.ok) {
        repos = ((await reposRes.json()) as Repo[]) ?? [];
      }
    }
  } catch (error) {
    console.error("Overview server preload error:", error);
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Overview</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Your org AI readiness at a glance</p>
      </div>

      <OverviewLiveData apiUrl={API_URL} initialStats={stats} initialRepos={repos} />
    </div>
  );
}
