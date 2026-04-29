"use client";

import type { AdminLoginEvent } from "../../../../lib/data";

export function AdminLoginsClient({ logins, total }: { logins: AdminLoginEvent[]; total: number }) {
  const grouped = logins.reduce<Record<string, AdminLoginEvent[]>>((acc, login) => {
    const key = login.created_at ? new Date(login.created_at).toDateString() : "Unknown";
    acc[key] = [...(acc[key] || []), login];
    return acc;
  }, {});
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold">Login Events</h1>
        <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{total} login events recorded.</p>
      </div>
      <form className="flex flex-wrap gap-3 rounded-[20px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <input className="min-w-[220px] flex-1 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" name="user_login" placeholder="User login" />
        <input className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" name="date_from" type="date" />
        <input className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" name="date_to" type="date" />
        <button className="rounded-lg bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]">Filter</button>
      </form>
      {Object.entries(grouped).map(([day, events]) => (
        <section className="space-y-3" key={day}>
          <div className="sticky top-[52px] bg-[color:var(--bg-base)] py-2 text-xs font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">{day}</div>
          {events.map((event) => (
            <div className="relative border-l border-[color:var(--bg-border)] pl-5" key={event.id}>
              <span className="absolute -left-[5px] top-4 h-3 w-3 rounded-full bg-blue-400 ring-4 ring-[color:var(--bg-base)]" />
              <div className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
                <div className="font-medium">@{event.user_login || "unknown"} · {event.user_email || "no email"}</div>
                <div className="mt-1 text-xs text-[color:var(--text-tertiary)]">{event.org_name || event.org_id || "No org"} · {event.ip_address || "No IP"} · {event.created_at ? new Date(event.created_at).toLocaleTimeString() : "-"}</div>
                <div className="mt-2 truncate text-xs text-[color:var(--text-secondary)]">{event.user_agent || "No user-agent"}</div>
              </div>
            </div>
          ))}
        </section>
      ))}
    </div>
  );
}
