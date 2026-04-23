import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { SectionFallback } from "@/components/section-fallback";
import { API_URL, type Org, type OrgCoverageSummary, type SkillCategory } from "../../../lib/data";

export const dynamic = "force-dynamic";

const categoryMeta: Record<SkillCategory, { label: string; icon: string; command: string }> = {
  codebase_architecture: { label: "Codebase Architecture", icon: "🏗️", command: "skilgen deliver --auto-detect" },
  code_style: { label: "Code Style", icon: "🎨", command: "skilgen deliver --project-root ." },
  testing_conventions: { label: "Testing Conventions", icon: "🧪", command: "skilgen deliver --project-root ." },
  internal_tools: { label: "Internal Tools", icon: "🔧", command: "skilgen analyze --source openapi" },
  security_compliance: { label: "Security Compliance", icon: "🔒", command: "skilgen analyze --source sarif" },
  design_system: { label: "Design System", icon: "🎯", command: "skilgen analyze --source all" },
  data_schema: { label: "Data Schema", icon: "🗄️", command: "skilgen analyze --source dbt" },
  operational_knowledge: { label: "Operational Knowledge", icon: "📋", command: "skilgen analyze --source runbooks" },
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

async function loadCoverage(accessToken: string, orgId: string): Promise<OrgCoverageSummary | null> {
  try {
    const res = await fetch(`${API_URL}/orgs/${orgId}/coverage-summary`, {
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined,
      next: { revalidate: 60 },
    });
    if (!res.ok) return null;
    return (await res.json()) as OrgCoverageSummary;
  } catch (error) {
    console.error("Sources page coverage fetch failed:", error);
    return null;
  }
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
  const coverage = org ? await loadCoverage(accessToken, org.id) : null;

  if (!coverage) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Sources</h1>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Org-wide knowledge source coverage</p>
        </div>
        <SectionFallback section="source coverage" />
      </div>
    );
  }

  const repoCount = coverage.repos.length;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Sources</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Org-wide knowledge source coverage</p>
      </div>

      <SectionErrorBoundary section="source coverage summary">
        <section className="mb-8 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
          <div className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Coverage score</div>
          <div className="mt-2 text-[44px] font-bold leading-none text-[color:var(--accent-primary)]">{coverage.org_coverage_score}%</div>
          <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
            <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${coverage.org_coverage_score}%` }} />
          </div>
        </section>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="source categories">
        <section className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {(Object.keys(categoryMeta) as SkillCategory[]).map((category) => {
            const meta = categoryMeta[category];
            const reposCovered = coverage.repos.filter((repo) => !repo.missing_categories.includes(category));
            const reposMissing = coverage.repos.filter((repo) => repo.missing_categories.includes(category));
            return (
              <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={category}>
                <div className="mb-4 flex items-center gap-2">
                  <span aria-hidden="true">{meta.icon}</span>
                  <h2 className="text-[14px] font-semibold text-[color:var(--text-primary)]">{meta.label}</h2>
                </div>
                <p className="text-[13px] text-[color:var(--text-secondary)]">
                  {reposCovered.length} of {repoCount} repos covered
                </p>
                {reposMissing.length > 0 ? (
                  <div className="mt-4 space-y-2">
                    {reposMissing.slice(0, 4).map((repo) => (
                      <Link className="block text-[12px] text-red-300 hover:text-red-200" href={`/dashboard/repos/${repo.repo_id}`} key={`${category}-${repo.repo_id}`}>
                        {repo.name}
                      </Link>
                    ))}
                  </div>
                ) : null}
              </article>
            );
          })}
        </section>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="source commands">
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">How to add sources</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {(Object.keys(categoryMeta) as SkillCategory[]).map((category) => {
              const meta = categoryMeta[category];
              return (
                <div className="rounded-lg border border-[color:var(--bg-border)] bg-black/10 p-4" key={`command-${category}`}>
                  <div className="text-[13px] font-semibold text-[color:var(--text-primary)]">{meta.label}</div>
                  <code className="mt-2 block rounded-md bg-black/30 px-3 py-2 font-mono text-[12px] text-[color:var(--accent-primary)]">{meta.command}</code>
                </div>
              );
            })}
          </div>
        </section>
      </SectionErrorBoundary>
    </div>
  );
}
