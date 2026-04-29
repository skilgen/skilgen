"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import type { AdminOrgDetail, UsageSeries } from "../../../../../lib/data";

function Card({ label, value }: { label: string; value: number | string }) {
  return <div className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4"><div className="text-xs uppercase tracking-widest text-[color:var(--text-tertiary)]">{label}</div><div className="mt-2 text-2xl font-semibold">{value}</div></div>;
}

function UsageChart({ usage }: { usage: UsageSeries | null }) {
  const series = usage?.series ?? [];
  const max = Math.max(1, ...series.flatMap((p) => [p.agent_sessions, p.prs_opened, p.logins, p.violations]));
  const width = 720;
  const height = 220;
  const path = (key: "agent_sessions" | "prs_opened" | "logins" | "violations") =>
    series.map((point, index) => `${(index / Math.max(1, series.length - 1)) * width},${height - (point[key] / max) * (height - 20) - 10}`).join(" ");
  return (
    <svg className="h-[260px] w-full overflow-visible" viewBox={`0 0 ${width} ${height + 40}`}>
      {[0, 1, 2, 3].map((i) => <line key={i} x1="0" x2={width} y1={(i / 3) * height} y2={(i / 3) * height} stroke="rgba(255,255,255,.08)" />)}
      <polyline fill="none" points={path("agent_sessions")} stroke="#3b82f6" strokeWidth="2" />
      <polyline fill="none" points={path("prs_opened")} stroke="#8b5cf6" strokeWidth="2" />
      <polyline fill="none" points={path("logins")} stroke="#10b981" strokeWidth="2" />
      <polyline fill="none" points={path("violations")} stroke="#ef4444" strokeWidth="2" />
      <text x="0" y={height + 28} fill="rgba(255,255,255,.55)" fontSize="12">Sessions · PRs · Logins · Violations</text>
    </svg>
  );
}

