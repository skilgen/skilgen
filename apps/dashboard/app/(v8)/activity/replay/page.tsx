import Link from "next/link";

import { ActivityHeader } from "../ActivityNav";
import { getActivitySessions, loadActivityContext, normalizeSearchParams } from "../activity-data";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

export default async function ActivityReplayIndexPage({ searchParams }: { searchParams?: PageSearchParams }) {
  const params = await normalizeSearchParams(searchParams);
  params.set("limit", params.get("limit") ?? "20");
  const context = await loadActivityContext();
  const payload = context.org?.id ? await getActivitySessions(context.accessToken, context.org.id, params) : null;
  const sessions = payload?.sessions ?? [];

  return (
    <div className="space-y-6">
      <ActivityHeader active="replay" />
      <section className="grid gap-3">
        {sessions.map((session) => (
          <Link className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 hover:border-[color:var(--accent-primary)]" href={`/activity/replay/${session.id}?repo=${session.repo_id}`} key={session.id}>
            <div className="text-sm font-semibold text-[color:var(--text-primary)]">{session.agent} - {session.repo_name}</div>
            <div className="mt-1 text-xs text-[color:var(--text-secondary)]">{session.files_touched.length} files - {session.risk_band} risk {session.risk_score}</div>
          </Link>
        ))}
        {sessions.length === 0 ? <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-sm text-[color:var(--text-secondary)]">No sessions are available for replay.</div> : null}
      </section>
    </div>
  );
}
