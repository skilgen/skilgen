import { notFound, redirect } from "next/navigation";

import { ActivityHeader } from "../../ActivityNav";
import { getActivityReplay, getActivitySessionDetail, loadActivityContext, normalizeSearchParams } from "../../activity-data";
import { ReplayClient } from "../ReplayClient";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

export default async function ActivityReplayPage({ params, searchParams }: { params: Promise<{ sessionId: string }>; searchParams?: PageSearchParams }) {
  const resolvedParams = await params;
  const query = await normalizeSearchParams(searchParams);
  const repoId = query.get("repo") || query.get("repo_id");
  const context = await loadActivityContext();
  if (!context.org?.id || !repoId) notFound();
  const payload = await getActivityReplay(context.accessToken, context.org.id, repoId, resolvedParams.sessionId);
  if (!payload) {
    const detail = await getActivitySessionDetail(context.accessToken, context.org.id, resolvedParams.sessionId);
    if (detail?.session?.repo_id && detail.session.repo_id !== repoId) {
      redirect(`/activity/replay/${resolvedParams.sessionId}?repo=${detail.session.repo_id}`);
    }
    redirect(`/activity/replay?repo_id=${repoId}`);
  }

  return (
    <div className="space-y-6">
      <ActivityHeader active="replay" />
      <ReplayClient exportHtml={payload.export_html} session={payload.session} timeline={payload.timeline} />
    </div>
  );
}
