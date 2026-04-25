import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getHalfLifeSummary, getMyOrg } from "../../../lib/data";
import { HalfLifeShell } from "./half-life-shell";

export const dynamic = "force-dynamic";

export default async function HalfLifePage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Half-life auth unavailable:", error);
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const summary = org?.id ? await getHalfLifeSummary(accessToken, org.id) : null;
  return <HalfLifeShell accessToken={accessToken} orgId={org?.id ?? ""} summary={summary} />;
}
