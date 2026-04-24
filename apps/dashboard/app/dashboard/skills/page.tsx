import Link from "next/link";
import { BookOpen, ChevronRight, LibraryBig, Search, Sparkles } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { SectionFallback } from "@/components/section-fallback";
import { API_URL, type Org, type Repo, type Skill, type SkillCategory } from "../../../lib/data";

export const dynamic = "force-dynamic";

type SearchParams = Record<string, string | string[] | undefined>;

type SkillsPageProps = {
  searchParams?: Promise<SearchParams>;
};

type SkillLibraryRow = Skill & {
  repoFullName: string;
};

type CategoryOption = {
  value: SkillCategory;
  label: string;
  shortLabel: string;
};

const CATEGORY_OPTIONS: CategoryOption[] = [
  { value: "codebase_architecture", label: "Codebase Architecture", shortLabel: "Architecture" },
  { value: "code_style", label: "Code Style", shortLabel: "Style" },
  { value: "testing_conventions", label: "Testing Conventions", shortLabel: "Testing" },
  { value: "internal_tools", label: "Internal Tools", shortLabel: "Tools" },
  { value: "security_compliance", label: "Security & Compliance", shortLabel: "Security" },
  { value: "design_system", label: "Design System", shortLabel: "Design" },
  { value: "data_schema", label: "Data Schema", shortLabel: "Data" },
  { value: "operational_knowledge", label: "Operational Knowledge", shortLabel: "Operations" },
];

const CATEGORY_LOOKUP = new Map(CATEGORY_OPTIONS.map((option) => [option.value, option]));

const SOURCE_TYPE_LABELS: Record<string, string> = {
  code: "Code",
  openapi: "OpenAPI",
  graphql: "GraphQL",
  postman: "Postman",
  terraform: "Terraform",
  kubernetes: "Kubernetes",
  helm: "Helm",
  dbt: "dbt",
  sql_schema: "SQL Schema",
  kafka: "Kafka",
  sarif: "SARIF",
  sbom: "SBOM",
  security_policy: "Security Policy",
  runbook: "Runbook",
  confluence: "Confluence",
  notion: "Notion",
  incident: "Incident",
  pagerduty: "PagerDuty",
};

function firstValue(value: string | string[] | undefined): string {
  return Array.isArray(value) ? value[0] ?? "" : value ?? "";
}

function normalizeSourceType(value: string | null | undefined): string {
  return value?.trim() ? value : "code";
}

function categoryLabel(value: string | null | undefined): string {
  if (!value) return "Uncategorized";
  return CATEGORY_LOOKUP.get(value as SkillCategory)?.label ?? value.replaceAll("_", " ");
}

function sourceTypeLabel(value: string | null | undefined): string {
  const normalized = normalizeSourceType(value);
  return SOURCE_TYPE_LABELS[normalized] ?? normalized.replaceAll("_", " ");
}

function scorePillClass(score: number): string {
  if (score <= 40) return "bg-red-900/30 text-red-300 ring-1 ring-red-500/20";
  if (score <= 70) return "bg-amber-900/30 text-amber-300 ring-1 ring-amber-500/20";
  return "bg-green-900/30 text-green-300 ring-1 ring-green-500/20";
}

function staleBadgeClass(isStale: boolean): string {
  return isStale
    ? "bg-red-900/25 text-red-300 ring-1 ring-red-500/20"
    : "bg-[rgb(var(--accent-green-rgb)/0.12)] text-[color:var(--accent-green)] ring-1 ring-[rgb(var(--accent-green-rgb)/0.18)]";
}

function coverageFillClass(covered: boolean): string {
  return covered
    ? "bg-[linear-gradient(90deg,rgb(var(--accent-primary-rgb)/0.95),rgb(var(--accent-bright-rgb)/0.95))]"
    : "bg-[color:var(--bg-elevated)]";
}

function formatRelativeTime(value: string | null): string {
  if (!value) return "Never";

  const timestamp = new Date(value).getTime();
  if (Number.isNaN(timestamp)) return "Never";

  const diff = Math.max(0, Date.now() - timestamp);
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (diff < hour) {
    const minutes = Math.max(1, Math.floor(diff / minute));
    return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  }

  if (diff < day) {
    const hours = Math.max(1, Math.floor(diff / hour));
    return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  }

  if (diff < 7 * day) {
    const days = Math.max(1, Math.floor(diff / day));
    return `${days} day${days === 1 ? "" : "s"} ago`;
  }

  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(timestamp));
}

async function fetchNoStore<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch (error) {
    console.error(`Failed to fetch ${path}:`, error);
    return null;
  }
}

