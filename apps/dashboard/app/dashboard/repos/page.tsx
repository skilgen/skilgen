import { withAuth } from "@workos-inc/authkit-nextjs";

import { ReposTable } from "@/components/repos-table";
import { getMyOrg, getOrgRepos, type Repo } from "../../../lib/data";

export const dynamic = "force-dynamic";

export default async function ReposPage() {
  const session = await withAuth({ ensureSignedIn: true });
  const accessToken = session.accessToken || "";
  let repos: Repo[] = [];

  try {
    const org = await getMyOrg(accessToken);
    if (org?.id) {
      repos = (await getOrgRepos(accessToken, org.id)) ?? [];
    }
  } catch (error) {
    console.error("Failed to fetch repos:", error);
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Repos</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Connected repositories and their Skilgen readiness.</p>
      </div>
      {repos.length > 0 ? (
        <ReposTable repos={repos} />
      ) : (
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
          No repositories found.
        </section>
      )}
    </div>
  );
}
