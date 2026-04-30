import { withAuth } from "@workos-inc/authkit-nextjs";
import { ClipboardList } from "lucide-react";

import { getBootstrapOrg, getMyOrg, getOrgRepos, getSLAPolicies } from "../../../lib/data";

export default async function SLAPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: true });
    accessToken = session.accessToken || "";
  } catch {
    accessToken = "";
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const [policies, repos] = org ? await Promise.all([getSLAPolicies(accessToken, org.id), getOrgRepos(accessToken, org.id)]) : [[], []];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Coverage SLA</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Set skill coverage targets and check whether repositories are breaching them.</p>
      </header>

      <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="font-semibold">Add SLA policy</h2>
        <form className="mt-4 grid gap-3 lg:grid-cols-[1.2fr_1fr_1fr_1.2fr_auto]">
          <input className="h-10 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-sm" name="name" placeholder="Policy name" />
          <select className="h-10 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-sm" name="repo_id">
            <option value="">Whole org</option>
            {(repos ?? []).map((repo) => <option key={repo.id} value={repo.id}>{repo.name}</option>)}
          </select>
          <input className="h-10 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-sm" defaultValue={80} max={100} min={60} name="coverage_target_pct" type="number" />
          <input className="h-10 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-sm" name="alert_email" placeholder="alerts@example.com" />
          <button className="h-10 rounded-md bg-[color:var(--accent-primary)] px-4 text-sm font-semibold text-[color:var(--bg-base)]" formAction="/api/sla" type="submit">Add</button>
        </form>
      </section>

      {(policies ?? []).length === 0 ? (
        <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
          <ClipboardList className="mx-auto h-10 w-10 text-[color:var(--accent-primary)]" />
          <h2 className="mt-3 text-lg font-semibold">No SLA policies yet</h2>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Create a policy to track coverage commitments across repos.</p>
        </section>
      ) : (
        <section className="grid gap-4 md:grid-cols-2">
          {(policies ?? []).map((policy) => {
            const statusClass = policy.last_status === "compliant" ? "text-[color:var(--accent-green)] bg-[color:var(--accent-green)]/10" : policy.last_status === "breaching" ? "text-[color:var(--accent-red)] bg-[color:var(--accent-red)]/10 animate-pulse" : "text-[color:var(--text-tertiary)] bg-white/5";
            return (
              <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={policy.id}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold">{policy.name}</h3>
                    <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{policy.repo_name ?? "Whole org"} · target {policy.coverage_target_pct}%</p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${statusClass}`}>{policy.last_status}</span>
                </div>
                <div className="relative mt-5 h-3 rounded-full bg-black/30">
                  <div className="h-3 rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${Math.min(100, policy.last_status === "compliant" ? policy.coverage_target_pct : Math.max(15, policy.coverage_target_pct - 20))}%` }} />
                  <div className="absolute top-[-4px] h-5 w-0.5 bg-white" style={{ left: `${policy.coverage_target_pct}%` }} />
                </div>
                <div className="mt-4 flex gap-2">
                  <button className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs font-semibold">Check now</button>
                  <button className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs font-semibold">Edit</button>
                  <button className="rounded-md border border-red-500/30 px-3 py-2 text-xs font-semibold text-red-200">Remove</button>
                </div>
              </article>
            );
          })}
        </section>
      )}
    </div>
  );
}
