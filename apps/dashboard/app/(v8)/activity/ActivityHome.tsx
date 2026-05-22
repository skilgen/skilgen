import { redirect } from "next/navigation";

import { ActivityHeader } from "./ActivityNav";
import { LiveFeedPanel } from "./LiveFeedPanel";
import { SetupReadinessBanner } from "./SetupReadinessBanner";
import { getActivityFeed, getActivitySetupStatus, loadActivityContext, normalizeSearchParams, type SearchParamsInput } from "./activity-data";

export async function ActivityHome({ searchParams }: { searchParams?: SearchParamsInput }) {
  const params = await normalizeSearchParams(searchParams);
  if (!params.has("hours")) params.set("hours", "168");
  if (!params.has("limit")) params.set("limit", "50");
  const offset = Number(params.get("offset") ?? 0);
  if (offset > 0) {
    const limit = Number(params.get("limit") ?? 50);
    params.delete("offset");
    params.set("limit", String(offset + limit));
    redirect(`/activity/live-feed?${params.toString()}`);
  }
  const context = await loadActivityContext();
  const [feed, setupStatus] = context.org?.id
    ? await Promise.all([
        getActivityFeed(context.accessToken, context.org.id, params),
        getActivitySetupStatus(context.accessToken, context.org.id),
      ])
    : [null, null];

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
