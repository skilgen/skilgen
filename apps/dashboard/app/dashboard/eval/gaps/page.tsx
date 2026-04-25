import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getEvalSkillGaps, getMyOrg } from "../../../../lib/data";
import { GapsShell } from "./gaps-shell";

export const dynamic = "force-dynamic";

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
  const status = params.status ?? "open";
  const gaps = (await getEvalSkillGaps(accessToken, orgId, status)) ?? [];
  return <GapsShell accessToken={accessToken} gaps={gaps} orgId={orgId} status={status} />;
}
