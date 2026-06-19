import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getMyOrg, getOrgSources } from "../../../lib/data";
import { SourcesClient } from "./sources-client";

export default async function SourcesPage({ searchParams }: { searchParams: Promise<{ tab?: string }> }) {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }
  const params = await searchParams;
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const sources = org?.id ? (await getOrgSources(accessToken, org.id)) ?? [] : [];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Connected Sources</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Data sources connected to Skillayer. Each source generates skills that guide your AI agents.</p>
      </div>
      <SourcesClient accessToken={accessToken} initialTab={params.tab === "finder" ? "finder" : "connected"} orgId={org?.id ?? ""} sources={sources} />
    </div>
  );
}
