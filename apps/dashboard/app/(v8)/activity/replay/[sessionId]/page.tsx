import { notFound, redirect } from "next/navigation";

import { ActivityHeader } from "../../ActivityNav";
import { getActivityReplay, getActivitySessions, loadActivityContext, normalizeSearchParams } from "../../activity-data";
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
    const fallbackParams = new URLSearchParams(query);
    fallbackParams.delete("repo");
    fallbackParams.delete("repo_id");
    fallbackParams.set("limit", "25");
    const fallback = await getActivitySessions(context.accessToken, context.org.id, fallbackParams);
    const nextSession = fallback?.sessions.find((session) => session.id !== resolvedParams.sessionId) ?? fallback?.sessions[0];
    if (nextSession) {
      redirect(`/activity/replay/${nextSession.id}?repo=${nextSession.repo_id}`);
    }
    notFound();
  }

  return (
    <div className="space-y-6">
      <ActivityHeader active="replay" />
      <ReplayClient exportHtml={payload.export_html} session={payload.session} timeline={payload.timeline} />
    </div>
  );
}
