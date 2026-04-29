import { withAuth } from "@workos-inc/authkit-nextjs";

import { getAgentScorecard, getBootstrapOrg, getMyOrg } from "../../../lib/data";
import { AgentScorecardClient } from "./scorecard-client";

const ALLOWED_DAYS = new Set([7, 30, 90]);

function parseDays(value: string | string[] | undefined): number {
  const raw = Array.isArray(value) ? value[0] : value;
  const parsed = Number.parseInt(raw ?? "30", 10);
  return ALLOWED_DAYS.has(parsed) ? parsed : 30;
}

export default async function AgentScorecardPage({ searchParams }: { searchParams?: Promise<Record<string, string | string[] | undefined>> }) {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const resolved = (await searchParams) ?? {};
  const days = parseDays(resolved.days);
  const initialData = org ? await getAgentScorecard(accessToken, org.id, days) : null;

  return (
    <AgentScorecardClient
      accessToken={accessToken}
      initialData={initialData}
      initialDays={days}
      orgId={org?.id ?? ""}
    />
  );
}
