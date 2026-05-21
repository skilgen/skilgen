import { redirect } from "next/navigation";

import { ActivityHeader } from "./ActivityNav";
import { LiveFeedPanel } from "./LiveFeedPanel";
import { SetupReadinessBanner } from "./SetupReadinessBanner";
import { getActivityAgentRepos, getActivityFeed, getActivitySessions, getActivitySetupStatus, loadActivityContext, normalizeSearchParams, type SearchParamsInput } from "./activity-data";

export async function ActivityHome({ searchParams }: { searchParams?: SearchParamsInput }) {
  const params = await normalizeSearchParams(searchParams);
  if (!params.has("hours")) params.set("hours", "24");
  if (!params.has("limit")) params.set("limit", "50");
  const offset = Number(params.get("offset") ?? 0);
  if (offset > 0) {
    const limit = Number(params.get("limit") ?? 50);
    params.delete("offset");
    params.set("limit", String(offset + limit));
    redirect(`/activity/live-feed?${params.toString()}`);
  }
  const context = await loadActivityContext();
  const sessionParams = new URLSearchParams();
  sessionParams.set("limit", "5");
  for (const key of ["repo_id", "agent_provider", "risk_band"]) {
    const value = params.get(key);
    if (value) sessionParams.set(key, value);
  }
  const [feed, sessions, setupStatus, repoOptions] = context.org?.id
    ? await Promise.all([
        getActivityFeed(context.accessToken, context.org.id, params),
        getActivitySessions(context.accessToken, context.org.id, sessionParams),
        getActivitySetupStatus(context.accessToken, context.org.id),
        getActivityAgentRepos(context.accessToken, context.org.id),
      ])
    : [null, null, null, []];

  return (
    <div className="space-y-6">
      <ActivityHeader active="live-feed" />
      <SetupReadinessBanner setupStatus={setupStatus} />
      <LiveFeedPanel
        events={feed?.events ?? []}
        orgId={context.org?.id ?? ""}
        searchParams={params}
        streamKey={context.streamKey}
      />
    </div>
  );
}
