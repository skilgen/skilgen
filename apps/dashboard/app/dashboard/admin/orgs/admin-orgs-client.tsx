"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import type { AdminOrg } from "../../../../lib/data";

export function AdminOrgsClient({ orgs, total }: { orgs: AdminOrg[]; total: number }) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [target, setTarget] = useState<AdminOrg | null>(null);
  const [mode, setMode] = useState<"suspend" | "delete" | null>(null);
  const [reason, setReason] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function run(path: string, init: RequestInit) {
    setError(null);
    const response = await fetch(path, init);
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new Error(body?.detail || "Admin action failed");
    }
  }

  function closeModal() {
    setTarget(null);
    setMode(null);
    setReason("");
    setConfirmation("");
  }

  function suspend(org: AdminOrg) {
    setTarget(org);
    setMode("suspend");
  }

  function deleteOrg(org: AdminOrg) {
    setTarget(org);
    setMode("delete");
  }

  function unsuspend(org: AdminOrg) {
    startTransition(async () => {
      try {
        await run(`/api/admin/orgs/${org.id}/unsuspend`, { method: "POST" });
        router.refresh();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not unsuspend org");
      }
    });
  }

  function confirmAction() {
    if (!target || !mode) return;
    startTransition(async () => {
      try {
        if (mode === "suspend") {
          await run(`/api/admin/orgs/${target.id}/suspend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reason }),
          });
        } else {
          await run(`/api/admin/orgs/${target.id}`, { method: "DELETE" });
        }
        closeModal();
        router.refresh();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Admin action failed");
      }
    });
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold">Admin Orgs</h1>
        <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{total} organizations tracked across Skillayer.</p>
      </div>
      <form className="flex flex-wrap gap-3 rounded-[20px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <input className="min-w-[220px] flex-1 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" name="search" placeholder="Search orgs" />
        <select className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" name="plan">
          <option value="">All plans</option>
          <option value="free">Free</option>
          <option value="team">Team</option>
          <option value="business">Business</option>
        </select>
        <select className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" name="sort_by">
          <option value="created_at">Created</option>
          <option value="last_active">Last active</option>
          <option value="skill_count">Skills</option>
          <option value="session_count">Sessions</option>
        </select>
        <button className="rounded-lg bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]">Filter</button>
        <span className="rounded-lg border border-[color:var(--bg-border)] px-4 py-2 text-sm text-[color:var(--text-tertiary)]">CSV export via /admin/metrics/export</span>
      </form>
      {error && <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>}
      <div className="overflow-x-auto rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <table className="w-full min-w-[1100px] text-left text-sm">
          <thead className="text-xs uppercase tracking-widest text-[color:var(--text-tertiary)]">
            <tr>{["Org", "Plan", "Status", "Users", "Logins", "Sessions", "PRs", "Skills", "Repos", "Created", "Last Active", "Actions"].map((h) => <th className="px-4 py-3" key={h}>{h}</th>)}</tr>
          </thead>
          <tbody>
            {orgs.map((org) => (
              <tr className={`border-t border-[color:var(--bg-border)] hover:bg-white/[0.03] ${org.is_suspended ? "bg-red-500/5" : ""}`} key={org.id}>
                <td className="px-4 py-3 font-medium">{org.name}</td>
                <td className="px-4 py-3">{org.plan}</td>
                <td className="px-4 py-3">{org.is_suspended ? <span className="text-red-300">Suspended</span> : <span className="text-emerald-300">Active</span>}</td>
                <td className="px-4 py-3">{org.user_count}</td>
                <td className="px-4 py-3">{org.login_count}</td>
                <td className="px-4 py-3">{org.session_count}</td>
                <td className="px-4 py-3">{org.pr_count}</td>
                <td className="px-4 py-3">{org.skill_count}</td>
                <td className="px-4 py-3">{org.repo_count}</td>
                <td className="px-4 py-3">{org.created_at ? new Date(org.created_at).toLocaleDateString() : "-"}</td>
                <td className="px-4 py-3">{org.last_active_at ? new Date(org.last_active_at).toLocaleDateString() : "Never"}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Link className="text-[color:var(--accent-primary)] hover:underline" href={`/dashboard/admin/orgs/${org.id}`}>View</Link>
                    {org.is_suspended ? (
                      <button disabled={isPending} onClick={() => unsuspend(org)} className="rounded-md border border-emerald-500/30 px-2 py-1 text-xs text-emerald-200 hover:bg-emerald-500/10 disabled:opacity-60">Unsuspend</button>
                    ) : (
                      <button disabled={isPending} onClick={() => suspend(org)} className="rounded-md border border-amber-500/30 px-2 py-1 text-xs text-amber-200 hover:bg-amber-500/10 disabled:opacity-60">Suspend</button>
                    )}
                    <button disabled={isPending} onClick={() => deleteOrg(org)} className="rounded-md border border-red-500/30 px-2 py-1 text-xs text-red-200 hover:bg-red-500/10 disabled:opacity-60">Delete</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {orgs.length === 0 && <div className="rounded-[24px] border border-[color:var(--bg-border)] p-8 text-center text-[color:var(--text-secondary)]">No orgs match your filters.</div>}
      {target && mode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="w-full max-w-lg rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 shadow-2xl">
            <h2 className="text-xl font-semibold">{mode === "suspend" ? `Suspend ${target.name}` : `Delete ${target.name}`}</h2>
            <p className="mt-2 text-sm text-[color:var(--text-secondary)]">
              {mode === "suspend" ? "Add a short reason so future admins understand why access was paused." : "This permanently deletes the organization and its child records through database cascades."}
            </p>
            {mode === "suspend" ? (
              <>
                <label className="mt-5 block text-sm font-medium text-[color:var(--text-secondary)]" htmlFor="list-suspend-reason">Reason</label>
                <textarea id="list-suspend-reason" value={reason} onChange={(event) => setReason(event.target.value)} className="mt-2 min-h-24 w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-sm outline-none focus:border-amber-400" />
              </>
            ) : (
              <>
                <label className="mt-5 block text-sm font-medium text-[color:var(--text-secondary)]" htmlFor="list-delete-confirm">Type the org name to confirm</label>
                <input id="list-delete-confirm" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} className="mt-2 w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-sm outline-none focus:border-red-400" placeholder={target.name} />
              </>
            )}
            <div className="mt-5 flex justify-end gap-2">
              <button onClick={closeModal} className="rounded-lg border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold">Cancel</button>
              <button disabled={isPending || (mode === "delete" && confirmation !== target.name)} onClick={confirmAction} className={mode === "suspend" ? "rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-black disabled:opacity-60" : "rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"}>
                {mode === "suspend" ? "Suspend org" : "Delete org"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
