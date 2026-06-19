import { withAuth } from "@workos-inc/authkit-nextjs";

import { getAgentPrs, getBootstrapOrg, getMyOrg, getOrgApiKey, getOrgRepos } from "../../../lib/data";
import { AgentPrInboxClient } from "./pr-inbox-client";

export default async function AgentPrInboxPage({ searchParams }: { searchParams?: Promise<Record<string, string | string[] | undefined>> }) {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const resolved = (await searchParams) ?? {};
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(resolved)) {
    if (Array.isArray(value)) {
      value.forEach((item) => params.append(key, item));
    } else if (value) {
      params.set(key, value);
    }
  }
  if (!params.has("state")) params.set("state", "all");
  const [initial, repos, apiKey] = org
    ? await Promise.all([
        getAgentPrs(accessToken, org.id, params),
        getOrgRepos(accessToken, org.id),
        getOrgApiKey(accessToken, org.id),
      ])
    : [null, null, null];

  return (
    <AgentPrInboxClient
      accessToken={accessToken}
      apiKey={apiKey?.api_key ?? ""}
      initialData={initial}
      initialParams={params.toString()}
      orgId={org?.id ?? ""}
      repos={repos ?? []}
    />
  );
}