async function loadSkillsLibrary(): Promise<{
  org: Org | null;
  repos: Repo[];
  skills: SkillLibraryRow[];
  repoSkillFailures: number;
  failedBootstrap: boolean;
}> {
  const org = await fetchNoStore<Org>("/orgs/bootstrap");
  if (!org) {
    return {
      org: null,
      repos: [],
      skills: [],
      repoSkillFailures: 0,
      failedBootstrap: true,
    };
  }

  const repos = (await fetchNoStore<Repo[]>(`/orgs/${org.id}/repos`)) ?? [];
  const skillPayloads = await Promise.all(
    repos.map(async (repo) => {
      const repoSkills = await fetchNoStore<Skill[]>(`/repos/${repo.id}/skills`);
      if (!repoSkills) {
        return {
          failed: true,
          skills: [] as SkillLibraryRow[],
        };
      }

      return {
        failed: false,
        skills: repoSkills.map((skill) => ({
          ...skill,
          repoFullName: repo.full_name,
        })),
      };
    }),
  );

  const skills = skillPayloads.flatMap((result) => result.skills);
  const repoSkillFailures = skillPayloads.filter((result) => result.failed).length;

  return {
    org,
    repos,
    skills,
    repoSkillFailures,
    failedBootstrap: false,
  };
}

function sourceTypeOptions(skills: SkillLibraryRow[]): string[] {
  return [...new Set(skills.map((skill) => normalizeSourceType(skill.source_type)))].sort((left, right) => left.localeCompare(right));
}

function matchesSearch(skill: SkillLibraryRow, query: string): boolean {
  if (!query) return true;
  const haystack = `${skill.domain} ${skill.repo_name} ${skill.repoFullName} ${skill.skill_path}`.toLowerCase();
  return haystack.includes(query);
}

function categoryCoverage(skills: SkillLibraryRow[]): CategoryOption[] {
  const covered = new Set(skills.map((skill) => skill.skill_category).filter(Boolean) as SkillCategory[]);
  return CATEGORY_OPTIONS.filter((option) => covered.has(option.value));
}

function averageScore(skills: SkillLibraryRow[]): number {
  if (skills.length === 0) return 0;
  return Math.round(skills.reduce((sum, skill) => sum + skill.score.total, 0) / skills.length);
}

