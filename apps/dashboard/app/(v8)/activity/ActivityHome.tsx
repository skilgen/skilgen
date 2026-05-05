import { ActivityHeader } from "./ActivityNav";
import { LiveFeedPanel } from "./LiveFeedPanel";
import { getActivityFeed, loadActivityContext, normalizeSearchParams, type SearchParamsInput } from "./activity-data";

export async function ActivityHome({ searchParams }: { searchParams?: SearchParamsInput }) {
  const params = await normalizeSearchParams(searchParams);
  if (!params.has("hours")) params.set("hours", "24");
  const context = await loadActivityContext();
  const feed = context.org?.id ? await getActivityFeed(context.accessToken, context.org.id, params) : null;

  return (
    <div className="space-y-6">
      <ActivityHeader active="live-feed" />
      <LiveFeedPanel events={feed?.events ?? []} orgId={context.org?.id ?? ""} searchParams={params} streamKey={context.streamKey} />
    </div>
  );
}
