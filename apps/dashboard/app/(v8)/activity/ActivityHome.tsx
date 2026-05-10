import { ActivityHeader } from "./ActivityNav";
import { LiveFeedPanel } from "./LiveFeedPanel";
import { SetupReadinessBanner } from "./SetupReadinessBanner";
import { getActivityFeed, getActivitySessions, getActivitySetupStatus, loadActivityContext, normalizeSearchParams, type SearchParamsInput } from "./activity-data";

export async function ActivityHome({ searchParams }: { searchParams?: SearchParamsInput }) {
  const params = await normalizeSearchParams(searchParams);
  if (!params.has("hours")) params.set("hours", "24");
  const context = await loadActivityContext();
  const feed = context.org?.id ? await getActivityFeed(context.accessToken, context.org.id, params) : null;
  const sessions = context.org?.id ? await getActivitySessions(context.accessToken, context.org.id, new URLSearchParams({ limit: "5" })) : null;
  const setupStatus = context.org?.id ? await getActivitySetupStatus(context.accessToken, context.org.id) : null;

  return (
    <div className="space-y-6">
      <ActivityHeader active="live-feed" />
      <SetupReadinessBanner setupStatus={setupStatus} />
      <LiveFeedPanel
        events={feed?.events ?? []}
        feedAvailable={feed !== null}
        orgId={context.org?.id ?? ""}
        query={Object.fromEntries(params.entries())}
        sessionCount={sessions?.total ?? 0}
        streamKey={context.streamKey}
      />
    </div>
  );
}
