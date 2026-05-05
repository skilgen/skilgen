import { loadAuditOrg } from "../common";
import { EvidencePackagesClient } from "./evidence-client";

export default async function EvidencePackagesPage() {
  const { accessToken, orgId } = await loadAuditOrg();
  return <EvidencePackagesClient accessToken={accessToken} orgId={orgId} />;
}
