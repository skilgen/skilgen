import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getEvalSkillGapsResponse, getMyOrg } from "../../../../lib/data";
import { GapsShell } from "./gaps-shell";

async function load(): Promise<{ accessToken: string; orgId: string }> {
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

export default async function SkillGapsPage({ searchParams }: { searchParams: Promise<{ status?: string }> }): Promise<React.ReactElement> {
  const { accessToken, orgId } = await load();
  const params = await searchParams;
  const status = params.status ?? "all";
  const response = await getEvalSkillGapsResponse(accessToken, orgId, status);
  return <GapsShell accessToken={accessToken} orgId={orgId} response={response} status={status} />;
}
