import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { CheckCircle2, Zap } from "lucide-react";

import { getAutopilotQueue, getBootstrapOrg, getOrgRepos, getRepoSkills, type AutopilotTask, type Skill } from "../../../lib/data";
import { AutopilotActions, TriggerAutopilotButton } from "./autopilot-actions";

export const dynamic = "force-dynamic";

function statusClass(status: string): string {
  if (status === "pending") return "bg-amber-500/15 text-amber-300 ring-1 ring-amber-500/20";
  if (status === "skipped") return "bg-white/8 text-[color:var(--text-tertiary)] ring-1 ring-white/10";
  return "bg-[rgb(var(--accent-green-rgb)/0.13)] text-[color:var(--accent-green)] ring-1 ring-[rgb(var(--accent-green-rgb)/0.2)]";
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold capitalize ${statusClass(status)}`}>
      {status === "pending" ? <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-amber-300" /> : status === "done" ? <CheckCircle2 className="h-3 w-3" /> : null}
      {status}
    </span>
  );
}

function taskSkill(task: AutopilotTask): string {
  return task.skill_domain || task.skill_name || task.skill_id || "Repository skill";
}

function taskRepo(task: AutopilotTask): string {
  return task.repo_name || task.repo_id;
}

async function monitoredSkillCount(accessToken: string, orgId: string): Promise<number> {
  const repos = (await getOrgRepos(accessToken, orgId)) ?? [];
  const skillLists = await Promise.all(repos.map((repo) => getRepoSkills(accessToken, repo.id)));
  return skillLists.reduce((sum, skills) => sum + ((skills ?? []) as Skill[]).length, 0);
}

export default async function AutopilotPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    // Local preview may not have auth.
  }

  const org = await getBootstrapOrg();
  const [queue, skillsMonitored] = org?.id
    ? await Promise.all([getAutopilotQueue(accessToken, org.id), monitoredSkillCount(accessToken, org.id)])
    : [null, 0];
  const tasks = queue ?? [];
  const pending = tasks.filter((task) => task.status === "pending").length;
  const skipped = tasks.filter((task) => task.status === "skipped").length;
  const approvedToday = tasks.filter((task) => task.status === "approved" && task.resolved_at && new Date(task.resolved_at).toDateString() === new Date().toDateString()).length;

  return (
    <div>
      <nav className="mb-6 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">Overview</Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">Autopilot</span>
      </nav>

      <section className="mb-6 rounded-[28px] border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[radial-gradient(circle_at_top_left,rgb(var(--accent-primary-rgb)/0.18),rgb(var(--bg-surface-rgb)/0.96)_46%)] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
              <Zap className="h-4 w-4" />
              Zero-touch lifecycle
            </div>
            <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Skill Autopilot</h1>
            <p className="mt-2 max-w-3xl text-[14px] leading-6 text-[color:var(--text-secondary)]">Zero-touch skill lifecycle management. Skillayer detects drift and queues fixes.</p>
          </div>
          {org?.id ? <TriggerAutopilotButton accessToken={accessToken} orgId={org.id} /> : null}
        </div>
      </section>

      <section className="mb-6 grid gap-4 md:grid-cols-4">
        {[
          ["Pending tasks", pending],
          ["Approved today", approvedToday],
          ["Skipped", skipped],
          ["Skills monitored", skillsMonitored],
        ].map(([label, value]) => (
          <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={label}>
            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
            <div className="mt-3 text-[30px] font-semibold text-[color:var(--text-primary)]">{value}</div>
          </article>
        ))}
      </section>

      <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
          <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">Task queue</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Regeneration tasks created when freshness drops below 60%.</p>
        </div>
        {tasks.length === 0 ? (
          <div className="px-8 py-14 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[rgb(var(--accent-green-rgb)/0.14)] text-[color:var(--accent-green)]">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <h3 className="text-[18px] font-semibold text-[color:var(--text-primary)]">All skills are healthy</h3>
            <p className="mt-2 text-[13px] text-[color:var(--text-secondary)]">No regeneration needed.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <div className="grid min-w-[980px] grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)_minmax(0,1.5fr)_110px_110px_180px] gap-4 border-b border-[color:var(--bg-border)] px-5 py-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">
              <div>Skill</div>
              <div>Repo</div>
              <div>Trigger reason</div>
              <div>Freshness</div>
              <div>Status</div>
              <div>Actions</div>
            </div>
            {tasks.map((task) => (
              <div className="grid min-w-[980px] grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)_minmax(0,1.5fr)_110px_110px_180px] items-center gap-4 border-b border-[color:var(--bg-elevated)] px-5 py-4 last:border-b-0" key={task.id}>
                <div className="truncate text-[13px] font-semibold text-[color:var(--text-primary)]">{taskSkill(task)}</div>
                <div className="truncate font-mono text-[12px] text-[color:var(--text-secondary)]">{taskRepo(task)}</div>
                <div className="text-[13px] text-[color:var(--text-secondary)]">{task.trigger_reason}</div>
                <div className="text-[13px] font-semibold text-[color:var(--text-primary)]">{task.freshness_at_trigger}/25</div>
                <div><StatusBadge status={task.status} /></div>
                <div>{task.status === "pending" && org?.id ? <AutopilotActions accessToken={accessToken} orgId={org.id} taskId={task.id} /> : <span className="text-[12px] text-[color:var(--text-tertiary)]">No action</span>}</div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
