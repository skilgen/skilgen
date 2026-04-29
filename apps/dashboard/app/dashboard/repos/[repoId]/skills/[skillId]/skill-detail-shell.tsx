"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle, ArrowLeft, CheckCircle2, Copy, FileText, Lightbulb, Loader2, Sparkles } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { SkillDetailViewer } from "@/components/skill-detail-viewer";
import type { Repo, Score, Skill, SkillUsageStats, SkillVersionSummary } from "../../../../../../lib/data";
import { PublishSkillButton } from "./publish-skill-button";
import { SkillEditor } from "./skill-editor";

type SkillDetailShellProps = {
  accessToken: string;
  repo: Repo | null;
  repoId: string;
  skill: Skill;
  usageStats: SkillUsageStats | null;
  versions: SkillVersionSummary[];
};

type Dimension = "groundedness" | "coverage" | "freshness" | "structure";

type ScoreHint = {
  why: string;
  improve: string | null;
};

type ImprovementIssue = {
  dimension: string;
  score: number;
  max: number;
  reason: string;
  fix: string;
  impact: "high" | "medium";
  points_available: number;
};

type ImprovementPlan = {
  skill_id: string;
  current_score: number;
  potential_score: number;
  score_gap: number;
  issues: ImprovementIssue[];
  word_count: number;
  code_block_count: number;
  is_improvable: boolean;
  quick_win: ImprovementIssue | null;
};

function scoreBadgeClass(score: number) {
  if (score <= 40) return "bg-red-900/50 text-red-400";
  if (score <= 70) return "bg-amber-900/50 text-amber-400";
  return "bg-green-900/50 text-green-400";
}

function subscoreBadgeClass(score: number) {
  if (score <= 8) return "bg-red-900/50 text-red-400";
  if (score <= 16) return "bg-amber-900/50 text-amber-400";
  return "bg-green-900/50 text-green-400";
}

