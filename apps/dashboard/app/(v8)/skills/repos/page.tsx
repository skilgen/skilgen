import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { Github, GitBranch, ShieldCheck } from "lucide-react";

import { API_URL, getBootstrapOrg, getMyOrg, type Org } from "../../../../lib/data";

type V8RepoItem = {
  id: string;
  full_name: string;
  name: string;
  language: string | null;
  sensitivity_tier: string;
  indexing_status: string;
  generated_skill_count: number;
  drift_count: number;
  policy_bindings: string[];
  last_analysed_at: string | null;
};

type V8ReposResponse = {
  repos: V8RepoItem[];
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

async function getRepos(accessToken: string, orgId: string): Promise<V8ReposResponse | null> {
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
    const response = await fetch(`${API_URL}/v8/orgs/${orgId}/skills/repos`, {
      cache: "no-store",
      headers,
    });
    if (!response.ok) return null;
    return (await response.json()) as V8ReposResponse;
  } catch {
    return null;
  }
}

function fmtDate(value: string | null): string {
  if (!value) return "Pending";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

function tierTone(tier: string): string {
  if (tier === "restricted") return "border-[#ef4444]/40 text-[#ef4444]";
  if (tier === "confidential") return "border-[#f59e0b]/40 text-[#f59e0b]";
  return "border-[color:var(--bg-border)] text-[color:var(--text-secondary)]";
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-3 text-[30px] font-semibold text-[color:var(--text-primary)]">{value}</div>
    </div>
  );
}

export default async function SkillsReposPage() {
  const { accessToken, org } = await loadContext();
  const response = org?.id ? await getRepos(accessToken, org.id) : null;
  const repos = response?.repos ?? [];
  const generatedSkills = repos.reduce((sum, repo) => sum + repo.generated_skill_count, 0);
  const indexed = repos.filter((repo) => repo.indexing_status === "indexed").length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Repositories</h1>
          <p className="mt-2 text-[15px] text-[color:var(--text-secondary)]">Repos connected to Skillayer and covered by generated skills.</p>
        </div>
        <a className="inline-flex items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)]" href="https://github.com/apps/skillayer/installations/new" rel="noreferrer" target="_blank">
          <Github className="h-4 w-4" />
          Connect repo
        </a>
      </div>

      {response === null ? (
        <div className="rounded-[8px] border border-red-900/60 bg-red-950/30 p-8 text-sm text-red-100">
          <p className="text-[15px] font-semibold">Unable to load repositories.</p>
          <p className="mt-2 text-red-100/75">Refresh after sign-in. If this is local preview, make sure the API is running in bootstrap mode.</p>
        </div>
      ) : repos.length === 0 ? (
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-sm text-[color:var(--text-secondary)]">
          <GitBranch className="mx-auto h-6 w-6 text-[color:var(--text-tertiary)]" />
          <p className="mt-4 text-[15px] font-semibold text-[color:var(--text-primary)]">No repositories connected yet.</p>
          <p className="mx-auto mt-2 max-w-xl leading-6">Connect a repository to generate skills, score coverage, and start governing agent activity.</p>
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <Metric label="Connected repos" value={response.total} />
            <Metric label="Indexed" value={indexed} />
            <Metric label="Generated skills" value={generatedSkills} />
            <Metric label="Policy bindings" value={new Set(repos.flatMap((repo) => repo.policy_bindings)).size} />
          </div>

          <section className="overflow-hidden rounded-[8px] border border-[color:var(--bg-border)]">
            <div className="grid grid-cols-[minmax(280px,1.5fr)_130px_130px_130px_160px] bg-[color:var(--bg-surface)] px-4 py-3 text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">
              <span>Repository</span>
              <span>Tier</span>
              <span>Status</span>
              <span>Skills</span>
              <span>Last analyzed</span>
            </div>
            {repos.map((repo) => (
              <article className="grid grid-cols-[minmax(280px,1.5fr)_130px_130px_130px_160px] gap-3 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm" key={repo.id}>
                <div>
                  <div className="font-medium text-[color:var(--text-primary)]">{repo.full_name}</div>
                  <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{repo.language ?? "Language unknown"}</div>
                </div>
                <div>
                  <span className={`inline-flex rounded-md border px-2 py-1 text-[12px] capitalize ${tierTone(repo.sensitivity_tier)}`}>{repo.sensitivity_tier}</span>
                </div>
                <div className="inline-flex w-fit items-center gap-1 rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-[12px] capitalize text-[color:var(--text-secondary)]">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  {repo.indexing_status}
                </div>
                <Link className="font-semibold text-[color:var(--accent-primary)] hover:underline" href={`/skills/registry?repo=${encodeURIComponent(repo.id)}`}>{repo.generated_skill_count}</Link>
                <div className="text-[color:var(--text-secondary)]">{fmtDate(repo.last_analysed_at)}</div>
              </article>
            ))}
          </section>
        </>
      )}
    </div>
  );
}
