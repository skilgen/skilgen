import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getMyOrg, getOrgApiKey, getOrgRepos, getOrgSetupStatus, type Repo, type SetupStatus } from "../../../lib/data";
import { ConnectShell } from "./connect-shell";

export const dynamic = "force-dynamic";

async function resolveConnectData(): Promise<{
  accessToken: string;
  orgId: string;
  apiKey: string;
  repos: Repo[];
  setupStatus: SetupStatus | null;
}> {
  let accessToken = "";

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    // Auth can be unavailable in local preview; continue with bootstrap data.
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const orgId = org?.id ?? "";
  const [apiKey, repos, setupStatus] = orgId
    ? await Promise.all([getOrgApiKey(accessToken, orgId), getOrgRepos(accessToken, orgId), getOrgSetupStatus(accessToken, orgId)])
    : [null, [], null];

  return {
    accessToken,
    orgId,
    apiKey: apiKey?.api_key ?? "",
    repos: repos ?? [],
    setupStatus,
  };
}

export default async function ConnectPage() {
  const data = await resolveConnectData();
  return <ConnectShell {...data} />;
}
