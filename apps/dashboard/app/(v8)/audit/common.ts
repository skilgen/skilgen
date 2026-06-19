import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getMyOrg } from "../../../lib/data";
import { mockOrg } from "@/lib/mock-data";

export async function loadAuditOrg() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    // Local previews can run without AuthKit.
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg()) ?? mockOrg;
  return { accessToken, orgId: org?.id ?? "" };
}
