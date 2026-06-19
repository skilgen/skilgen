import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getEvalSessions, getEvalSummary, getMyOrg } from "../../../lib/data";
import { EvalShell } from "./eval-shell";

async function loadOrg(): Promise<{ accessToken: string; orgId: string }> {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: true });
    accessToken = session.accessToken || "";
    const org = accessToken ? await getMyOrg(accessToken) : null;
    if (org) return { accessToken, orgId: org.id };
  } catch {
    // Local preview can run without WorkOS.
  }
  const org = await getBootstrapOrg();
  return { accessToken, orgId: org?.id ?? "current" };
}

export default async function EvalPage(): Promise<React.ReactElement> {
  const { accessToken, orgId } = await loadOrg();
  const [summary, sessions] = await Promise.all([getEvalSummary(accessToken, orgId), getEvalSessions(accessToken, orgId)]);
  return <EvalShell accessToken={accessToken} orgId={orgId} sessions={sessions?.sessions ?? []} summary={summary} />;
}
