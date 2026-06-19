import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { AlertTriangle, Clock3, GitBranch, RefreshCcw, TimerReset } from "lucide-react";

import { API_URL, getBootstrapOrg, getMyOrg, type Org } from "../../../../lib/data";

type V8DriftEvent = {
  skill_id: string;
  name: string;
  repo_id: string;
  repo_name: string;
  predicted_decay_date: string | null;
  predicted_decay_days: number;
  decay_confidence: number;
  commits_30d: number;
  file_churn_30d: number;
  regen_queued: boolean;
  computed_at: string;
};

type V8DriftResponse = {
  events: V8DriftEvent[];
  total: number;
};

async function loadContext(): Promise<{ accessToken: string; org: Org | null }> {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  return { accessToken, org };
}

async function getDrift(accessToken: string, orgId: string): Promise<V8DriftResponse | null> {
  try {
    const response = await fetch(`${API_URL}/v8/orgs/${orgId}/skills/drift`, {
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) return null;
    return (await response.json()) as V8DriftResponse;
  } catch {
    return null;
  }
}

function fmtDate(value: string | null): string {
  if (!value) return "Not predicted";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

function driftTone(days: number): string {
  if (days <= 7) return "text-[color:var(--accent-red)]";
  if (days <= 30) return "text-amber-200";
  return "text-[color:var(--accent-green)]";
}

function driftLabel(days: number): string {
  if (days <= 7) return "Critical";
  if (days <= 30) return "Watch";
  return "Healthy";
}

function confidence(value: number): string {
  return `${Math.round(Math.max(0, Math.min(1, value)) * 100)}%`;
}

function EmptyState({ unavailable }: { unavailable?: boolean }) {
  return (
    <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
      <TimerReset className="mx-auto h-8 w-8 text-[color:var(--text-tertiary)]" />
      <h2 className="mt-3 font-semibold text-[color:var(--text-primary)]">{unavailable ? "Drift data unavailable" : "No drift events yet"}</h2>
      <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-[color:var(--text-secondary)]">
        {unavailable ? "Refresh after sign-in. Drift predictions will appear here when the authenticated v8 Skills API call succeeds." : "Skillayer will show half-life predictions here once skills have been re-grounded against current repository activity."}
      </p>
    </section>
  );
}

function Metric({ label, value, detail, icon, tone = "text-[color:var(--text-primary)]" }: { label: string; value: string | number; detail: string; icon: React.ReactNode; tone?: string }) {
  return (
    <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="flex items-center justify-between gap-3">
        <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">{label}</div>
        <div className="text-[color:var(--accent-primary)]">{icon}</div>
      </div>
      <div className={`mt-3 text-[30px] font-semibold ${tone}`}>{value}</div>
      <p className="mt-2 text-xs leading-5 text-[color:var(--text-secondary)]">{detail}</p>
    </article>
  );
}

export default async function SkillsDriftPage() {
  const { accessToken, org } = await loadContext();
  const drift = org?.id ? await getDrift(accessToken, org.id) : null;
  const events = drift?.events ?? [];
  const critical = events.filter((event) => event.predicted_decay_days <= 7).length;
  const queued = events.filter((event) => event.regen_queued).length;
  const avgDays = events.length ? Math.round(events.reduce((sum, event) => sum + event.predicted_decay_days, 0) / events.length) : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Drift</h1>
          <p className="mt-2 max-w-3xl text-[15px] leading-6 text-[color:var(--text-secondary)]">Skill half-life predictions show when generated skills are likely to stop matching the code they govern. Use this view to prioritize re-grounding before stale guidance reaches agents.</p>
        </div>
        <Link className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-4 py-2.5 text-[13px] font-semibold text-[color:var(--text-primary)] hover:bg-[color:var(--bg-surface)]" href="/skills/repos">
          <GitBranch className="h-4 w-4" />
          Repos
        </Link>
      </div>

      {drift === null ? (
        <EmptyState unavailable />
      ) : events.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <section className="grid gap-4 md:grid-cols-4">
            <Metric detail="Skills with a decay prediction in the current window." icon={<TimerReset className="h-4 w-4" />} label="Drift events" value={drift.total} />
            <Metric detail="Predicted to decay in seven days or less." icon={<AlertTriangle className="h-4 w-4" />} label="Critical" tone={critical ? "text-[color:var(--accent-red)]" : undefined} value={critical} />
            <Metric detail="Regeneration has already been queued." icon={<RefreshCcw className="h-4 w-4" />} label="Queued" value={queued} />
            <Metric detail="Average predicted half-life across listed skills." icon={<Clock3 className="h-4 w-4" />} label="Avg days" tone={driftTone(avgDays)} value={avgDays} />
          </section>

          <section className="rounded-[8px] border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
            <p className="text-sm leading-6 text-[color:var(--text-secondary)]">Drift events become governance signals: they can inform Policy rules, show up in Audit evidence, and tell teams when to refresh Skillayer-generated skills before agents rely on stale instructions.</p>
          </section>

          <section className="space-y-3">
            {events.map((event) => (
              <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={event.skill_id}>
                <div className="grid gap-5 lg:grid-cols-[minmax(0,1.35fr)_minmax(260px,0.85fr)]">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="font-semibold text-[color:var(--text-primary)]">{event.name}</h2>
                      <span className={`rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs font-semibold ${driftTone(event.predicted_decay_days)}`}>{driftLabel(event.predicted_decay_days)}</span>
                      {event.regen_queued ? <span className="rounded-md bg-[color:var(--accent-primary)]/15 px-2 py-1 text-xs font-semibold text-[color:var(--accent-primary)]">regen queued</span> : null}
                    </div>
                    <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{event.repo_name} · predicted decay {fmtDate(event.predicted_decay_date)}</p>
                    <div className="mt-4 grid gap-3 sm:grid-cols-3">
                      <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
                        <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Commits 30d</div>
                        <div className="mt-2 font-mono text-lg text-[color:var(--text-primary)]">{event.commits_30d}</div>
                      </div>
                      <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
                        <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">File churn</div>
                        <div className="mt-2 font-mono text-lg text-[color:var(--text-primary)]">{event.file_churn_30d}</div>
                      </div>
                      <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
                        <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Confidence</div>
                        <div className="mt-2 font-mono text-lg text-[color:var(--text-primary)]">{confidence(event.decay_confidence)}</div>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
                    <div className={`text-[34px] font-semibold leading-none ${driftTone(event.predicted_decay_days)}`}>{Math.round(event.predicted_decay_days)} days</div>
                    <p className="mt-2 text-sm text-[color:var(--text-secondary)]">predicted skill half-life remaining</p>
                    <div className="mt-5 h-2 overflow-hidden rounded-full bg-black/40">
                      <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${Math.max(8, Math.min(100, event.predicted_decay_days * 3))}%` }} />
                    </div>
                    <p className="mt-4 text-xs leading-5 text-[color:var(--text-tertiary)]">Computed {fmtDate(event.computed_at)} from recent commits and file churn.</p>
                  </div>
                </div>
              </article>
            ))}
          </section>
        </>
      )}
    </div>
  );
}
