"use client";

import Link from "next/link";
import type { AdminOrg, AdminOverview, AdminUser } from "../../../lib/data";

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-[20px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="text-xs uppercase tracking-widest text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-3 text-3xl font-semibold text-[color:var(--text-primary)]">{value}</div>
    </div>
  );
}

export function AdminOverviewClient({ overview, orgs, users }: { overview: AdminOverview; orgs: AdminOrg[]; users: AdminUser[] }) {
  const plans = overview.orgs.by_plan || {};
  const totalPlans = Math.max(1, Object.values(plans).reduce((sum, value) => sum + value, 0));
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="mb-2 inline-flex rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-semibold text-red-300">ADMIN</div>
          <h1 className="text-3xl font-semibold tracking-tight">Platform Admin</h1>
          <p className="mt-2 text-sm text-[color:var(--text-secondary)]">Operational control plane for Skillayer cloud.</p>
        </div>
        <div className="flex gap-2">
          <Link className="rounded-lg border border-[color:var(--bg-border)] px-3 py-2 text-sm hover:bg-[color:var(--bg-surface)]" href="/dashboard/admin/orgs">Orgs</Link>
          <Link className="rounded-lg border border-[color:var(--bg-border)] px-3 py-2 text-sm hover:bg-[color:var(--bg-surface)]" href="/dashboard/admin/users">Users</Link>
          <Link className="rounded-lg border border-[color:var(--bg-border)] px-3 py-2 text-sm hover:bg-[color:var(--bg-surface)]" href="/dashboard/admin/logins">Logins</Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Total Orgs" value={overview.orgs.total} />
        <StatCard label="Active Orgs (30d)" value={overview.orgs.active_30d} />
        <StatCard label="Total Users" value={overview.users.total_unique} />
        <StatCard label="Logins (30d)" value={overview.users.logins_30d} />
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Total Skills" value={overview.data.total_skills ?? 0} />
        <StatCard label="Agent Sessions (30d)" value={overview.data.sessions_30d ?? 0} />
        <StatCard label="PRs Attributed (30d)" value={overview.data.prs_30d ?? 0} />
        <StatCard label="Analysis Runs" value={overview.data.total_analysis_runs ?? 0} />
      </div>

      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-lg font-semibold">Plan distribution</h2>
        <div className="mt-4 flex h-4 overflow-hidden rounded-full bg-white/5">
          {(["free", "team", "business"] as const).map((plan) => (
            <div key={plan} className={plan === "free" ? "bg-slate-400" : plan === "team" ? "bg-blue-400" : "bg-emerald-400"} style={{ width: `${((plans[plan] || 0) / totalPlans) * 100}%` }} />
          ))}
        </div>
        <div className="mt-3 flex gap-4 text-sm text-[color:var(--text-secondary)]">
          <span>Free {plans.free || 0}</span>
          <span>Team {plans.team || 0}</span>
          <span>Business {plans.business || 0}</span>
        </div>
      </section>

      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="border-b border-[color:var(--bg-border)] p-5">
          <h2 className="text-lg font-semibold">Top active orgs</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="text-xs uppercase tracking-widest text-[color:var(--text-tertiary)]">
              <tr>{["Org", "Plan", "Users", "Logins", "Sessions", "PRs", "Skills", "Last Active", "Status"].map((h) => <th className="px-5 py-3" key={h}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {orgs.slice(0, 10).map((org) => (
                <tr className="border-t border-[color:var(--bg-border)] hover:bg-white/[0.03]" key={org.id}>
                  <td className="px-5 py-3"><Link className="font-medium hover:text-[color:var(--accent-primary)]" href={`/dashboard/admin/orgs/${org.id}`}>{org.name}</Link></td>
                  <td className="px-5 py-3">{org.plan}</td>
                  <td className="px-5 py-3">{org.user_count}</td>
                  <td className="px-5 py-3">{org.login_count}</td>
                  <td className="px-5 py-3">{org.session_count}</td>
                  <td className="px-5 py-3">{org.pr_count}</td>
                  <td className="px-5 py-3">{org.skill_count}</td>
                  <td className="px-5 py-3">{org.last_active_at ? new Date(org.last_active_at).toLocaleDateString() : "Never"}</td>
                  <td className="px-5 py-3"><span className={org.is_suspended ? "rounded-full bg-red-500/10 px-2 py-1 text-red-300" : "rounded-full bg-emerald-500/10 px-2 py-1 text-emerald-300"}>{org.is_suspended ? "Suspended" : "Active"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-lg font-semibold">Most active users</h2>
        <div className="mt-4 grid gap-2">
          {users.slice(0, 10).map((user) => (
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[color:var(--bg-border)] p-3" key={user.user_login}>
              <div>
                <div className="font-medium">@{user.user_login}</div>
                <div className="text-xs text-[color:var(--text-tertiary)]">{user.orgs.map((org) => org.org_name).join(", ") || "No org"}</div>
              </div>
              <div className="text-sm text-[color:var(--text-secondary)]">{user.login_count} logins · {user.sessions_count} sessions · {user.prs_count} PRs</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