function ScoreBadge({ score }: { score: Score }) {
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-[12px] font-semibold ${scoreBadgeClass(score.total)}`}>{score.total}/100</span>;
}

function StaleBadge({ isStale }: { isStale: boolean }) {
  return (
    <span
      className={
        isStale
          ? "inline-flex rounded-full bg-red-900/40 px-2.5 py-1 text-[12px] font-semibold text-red-300"
          : "inline-flex rounded-full bg-[rgb(var(--accent-green-rgb)/0.14)] px-2.5 py-1 text-[12px] font-semibold text-[color:var(--accent-green)]"
      }
    >
      {isStale ? "Stale" : "Fresh"}
    </span>
  );
}

function VersionBadge({ versionNumber }: { versionNumber: number | null }) {
  if (!versionNumber) return null;
  return <span className="inline-flex rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-2.5 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">v{versionNumber}</span>;
}

function sourceDescription(sourceType: string | null | undefined): string {
  const labels: Record<string, string> = {
    code: "Generated from codebase analysis",
    openapi: "Generated from OpenAPI spec",
    graphql: "Generated from GraphQL schema",
    postman: "Generated from Postman collection",
    terraform: "Generated from Terraform modules",
    kubernetes: "Generated from Kubernetes manifests",
    helm: "Generated from Helm charts",
    dbt: "Generated from dbt project",
    sql_schema: "Generated from SQL schema",
    kafka: "Generated from Kafka schemas",
    sarif: "Generated from SARIF findings",
    sbom: "Generated from SBOM inventory",
    security_policy: "Generated from security policy",
    runbook: "Generated from runbooks",
    confluence: "Generated from Confluence export",
    notion: "Generated from Notion export",
    incident: "Generated from incident reports",
    pagerduty: "Generated from PagerDuty export",
  };
  const key = sourceType ?? "code";
  return labels[key] ?? `Generated from ${key}`;
}

function formatRelativeTime(value: string | null): string {
  if (!value) return "Never";
  const date = new Date(value);
  const timestamp = date.getTime();
  if (Number.isNaN(timestamp)) return "Unknown";
  const diffMinutes = Math.max(0, Math.floor((Date.now() - timestamp) / 60000));
  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(date);
}

function categoryLabel(category: string | null): string | null {
  if (!category) return null;
  return category
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function scoreHints(dimension: Dimension, value: number, content: string): ScoreHint {
  void content;
  const bucket = value <= 6 ? "low" : value <= 12 ? "weak" : value <= 18 ? "good" : "strong";
  const hints: Record<Dimension, Record<typeof bucket, ScoreHint>> = {
    groundedness: {
      low: {
        why: "No file paths or code patterns referenced.",
        improve: "Add at least 3 specific file paths and one code pattern your team uses.",
      },
      weak: {
        why: "Minimal grounding — a few references but no patterns.",
        improve: "Add ## Key patterns section with real examples from the codebase.",
      },
      good: {
        why: "Good grounding but missing concrete code examples.",
        improve: "Add a short code block showing the canonical pattern.",
      },
      strong: {
        why: "Well-grounded with files and patterns.",
        improve: null,
      },
    },
    coverage: {
      low: {
        why: "Very thin — fewer than 150 words.",
        improve: "Expand with sections for error handling, edge cases, and related files.",
      },
      weak: {
        why: "Partial coverage — key sub-topics missing.",
        improve: "Add ## sections for testing, auth, and error patterns in this domain.",
      },
      good: {
        why: "Most patterns covered but some gaps.",
        improve: "Check for missing edge cases or environment-specific behaviour.",
      },
      strong: {
        why: "Comprehensive domain coverage.",
        improve: null,
      },
    },
    freshness: {
      low: {
        why: "No recency signals — skill may describe stale patterns.",
        improve: "Add version constraints, recent commit references, or a 'Last updated' note.",
      },
      weak: {
        why: "Some recency signals but no explicit version pinning.",
        improve: "Reference the current framework/library version used in this repo.",
      },
      good: {
        why: "Reasonably fresh but no explicit update timestamp.",
        improve: "Add a '## Last verified' line with the current month and year.",
      },
      strong: {
        why: "Skill is fresh and version-aware.",
        improve: null,
      },
    },
    structure: {
      low: {
        why: "Unstructured — no headings, single block of text.",
        improve: "Add ## headings: Domain summary, Key patterns, Related files, Do / Don't.",
      },
      weak: {
        why: "Basic structure but headings are generic.",
        improve: "Rename headings to be action-oriented, e.g. '## When to use this pattern'.",
      },
      good: {
        why: "Good structure, could use a summary lede.",
        improve: "Add a one-sentence domain summary at the very top (before any heading).",
      },
      strong: {
        why: "Well-structured with clear actionable sections.",
        improve: null,
      },
    },
  };

  return hints[dimension][bucket];
}

function ScoreIntelligenceGrid({ score, content }: { score: Score; content: string }) {
  const dimensions: Array<{ key: Dimension; label: string; value: number }> = [
    { key: "groundedness", label: "Groundedness", value: score.groundedness },
    { key: "coverage", label: "Coverage", value: score.coverage },
    { key: "freshness", label: "Freshness", value: score.freshness },
    { key: "structure", label: "Structure", value: score.structure },
  ];

  return (
    <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {dimensions.map((dimension) => {
        const boundedValue = Math.max(0, Math.min(25, dimension.value));
        const hints = scoreHints(dimension.key, boundedValue, content);
        return (
          <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={dimension.key}>
            <div className="mb-3 flex items-center justify-between gap-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{dimension.label}</div>
              <span className={`inline-flex rounded-full px-2 py-0.5 text-[12px] font-semibold ${subscoreBadgeClass(boundedValue)}`}>{boundedValue}/25</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${(boundedValue / 25) * 100}%` }} />
            </div>
            <p className="mt-3 text-[12px] leading-5 text-[color:var(--text-secondary)]">{hints.why}</p>
            {hints.improve && boundedValue <= 18 ? <p className="mt-1 text-[12px] leading-5 text-amber-300">▲ {hints.improve}</p> : null}
          </article>
        );
      })}
    </div>
  );
}