export default async function SkillsPage({ searchParams }: SkillsPageProps) {
  const params = searchParams ? await searchParams : {};
  const search = firstValue(params.search).trim();
  const normalizedSearch = search.toLowerCase();
  const selectedCategory = firstValue(params.category);
  const selectedSourceType = firstValue(params.source_type);

  const { org, repos, skills, repoSkillFailures, failedBootstrap } = await loadSkillsLibrary();

  if (failedBootstrap) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Skills Library</h1>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Unable to load the library right now.</p>
        </div>
        <SectionFallback section="skills library" />
      </div>
    );
  }

  const availableSourceTypes = sourceTypeOptions(skills);
  const validCategory = CATEGORY_OPTIONS.some((option) => option.value === selectedCategory) ? selectedCategory : "";
  const validSourceType = availableSourceTypes.includes(selectedSourceType) ? selectedSourceType : "";

  const filteredSkills = skills
    .filter((skill) => matchesSearch(skill, normalizedSearch))
    .filter((skill) => !validCategory || skill.skill_category === validCategory)
    .filter((skill) => !validSourceType || normalizeSourceType(skill.source_type) === validSourceType)
    .sort((left, right) => {
      const scoreDelta = right.score.total - left.score.total;
      if (scoreDelta !== 0) return scoreDelta;
      return left.domain.localeCompare(right.domain);
    });

  const coveredCategories = categoryCoverage(skills);
  const coveredCategorySet = new Set(coveredCategories.map((category) => category.value));
  const filteredCountLabel =
    filteredSkills.length === skills.length
      ? `${skills.length} skills`
      : `${filteredSkills.length} of ${skills.length} skills`;

  return (
    <div>
      <div className="mb-8 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="mb-3 flex items-center gap-2 text-[12px] text-[color:var(--text-tertiary)]">
            <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">
              Overview
            </Link>
            <span>/</span>
            <span className="text-[color:var(--text-secondary)]">Skills</span>
          </div>
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Skills Library</h1>
          <p className="mt-1 max-w-2xl text-sm text-[color:var(--text-secondary)]">
            Browse the knowledge layer across {org?.name ?? "your organization"}: generated skills, their source systems, and what the org is actually loading.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.16)] bg-[rgb(var(--accent-primary-rgb)/0.08)] px-3 py-1.5 text-[12px] font-medium text-[color:var(--accent-primary)]">
          <Sparkles className="h-3.5 w-3.5" />
          {filteredCountLabel} in view
        </div>
      </div>

      <SectionErrorBoundary section="skills hero">
        <section className="mb-6 overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgb(var(--bg-surface-rgb)/1),rgb(var(--bg-surface-rgb)/0.92))]">
          <div className="grid gap-6 p-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.9fr)]">
            <div>
              <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl border border-[rgb(var(--accent-primary-rgb)/0.16)] bg-[rgb(var(--accent-primary-rgb)/0.1)] text-[color:var(--accent-primary)]">
                <LibraryBig className="h-5 w-5" />
              </div>
              <div className="flex flex-wrap items-end gap-3">
                <div className="text-4xl font-semibold leading-none text-[color:var(--text-primary)]">{skills.length}</div>
                <div className="pb-1 text-sm text-[color:var(--text-secondary)]">
                  skills across <span className="font-medium text-[color:var(--text-primary)]">{repos.length}</span> repos
                </div>
              </div>
              <p className="mt-3 max-w-2xl text-[14px] leading-6 text-[color:var(--text-secondary)]">
                This is the org-wide library view: every generated skill, flattened across repositories, ready for search by domain, repository, category, and source system.
              </p>

              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
                  <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">Category Coverage</div>
                  <div className="mt-2 text-2xl font-semibold text-[color:var(--text-primary)]">
                    {coveredCategories.length}
                    <span className="ml-1 text-sm font-medium text-[color:var(--text-tertiary)]">/ 8</span>
                  </div>
                </div>
                <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
                  <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">Average Score</div>
                  <div className="mt-2 text-2xl font-semibold text-[color:var(--text-primary)]">{averageScore(skills)}</div>
                </div>
                <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
                  <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">Source Types</div>
                  <div className="mt-2 text-2xl font-semibold text-[color:var(--text-primary)]">{availableSourceTypes.length}</div>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-[color:var(--bg-border)] bg-[rgb(var(--bg-base-rgb)/0.74)] p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">Org Coverage Map</div>
                  <div className="mt-1 text-[15px] font-medium text-[color:var(--text-primary)]">
                    {coveredCategories.length} of 8 knowledge categories represented
                  </div>
                </div>
                <div className="rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
                  Org-wide
                </div>
              </div>

              <div className="mt-5 grid grid-cols-8 gap-2">
                {CATEGORY_OPTIONS.map((option) => {
                  const covered = coveredCategorySet.has(option.value);
                  return (
                    <div className="space-y-2" key={option.value}>
                      <div className={`h-2 rounded-full ${coverageFillClass(covered)}`} />
                      <div className={`text-[11px] leading-4 ${covered ? "text-[color:var(--text-secondary)]" : "text-[color:var(--text-tertiary)]"}`}>
                        {option.shortLabel}
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-5 flex flex-wrap gap-2">
                {CATEGORY_OPTIONS.map((option) => {
                  const covered = coveredCategorySet.has(option.value);
                  return (
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-medium ${
                        covered
                          ? "bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[color:var(--accent-primary)]"
                          : "bg-[color:var(--bg-elevated)] text-[color:var(--text-tertiary)]"
                      }`}
                      key={option.value}
                    >
                      {option.shortLabel}
                    </span>
                  );
                })}
              </div>
            </div>
          </div>
        </section>
      </SectionErrorBoundary>

      {repoSkillFailures > 0 ? (
        <section className="mb-6 rounded-lg border border-amber-500/20 bg-amber-950/20 px-4 py-3 text-[13px] text-amber-200">
          Some repositories could not load skills right now. Showing {skills.length} skills from the repos that responded.
        </section>
      ) : null}

      <SectionErrorBoundary section="skills filters">
        <form className="mb-6 grid gap-3 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 xl:grid-cols-[minmax(0,1fr)_220px_220px_auto]">
          <label className="relative block">
            <span className="sr-only">Search skills</span>
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
            <input
              className="h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] pl-9 pr-3 text-[14px] text-[color:var(--text-primary)] outline-none transition-colors placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]"
              defaultValue={search}
              name="search"
              placeholder="Search by skill or repository"
              type="search"
            />
          </label>

          <select
            className="h-11 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]"
            defaultValue={validCategory}
            name="category"
          >
            <option value="">All categories</option>
            {CATEGORY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <select
            className="h-11 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]"
            defaultValue={validSourceType}
            name="source_type"
          >
            <option value="">All sources</option>
            {availableSourceTypes.map((sourceType) => (
              <option key={sourceType} value={sourceType}>
                {sourceTypeLabel(sourceType)}
              </option>
            ))}
          </select>

          <div className="flex gap-3">
            <button
              className="inline-flex h-11 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]"
              type="submit"
            >
              Apply filters
            </button>
            {(search || validCategory || validSourceType) ? (
              <Link
                className="inline-flex h-11 items-center justify-center rounded-md border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]"
                href="/dashboard/skills"
              >
                Reset
              </Link>
            ) : null}
          </div>
        </form>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="skills table">
        {skills.length === 0 ? (
          <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-8 py-14 text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[color:var(--accent-primary)]">
              <BookOpen className="h-6 w-6" />
            </div>
            <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Your library is still empty</h2>
            <p className="mx-auto mt-3 max-w-xl text-[14px] leading-6 text-[color:var(--text-secondary)]">
              Connect and analyse repositories to populate the org-wide knowledge library with generated skills, category coverage, and usage signals.
            </p>
            <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
              <Link
                className="inline-flex h-11 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-5 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]"
                href="/dashboard/repos"
              >
                Go to Repos
              </Link>
              <Link
                className="inline-flex h-11 items-center justify-center rounded-md border border-[color:var(--bg-border)] px-5 text-[13px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]"
                href="https://github.com/RaviChanduUmmadisetti/skilgen/tree/main/docs"
                target="_blank"
              >
                Read the docs
              </Link>
            </div>
          </section>
        ) : filteredSkills.length > 0 ? (
          <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
            <div className="grid min-w-[1100px] grid-cols-[minmax(0,2.1fr)_minmax(0,1.4fr)_160px_150px_120px_110px_110px_130px] gap-4 border-b border-[color:var(--bg-border)] px-5 py-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">
              <div>Domain</div>
              <div>Repository</div>
              <div>Category</div>
              <div>Source</div>
              <div>Score</div>
              <div>Freshness</div>
              <div>Loads 30d</div>
              <div>Last loaded</div>
            </div>

            <div className="overflow-x-auto">
              <div className="min-w-[1100px]">
                {filteredSkills.map((skill) => (
                  <Link
                    className="grid grid-cols-[minmax(0,2.1fr)_minmax(0,1.4fr)_160px_150px_120px_110px_110px_130px] gap-4 border-b border-[color:var(--bg-elevated)] px-5 py-4 transition-colors last:border-b-0 hover:bg-white/5"
                    href={`/dashboard/repos/${skill.repo_id}/skills/${skill.id}`}
                    key={skill.id}
                  >
                    <div className="min-w-0">
                      <div className="truncate text-[14px] font-semibold text-[color:var(--text-primary)]">{skill.domain}</div>
                      <div className="mt-1 truncate font-mono text-[12px] text-[color:var(--text-tertiary)]">{skill.skill_path}</div>
                    </div>

                    <div className="min-w-0">
                      <div className="truncate text-[13px] font-medium text-[color:var(--text-primary)]">{skill.repo_name}</div>
                      <div className="mt-1 truncate font-mono text-[12px] text-[color:var(--text-tertiary)]">{skill.repoFullName}</div>
                    </div>

                    <div className="flex items-center">
                      <span className="inline-flex max-w-full truncate rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-2.5 py-1 text-[11px] font-medium text-[color:var(--accent-primary)]">
                        {categoryLabel(skill.skill_category)}
                      </span>
                    </div>

                    <div className="flex items-center">
                      <span className="inline-flex max-w-full truncate rounded-full bg-[color:var(--bg-elevated)] px-2.5 py-1 text-[11px] font-medium text-[color:var(--text-secondary)]">
                        {sourceTypeLabel(skill.source_type)}
                      </span>
                    </div>

                    <div className="flex items-center">
                      <span className={`inline-flex rounded-full px-2.5 py-1 text-[12px] font-semibold ${scorePillClass(skill.score.total)}`}>
                        {skill.score.total}/100
                      </span>
                    </div>

                    <div className="flex items-center">
                      <span className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold ${staleBadgeClass(skill.is_stale)}`}>
                        {skill.is_stale ? "Stale" : "Fresh"}
                      </span>
                    </div>

                    <div className="flex items-center text-[13px] text-[color:var(--text-secondary)]">{skill.load_count_30d}</div>

                    <div className="flex items-center justify-between gap-2 text-[13px] text-[color:var(--text-secondary)]">
                      <span>{formatRelativeTime(skill.last_loaded_at)}</span>
                      <ChevronRight className="h-4 w-4 shrink-0 text-[color:var(--text-tertiary)]" />
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </section>
        ) : (
          <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-8 py-14 text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[color:var(--accent-primary)]">
              <Search className="h-6 w-6" />
            </div>
            <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">No skills match those filters</h2>
            <p className="mx-auto mt-3 max-w-xl text-[14px] leading-6 text-[color:var(--text-secondary)]">
              Try a broader search, switch categories, or clear the source filter to see more of the library.
            </p>
            <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
              <Link
                className="inline-flex h-11 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-5 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]"
                href="/dashboard/skills"
              >
                Clear filters
              </Link>
              <Link
                className="inline-flex h-11 items-center justify-center rounded-md border border-[color:var(--bg-border)] px-5 text-[13px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]"
                href="/dashboard/repos"
              >
                Go to Repos
              </Link>
            </div>
          </section>
        )}
      </SectionErrorBoundary>
    </div>
  );
}
