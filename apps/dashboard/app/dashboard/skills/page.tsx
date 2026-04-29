import Link from "next/link";
import { ArrowRight, BookOpen, ChevronRight, HelpCircle, LibraryBig, Search, Sparkles } from "lucide-react";

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

function matchesNaturalSearch(skill: SkillLibraryRow, query: string, mode: string): boolean {
  if (!query.trim()) return false;
  const normalized = query.toLowerCase();
  const haystack = `${skill.domain} ${skill.repo_name} ${skill.repoFullName} ${skill.skill_path} ${skill.skill_category ?? ""} ${skill.source_type ?? ""}`.toLowerCase();
  if (mode === "skillql") {
    const clauses = normalized.split(/\s+/).filter(Boolean);
    return clauses.every((clause) => {
      const [rawKey, ...rest] = clause.split(":");
      const value = rest.join(":");
      if (!value) return haystack.includes(rawKey);
      if (rawKey === "repo") return skill.repo_name.toLowerCase().includes(value) || skill.repoFullName.toLowerCase().includes(value);
      if (rawKey === "domain") return skill.domain.toLowerCase().includes(value);
      if (rawKey === "category") return String(skill.skill_category ?? "").toLowerCase().includes(value);
      if (rawKey === "source") return normalizeSourceType(skill.source_type).toLowerCase().includes(value);
      if (rawKey === "stale") return String(skill.is_stale) === value;
      if (rawKey === "score<") return skill.score.total < Number(value);
      if (rawKey === "score>") return skill.score.total > Number(value);
      return haystack.includes(clause);
    });
  }
  const wantsRisk = /\b(stale|low|weak|risk|bad|needs work)\b/.test(normalized);
  const wantsRecentLoads = /\b(loaded|used|active)\b/.test(normalized);
  const textMatch = normalized.split(/\s+/).some((term) => term.length > 2 && haystack.includes(term));
  return textMatch || (wantsRisk && (skill.is_stale || skill.score.total < 70)) || (wantsRecentLoads && skill.load_count_30d > 0);
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
  const smartQuery = firstValue(params.q).trim();
  const smartMode = firstValue(params.mode) === "skillql" ? "skillql" : "natural";
  const smartActive = smartQuery.length > 0;
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
  const smartResults = smartActive
    ? skills
        .filter((skill) => matchesNaturalSearch(skill, smartQuery, smartMode))
        .sort((left, right) => {
          const staleDelta = Number(right.is_stale) - Number(left.is_stale);
          if (staleDelta !== 0) return staleDelta;
          return left.score.total - right.score.total;
        })
    : [];

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

      <SectionErrorBoundary section="skills value story">
        <section className="mb-6 rounded-xl border border-[color:var(--bg-border)] bg-[radial-gradient(circle_at_top,rgb(var(--accent-primary-rgb)/0.16),rgb(var(--bg-surface-rgb)/0.96)_42%)] p-5">
          <div className="mb-5 flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--accent-primary)]">How skills improve your code</div>
              <h2 className="mt-2 text-[22px] font-semibold text-[color:var(--text-primary)]">Generic agents become repo-aware engineers.</h2>
            </div>
            <div className="text-[12px] text-[color:var(--text-tertiary)]">BAD CODE → SKILLS LOADED → GOOD CODE</div>
          </div>
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_56px_minmax(0,1fr)_56px_minmax(0,1fr)]">
            <article className="rounded-lg border border-red-500/25 bg-red-950/20 p-4">
              <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-red-300">Without Skillayer</div>
              <h3 className="text-[16px] font-semibold text-[color:var(--text-primary)]">Agent writes generic code</h3>
              <p className="mt-1 text-[13px] leading-5 text-[color:var(--text-secondary)]">No institutional context. Agents guess at your patterns.</p>
              <pre className="mt-4 overflow-x-auto rounded-md border border-red-500/20 bg-black/35 p-3 font-mono text-[12px] leading-5 text-red-100">{`# Agent uses raw SQL (violates your pattern)
result = db.execute(f"SELECT * FROM users WHERE id = {user_id}")
# No error handling, wrong naming convention`}</pre>
            </article>

            <div className="hidden items-center justify-center xl:flex">
              <ArrowRight className="h-8 w-8 animate-pulse text-[color:var(--accent-primary)]" />
            </div>

            <article className="rounded-lg border border-[rgb(var(--accent-primary-rgb)/0.45)] bg-[rgb(var(--accent-primary-rgb)/0.1)] p-4 shadow-[0_0_38px_rgb(var(--accent-primary-rgb)/0.12)]">
              <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--accent-primary)]">Skillayer loads your skills</div>
              <h3 className="text-[16px] font-semibold text-[color:var(--text-primary)]">SKILL.md context enters the prompt</h3>
              <pre className="mt-4 overflow-x-auto rounded-md border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-black/35 p-3 font-mono text-[12px] leading-5 text-[color:var(--text-secondary)]">{`## Key patterns
- Always use SQLAlchemy ORM, never raw SQL
- snake_case for all variables
- Wrap DB calls in try/except with logging`}</pre>
              <div className="mt-4 inline-flex rounded-full border border-[rgb(var(--accent-primary-rgb)/0.26)] bg-[rgb(var(--accent-primary-rgb)/0.12)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
                3 loads in last 30d · agents/SKILL.md
              </div>
            </article>

            <div className="hidden items-center justify-center xl:flex">
              <ArrowRight className="h-8 w-8 animate-pulse text-[color:var(--accent-green)]" />
            </div>

            <article className="rounded-lg border border-[rgb(var(--accent-green-rgb)/0.28)] bg-[rgb(var(--accent-green-rgb)/0.1)] p-4">
              <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--accent-green)]">Agent writes your code</div>
              <h3 className="text-[16px] font-semibold text-[color:var(--text-primary)]">Agent writes YOUR code</h3>
              <p className="mt-1 text-[13px] leading-5 text-[color:var(--text-secondary)]">Follows your patterns, passes review first time.</p>
              <pre className="mt-4 overflow-x-auto rounded-md border border-[rgb(var(--accent-green-rgb)/0.2)] bg-black/35 p-3 font-mono text-[12px] leading-5 text-green-100">{`# Agent follows your skill — ORM, error handling, naming
try:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
except SQLAlchemyError as e:
    logger.error("DB query failed: %s", e)
    raise`}</pre>
            </article>
          </div>
        </section>
      </SectionErrorBoundary>

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

      <SectionErrorBoundary section="skillql search">
        <section className="mb-4 rounded-xl border border-[rgb(var(--accent-primary-rgb)/0.28)] bg-[rgb(var(--accent-primary-rgb)/0.08)] p-4">
          <form className="grid gap-3 xl:grid-cols-[auto_minmax(0,1fr)_auto]">
            <div className="inline-flex h-11 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-1">
              <Link className={smartMode === "natural" ? "inline-flex items-center rounded px-3 text-[12px] font-semibold bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "inline-flex items-center rounded px-3 text-[12px] font-semibold text-[color:var(--text-secondary)]"} href={`/dashboard/skills?mode=natural${smartQuery ? `&q=${encodeURIComponent(smartQuery)}` : ""}`}>
                Natural
              </Link>
              <Link className={smartMode === "skillql" ? "inline-flex items-center rounded px-3 text-[12px] font-semibold bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "inline-flex items-center rounded px-3 text-[12px] font-semibold text-[color:var(--text-secondary)]"} href={`/dashboard/skills?mode=skillql${smartQuery ? `&q=${encodeURIComponent(smartQuery)}` : ""}`}>
                SkillQL
              </Link>
            </div>
            <label className="relative block">
              <span className="sr-only">Natural language or SkillQL search</span>
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
              <input className="h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] pl-9 pr-10 text-[14px] text-[color:var(--text-primary)] outline-none placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]" defaultValue={smartQuery} name="q" placeholder={smartMode === "skillql" ? "repo:api category:testing score<70" : "Find stale auth skills used by agents"} type="search" />
              <span title="Natural search understands intent words like stale, low, active. SkillQL supports repo:, domain:, category:, source:, stale:true, score&lt;, score&gt;." className="absolute right-3 top-1/2 -translate-y-1/2 text-[color:var(--text-tertiary)]">
                <HelpCircle className="h-4 w-4" />
              </span>
            </label>
            <div className="flex gap-3">
              <input name="mode" type="hidden" value={smartMode} />
              <button className="inline-flex h-11 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]" type="submit">
                Search
              </button>
              {smartActive ? (
                <Link className="inline-flex h-11 items-center justify-center rounded-md border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]" href="/dashboard/skills">
                  Clear
                </Link>
              ) : null}
            </div>
          </form>
        </section>
      </SectionErrorBoundary>

      <section className="mb-4 flex flex-col gap-3 rounded-xl border border-[rgb(var(--accent-primary-rgb)/0.26)] bg-[rgb(var(--accent-primary-rgb)/0.12)] px-4 py-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="text-[14px] font-semibold text-[color:var(--text-primary)]">The more specific your skills, the better your agents code.</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {["Add anti-patterns", "Add code examples", "Add a Last verified date"].map((tip) => (
              <span className="rounded-full bg-black/20 px-2.5 py-1 text-[11px] font-semibold text-[color:var(--accent-primary)]" key={tip}>{tip}</span>
            ))}
          </div>
        </div>
        <Link className="text-[13px] font-semibold text-[color:var(--accent-primary)] hover:text-[color:var(--accent-bright)]" href="/dashboard/repos">
          See improvement guide →
        </Link>
      </section>

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
        {smartActive ? (
          <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
            <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
              <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">{smartResults.length} smart result{smartResults.length === 1 ? "" : "s"}</h2>
              <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{smartMode === "skillql" ? "SkillQL" : "Natural"} query: <span className="font-mono text-[color:var(--accent-primary)]">{smartQuery}</span></p>
            </div>
            {smartResults.length ? (
              <div className="grid gap-3 p-4 md:grid-cols-2 xl:grid-cols-3">
                {smartResults.map((skill) => (
                  <Link className="rounded-lg border border-[color:var(--bg-border)] bg-black/10 p-4 hover:border-[rgb(var(--accent-primary-rgb)/0.4)]" href={`/dashboard/repos/${skill.repo_id}/skills/${skill.id}`} key={skill.id}>
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="truncate text-[14px] font-semibold text-[color:var(--text-primary)]">{skill.domain}</div>
                        <div className="mt-1 truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{skill.skill_path}</div>
                      </div>
                      <span className={`shrink-0 rounded-full px-2.5 py-1 text-[12px] font-semibold ${scorePillClass(skill.score.total)}`}>{skill.score.total}</span>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <span className="rounded-full bg-[color:var(--bg-elevated)] px-2 py-1 text-[11px] text-[color:var(--text-secondary)]">{skill.repo_name}</span>
                      <span className={`rounded-full px-2 py-1 text-[11px] font-semibold ${staleBadgeClass(skill.is_stale)}`}>{skill.is_stale ? "Stale" : "Fresh"}</span>
                      <span className="rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-2 py-1 text-[11px] text-[color:var(--accent-primary)]">{categoryLabel(skill.skill_category)}</span>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="px-8 py-14 text-center text-[color:var(--text-secondary)]">No smart search results. Try a broader natural query or a simpler SkillQL clause.</div>
            )}
          </section>
        ) : skills.length === 0 ? (
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