export function AdminOrgDetailClient({ org, usage }: { org: AdminOrgDetail; usage: UsageSeries | null }) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [actionError, setActionError] = useState<string | null>(null);
  const [suspendOpen, setSuspendOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [deleteConfirmation, setDeleteConfirmation] = useState("");

  async function runAction(path: string, init: RequestInit, onSuccess?: () => void) {
    setActionError(null);
    const response = await fetch(path, init);
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new Error(body?.detail || "Admin action failed");
    }
    onSuccess?.();
  }

  function suspend() {
    startTransition(async () => {
      try {
        await runAction(`/api/admin/orgs/${org.id}/suspend`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ reason }),
        }, () => {
          setSuspendOpen(false);
          router.refresh();
        });
      } catch (error) {
        setActionError(error instanceof Error ? error.message : "Could not suspend org");
      }
    });
  }

  function unsuspend() {
    startTransition(async () => {
      try {
        await runAction(`/api/admin/orgs/${org.id}/unsuspend`, { method: "POST" }, () => router.refresh());
      } catch (error) {
        setActionError(error instanceof Error ? error.message : "Could not unsuspend org");
      }
    });
  }

  function deleteSelectedOrg() {
    startTransition(async () => {
      try {
        await runAction(`/api/admin/orgs/${org.id}`, { method: "DELETE" }, () => router.push("/dashboard/admin/orgs"));
      } catch (error) {
        setActionError(error instanceof Error ? error.message : "Could not delete org");
      }
    });
  }

  return (
    <div className="space-y-6">
      <div>
        <a className="text-sm text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href="/dashboard/admin/orgs">← Back to orgs</a>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-semibold">{org.name}</h1>
          <span className="rounded-full border border-[color:var(--bg-border)] px-3 py-1 text-xs uppercase">{org.plan}</span>
          <span className={org.is_suspended ? "rounded-full bg-red-500/10 px-3 py-1 text-xs text-red-300" : "rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300"}>{org.is_suspended ? "Suspended" : "Active"}</span>
        </div>
        {org.suspended_reason && <p className="mt-2 text-sm text-red-200">Suspension reason: {org.suspended_reason}</p>}
      </div>
      <section className="sticky top-4 z-10 flex flex-wrap items-center justify-between gap-3 rounded-[20px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]/95 p-4 shadow-xl backdrop-blur">
        <div>
          <p className="text-sm font-semibold text-[color:var(--text-primary)]">Admin actions</p>
          <p className="text-xs text-[color:var(--text-secondary)]">Suspend, restore, or permanently delete this organization.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {org.is_suspended ? (
            <button disabled={isPending} onClick={unsuspend} className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm font-semibold text-emerald-200 hover:bg-emerald-500/15 disabled:opacity-60">Unsuspend</button>
          ) : (
            <button disabled={isPending} onClick={() => setSuspendOpen(true)} className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-semibold text-amber-200 hover:bg-amber-500/15 disabled:opacity-60">Suspend</button>
          )}
          <button disabled={isPending} onClick={() => setDeleteOpen(true)} className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-semibold text-red-200 hover:bg-red-500/15 disabled:opacity-60">Delete</button>
        </div>
        {actionError && <div className="basis-full rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">{actionError}</div>}
      </section>
      <div className="grid gap-4 md:grid-cols-4">
        <Card label="Skills" value={org.skill_count} />
        <Card label="Sessions" value={org.session_count} />
        <Card label="PRs" value={org.pr_count} />
        <Card label="Violations 30d" value={org.violations_30d} />
      </div>
      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-lg font-semibold">Usage Chart</h2>
        <UsageChart usage={usage} />
      </section>
      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          <h2 className="text-lg font-semibold">Repos</h2>
          <div className="mt-4 space-y-2">{org.repos.map((repo) => <div className="flex justify-between rounded-xl border border-[color:var(--bg-border)] p-3" key={repo.id}><span>{repo.full_name}</span><span>{repo.skill_count} skills</span></div>)}</div>
        </section>
        <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          <h2 className="text-lg font-semibold">Recent Logins</h2>
          <div className="mt-4 space-y-2">{org.recent_logins.map((login, i) => <div className="rounded-xl border border-[color:var(--bg-border)] p-3" key={`${login.user_login}-${i}`}><div>@{login.user_login} · {login.user_email}</div><div className="text-xs text-[color:var(--text-tertiary)]">{login.ip_address} · {login.created_at ? new Date(login.created_at).toLocaleString() : "-"}</div></div>)}</div>
        </section>
      </div>
      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-lg font-semibold">Raw Data</h2>
        <pre className="mt-4 max-h-[480px] overflow-auto rounded-xl bg-[color:var(--bg-base)] p-4 text-xs text-[color:var(--text-secondary)]">{JSON.stringify(org, null, 2)}</pre>
      </section>
      {suspendOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="w-full max-w-lg rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 shadow-2xl">
            <h2 className="text-xl font-semibold">Suspend {org.name}</h2>
            <p className="mt-2 text-sm text-[color:var(--text-secondary)]">Suspended orgs remain in the system, but admins can see why access was paused.</p>
            <label className="mt-5 block text-sm font-medium text-[color:var(--text-secondary)]" htmlFor="suspend-reason">Reason</label>
            <textarea id="suspend-reason" value={reason} onChange={(event) => setReason(event.target.value)} className="mt-2 min-h-24 w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-sm outline-none focus:border-amber-400" placeholder="Reason shown to admins" />
            <div className="mt-5 flex justify-end gap-2">
              <button onClick={() => setSuspendOpen(false)} className="rounded-lg border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold">Cancel</button>
              <button disabled={isPending} onClick={suspend} className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-black disabled:opacity-60">Suspend org</button>
            </div>
          </div>
        </div>
      )}
      {deleteOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="w-full max-w-lg rounded-[24px] border border-red-500/30 bg-[color:var(--bg-surface)] p-6 shadow-2xl">
            <h2 className="text-xl font-semibold text-red-100">Delete {org.name}</h2>
            <p className="mt-2 text-sm text-[color:var(--text-secondary)]">This permanently deletes the organization and its child records through database cascades.</p>
            <label className="mt-5 block text-sm font-medium text-[color:var(--text-secondary)]" htmlFor="delete-confirm">Type the org name to confirm</label>
            <input id="delete-confirm" value={deleteConfirmation} onChange={(event) => setDeleteConfirmation(event.target.value)} className="mt-2 w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-sm outline-none focus:border-red-400" placeholder={org.name} />
            <div className="mt-5 flex justify-end gap-2">
              <button onClick={() => setDeleteOpen(false)} className="rounded-lg border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold">Cancel</button>
              <button disabled={isPending || deleteConfirmation !== org.name} onClick={deleteSelectedOrg} className="rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50">Delete org</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
