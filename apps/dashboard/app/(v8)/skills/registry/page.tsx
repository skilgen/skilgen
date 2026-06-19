import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { Bot, BookOpen, GitBranch, ShieldCheck } from "lucide-react";

import { API_URL, getBootstrapOrg, getMyOrg, type Org } from "../../../../lib/data";

type V8SkillRegistryItem = {
  skill_id: string;
  name: string;
  version: string;
  signature_status: string;
  score: {
    total: number;
    groundedness: number;
    coverage: number;
    freshness: number;
    structure: number;
  };
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

type V8RegistryResponse = {
  items: V8SkillRegistryItem[];
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

async function getRegistry(accessToken: string, orgId: string): Promise<V8RegistryResponse | null> {
  try {
    const response = await fetch(`${API_URL}/v8/orgs/${orgId}/skills/registry?limit=100`, {
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) return null;
    return (await response.json()) as V8RegistryResponse;
  } catch {
    return null;
  }
}

function scoreTone(score: number): string {
  if (score >= 70) return "text-[color:var(--accent-green)]";
  if (score >= 40) return "text-[#f59e0b]";
  return "text-[#ef4444]";
}

function fmtDate(value: string | null): string {
  if (!value) return "Never";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

function Summary({ items, total }: { items: V8SkillRegistryItem[]; total: number }) {
  const verified = items.filter((item) => item.signature_status === "verified").length;
  const avg = items.length ? Math.round(items.reduce((sum, item) => sum + item.score.total, 0) / items.length) : 0;
  const repos = new Set(items.map((item) => item.repo_id)).size;
  const dependentAgents = new Set(items.flatMap((item) => item.dependent_agents)).size;
  const policyBindings = new Set(items.flatMap((item) => item.policy_bindings)).size;
  return (
    <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
      <Metric label="Generated skills" value={total} />
      <Metric label="Repos covered" value={repos} />
      <Metric label="Verified signatures" value={verified} />
      <Metric label="Dependent agents" value={dependentAgents} />
      <Metric label="Policy bindings" value={policyBindings} />
      <Metric label="Average score" value={`${avg}/100`} tone={scoreTone(avg)} />
    </div>
  );
}

function Metric({ label, value, tone = "text-[color:var(--text-primary)]" }: { label: string; value: string | number; tone?: string }) {
  return (
    <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className={`mt-3 text-[30px] font-semibold ${tone}`}>{value}</div>
    </div>
  );
}

function PillList({ empty, items }: { empty: string; items: string[] }) {
  if (!items.length) return <span className="text-xs text-[color:var(--text-tertiary)]">{empty}</span>;
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.slice(0, 3).map((item) => (
        <span className="max-w-[180px] truncate rounded-sm border border-[color:var(--bg-border)] px-2 py-0.5 text-[11px] text-[color:var(--text-secondary)]" key={item} title={item}>
          {item}
        </span>
      ))}
      {items.length > 3 ? <span className="rounded-sm border border-[color:var(--bg-border)] px-2 py-0.5 text-[11px] text-[color:var(--text-tertiary)]">+{items.length - 3}</span> : null}
    </div>
  );
}

export default async function SkillsRegistryPage() {
  const { accessToken, org } = await loadContext();
  const registry = org?.id ? await getRegistry(accessToken, org.id) : null;
  const items = registry?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Skill Registry</h1>
          <p className="mt-2 text-[15px] text-[color:var(--text-secondary)]">Generated Skillayer skills already indexed from your repositories.</p>
        </div>
        <Link className="inline-flex items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)]" href="/skills/repos">
          <GitBranch className="h-4 w-4" />
          Analyze repo
        </Link>
      </div>

      {registry === null ? (
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-sm text-[color:var(--text-secondary)]">
          <BookOpen className="mx-auto h-6 w-6 text-[color:var(--text-tertiary)]" />
          <p className="mt-4 text-[15px] font-semibold text-[color:var(--text-primary)]">Skill registry could not reach the API.</p>
          <p className="mx-auto mt-2 max-w-xl leading-6">Refresh after sign-in. Your generated skills will appear here once the authenticated API call succeeds.</p>
        </div>
      ) : items.length === 0 ? (
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-sm text-[color:var(--text-secondary)]">
          <BookOpen className="mx-auto h-6 w-6 text-[color:var(--text-tertiary)]" />
          <p className="mt-4 text-[15px] font-semibold text-[color:var(--text-primary)]">No generated skills yet.</p>
          <p className="mx-auto mt-2 max-w-xl leading-6">Analyze a repository to generate the first Skillayer skills for this org.</p>
        </div>
      ) : (
        <>
          <Summary items={items} total={registry.total} />
          <section className="overflow-hidden rounded-[8px] border border-[color:var(--bg-border)]">
            <div className="overflow-x-auto">
              <div className="grid min-w-[1040px] grid-cols-[minmax(260px,1.4fr)_minmax(190px,1fr)_minmax(260px,1.2fr)_100px_130px_130px] bg-[color:var(--bg-surface)] px-4 py-3 text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">
                <span>Skill</span>
                <span>Repo</span>
                <span>Governance evidence</span>
                <span>Score</span>
                <span>Signature</span>
                <span>Grounded</span>
              </div>
              {items.map((item) => (
                <article className="grid min-w-[1040px] grid-cols-[minmax(260px,1.4fr)_minmax(190px,1fr)_minmax(260px,1.2fr)_100px_130px_130px] gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm" key={item.skill_id}>
                  <div>
                    <div className="font-medium text-[color:var(--text-primary)]">{item.name}</div>
                    <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{item.owning_team} · {item.version} · {item.drift_status}</div>
                  </div>
                  <Link className="text-[color:var(--accent-primary)] hover:underline" href={`/skills/repos?repo=${encodeURIComponent(item.repo_id)}`}>{item.repo_full_name}</Link>
                  <div className="space-y-2">
                    <div className="flex items-start gap-2">
                      <Bot className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[color:var(--accent-primary)]" />
                      <PillList empty="No dependent agents" items={item.dependent_agents} />
                    </div>
                    <div className="flex items-start gap-2">
                      <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[color:var(--accent-primary)]" />
                      <PillList empty="No policy bindings" items={item.policy_bindings} />
                    </div>
                  </div>
                  <div className={`font-semibold ${scoreTone(item.score.total)}`}>{item.score.total}/100</div>
                  <div className="inline-flex h-fit w-fit items-center gap-1 rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-[12px] capitalize text-[color:var(--text-secondary)]">
                    <ShieldCheck className="h-3.5 w-3.5" />
                    {item.signature_status}
                  </div>
                  <div className="text-[color:var(--text-secondary)]">{fmtDate(item.last_code_grounded_at)}</div>
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
