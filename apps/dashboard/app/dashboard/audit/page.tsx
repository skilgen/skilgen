import { withAuth } from "@workos-inc/authkit-nextjs";

import { AuditLogClient } from "./audit-log-client";
import { getAuditLog, getAuditLogEventTypes, getBootstrapOrg, getMyOrg, getOrgRepos } from "../../../lib/data";

export default async function AuditPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Audit auth unavailable:", error);
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const orgId = org?.id ?? "";
  const params = new URLSearchParams({ limit: "50" });
  const [initialAudit, eventTypes, repos] = orgId
    ? await Promise.all([
        getAuditLog(accessToken, orgId, params),
        getAuditLogEventTypes(accessToken, orgId),
        getOrgRepos(accessToken, orgId),
      ])
    : [null, [], []];

  return (
    <AuditLogClient
      accessToken={accessToken}
      eventTypes={eventTypes ?? []}
      initialAudit={initialAudit}
      orgId={orgId}
      repos={repos ?? []}
    />
  );
}
