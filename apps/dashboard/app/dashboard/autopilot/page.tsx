import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { Activity, CheckCircle2, Clock3, GitPullRequest, Sparkles, XCircle } from "lucide-react";

import { getAutopilotQueue, getBootstrapOrg, getMyOrg, type AutopilotTask } from "../../../lib/data";
import { GenerateImprovementButton, ReviewActions, TriggerAutopilotButton } from "./autopilot-actions";

export const dynamic = "force-dynamic";

function taskSkill(task: AutopilotTask): string {
  return task.skill_domain || task.skill_name || task.skill_id || "Repository skill";
}

function taskRepo(task: AutopilotTask): string {
  return task.repo_name || task.repo_id;
}

function statusClass(status: string): string {
  if (status === "pending") return "bg-amber-500/15 text-amber-300 ring-1 ring-amber-500/20";
  if (status === "rejected" || status === "skipped") return "bg-white/8 text-[color:var(--text-tertiary)] ring-1 ring-white/10";
  return "bg-[rgb(var(--accent-green-rgb)/0.13)] text-[color:var(--accent-green)] ring-1 ring-[rgb(var(--accent-green-rgb)/0.2)]";
}

function StatusBadge({ status }: { status: string }) {
  return <span className={`inline-flex items-center rounded-full px-2 py-1 text-[11px] font-semibold capitalize ${statusClass(status)}`}>{status}</span>;
}

function contentLines(value: string | null | undefined): string[] {
  return (value || "").split("\n").slice(0, 90);
}

function DiffPane({ title, content }: { title: string; content: string | null | undefined }) {
  const lines = contentLines(content);
  return (
    <div className="min-w-0 overflow-hidden rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)]">
      <div className="border-b border-[color:var(--bg-border)] px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.12em] text-[color:var(--text-tertiary)]">{title}</div>
      <pre className="max-h-[420px] overflow-auto p-3 text-[11px] leading-5 text-[color:var(--text-secondary)]">
        {lines.length ? lines.map((line, index) => `${String(index + 1).padStart(3, " ")}  ${line}`).join("\n") : "No content"}
      </pre>
    </div>
  );
}

