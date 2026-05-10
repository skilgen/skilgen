import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { BadgeCheck, Gauge, GitBranch, ShieldCheck, TrendingUp } from "lucide-react";

import { API_URL, getBootstrapOrg, getMyOrg, type Org } from "../../../../lib/data";

type V8SkillScore = {
  total: number;
  groundedness: number;
  coverage: number;
  freshness: number;
  structure: number;
};

type V8SkillRegistryItem = {
  skill_id: string;
  name: string;
  version: string;
  signature_status: string;
  score: V8SkillScore;
  drift_status: string;
  last_code_grounded_at: string | null;
  owning_team: string;
  dependent_agents: string[];
  policy_bindings: string[];
  repo_id: string;
  repo_name: string;
  repo_full_name: string;
  sensitivity_tier: string;
};

type V8ScoreResponse = {
  subscores: string[];
  items: V8SkillRegistryItem[];
  total: number;
  average_score: number;
  rubric_path: string;
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

async function getScore(accessToken: string, orgId: string): Promise<V8ScoreResponse | null> {
  try {
    const response = await fetch(`${API_URL}/v8/orgs/${orgId}/skills/score?limit=100`, {
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) return null;
    return (await response.json()) as V8ScoreResponse;
  } catch {
    return null;
  }
}

function scoreTone(score: number): string {
  if (score >= 70) return "text-[color:var(--accent-green)]";
  if (score >= 40) return "text-amber-200";
  return "text-[color:var(--accent-red)]";
}

function scoreBand(score: number): string {
  if (score >= 70) return "Governed";
  if (score >= 40) return "Needs review";
  return "Critical";
}

function pct(value: number): string {
  return `${Math.max(0, Math.min(100, value))}%`;
}

function subscoreEntries(score: V8SkillScore) {
  return [
    ["Groundedness", score.groundedness],
    ["Coverage", score.coverage],
    ["Freshness", score.freshness],
    ["Structure", score.structure],
  ] as const;
}

function Metric({
  label,
  value,
  detail,
  icon,
  tone = "text-[color:var(--text-primary)]",
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: React.ReactNode;
  tone?: string;
}) {
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

function EmptyState({ unavailable }: { unavailable?: boolean }) {
  return (
    <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
      <Gauge className="mx-auto h-8 w-8 text-[color:var(--text-tertiary)]" />
      <h2 className="mt-3 font-semibold text-[color:var(--text-primary)]">{unavailable ? "Score data unavailable" : "No scored skills yet"}</h2>
      <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-[color:var(--text-secondary)]">
        {unavailable ? "Refresh after sign-in. Score data will appear here when the authenticated v8 Skills API call succeeds." : "Analyze a repository to generate skills, score them against the open rubric, and bind them to governance policies."}
      </p>
    </section>
  );
}

export default async function SkillsScorePage() {
  const { accessToken, org } = await loadContext();
  const score = org?.id ? await getScore(accessToken, org.id) : null;
  const items = score?.items ?? [];
  const weak = items.filter((item) => item.score.total < 70).length;
  const verified = items.filter((item) => item.signature_status === "verified").length;
  const bound = items.filter((item) => item.policy_bindings.length > 0).length;
  const average = Math.round(score?.average_score ?? 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Skilgen Score</h1>
          <p className="mt-2 max-w-3xl text-[15px] leading-6 text-[color:var(--text-secondary)]">Open Skilgen Score evidence over groundedness, coverage, freshness, and structure. Skillayer uses it as the governance substrate for deciding which skills can be trusted in agent workflows.</p>
        </div>
        <Link className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-4 py-2.5 text-[13px] font-semibold text-[color:var(--text-primary)] hover:bg-[color:var(--bg-surface)]" href="/skills/registry">
          <GitBranch className="h-4 w-4" />
          Registry
        </Link>
      </div>

      {score === null ? (
        <EmptyState unavailable />
      ) : items.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <section className="grid gap-4 md:grid-cols-4">
            <Metric detail="Mean total score across the current skill sample." icon={<Gauge className="h-4 w-4" />} label="Average score" tone={scoreTone(average)} value={`${average}/100`} />
            <Metric detail="Skills below the governed threshold and worth review." icon={<TrendingUp className="h-4 w-4" />} label="Needs review" value={weak} />
            <Metric detail="Skills with signed or content-addressed versions." icon={<BadgeCheck className="h-4 w-4" />} label="Verified" value={verified} />
            <Metric detail="Skills already attached to active policy controls." icon={<ShieldCheck className="h-4 w-4" />} label="Policy bound" value={bound} />
          </section>

          <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 className="font-semibold text-[color:var(--text-primary)]">Open Skilgen Score rubric</h2>
                <p className="mt-1 text-sm leading-6 text-[color:var(--text-secondary)]">Subscores are additive and stay visible so teams can tell whether a skill is stale, shallow, ungrounded, or malformed.</p>
              </div>
              <div className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 font-mono text-xs text-[color:var(--text-secondary)]">{score.rubric_path}</div>
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-4">
              {score.subscores.map((subscore) => (
                <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4" key={subscore}>
                  <div className="text-sm font-semibold text-[color:var(--text-primary)]">{subscore}</div>
                  <p className="mt-2 text-xs leading-5 text-[color:var(--text-secondary)]">{subscore === "Groundedness" ? "Matches the code it claims to describe." : subscore === "Coverage" ? "Covers the scope the skill advertises." : subscore === "Freshness" ? "Was recently verified against current HEAD." : "Conforms to the open SKILL.md structure."}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="space-y-3">
            {items.map((item) => (
              <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={item.skill_id}>
                <div className="grid gap-5 lg:grid-cols-[minmax(0,1.4fr)_minmax(260px,0.9fr)] lg:items-start">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="font-semibold text-[color:var(--text-primary)]">{item.name}</h2>
                      <span className={`rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs font-semibold ${scoreTone(item.score.total)}`}>{scoreBand(item.score.total)}</span>
                    </div>
                    <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{item.repo_full_name} · {item.version} · {item.sensitivity_tier}</p>
                    <div className="mt-4 flex flex-wrap gap-2 text-xs text-[color:var(--text-secondary)]">
                      <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1">{item.signature_status}</span>
                      <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1">{item.drift_status}</span>
                      <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1">{item.policy_bindings.length} policies</span>
                      <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1">{item.dependent_agents.length} agents</span>
                    </div>
                  </div>

                  <div>
                    <div className={`text-right text-[28px] font-semibold leading-none ${scoreTone(item.score.total)}`}>{item.score.total}/100</div>
                    <div className="mt-4 space-y-3">
                      {subscoreEntries(item.score).map(([label, value]) => (
                        <div key={`${item.skill_id}-${label}`}>
                          <div className="mb-1 flex items-center justify-between gap-3 text-xs">
                            <span className="font-medium text-[color:var(--text-secondary)]">{label}</span>
                            <span className="font-mono text-[color:var(--text-tertiary)]">{value}/25</span>
                          </div>
                          <div className="h-2 overflow-hidden rounded-full bg-[color:var(--bg-base)]">
                            <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: pct(value * 4) }} />
                          </div>
                        </div>
                      ))}
                    </div>
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
