import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { BookOpen, Search } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { API_URL, getRegistrySkills, type Org, type RegistrySkill } from "../../../lib/data";
import { ImportButton } from "./import-button";

export const dynamic = "force-dynamic";

type SearchParams = Record<string, string | string[] | undefined>;

type RegistryPageProps = {
  searchParams?: Promise<SearchParams>;
};

function firstValue(value: string | string[] | undefined): string {
  return Array.isArray(value) ? value[0] ?? "" : value ?? "";
}

function sortValue(value: string): string {
  return ["imports", "score", "newest"].includes(value) ? value : "imports";
}

function tabValue(value: string): "browse" | "published" {
  return value === "published" ? "published" : "browse";
}

async function bootstrapOrgId(): Promise<string | null> {
  try {
    const response = await fetch(`${API_URL}/orgs/bootstrap`, { next: { revalidate: 60 } });
    if (!response.ok) return null;
    const org = (await response.json()) as Org;
    return org.id;
  } catch (error) {
    console.error("Failed to load registry org:", error);
    return null;
  }
}

function scoreClass(score: number): string {
  if (score >= 85) return "bg-green-900/30 text-green-300";
  if (score >= 70) return "bg-emerald-900/30 text-emerald-300";
  if (score >= 50) return "bg-amber-900/30 text-amber-300";
  return "bg-red-900/30 text-red-300";
}

function RegistryCard({ skill }: { skill: RegistrySkill }) {
  return (
    <article className="cursor-pointer rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5 transition-colors hover:border-[rgb(var(--accent-primary-rgb)/0.4)]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h2 className="truncate text-[16px] font-semibold text-[color:var(--text-primary)]">{skill.name}</h2>
          <p className="mt-1 font-mono text-[12px] text-[color:var(--text-tertiary)]">{skill.domain}</p>
        </div>
        <span className={`shrink-0 rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreClass(skill.score_total)}`}>
          {skill.score_total}/100
        </span>
      </div>
      <p className="mt-4 line-clamp-3 min-h-[60px] text-[13px] leading-5 text-[color:var(--text-secondary)]">{skill.description}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {skill.is_official ? <span className="rounded-full bg-[rgb(var(--accent-primary-rgb)/0.14)] px-2 py-0.5 text-[11px] font-semibold text-[color:var(--accent-primary)]">Official</span> : null}
        {skill.tags.map((tag) => (
          <span className="rounded-full bg-[color:var(--bg-elevated)] px-2 py-0.5 text-[11px] text-[color:var(--text-secondary)]" key={tag}>
            {tag}
          </span>
        ))}
      </div>
      <div className="mt-5 flex items-center justify-between border-t border-[color:var(--bg-border)] pt-4 text-[12px] text-[color:var(--text-tertiary)]">
        <span>{skill.import_count} imports</span>
        <span>{new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric" }).format(new Date(skill.created_at))}</span>
      </div>
    </article>
  );
}

export default async function RegistryPage({ searchParams }: RegistryPageProps) {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Registry auth unavailable:", error);
  }

  const params = searchParams ? await searchParams : {};
  const tab = tabValue(firstValue(params.tab));
  const search = firstValue(params.search);
  const tag = firstValue(params.tag);
  const sort = sortValue(firstValue(params.sort));
  const orgId = await bootstrapOrgId();
  const query = new URLSearchParams({ limit: "24", sort });
  if (search) query.set("search", search);
  if (tag) query.set("tag", tag);
  if (tab === "published") {
    if (orgId) query.set("org_id", orgId);
  }
  const registry = await getRegistrySkills(query);
  const skills = registry?.skills ?? [];
  const hasActiveFilters = Boolean(search || tag || sort !== "imports");

  return (
    <div>
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between md:gap-6">
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Registry</h1>
          <div>
            <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{registry?.total ?? 0} public skills available</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="inline-flex rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-1">
            <Link className={`rounded-md px-3 py-1.5 text-[13px] font-semibold ${tab === "browse" ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "text-[color:var(--text-secondary)]"}`} href="/dashboard/registry">
              Browse
            </Link>
            <Link className={`rounded-md px-3 py-1.5 text-[13px] font-semibold ${tab === "published" ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "text-[color:var(--text-secondary)]"}`} href="/dashboard/registry?tab=published">
              Published
            </Link>
          </div>
          {orgId ? <ImportButton accessToken={accessToken} orgId={orgId} /> : null}
        </div>
      </div>

      <SectionErrorBoundary section="registry filters">
        <form className="mb-6 grid gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-[1fr_180px_180px_auto]">
          <input name="tab" type="hidden" value={tab} />
          <label className="relative block">
            <span className="sr-only">Search registry</span>
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
            <input className="h-10 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] pl-9 pr-3 text-[14px] outline-none focus:border-[color:var(--accent-primary)]" defaultValue={search} name="search" placeholder="Search skills" type="search" />
          </label>
          <input className="h-10 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] outline-none focus:border-[color:var(--accent-primary)]" defaultValue={tag} name="tag" placeholder="Tag" />
          <select className="h-10 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] outline-none focus:border-[color:var(--accent-primary)]" defaultValue={sort} name="sort">
            <option value="imports">Imports</option>
            <option value="score">Score</option>
            <option value="newest">Newest</option>
          </select>
          <button className="inline-flex h-10 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]" type="submit">
            Apply
          </button>
        </form>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="registry skills">
        {skills.length > 0 ? (
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {skills.map((skill) => (
              <Link href={`/dashboard/registry/${skill.id}`} key={skill.id}>
                <RegistryCard skill={skill} />
              </Link>
            ))}
          </section>
        ) : !hasActiveFilters ? (
          <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-12 text-center">
            <BookOpen className="mx-auto mb-4 h-10 w-10 text-[color:var(--text-tertiary)]" />
            <h2 className="text-[17px] font-semibold text-[color:var(--text-primary)]">No published skills</h2>
            <p className="mx-auto mt-2 max-w-md text-[14px] text-[color:var(--text-secondary)]">
              Publish a skill to the registry to share it with your team or the community. Skills are published from the repo detail page.
            </p>
            <div className="mt-6 flex justify-center gap-3">
              <Link
                className="inline-flex h-10 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]"
                href="/dashboard/repos"
              >
                Go to Repos
              </Link>
            </div>
            <div className="mt-8 rounded-lg border border-[color:var(--bg-border)] bg-black/10 p-4 text-left">
              <p className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Or publish via CLI</p>
              <code className="mt-2 block font-mono text-[13px] text-[color:var(--accent-primary)]">skilgen publish --repo {"{repo}"} --skill {"{domain}"}</code>
            </div>
          </section>
        ) : (
          <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
            <BookOpen className="mx-auto mb-4 h-8 w-8 text-[color:var(--accent-primary)]" />
            <h2 className="text-[17px] font-semibold text-[color:var(--text-primary)]">No registry skills found</h2>
            <p className="mt-2 text-[14px] text-[color:var(--text-secondary)]">Adjust the current filters or publish a skill from one of your repositories.</p>
          </section>
        )}
      </SectionErrorBoundary>
    </div>
  );
}