function QueueItem({ accessToken, orgId, task, active }: { accessToken: string; orgId: string; task: AutopilotTask; active: boolean }) {
  const hasDraft = Boolean(task.generated_content);
  return (
    <article className={`rounded-md border p-3 ${active ? "border-[color:var(--accent-primary)] bg-[rgb(var(--accent-primary-rgb)/0.08)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)]"}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="truncate text-[13px] font-semibold text-[color:var(--text-primary)]">{taskSkill(task)}</div>
          <div className="mt-1 truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{taskRepo(task)}</div>
        </div>
        <StatusBadge status={task.improvement_status || task.status} />
      </div>
      <p className="mt-3 line-clamp-2 text-[12px] leading-5 text-[color:var(--text-secondary)]">{task.trigger_reason}</p>
      <div className="mt-3 flex items-center justify-between gap-2">
        <span className="text-[12px] font-semibold text-[color:var(--text-primary)]">{task.freshness_at_trigger}/25</span>
        {hasDraft ? <Link className="text-[12px] font-semibold text-[color:var(--accent-primary)]" href={`/dashboard/autopilot?task=${task.id}`}>Review</Link> : <GenerateImprovementButton accessToken={accessToken} orgId={orgId} taskId={task.id} />}
      </div>
    </article>
  );
}

export default async function AutopilotPage({ searchParams }: { searchParams?: Promise<{ task?: string }> }) {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    // Local preview may not have auth.
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const params = searchParams ? await searchParams : {};
  const queue = org?.id ? await getAutopilotQueue(accessToken, org.id) : null;
  const tasks = queue ?? [];
  const pending = tasks.filter((task) => task.status === "pending");
  const reviewable = tasks.filter((task) => task.generated_content && task.status === "pending");
  const activeTask = tasks.find((task) => task.id === params.task) || reviewable[0] || pending[0] || tasks[0];
  const activity = tasks.filter((task) => task.status !== "pending" || task.reviewed_at || task.pr_url).slice(0, 12);

  return (
    <div>
      <nav className="mb-5 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">Overview</Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">Autopilot</span>
      </nav>

      <section className="mb-5 flex flex-col gap-3 border-b border-[color:var(--bg-border)] pb-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Autopilot improvement queue</h1>
          <p className="mt-2 text-[13px] text-[color:var(--text-secondary)]">{pending.length} pending, {reviewable.length} ready for review, {activity.length} recent decisions.</p>
        </div>
        {org?.id ? <TriggerAutopilotButton accessToken={accessToken} orgId={org.id} /> : null}
      </section>

      <section className="grid min-h-[640px] gap-4 xl:grid-cols-[320px_minmax(0,1fr)_300px]">
        <div className="min-w-0 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="flex items-center gap-2 border-b border-[color:var(--bg-border)] px-4 py-3">
            <Clock3 className="h-4 w-4 text-[color:var(--accent-primary)]" />
            <h2 className="text-[14px] font-semibold text-[color:var(--text-primary)]">Queue</h2>
          </div>
          <div className="grid max-h-[720px] gap-3 overflow-auto p-3">
            {pending.length ? pending.map((task) => (org?.id ? <QueueItem accessToken={accessToken} active={activeTask?.id === task.id} key={task.id} orgId={org.id} task={task} /> : null)) : <div className="px-2 py-8 text-center text-[13px] text-[color:var(--text-tertiary)]">Queue is clear.</div>}
          </div>
        </div>

        <div className="min-w-0 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="flex items-center justify-between gap-3 border-b border-[color:var(--bg-border)] px-4 py-3">
            <div className="flex min-w-0 items-center gap-2">
              <Sparkles className="h-4 w-4 shrink-0 text-[color:var(--accent-primary)]" />
              <h2 className="truncate text-[14px] font-semibold text-[color:var(--text-primary)]">Review</h2>
            </div>
            {activeTask ? <StatusBadge status={activeTask.improvement_status || activeTask.status} /> : null}
          </div>
          {activeTask ? (
            <div className="grid gap-4 p-4">
              <div>
                <h3 className="text-[16px] font-semibold text-[color:var(--text-primary)]">{taskSkill(activeTask)}</h3>
                <p className="mt-1 font-mono text-[12px] text-[color:var(--text-tertiary)]">{activeTask.skill_path || taskRepo(activeTask)}</p>
              </div>
              {activeTask.generated_content ? (
                <>
                  <div className="grid gap-3 lg:grid-cols-2">
                    <DiffPane content={activeTask.original_content} title="Current" />
                    <DiffPane content={activeTask.generated_content} title="Generated" />
                  </div>
                  {org?.id ? <ReviewActions accessToken={accessToken} orgId={org.id} task={activeTask} /> : null}
                </>
              ) : (
                <div className="rounded-md border border-dashed border-[color:var(--bg-border)] px-4 py-10 text-center">
                  <Sparkles className="mx-auto mb-3 h-7 w-7 text-[color:var(--accent-primary)]" />
                  <p className="text-[13px] text-[color:var(--text-secondary)]">No AI draft generated yet.</p>
                  <div className="mt-4">{org?.id ? <GenerateImprovementButton accessToken={accessToken} orgId={org.id} taskId={activeTask.id} /> : null}</div>
                </div>
              )}
            </div>
          ) : (
            <div className="px-4 py-16 text-center text-[13px] text-[color:var(--text-tertiary)]">No task selected.</div>
          )}
        </div>

        <div className="min-w-0 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="flex items-center gap-2 border-b border-[color:var(--bg-border)] px-4 py-3">
            <Activity className="h-4 w-4 text-[color:var(--accent-primary)]" />
            <h2 className="text-[14px] font-semibold text-[color:var(--text-primary)]">Activity</h2>
          </div>
          <div className="grid max-h-[720px] gap-3 overflow-auto p-3">
            {activity.length ? activity.map((task) => (
              <article className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] p-3" key={task.id}>
                <div className="flex items-center gap-2">
                  {task.status === "approved" ? <CheckCircle2 className="h-4 w-4 text-[color:var(--accent-green)]" /> : task.status === "rejected" ? <XCircle className="h-4 w-4 text-[color:var(--text-tertiary)]" /> : <Clock3 className="h-4 w-4 text-[color:var(--text-tertiary)]" />}
                  <div className="truncate text-[13px] font-semibold text-[color:var(--text-primary)]">{taskSkill(task)}</div>
                </div>
                <div className="mt-2 text-[12px] capitalize text-[color:var(--text-secondary)]">{task.improvement_status || task.status}</div>
                {task.pr_url ? (
                  <a className="mt-3 inline-flex items-center gap-1.5 text-[12px] font-semibold text-[color:var(--accent-primary)]" href={task.pr_url}>
                    <GitPullRequest className="h-3.5 w-3.5" />
                    PR #{task.pr_number}
                  </a>
                ) : null}
              </article>
            )) : <div className="px-2 py-8 text-center text-[13px] text-[color:var(--text-tertiary)]">No recent activity.</div>}
          </div>
        </div>
      </section>
    </div>
  );
}