function ImprovementPlanPanel({
  accessToken,
  repoId,
  skillId,
  score,
  onImproved,
}: {
  accessToken: string;
  repoId: string;
  skillId: string;
  score: Score;
  onImproved: (newScore: number, content: string | null, newVersion: number | null) => void;
}) {
  const [plan, setPlan] = useState<ImprovementPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [improving, setImproving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [aiConfigMissing, setAiConfigMissing] = useState(false);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  async function loadPlan() {
    setLoading(true);
    const response = await fetch(`${apiUrl}/repos/${repoId}/skills/${skillId}/improvement-plan`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (response.ok) {
      setPlan((await response.json()) as ImprovementPlan);
    }
    setLoading(false);
  }

  useEffect(() => {
    void loadPlan();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repoId, skillId]);

  async function improveWithAi() {
    setImproving(true);
    setMessage(null);
    setAiConfigMissing(false);
    const before = plan?.current_score ?? score.total;
    const response = await fetch(`${apiUrl}/repos/${repoId}/skills/${skillId}/improve`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ mode: "enhance" }),
    });
    const payload = await response.json().catch(() => null);
    setImproving(false);
    const reason = String(payload?.reason ?? payload?.detail?.error ?? payload?.detail?.message ?? payload?.detail ?? payload?.code ?? "");
    if (response.status === 402 || reason.includes("llm_not_configured")) {
      setAiConfigMissing(true);
      setMessage(null);
      return;
    }
    if (!response.ok || !payload?.improved) {
      setMessage(payload?.reason || payload?.detail || "Unable to improve this skill right now.");
      return;
    }
    const nextScore = Math.round(Number(payload.new_score ?? before));
    const delta = Math.round(Number(payload.score_delta ?? nextScore - before));
    setMessage(`Score improved from ${before} -> ${nextScore} (+${delta} points!)`);
    onImproved(nextScore, payload.content ?? null, payload.new_version ?? null);
    await loadPlan();
  }

  async function copySuggestions() {
    if (!plan) return;
    const text = plan.issues.map((issue) => `${issue.dimension} (${issue.score}/${issue.max}, +${issue.points_available} pts)\nReason: ${issue.reason}\nFix: ${issue.fix}`).join("\n\n");
    await navigator.clipboard.writeText(text);
    setMessage("Suggestions copied.");
  }

  if (loading) {
    return (
      <section className="mb-8 rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 text-[14px] text-[color:var(--text-secondary)]">
        Loading improvement plan...
      </section>
    );
  }

  if (!plan) return null;

  if (!plan.is_improvable && score.total >= 70) {
    return (
      <section className="mb-8 rounded-[24px] border border-[rgb(var(--accent-green-rgb)/0.28)] bg-[rgb(var(--accent-green-rgb)/0.1)] p-6">
        <div className="flex items-center gap-2 text-[16px] font-semibold text-[color:var(--accent-green)]">
          <CheckCircle2 className="h-5 w-5" />
          This skill is in great shape
        </div>
      </section>
    );
  }

  return (
    <section className="mb-8 rounded-[24px] border border-[rgb(var(--accent-primary-rgb)/0.22)] bg-[linear-gradient(180deg,rgb(var(--accent-primary-rgb)/0.08),rgba(255,255,255,0.02))] p-6">
      <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[rgb(var(--accent-primary-rgb)/0.1)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
            <Lightbulb className="h-3.5 w-3.5" />
            Improvement Plan
          </div>
          <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">This skill can reach {plan.potential_score}/100 with fixes</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{plan.word_count} words · {plan.code_block_count} code examples · +{plan.score_gap} points available</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="inline-flex items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-[13px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-70"
            disabled={improving}
            onClick={improveWithAi}
            title="Configure an AI model in settings to enable AI improvement"
            type="button"
          >
            {improving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            {improving ? "Improving..." : "Improve with AI"}
          </button>
          <button className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-4 py-2 text-[13px] font-semibold text-[color:var(--text-primary)] hover:bg-white/5" onClick={copySuggestions} type="button">
            <Copy className="h-4 w-4" />
            Copy suggestions
          </button>
        </div>
      </div>

      {aiConfigMissing ? (
        <div className="mb-4 rounded-lg border border-amber-500/35 bg-amber-500/10 px-4 py-4 text-[13px] text-amber-100">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
            <div>
              <div className="font-semibold text-amber-100">AI model configuration required</div>
              <p className="mt-1 leading-5 text-amber-100/80">Improve with AI needs a saved provider, model, and API key before it can rewrite this skill.</p>
              <Link className="mt-3 inline-flex rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-[12px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]" href="/dashboard/settings#ai-model">
                Configure AI Model
              </Link>
            </div>
          </div>
        </div>
      ) : message ? (
        <div className={`mb-4 rounded-lg border px-4 py-3 text-[13px] ${message.includes("improved") || message.includes("copied") ? "border-green-500/30 bg-green-500/10 text-green-200" : "border-amber-500/30 bg-amber-500/10 text-amber-200"}`}>
              {message.toLowerCase().includes("llm_not_configured") ? (
                <>
                  AI improvement needs an AI model configured.{" "}
                  <Link className="font-semibold text-[color:var(--accent-primary)] hover:text-[color:var(--accent-bright)]" href="/dashboard/settings#ai-model">
                    Configure AI model
                  </Link>
                </>
          ) : (
            message
          )}
        </div>
      ) : null}

      <div className="grid gap-3">
        {plan.issues.map((issue) => (
          <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={`${issue.dimension}-${issue.reason}`}>
            <div className="flex items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${issue.impact === "high" ? "bg-red-500/15 text-red-200" : "bg-amber-500/15 text-amber-200"}`}>
                  {issue.impact === "high" ? "HIGH IMPACT" : "MEDIUM"}
                </span>
                <h3 className="text-[14px] font-semibold text-[color:var(--text-primary)]">{issue.dimension}</h3>
                <span className="text-[13px] text-[color:var(--text-secondary)]">{issue.score}/{issue.max}</span>
              </div>
              <span className="text-[13px] font-semibold text-[color:var(--accent-primary)]">+{issue.points_available} pts</span>
            </div>
            <p className="mt-3 text-[13px] leading-5 text-[color:var(--text-secondary)]">{issue.reason}</p>
            <p className="mt-3 text-[13px] leading-5 text-[color:var(--text-primary)]">→ Fix: {issue.fix}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function ScoreRing({ score }: { score: number }) {
  const clamped = Math.max(0, Math.min(100, score));
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;
  const tone = clamped <= 40 ? "text-red-400" : clamped <= 70 ? "text-amber-400" : "text-[color:var(--accent-green)]";

  return (
    <div className="relative flex h-28 w-28 items-center justify-center">
      <svg className="-rotate-90 h-28 w-28" viewBox="0 0 120 120">
        <circle cx="60" cy="60" fill="none" r={radius} stroke="rgba(255,255,255,0.08)" strokeWidth="10" />
        <circle
          className={tone}
          cx="60"
          cy="60"
          fill="none"
          r={radius}
          stroke="currentColor"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          strokeWidth="10"
        />
      </svg>
      <div className="absolute text-center">
        <div className="text-2xl font-semibold text-[color:var(--text-primary)]">{clamped}</div>
        <div className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">Score</div>
      </div>
    </div>
  );
}

function UsageAlertBadge({ alert }: { alert: SkillUsageStats["alert"] }) {
  if (alert === "stale_but_active") {
    return (
      <span className="inline-flex items-center gap-2 rounded-full bg-red-500/12 px-3 py-1 text-[12px] font-semibold text-red-300">
        <span className="h-2 w-2 animate-pulse rounded-full bg-red-400" />
        Stale but active
      </span>
    );
  }
  if (alert === "dead_skill") {
    return (
      <span className="inline-flex items-center gap-2 rounded-full bg-white/8 px-3 py-1 text-[12px] font-semibold text-[color:var(--text-secondary)]">
        <span>Never loaded</span>
      </span>
    );
  }
  return null;
}

function UsageSparkline({ points }: { points: SkillUsageStats["daily_loads"] }) {
  const width = 420;
  const height = 92;
  const maxLoads = Math.max(1, ...points.map((point) => point.loads));
  const coordinates = points.map((point, index) => {
    const x = points.length <= 1 ? width / 2 : (index / (points.length - 1)) * width;
    const y = height - (point.loads / maxLoads) * (height - 12) - 6;
    return `${x},${y}`;
  });

  return (
    <svg aria-label="30-day skill activity" className="h-[92px] w-full" preserveAspectRatio="none" viewBox={`0 0 ${width} ${height}`}>
      <polyline fill="none" points={coordinates.join(" ")} stroke="#C9973A" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
    </svg>
  );
}

function RuntimeBreakdown({ runtimes }: { runtimes: SkillUsageStats["agent_runtimes"] }) {
  const entries = Object.entries(runtimes).sort((left, right) => right[1] - left[1]);
  const total = entries.reduce((sum, [, count]) => sum + count, 0);
  const labels: Record<string, string> = {
    claude_code: "Claude Code",
    cursor: "Cursor",
    codex: "Codex",
    copilot: "Copilot",
    unknown: "Other",
  };

  if (total === 0 || entries.length === 0) {
    return <div className="rounded-2xl border border-dashed border-[color:var(--bg-border)] p-4 text-[13px] text-[color:var(--text-secondary)]">No runtime activity recorded yet.</div>;
  }

  return (
    <div className="space-y-3">
      {entries.map(([runtime, count]) => {
        const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
        return (
          <div className="grid grid-cols-[110px_minmax(0,1fr)_72px] items-center gap-3 text-[13px]" key={runtime}>
            <span className="font-medium text-[color:var(--text-primary)]">{labels[runtime] ?? runtime}</span>
            <div className="h-2.5 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-[#C9973A]" style={{ width: `${Math.max(6, percentage)}%` }} />
            </div>
            <span className="text-right text-[color:var(--text-secondary)]">
              {count} ({percentage}%)
            </span>
          </div>
        );
      })}
    </div>
  );
}

function UsageIntelligencePanel({ usage }: { usage: SkillUsageStats | null }) {
  if (!usage) {
    return (
      <section className="mb-8 rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <div className="mb-2 text-[18px] font-semibold text-[color:var(--text-primary)]">Usage Intelligence</div>
        <p className="text-[14px] text-[color:var(--text-secondary)]">No usage data recorded yet.</p>
      </section>
    );
  }

  return (
    <section className="mb-8 rounded-[24px] border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-6">
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Usage Intelligence</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Live activity on this skill across the last 30 days.</p>
        </div>
        <UsageAlertBadge alert={usage.alert} />
      </div>

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <article className="rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Criticality Score</div>
          <div className="mt-3 text-[32px] font-semibold text-[color:var(--text-primary)]">{usage.criticality_score}/100</div>
        </article>
        <article className="rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Loads (30d)</div>
          <div className="mt-3 text-[32px] font-semibold text-[color:var(--text-primary)]">{usage.loads_30d}</div>
        </article>
        <article className="rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Last Loaded</div>
          <div className="mt-3 text-[32px] font-semibold text-[color:var(--text-primary)]">{formatRelativeTime(usage.last_loaded_at)}</div>
        </article>
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(280px,0.9fr)]">
        <div className="rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-5">
          <h3 className="text-[14px] font-semibold text-[color:var(--text-primary)]">30-day load activity</h3>
          <p className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">Daily load counts with missing days filled as zero.</p>
          <div className="mt-4">
            <UsageSparkline points={usage.daily_loads} />
          </div>
        </div>
        <div className="rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-5">
          <h3 className="text-[14px] font-semibold text-[color:var(--text-primary)]">Runtime breakdown</h3>
          <p className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">Which coding agents are loading this skill.</p>
          <div className="mt-4">
            <RuntimeBreakdown runtimes={usage.agent_runtimes} />
          </div>
        </div>
      </div>
    </section>
  );
}

function ZeroSubscoreWarning({ score }: { score: Score }) {
  const zeroCount = [
    score.groundedness,
    score.coverage,
    score.freshness,
    score.structure,
  ].filter((value) => value === 0).length;

  if (score.total <= 0 || zeroCount < 2) {
    return null;
  }

  return (
    <section className="mb-4 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-[13px] text-amber-200">
      Some subscores are incomplete. Re-analysing this repo will produce a full Skilgen Score across all four dimensions.
    </section>
  );
}

function VersionDiffLinks({ repoId, skillId, versions }: { repoId: string; skillId: string; versions: SkillVersionSummary[] }) {
  if (versions.length === 0) {
    return null;
  }

  return (
    <section className="mb-8 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
        <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Version diffs</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Compare each version against the previous saved snapshot.</p>
      </div>
      <div className="divide-y divide-[color:var(--bg-elevated)]">
        {versions.map((version, index) => {
          const hasPrevious = index < versions.length - 1;
          return (
            <div className="flex flex-col gap-3 px-5 py-4 md:flex-row md:items-center md:justify-between" key={version.id}>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[13px] font-semibold text-[color:var(--text-primary)]">v{version.version_number}</span>
                  {version.is_latest ? (
                    <span className="rounded-full bg-[rgb(var(--accent-green-rgb)/0.12)] px-2 py-0.5 text-[11px] font-semibold text-[color:var(--accent-green)]">
                      Latest
                    </span>
                  ) : null}
                </div>
                <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">
                  {new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(version.created_at))}
                </div>
              </div>
              {hasPrevious ? (
                <Link className="text-[12px] text-[color:var(--accent-primary)] hover:underline" href={`/dashboard/repos/${repoId}/skills/${skillId}/versions/${version.id}`}>
                  View diff →
                </Link>
              ) : (
                <span className="text-[12px] text-[color:var(--text-tertiary)]">No previous version</span>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

export function SkillDetailShell({ accessToken, repo, repoId, skill, usageStats, versions }: SkillDetailShellProps) {
  const [score, setScore] = useState<Score>(skill.score);
  const [content, setContent] = useState(skill.content ?? "");
  const [versionNumber, setVersionNumber] = useState<number | null>(skill.latest_version_number);
  const viewerSkill = {
    ...skill,
    content,
    latest_version_number: versionNumber,
    version_count: Math.max(skill.version_count, versionNumber ?? skill.version_count),
  };

  return (
    <div>
      <nav className="mb-6 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">
          Overview
        </Link>
        <span>/</span>
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard/repos">
          Repos
        </Link>
        <span>/</span>
        <Link className="hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}`}>
          {repo?.name ?? skill.repo_name}
        </Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">{skill.domain}</span>
      </nav>

      <SectionErrorBoundary section="skill header">
        <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:gap-6">
            <ScoreRing score={score.total} />
            <div>
              <Link className="mb-4 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}`}>
                <ArrowLeft className="h-4 w-4" />
                Back to repository
              </Link>
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-[rgb(var(--accent-primary-rgb)/0.2)] bg-[rgb(var(--accent-primary-rgb)/0.1)]">
                  <FileText className="h-5 w-5 text-[color:var(--accent-primary)]" />
                </div>
                <div>
                  <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">{skill.domain}</h1>
                  <p className="mt-1 font-mono text-[12px] text-[color:var(--text-secondary)]">{skill.skill_path}</p>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <div className="inline-flex rounded-full border border-[rgb(var(--accent-primary-rgb)/0.28)] bg-[rgb(var(--accent-primary-rgb)/0.08)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
                  Source: {sourceDescription(skill.source_type)}
                </div>
                {categoryLabel(skill.skill_category) ? (
                  <div className="inline-flex rounded-full border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-1 text-[12px] font-semibold text-[color:var(--text-secondary)]">
                    Category: {categoryLabel(skill.skill_category)}
                  </div>
                ) : null}
              </div>
              <div className="mt-4 flex flex-wrap gap-4 text-[13px] text-[color:var(--text-secondary)]">
                <span>{skill.load_count_30d} loads in 30d</span>
                <span>Last loaded: {formatRelativeTime(skill.last_loaded_at)}</span>
                <span>{versions.length || skill.version_count} version{(versions.length || skill.version_count) === 1 ? "" : "s"}</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <ScoreBadge score={score} />
            <PublishSkillButton accessToken={accessToken} domain={skill.domain} skillId={skill.id} />
            <StaleBadge isStale={skill.is_stale} />
            <VersionBadge versionNumber={versionNumber} />
          </div>
        </div>
      </SectionErrorBoundary>

      <SectionErrorBoundary section="skill subscores">
        <ZeroSubscoreWarning score={score} />
        <ImprovementPlanPanel
          accessToken={accessToken}
          onImproved={(newScore, improvedContent, newVersion) => {
            setScore((current) => ({ ...current, total: newScore }));
            if (improvedContent) setContent(improvedContent);
            if (newVersion) setVersionNumber(newVersion);
          }}
          repoId={repoId}
          score={score}
          skillId={skill.id}
        />
        <ScoreIntelligenceGrid content={content} score={score} />
      </SectionErrorBoundary>

      <SectionErrorBoundary section="skill usage intelligence">
        <UsageIntelligencePanel usage={usageStats} />
      </SectionErrorBoundary>

      <SectionErrorBoundary section="skill version diffs">
        <VersionDiffLinks repoId={repoId} skillId={skill.id} versions={versions} />
      </SectionErrorBoundary>

      <SectionErrorBoundary section="skill content">
        <SkillDetailViewer accessToken={accessToken} copyLabel="Copy skill path" copyValue={skill.skill_path} key={`${skill.id}-${versionNumber}-${content.length}`} skill={viewerSkill} versions={versions} />
        <SkillEditor
          accessToken={accessToken}
          initialContent={content}
          onContentSaved={setContent}
          onSaved={(newScore, newVersionNumber) => {
            setScore(newScore);
            setVersionNumber(newVersionNumber);
          }}
          repoId={repoId}
          skillId={skill.id}
        />
      </SectionErrorBoundary>
    </div>
  );
}
