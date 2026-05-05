import { loadAuditOrg } from "../common";
import { AuditExportsClient } from "./exports-client";

export default async function AuditExportsPage() {
  const { accessToken, orgId } = await loadAuditOrg();
  return <AuditExportsClient accessToken={accessToken} orgId={orgId} />;
}
