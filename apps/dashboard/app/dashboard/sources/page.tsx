import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { API_URL, type Org, getOrgCoverageSummary, type OrgCoverageSummary, type RepoCoverageSummary, type SkillCategory } from "../../../lib/data";

export const dynamic = "force-dynamic";

const CATEGORY_META: Record<SkillCategory, { label: string; icon: string; cliCommand: string }> = {
  codebase_architecture: {
    label: "Codebase Architecture",
    icon: "🏗️",
    cliCommand: "skilgen analyze --source terraform",
  },
  code_style: {
    label: "Code Style & Conventions",
    icon: "🎨",
    cliCommand: "skilgen deliver --project-root .",
  },
  testing_conventions: {
    label: "Testing Conventions",
    icon: "🧪",
    cliCommand: "skilgen deliver --project-root .",
  },
  internal_tools: {
    label: "Internal Tools & APIs",
    icon: "🔧",
    cliCommand: "skilgen analyze --source openapi",
  },
  security_compliance: {
    label: "Security & Compliance",
    icon: "🔒",
    cliCommand: "skilgen analyze --source sarif",
  },
  design_system: {
    label: "Design System",
    icon: "🎯",
    cliCommand: "skilgen deliver --project-root .",
  },
  data_schema: {
    label: "Data & Schema",
    icon: "🗄️",
    cliCommand: "skilgen analyze --source dbt",
  },
  operational_knowledge: {
    label: "Operational Knowledge",
    icon: "📋",
    cliCommand: "skilgen analyze --source runbooks",
  },
};

async function loadBootstrapOrg(): Promise<Org | null> {
  try {
    const res = await fetch(`${API_URL}/orgs/bootstrap`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    return (await res.json()) as Org;
  } catch (error) {
    console.error("Sources page org fetch failed:", error);
    return null;
  }
}

function coveredRepoCount(category: SkillCategory, repos: RepoCoverageSummary[]): number {
  return repos.filter((repo) => !repo.missing_categories.includes(category)).length;
}

function missingRepoNames(category: SkillCategory, repos: RepoCoverageSummary[]): string[] {
  return repos.filter((repo) => repo.missing_categories.includes(category)).map((repo) => repo.name);
}

export default async function SourcesPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: true });
    accessToken = session.accessToken || "";
  } catch (error) {
    console.error("Sources page auth unavailable:", error);
  }

  const org = await loadBootstrapOrg();
  let coverage: OrgCoverageSummary | null = null;

  try {
    coverage = org ? await getOrgCoverageSummary(accessToken, org.id) : null;
  } catch (error) {
    console.error("Sources page coverage fetch failed:", error);
  }

  if (!coverage) {
    return (
      <div className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 text-[color:var(--text-secondary)]">
        Unable to load coverage data. Refresh or contact support.
      </div>
    );
  }

  const reposByAttention = [...coverage.repos].sort((left, right) => left.coverage_score - right.coverage_score);
  const coveredCategories = Math.round((coverage.org_coverage_score / 100) * 8);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Knowledge Coverage</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Which knowledge categories are covered across your org</p>
      </div>

      <section className="mb-8 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <div className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Org coverage score</div>
        <div className="mt-2 text-[44px] font-bold leading-none text-[color:var(--accent-primary)]">{coverage.org_coverage_score}%</div>
        <p className="mt-2 text-[13px] text-[color:var(--text-secondary)]">
          of skill categories covered across your org ({coveredCategories} of 8)
        </p>
        <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
          <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${coverage.org_coverage_score}%` }} />
        </div>
      </section>

      <section className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {(Object.keys(CATEGORY_META) as SkillCategory[]).map((category) => {
          const meta = CATEGORY_META[category];
          const coveredCount = coveredRepoCount(category, coverage.repos);
          const missingNames = missingRepoNames(category, coverage.repos);
          const covered = coveredCount > 0;
          return (
            <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={category}>
              <div className="mb-4 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span aria-hidden="true">{meta.icon}</span>
                  <h2 className="text-[14px] font-semibold text-[color:var(--text-primary)]">{meta.label}</h2>
                </div>
                <span
                  className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                    covered ? "bg-green-900/30 text-green-300" : "bg-red-900/30 text-red-300"
                  }`}
                >
                  {covered ? `Covered in ${coveredCount} repos` : "Not covered"}
                </span>
              </div>
              <div className="space-y-2 text-[12px] text-[color:var(--text-secondary)]">
                {missingNames.length > 0 ? <p>Missing in {missingNames.slice(0, 3).join(", ")}</p> : <p>Covered across every connected repo.</p>}
                {!covered ? (
                  <code className="block rounded-md bg-black/30 px-3 py-2 font-mono text-[12px] text-[color:var(--text-tertiary)]">
                    {meta.cliCommand}
                  </code>
                ) : null}
              </div>
            </article>
          );
        })}
      </section>

      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
          <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Repos needing attention</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse text-left text-[13px]">
            <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
              <tr className="border-b border-[color:var(--bg-border)]">
                <th className="px-5 py-3 font-semibold">Repo</th>
                <th className="px-5 py-3 font-semibold">Coverage score</th>
                <th className="px-5 py-3 font-semibold">Missing categories</th>
              </tr>
            </thead>
            <tbody>
              {reposByAttention.map((repo) => (
                <tr className="border-b border-[color:var(--bg-elevated)] last:border-b-0" key={repo.repo_id}>
                  <td className="px-5 py-4 font-medium text-[color:var(--text-primary)]">
                    <Link className="hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repo.repo_id}`}>
                      {repo.name}
                    </Link>
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <span className="w-12 text-[color:var(--text-primary)]">{repo.coverage_score}%</span>
                      <div className="h-2 flex-1 overflow-hidden rounded-full bg-white/10">
                        <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${repo.coverage_score}%` }} />
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex flex-wrap gap-2">
                      {repo.missing_categories.map((category) => (
                        <span className="rounded-full bg-red-900/30 px-2 py-0.5 text-[12px] font-semibold text-red-300" key={`${repo.repo_id}-${category}`}>
                          {CATEGORY_META[category]?.label ?? category}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
