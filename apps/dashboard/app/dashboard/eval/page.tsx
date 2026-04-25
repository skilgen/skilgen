import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getEvalROI, getMyOrg, type EvalROI } from "../../../lib/data";
import { EvalShell } from "./eval-shell";

export const dynamic = "force-dynamic";

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
  const roi: EvalROI =
    (await getEvalROI(accessToken, orgId)) ?? {
      total_tasks: 0,
      success_rate: null,
      multiplier: null,
      high_skill_success_rate: null,
      low_skill_success_rate: null,
      by_skill_score_bucket: [],
      by_agent_runtime: [],
      skill_gaps: [],
      trend: [],
      benchmark: {},
    };
  return <EvalShell orgId={orgId} roi={roi} />;
}
