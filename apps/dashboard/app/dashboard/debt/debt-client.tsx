"use client";

import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import Link from "next/link";
import { AlertTriangle, CheckCircle2, Clock, Eye, Loader2, Sparkles, TrendingDown } from "lucide-react";

import type { SkillDebtResponse, SkillDebtSkill } from "../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type TabKey = "gaps" | "stale" | "low" | "never";
type Preview = { content: string; suggested_path: string; ready_to_push: boolean };

const labels: Record<string, string> = {
  codebase_architecture: "Architecture",
  code_style: "Code Style",
  testing_conventions: "Testing",
  internal_tools: "Internal Tools",
  security_compliance: "Security",
  design_system: "Design System",
  data_schema: "Data Schema",
  operational_knowledge: "Operations",
};

function titleize(domain: string): string {
  return labels[domain] ?? domain.replaceAll("_", " ");
}

function headers(accessToken: string): HeadersInit {
  return { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) };
}

function scoreBadgeClass(score: number): string {
  if (score < 40) return "bg-red-900/30 text-red-300";
  if (score < 70) return "bg-amber-900/30 text-amber-300";
  return "bg-green-900/30 text-green-300";
}

function relative(value?: string | null): string {
  if (!value) return "Never";
  const hours = Math.floor((Date.now() - new Date(value).getTime()) / 3600000);
  if (!Number.isFinite(hours) || hours < 0) return "Just now";
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function skillFix(skill: SkillDebtSkill): string {
  const scores = [
    { value: skill.score_groundedness ?? 0, fix: "Add file references and concrete examples" },
    { value: skill.score_coverage ?? 0, fix: "Add missing anti-patterns and edge cases" },
    { value: skill.score_freshness ?? 0, fix: "Regenerate against current repo state" },
    { value: skill.score_structure ?? 0, fix: "Rebuild the SKILL.md sections" },
  ].sort((a, b) => a.value - b.value)[0];
  return scores.fix;
}

function AnalysisBanner({ accessToken, debt, orgId }: { accessToken: string; debt: SkillDebtResponse; orgId: string }) {
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState("");
  const last = debt.summary.last_debt_analysis_at;

  async function run() {
    setRunning(true);
    setMessage("Analysing connected repos...");
    try {
      const response = await fetch(`${API_URL}/orgs/${orgId}/debt/run-analysis`, { method: "POST", headers: headers(accessToken) });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Analysis failed");
      setMessage(`Analysis complete - ${body.gaps_found ?? 0} gaps found across ${body.repos_analyzed ?? 0} repos.`);
      window.setTimeout(() => window.location.reload(), 900);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Analysis failed");
    } finally {
      setRunning(false);
    }
  }

  const stale = !last || Date.now() - new Date(last).getTime() > 24 * 3600000;
  return (
    <section className={`rounded-xl border p-4 ${stale ? "border-[rgb(var(--accent-primary-rgb)/0.32)] bg-[rgb(var(--accent-primary-rgb)/0.10)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]"}`}>
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="font-semibold text-[color:var(--text-primary)]">{stale ? "Run a fresh analysis to see current skill gaps" : `Last analysed ${relative(last)}`}</div>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Skillayer checks every connected repo against the 8 knowledge areas and prepares AI-generated fixes.</p>
          {message ? <p className="mt-2 text-[12px] text-[color:var(--accent-primary)]">{message}</p> : null}
        </div>
        <button className="inline-flex items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)] disabled:opacity-60" disabled={running} onClick={run} type="button">
          {running ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
          {stale ? "Run analysis - ~30 seconds" : "Re-run analysis"}
        </button>
      </div>
    </section>
  );
}

function GapGenerateButton({ accessToken, gapId, orgId }: { accessToken: string; gapId: string; orgId: string }) {
  const [preview, setPreview] = useState<Preview | null>(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  async function generate(mode: "preview" | "push") {
    setBusy(true);
    setStatus(mode === "preview" ? "Generating preview..." : "Opening pull request...");
    try {
      const response = await fetch(`${API_URL}/orgs/${orgId}/debt/gaps/${gapId}/generate`, { method: "POST", headers: headers(accessToken), body: JSON.stringify({ mode }) });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Could not generate skill");
      if (mode === "preview") setPreview(body as Preview);
      if (mode === "push") setStatus(body.pr_url ? `PR #${body.pr_number} opened` : "Skill generated");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not generate skill");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mt-2">
      <button className="inline-flex items-center rounded-md border border-[rgb(var(--accent-primary-rgb)/0.32)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--accent-primary)] disabled:opacity-60" disabled={busy} onClick={() => generate("preview")} type="button">
        {busy ? <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> : <Sparkles className="mr-1.5 h-3.5 w-3.5" />}
        Generate
      </button>
      {preview ? (
        <div className="mt-3 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <div className="text-[12px] font-semibold text-[color:var(--text-primary)]">Generated preview · {preview.suggested_path}</div>
          <details className="mt-2">
            <summary className="cursor-pointer text-[12px] text-[color:var(--accent-primary)]">Read SKILL.md preview</summary>
            <pre className="mt-2 max-h-[260px] overflow-auto whitespace-pre-wrap rounded-md bg-black/20 p-3 text-[11px] leading-5 text-[color:var(--text-secondary)]">{preview.content}</pre>
          </details>
          <div className="mt-3 flex flex-wrap gap-2">
            <button className="rounded-md bg-[color:var(--accent-primary)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--bg-base)]" disabled={busy} onClick={() => generate("push")} type="button">Looks good - Push as PR</button>
            <button className="rounded-md border border-[color:var(--bg-border)] px-3 py-1.5 text-[12px] text-[color:var(--text-secondary)]" onClick={() => setPreview(null)} type="button">Discard</button>
          </div>
        </div>
      ) : null}
      {status ? <div className="mt-2 text-[12px] text-[color:var(--text-secondary)]">{status}</div> : null}
    </div>
  );
}

function SkillActionTable({ action, emptyMessage, repoNames, skills }: { action: "stale" | "low" | "never"; emptyMessage: string; repoNames: Map<string, string>; skills: SkillDebtSkill[] }) {
  const [diagnosis, setDiagnosis] = useState<Record<string, string>>({});
  if (!skills.length) {
    return <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center text-sm text-[color:var(--text-secondary)]">{emptyMessage}</section>;
  }
  return (
    <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      {skills.map((skill) => (
        <article className="border-b border-[color:var(--bg-border)] p-5 last:border-b-0" key={skill.id}>
          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h3 className="font-semibold text-[color:var(--text-primary)]">{skill.domain}</h3>
                <span className={`rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreBadgeClass(skill.score_total)}`}>{skill.score_total}/100</span>
                <span className="text-[12px] text-[color:var(--text-tertiary)]">{repoNames.get(skill.repo_id) ?? "Repo"}</span>
              </div>
              <p className="mt-2 text-[13px] text-[color:var(--text-secondary)]">
                {action === "low" ? `${skillFix(skill)}. Skillayer can generate an improved version for review.` : action === "stale" ? "Skillayer can regenerate this skill from current repo context and open a PR." : "Skillayer can diagnose why agents are not discovering this skill."}
              </p>
              {diagnosis[skill.id] ? <div className="mt-3 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-[12px] text-[color:var(--text-secondary)]">{diagnosis[skill.id]}</div> : null}
            </div>
            <div className="flex shrink-0 flex-wrap gap-2">
              {action === "never" ? (
                <button className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-[12px] font-semibold text-[color:var(--accent-primary)]" onClick={() => setDiagnosis((current) => ({ ...current, [skill.id]: "Likely cause: this skill is not referenced by an agent startup file or the domain name does not match task language. Fix: use Skillayer's Connect Agent setup to refresh skill references for this repo." }))} type="button">Find why</button>
              ) : (
                <Link className="rounded-md border border-[rgb(var(--accent-primary-rgb)/0.32)] px-3 py-2 text-[12px] font-semibold text-[color:var(--accent-primary)]" href={`/dashboard/autopilot?skill=${skill.id}`}>{action === "low" ? "Improve with AI" : "Regenerate with AI"}</Link>
              )}
              <Link className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-[12px] text-[color:var(--text-secondary)]" href={`/dashboard/repos/${skill.repo_id}/skills/${skill.id}`}>View skill</Link>
            </div>
          </div>
        </article>
      ))}
    </section>
  );
}

export function DebtClient({ accessToken, debt, initialDomain = "", initialTab = "gaps", orgId }: { accessToken: string; debt: SkillDebtResponse; initialDomain?: string; initialTab?: TabKey; orgId: string }) {
  const [tab, setTab] = useState<TabKey>(initialTab);
  const [domainFilter, setDomainFilter] = useState(initialDomain.trim());
  const repoNames = useMemo(() => {
    const map = new Map<string, string>();
    for (const gap of debt.repo_coverage_gaps) map.set(gap.repo_id, gap.repo_name);
    return map;
  }, [debt.repo_coverage_gaps]);
  const totalGaps = debt.repo_coverage_gaps.reduce((sum, repo) => sum + repo.missing_categories.length, 0);
  const displayedGapRepos = useMemo(() => {
    if (!domainFilter) return debt.repo_coverage_gaps;
    return debt.repo_coverage_gaps
      .filter((repo) => repo.missing_categories.includes(domainFilter))
      .map((repo) => ({ ...repo, missing_categories: repo.missing_categories.filter((domain) => domain === domainFilter) }));
  }, [debt.repo_coverage_gaps, domainFilter]);
  const displayedGapCount = displayedGapRepos.reduce((sum, repo) => sum + repo.missing_categories.length, 0);
  const tabs: Array<{ key: TabKey; label: string; count: number; icon: ReactNode }> = [
    { key: "gaps", label: "Coverage Gaps", count: totalGaps, icon: <Eye className="h-3.5 w-3.5" /> },
    { key: "stale", label: "Stale Skills", count: debt.summary.stale_count, icon: <Clock className="h-3.5 w-3.5" /> },
    { key: "low", label: "Low Score", count: debt.summary.low_score_count, icon: <TrendingDown className="h-3.5 w-3.5" /> },
    { key: "never", label: "Never Loaded", count: debt.summary.never_loaded_count, icon: <AlertTriangle className="h-3.5 w-3.5" /> },
  ];

  return (
    <div className="space-y-6">
      <AnalysisBanner accessToken={accessToken} debt={debt} orgId={orgId} />
      <div className="flex flex-wrap gap-2">
        {tabs.map((item) => (
          <button className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-[13px] font-semibold ${tab === item.key ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "border border-[color:var(--bg-border)] text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)]"}`} key={item.key} onClick={() => setTab(item.key)} type="button">
            {item.icon}
            {item.label}
            <span className="rounded-full bg-white/10 px-1.5 py-0.5 text-[11px]">{item.count}</span>
          </button>
        ))}
      </div>

      {tab === "gaps" ? (
        <section className="space-y-4">
          {totalGaps > 0 ? (
            <div className="rounded-xl border border-[rgb(var(--accent-primary-rgb)/0.28)] bg-[rgb(var(--accent-primary-rgb)/0.10)] p-4">
              <div className="font-semibold text-[color:var(--text-primary)]">
                {domainFilter ? `${displayedGapCount} ${titleize(domainFilter)} gaps need action` : `${totalGaps} coverage gaps across ${debt.repo_coverage_gaps.length} repos. Skillayer can generate missing skills with AI.`}
              </div>
              <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Every generated skill is previewed before it is pushed as a pull request.</p>
              {domainFilter ? (
                <button className="mt-3 text-[12px] font-semibold text-[color:var(--accent-primary)] hover:underline" onClick={() => setDomainFilter("")} type="button">
                  Show all coverage gaps
                </button>
              ) : null}
            </div>
          ) : null}
          {displayedGapRepos.length ? displayedGapRepos.map((repo) => (
            <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={repo.repo_id}>
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">{repo.repo_name}</h2>
                    <span className="rounded-full bg-amber-500/15 px-2.5 py-0.5 text-[11px] font-semibold text-amber-300">{repo.coverage_score}% covered</span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {repo.covered_categories.map((domain) => <span className="rounded-full bg-green-900/30 px-2 py-0.5 text-[11px] font-semibold text-green-300" key={domain}><CheckCircle2 className="mr-1 inline h-3 w-3" />{titleize(domain)}</span>)}
                  </div>
                </div>
                <Link className="text-[13px] font-semibold text-[color:var(--accent-primary)] hover:underline" href={`/dashboard/repos/${repo.repo_id}`}>View repo</Link>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {repo.missing_categories.map((domain) => {
                  const gap = repo.gaps?.find((item) => item.domain === domain);
                  return (
                    <div className="rounded-lg border border-red-500/20 bg-red-900/10 p-3" key={domain}>
                      <div className="flex items-center justify-between gap-3">
                        <span className="text-[13px] font-semibold text-red-200">✗ {titleize(domain)}</span>
                        {gap?.status === "pr_opened" ? <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] text-amber-300">PR pending</span> : null}
                      </div>
                      <p className="mt-1 text-[12px] text-[color:var(--text-secondary)]">Agents have no reliable guidance for this domain in {repo.repo_name}.</p>
                      {gap?.gap_id ? <GapGenerateButton accessToken={accessToken} gapId={gap.gap_id} orgId={orgId} /> : <div className="mt-2 text-[12px] text-[color:var(--text-tertiary)]">Run analysis to prepare this gap.</div>}
                    </div>
                  );
                })}
              </div>
            </article>
          )) : (
            <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center text-sm text-[color:var(--text-secondary)]">
              {domainFilter ? `No open ${titleize(domainFilter)} coverage gaps found.` : "No coverage gaps detected. Re-run analysis to verify every repo is still covered."}
            </section>
          )}
        </section>
      ) : null}

      {tab === "stale" ? <SkillActionTable action="stale" emptyMessage="No stale skills - everything is fresh." repoNames={repoNames} skills={debt.stale_skills} /> : null}
      {tab === "low" ? <SkillActionTable action="low" emptyMessage="No low-score skills - great quality." repoNames={repoNames} skills={debt.low_score_skills} /> : null}
      {tab === "never" ? <SkillActionTable action="never" emptyMessage="All skills are being loaded by agents." repoNames={repoNames} skills={debt.never_loaded_skills} /> : null}
    </div>
  );
}
