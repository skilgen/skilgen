import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getMyOrg, getOrgRepos } from "../../../../lib/data";
import { DependencyGraphClient } from "./dependency-graph-client";

export default async function DependencyGraphPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Dependency graph auth unavailable:", error);
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const repos = org?.id ? (await getOrgRepos(accessToken, org.id)) ?? [] : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Skill Dependency Graph</h1>
        <p className="mt-2 max-w-3xl text-[15px] text-[color:var(--text-secondary)]">
          See how skills connect within each repo and discover cross-repo skill opportunities.
        </p>
      </div>
      {org?.id ? (
        <DependencyGraphClient
          accessToken={accessToken}
          orgId={org.id}
          repos={repos.map((repo) => ({ id: repo.id, name: repo.name }))}
        />
      ) : (
        <div className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-[13px] text-[color:var(--text-secondary)]">
          Connect an organisation to compute skill dependencies.
        </div>
      )}
    </div>
  );
}
