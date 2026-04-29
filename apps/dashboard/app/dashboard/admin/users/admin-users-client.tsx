"use client";

import type { AdminUser } from "../../../../lib/data";

export function AdminUsersClient({ users, total }: { users: AdminUser[]; total: number }) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold">Admin Users</h1>
        <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{total} users found from login telemetry.</p>
      </div>
      <form className="flex flex-wrap gap-3 rounded-[20px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <input className="min-w-[260px] flex-1 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" name="search" placeholder="Search login or email" />
        <button className="rounded-lg bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]">Search</button>
      </form>
      <div className="overflow-x-auto rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead className="text-xs uppercase tracking-widest text-[color:var(--text-tertiary)]">
            <tr>{["User", "Email", "Orgs", "Total Logins", "Last Login", "First Seen", "Sessions", "PRs"].map((h) => <th className="px-4 py-3" key={h}>{h}</th>)}</tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr className="border-t border-[color:var(--bg-border)] hover:bg-white/[0.03]" key={user.user_login}>
                <td className="px-4 py-3 font-medium">@{user.user_login}</td>
                <td className="px-4 py-3">{user.user_email || "-"}</td>
                <td className="px-4 py-3">{user.orgs.map((org) => org.org_name).join(", ") || "-"}</td>
                <td className="px-4 py-3">{user.login_count}</td>
                <td className="px-4 py-3">{user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "-"}</td>
                <td className="px-4 py-3">{user.first_login_at ? new Date(user.first_login_at).toLocaleDateString() : "-"}</td>
                <td className="px-4 py-3">{user.sessions_count}</td>
                <td className="px-4 py-3">{user.prs_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
