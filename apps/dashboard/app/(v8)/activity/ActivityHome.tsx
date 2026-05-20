import { redirect } from "next/navigation";

import { ActivityHeader } from "./ActivityNav";
import { LiveFeedPanel } from "./LiveFeedPanel";
import { SetupReadinessBanner } from "./SetupReadinessBanner";
import { getActivityAgentRepos, getActivityFeed, getActivitySessions, getActivitySetupStatus, loadActivityContext, normalizeSearchParams, type SearchParamsInput } from "./activity-data";

export async function ActivityHome({ searchParams }: { searchParams?: SearchParamsInput }) {
  const params = await normalizeSearchParams(searchParams);
  if (!params.has("hours")) params.set("hours", "24");
  if (!params.has("limit")) params.set("limit", "25");
  const offset = Number(params.get("offset") ?? 0);
  if (offset > 0) {
    const limit = Number(params.get("limit") ?? 25);
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
        feedAvailable={feed !== null}
        orgId={context.org?.id ?? ""}
        query={Object.fromEntries(params.entries())}
        repoOptions={repoOptions}
        sessionCount={sessions?.total ?? 0}
        streamKey={context.streamKey}
        hasMore={Boolean(feed?.has_more)}
        nextOffset={feed?.next_offset ?? null}
        total={feed?.total ?? feed?.events.length ?? 0}
      />
    </div>
  );
}
