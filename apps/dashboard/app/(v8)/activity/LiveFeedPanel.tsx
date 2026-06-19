"use client";

import Link from "next/link";
import { AlertTriangle, ChevronDown, ExternalLink, Filter, Radio, Search, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { ActivityEvent, RiskContributor } from "./activity-data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
const FALLBACK_SESSION_GAP_MS = 5 * 60 * 1000;

type SkillCoverage = {
  loaded_count: number;
  relevant_count: number;
  coverage_percent: number;
  loaded_skills: string[];
  relevant_skills: string[];
  zero_loaded_relevant: boolean;
};

type ExtendedActivityEvent = ActivityEvent & {
  model?: string | null;
  model_name?: string | null;
  tokens_total?: number | null;
  total_tokens?: number | null;
  token_count?: number | null;
  input_tokens?: number | null;
  output_tokens?: number | null;
  cost_usd?: number | null;
  spend_usd?: number | null;
  cost?: number | null;
  summary?: string | null;
  replay_url?: string | null;
  url?: string | null;
  skill_coverage?: SkillCoverage | null;
  risk_contributors?: RiskContributor[] | string[] | Record<string, number | string | boolean | null> | null;
};

type SessionGroup = {
  id: string;
  events: ExtendedActivityEvent[];
  agent: string;
  provider: string;
  model: string;
  user: string;
  repo: string;
  repoId: string;
  skillNames: string[];
  filesTouched: string[];
  startedAt: string | null;
  endedAt: string | null;
  latestAt: string | null;
  outcome: string;
  riskBand: ActivityEvent["risk_band"];
  riskScore: number;
  riskContributors: string[];
  coverage: SkillCoverage | null;
  tokens: number;
  cost: number;
  sessionDbId: string | null;
  sessionId: string;
  trigger: ActivityEvent["trigger"];
};

type ViewMode = "grouped" | "chronological";

const FILTER_LABELS: Record<string, string> = {
  agent_provider: "Provider",
  hours: "Window",
  repo_id: "Repo",
  repo_sensitivity_tier: "Tier",
  risk_band: "Risk",
};

function formatTime(value: string | null): string {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit", month: "short", day: "numeric" }).format(date);
}

function formatWindow(startedAt: string | null, endedAt: string | null): string {
  if (!startedAt && !endedAt) return "Unknown time";
  if (!startedAt || startedAt === endedAt) return formatTime(endedAt ?? startedAt);
  return `${formatTime(startedAt)} - ${formatTime(endedAt)}`;
}

function timestampValue(value: string | null): number {
  if (!value) return 0;
  const time = new Date(value).getTime();
  return Number.isNaN(time) ? 0 : time;
}

function riskTone(band: ActivityEvent["risk_band"]): { rail: string; text: string; segment: string } {
  if (band === "high") return { rail: "bg-red-500", segment: "bg-red-400", text: "text-red-200" };
  if (band === "medium") return { rail: "bg-amber-500", segment: "bg-amber-400", text: "text-amber-200" };
  return { rail: "bg-[color:var(--accent-green)]", segment: "bg-[color:var(--accent-green)]", text: "text-[color:var(--accent-green)]" };
}

function outcomeClass(outcome: string): string {
  const normalized = outcome.toLowerCase();
  if (["failed", "error", "denied", "blocked"].some((item) => normalized.includes(item))) return "border-red-500/35 bg-red-500/10 text-red-200";
  if (["warning", "partial", "skipped"].some((item) => normalized.includes(item))) return "border-amber-500/35 bg-amber-500/10 text-amber-200";
  return "border-[color:var(--accent-green)]/35 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]";
}

function formatOutcome(outcome: string): string {
  const value = outcome || "unknown";
  return value.replaceAll("_", " ").replaceAll("-", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function numberValue(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function eventTokens(event: ExtendedActivityEvent): number {
  return numberValue(event.tokens_total) || numberValue(event.total_tokens) || numberValue(event.token_count) || numberValue(event.input_tokens) + numberValue(event.output_tokens);
}

function eventCost(event: ExtendedActivityEvent): number {
  return numberValue(event.cost_usd) || numberValue(event.spend_usd) || numberValue(event.cost);
}

function normalizeCoverage(coverage: SkillCoverage | null | undefined): SkillCoverage | null {
  if (!coverage) return null;
  const loadedSkills = Array.isArray(coverage.loaded_skills) ? coverage.loaded_skills : [];
  const relevantSkills = Array.isArray(coverage.relevant_skills) ? coverage.relevant_skills : [];
  const relevantCount = numberValue(coverage.relevant_count) || relevantSkills.length;
  const loadedCount = numberValue(coverage.loaded_count) || loadedSkills.length;
  const rawPercent = numberValue(coverage.coverage_percent);
  const coveragePercent = rawPercent <= 1 && rawPercent > 0 ? rawPercent * 100 : rawPercent;

  return {
    loaded_count: loadedCount,
    relevant_count: relevantCount,
    coverage_percent: Math.max(0, Math.min(100, coveragePercent)),
    loaded_skills: loadedSkills,
    relevant_skills: relevantSkills,
    zero_loaded_relevant: Boolean(coverage.zero_loaded_relevant || (relevantCount > 0 && loadedCount === 0)),
  };
}

function mergeCoverage(events: ExtendedActivityEvent[]): SkillCoverage | null {
  const coverages = events.map((event) => normalizeCoverage(event.skill_coverage)).filter((coverage): coverage is SkillCoverage => coverage != null);
  if (!coverages.length) return null;
  const loadedSkills = unique(coverages.flatMap((coverage) => coverage.loaded_skills));
  const relevantSkills = unique(coverages.flatMap((coverage) => coverage.relevant_skills));
  const relevantCount = relevantSkills.length || Math.max(...coverages.map((coverage) => coverage.relevant_count));
  const loadedCount = loadedSkills.length || Math.max(...coverages.map((coverage) => coverage.loaded_count));
  const averagePercent = coverages.reduce((sum, coverage) => sum + coverage.coverage_percent, 0) / coverages.length;

  return {
    loaded_count: loadedCount,
    relevant_count: relevantCount,
    coverage_percent: relevantCount ? Math.max(0, Math.min(100, averagePercent)) : 0,
    loaded_skills: loadedSkills,
    relevant_skills: relevantSkills,
    zero_loaded_relevant: coverages.some((coverage) => coverage.zero_loaded_relevant),
  };
}

function getRiskContributors(event: ExtendedActivityEvent): string[] {
  const contributors = event.risk_contributors;
  if (!contributors) return [];
  if (Array.isArray(contributors)) {
    return contributors
      .filter(Boolean)
      .map((item) => (typeof item === "string" ? item : item.label || item.factor))
      .filter(Boolean);
  }
  return Object.entries(contributors)
    .filter(([, value]) => value != null && value !== 0 && value !== false && value !== "")
    .map(([key]) => key);
}

function flagLabelsForGroup(group: SessionGroup): string[] {
  const normalizeFlag = (label: string): string => {
    const value = label.replace(/^dangerous command\s*-\s*/i, "").replace(/:\s*.+$/, "").trim();
    if (/full filesystem access/i.test(value)) return "Full filesystem access";
    if (/full access scope/i.test(value)) return "Full access scope";
    if (/0 skill docs loaded|no skill docs/i.test(value)) return "No skill docs loaded";
    if (/process or automation/i.test(value)) return "Process or automation launch";
    if (/credential|secret|env/i.test(value)) return "Credential access";
    if (/remote code/i.test(value)) return "Remote code execution";
    if (/database file/i.test(value)) return "Database file movement";
    if (/force push/i.test(value)) return "Force push";
    if (/destructive/i.test(value)) return "Destructive command";
    if (/unapproved MCP|tool call/i.test(value)) return "Unapproved tool";
    if (/sensitive path/i.test(value)) return "Sensitive path touched";
    return value;
  };
  const labels = unique([
    ...group.riskContributors,
    ...group.events.flatMap((event) => event.risk_reasons ?? []),
  ])
    .map(normalizeFlag)
    .filter(Boolean)
    .filter((label) => !/^write activity$/i.test(label))
    .filter((label) => !/^\d+ file target/i.test(label))
    .filter((label) => !/^internal repository$/i.test(label))
    .map((label) => label.replace(/\bapi\b/gi, "API"));

  const specific = labels.filter((label) => /full filesystem|env|credential|secret|force push|remote code|database file|destructive|automation|sudo|unapproved|sensitive|curl|chmod|rm -rf|skill docs/i.test(label));
  if (specific.length) return unique(specific).slice(0, 4);
  if (group.coverage?.zero_loaded_relevant) return ["No skill docs loaded"];
  if (group.riskBand === "high") return unique(labels).slice(0, 3);
  return [];
}

function unique(values: Array<string | null | undefined>): string[] {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}

function aggregateOutcome(events: ExtendedActivityEvent[]): string {
  const priority = ["failed", "error", "denied", "blocked", "partial", "warning", "skipped", "success", "completed"];
  const outcomes = events.map((event) => event.outcome || "unknown");
  return outcomes.sort((a, b) => {
    const aIndex = priority.findIndex((item) => a.toLowerCase().includes(item));
    const bIndex = priority.findIndex((item) => b.toLowerCase().includes(item));
    return (aIndex === -1 ? priority.length : aIndex) - (bIndex === -1 ? priority.length : bIndex);
  })[0] ?? "unknown";
}

function aggregateRisk(events: ExtendedActivityEvent[]): { band: ActivityEvent["risk_band"]; score: number } {
  return events.reduce(
    (current, event) => {
      if (event.risk_score > current.score) return { band: event.risk_band, score: event.risk_score };
      if (event.risk_score === current.score && event.risk_band === "high") return { band: "high", score: event.risk_score };
      if (event.risk_score === current.score && event.risk_band === "medium" && current.band === "low") return { band: "medium", score: event.risk_score };
      return current;
    },
    { band: "low" as ActivityEvent["risk_band"], score: 0 },
  );
}

function buildGroup(id: string, events: ExtendedActivityEvent[]): SessionGroup {
  const ordered = [...events].sort((a, b) => timestampValue(a.timestamp) - timestampValue(b.timestamp));
  const latest = ordered[ordered.length - 1] ?? events[0];
  const risk = aggregateRisk(events);
  const filesTouched = unique(events.flatMap((event) => event.file_scope ?? []));
  const skillNames = unique(events.flatMap((event) => [event.skill, ...(event.skill_coverage?.loaded_skills ?? [])])).filter((item) => !item.toLowerCase().includes("no skill loads recorded") && !item.toLowerCase().startsWith("agent session"));

  return {
    id,
    events: ordered,
    agent: latest?.agent || "Unknown agent",
    provider: latest?.agent_provider || "unknown",
    model: latest?.model || latest?.model_name || latest?.agent_provider || "model unknown",
    user: latest?.user || "Unknown user",
    repo: latest?.repo_name || latest?.repo || "Unknown repo",
    repoId: latest?.repo_id || "",
    skillNames,
    filesTouched,
    startedAt: ordered[0]?.timestamp ?? null,
    endedAt: latest?.timestamp ?? null,
    latestAt: latest?.timestamp ?? null,
    outcome: aggregateOutcome(events),
    riskBand: risk.band,
    riskScore: risk.score,
    riskContributors: unique(events.flatMap(getRiskContributors)),
    coverage: mergeCoverage(events),
    tokens: events.reduce((sum, event) => sum + eventTokens(event), 0),
    cost: events.reduce((sum, event) => sum + eventCost(event), 0),
    sessionDbId: latest?.session_db_id ?? null,
    sessionId: latest?.session_id || id,
    trigger: latest?.trigger ?? events.find((event) => event.trigger)?.trigger ?? null,
  };
}

function groupEvents(rows: ExtendedActivityEvent[]): SessionGroup[] {
  const sessionBuckets = new Map<string, ExtendedActivityEvent[]>();
  const fallbackBuckets: Array<{ key: string; id: string; lastAt: number; events: ExtendedActivityEvent[] }> = [];

  for (const event of [...rows].sort((a, b) => timestampValue(a.timestamp) - timestampValue(b.timestamp))) {
    const sessionKey = event.session_db_id || event.session_id;
    if (sessionKey) {
      const key = `session:${sessionKey}`;
      sessionBuckets.set(key, [...(sessionBuckets.get(key) ?? []), event]);
      continue;
    }

    const time = timestampValue(event.timestamp);
    const fallbackKey = `${event.agent_provider}:${event.agent}:${event.repo_id || event.repo}`;
    const bucket = fallbackBuckets.find((item) => item.key === fallbackKey && Math.abs(time - item.lastAt) <= FALLBACK_SESSION_GAP_MS);
    if (bucket) {
      bucket.events.push(event);
      bucket.lastAt = time;
    } else {
      fallbackBuckets.push({ key: fallbackKey, id: `fallback:${fallbackKey}:${time || event.id}`, lastAt: time, events: [event] });
    }
  }

  return [
    ...Array.from(sessionBuckets.entries()).map(([id, bucketEvents]) => buildGroup(id, bucketEvents)),
    ...fallbackBuckets.map((bucket) => buildGroup(bucket.id, bucket.events)),
  ].sort((a, b) => b.riskScore - a.riskScore || timestampValue(b.latestAt) - timestampValue(a.latestAt));
}

function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}m`;
  if (tokens >= 1_000) return `${(tokens / 1_000).toFixed(1)}k`;
  return `${tokens}`;
}

function formatCost(cost: number): string {
  if (!cost) return "$0";
  if (cost < 0.01) return "<$0.01";
  return new Intl.NumberFormat(undefined, { currency: "USD", maximumFractionDigits: 2, style: "currency" }).format(cost);
}

function summaryForGroup(group: SessionGroup): string {
  const metrics = group.events.reduce(
    (current, event) => {
      const values = event.activity_metrics ?? {};
      current.edits += numberValue(values.edited_files);
      current.explored += numberValue(values.explored_files);
      current.searches += numberValue(values.searches);
      current.commands += numberValue(values.commands);
      return current;
    },
    { commands: 0, edits: 0, explored: 0, searches: 0 },
  );
  const actions = [
    metrics.edits ? `edited ${metrics.edits} file${metrics.edits === 1 ? "" : "s"}` : null,
    metrics.commands ? `ran ${metrics.commands} command${metrics.commands === 1 ? "" : "s"}` : null,
    metrics.searches ? `${metrics.searches} search${metrics.searches === 1 ? "" : "es"}` : null,
    metrics.explored ? `explored ${metrics.explored} file${metrics.explored === 1 ? "" : "s"}` : null,
  ].filter(Boolean);
  const activity = actions.length ? actions.slice(0, 2).join(" and ") : `${group.events.length} action${group.events.length === 1 ? "" : "s"}`;
  const coverage = group.coverage?.zero_loaded_relevant
    ? "no skill docs loaded"
    : group.coverage
      ? `${group.coverage.loaded_count} of ${group.coverage.relevant_count} relevant skills loaded`
      : "skill coverage unknown";
  return `${activity.charAt(0).toUpperCase()}${activity.slice(1)}. ${coverage.charAt(0).toUpperCase()}${coverage.slice(1)}.`;
}

function metadataForGroup(group: SessionGroup): string {
  return [
    `${group.filesTouched.length} file${group.filesTouched.length === 1 ? "" : "s"}`,
    `${formatTokens(group.tokens)} tokens`,
    formatCost(group.cost),
    `${group.events[0]?.repo_sensitivity_tier || "unknown"} tier`,
  ].join(" · ");
}

function eventLabel(event: ExtendedActivityEvent): string {
  const raw = event.action || event.action_class || "Activity";
  if (/agent session/i.test(raw) || /no skill loads recorded/i.test(raw)) return "Session activity";
  return raw.replaceAll("_", " ").replaceAll("-", " ");
}

function removeFilterHref(searchParams: URLSearchParams, key: string): string {
  const next = new URLSearchParams(searchParams);
  next.delete(key);
  const query = next.toString();
  return query ? `/activity/live-feed?${query}` : "/activity/live-feed";
}

function filterChips(searchParams: URLSearchParams): Array<{ key: string; label: string; value: string; href: string }> {
  return Array.from(searchParams.entries())
    .filter(([key, value]) => Boolean(value) && key in FILTER_LABELS)
    .map(([key, value]) => ({ key, label: FILTER_LABELS[key], value, href: removeFilterHref(searchParams, key) }));
}

function KpiStrip({ groups, events }: { groups: SessionGroup[]; events: ExtendedActivityEvent[] }) {
  const totalCost = groups.reduce((sum, group) => sum + group.cost, 0);
  const totalTokens = groups.reduce((sum, group) => sum + group.tokens, 0);
  const coverageValues = groups.map((group) => group.coverage?.coverage_percent).filter((value): value is number => value != null);
  const avgCoverage = coverageValues.length ? coverageValues.reduce((sum, value) => sum + value, 0) / coverageValues.length : null;
  const zeroLoadedCount = groups.filter((group) => group.coverage?.zero_loaded_relevant).length;
  const zeroLoadedRelevant = zeroLoadedCount > 0;
  const highRiskRuns = groups.filter((group) => group.riskBand === "high").length;
  const coverageIsAlarm = avgCoverage == null || zeroLoadedRelevant || avgCoverage < 70;
  const highRiskIsAlarm = highRiskRuns > 0;
  const coverageAlert = avgCoverage == null ? "No signal" : coverageIsAlarm ? "Below target" : "Covered";
  const coverageTrack = avgCoverage == null ? 0 : Math.max(0, Math.min(100, avgCoverage));

  return (
    <div className="grid gap-2 md:grid-cols-4">
      <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3.5">
        <div className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">Agent sessions</div>
        <div className="mt-1 text-[26px] font-medium leading-tight text-[color:var(--text-primary)]">{groups.length}</div>
        <div className="mt-1 text-xs text-[color:var(--text-secondary)]">{events.length} raw events in window</div>
      </article>
      <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3.5">
        <div className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">Spend</div>
        <div className="mt-1 text-[26px] font-medium leading-tight text-[color:var(--text-primary)]">{formatCost(totalCost)}</div>
        <div className="mt-1 text-xs text-[color:var(--text-secondary)]">{formatTokens(totalTokens)} tokens in window</div>
      </article>
      <article className={`rounded-lg border p-3.5 ${coverageIsAlarm ? "border-red-500/35 bg-red-500/10" : "border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]"}`}>
        <div className={`inline-flex items-center gap-1.5 text-[11px] uppercase tracking-wide ${coverageIsAlarm ? "text-red-200" : "text-[color:var(--text-tertiary)]"}`}>
          {coverageIsAlarm ? <AlertTriangle className="h-3.5 w-3.5" /> : null}
          Skill coverage
        </div>
        <div className={`mt-1 text-[26px] font-medium leading-tight ${coverageIsAlarm ? "text-red-100" : "text-[color:var(--text-primary)]"}`}>{avgCoverage == null ? "--" : `${Math.round(avgCoverage)}%`}</div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-black/35">
          <div className={`h-full ${coverageIsAlarm ? "bg-red-400" : "bg-[color:var(--accent-green)]"}`} style={{ width: `${coverageTrack}%` }} />
        </div>
        <div className="mt-1 text-xs text-[color:var(--text-secondary)]">{zeroLoadedCount} of {groups.length} runs loaded 0 skills · {coverageAlert}</div>
      </article>
      <article className={`rounded-lg border p-3.5 ${highRiskIsAlarm ? "border-red-500/35 bg-red-500/10" : "border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]"}`}>
        <div className={`inline-flex items-center gap-1.5 text-[11px] uppercase tracking-wide ${highRiskIsAlarm ? "text-red-200" : "text-[color:var(--text-tertiary)]"}`}>
          {highRiskIsAlarm ? <AlertTriangle className="h-3.5 w-3.5" /> : null}
          High-risk runs
        </div>
        <div className={`mt-1 text-[26px] font-medium leading-tight ${highRiskIsAlarm ? "text-red-100" : "text-[color:var(--text-primary)]"}`}>{highRiskRuns}</div>
        <div className="mt-1 text-xs text-[color:var(--text-secondary)]">Score 70 or higher</div>
      </article>
    </div>
  );
}

function SessionCard({ group, defaultOpen }: { group: SessionGroup; defaultOpen: boolean }) {
  const tone = riskTone(group.riskBand);
  const coverage = group.coverage;
  const loaded = coverage?.loaded_count ?? 0;
  const relevant = coverage?.relevant_count ?? 0;
  const segmentCount = Math.max(1, relevant || loaded || 1);
  const flags = flagLabelsForGroup(group);
  const grounded = !flags.length && group.riskBand === "low" && coverage != null && relevant > 0 && loaded >= relevant;

  return (
    <details className="group overflow-hidden rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]" open={defaultOpen}>
      <summary className="relative grid cursor-pointer list-none gap-0 md:grid-cols-[minmax(0,1fr)_132px]">
        <div className={`absolute inset-y-0 left-0 w-1 ${tone.rail}`} />
        <div className="min-w-0 space-y-2 py-3 pl-4 pr-3 md:pl-5">
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
            <span className="text-sm font-medium text-[color:var(--text-primary)]">{group.agent}</span>
            <span className="rounded border border-[rgb(var(--accent-primary-rgb)/0.25)] bg-[rgb(var(--accent-primary-rgb)/0.07)] px-1.5 py-0.5 text-[11px] text-[color:var(--accent-primary)]">{group.model}</span>
            <code className="text-[11px] text-[color:var(--text-tertiary)]">{group.repo}</code>
            <span className="text-[11px] text-[color:var(--text-tertiary)]">{formatWindow(group.startedAt, group.endedAt)}</span>
            <span className={`rounded border px-1.5 py-0.5 text-[11px] ${outcomeClass(group.outcome)}`}>{formatOutcome(group.outcome)}</span>
          </div>
          <p className="text-sm leading-5 text-[color:var(--text-secondary)]">{summaryForGroup(group)}</p>
          <p className="text-xs text-[color:var(--text-tertiary)]">{metadataForGroup(group)}</p>
          <div className="flex flex-wrap gap-1.5">
            {flags.length ? flags.map((flag) => (
              <span className="rounded-full border border-red-500/30 bg-red-500/10 px-2 py-0.5 text-[11px] text-red-100" key={flag}>{flag}</span>
            )) : (
              <span className={`rounded-full border px-2 py-0.5 text-[11px] ${grounded ? "border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : "border-[color:var(--bg-border)] bg-black/15 text-[color:var(--text-tertiary)]"}`}>
                {grounded ? "Grounded · no flags" : "No classifier flags"}
              </span>
            )}
          </div>
        </div>
        <div className="border-t border-[color:var(--bg-border)] px-3 py-3 md:border-l md:border-t-0">
          <div className="flex items-start justify-between gap-2 md:block">
            <div>
              <div className={`text-[28px] font-medium leading-none ${tone.text}`}>{group.riskScore}</div>
              <div className={`mt-0.5 text-[11px] ${tone.text}`}>{group.riskBand} band</div>
            </div>
            <ChevronDown className="h-4 w-4 text-[color:var(--text-tertiary)] transition-transform group-open:rotate-180 md:float-right" />
          </div>
          <div className="mt-3">
            <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${segmentCount}, minmax(0, 1fr))` }}>
              {Array.from({ length: segmentCount }).map((_, index) => (
                <span className={`h-1.5 rounded-full ${index < loaded ? tone.segment : coverage?.zero_loaded_relevant ? "bg-red-500/25" : "bg-white/10"}`} key={index} />
              ))}
            </div>
            <div className={`mt-1 text-[11px] ${coverage?.zero_loaded_relevant ? "text-red-200" : "text-[color:var(--text-tertiary)]"}`}>{coverage ? `${loaded} of ${relevant}` : "No signal"}</div>
          </div>
          {group.sessionDbId ? (
            <Link className="mt-3 inline-flex w-full items-center justify-center rounded-md border border-[color:var(--bg-border)] px-2 py-1.5 text-xs text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" href={`/activity/replay/${group.sessionDbId}?repo=${group.repoId}`}>
              Replay
            </Link>
          ) : (
            <span className="mt-3 inline-flex w-full items-center justify-center rounded-md border border-[color:var(--bg-border)] px-2 py-1.5 text-xs text-[color:var(--text-tertiary)]">No replay</span>
          )}
        </div>
      </summary>

      <div className="border-t border-[color:var(--bg-border)] bg-black/10 px-4 pb-3 pt-2 md:px-5">
        <div className="divide-y divide-[color:var(--bg-border)]">
          {group.events.map((event) => (
            <div className="grid gap-2 py-2 text-sm md:grid-cols-[104px_minmax(0,1fr)_minmax(120px,0.35fr)]" key={event.id}>
              <span className="text-xs text-[color:var(--text-tertiary)]">{formatTime(event.timestamp)}</span>
              <span className="min-w-0">
                <span className="block truncate text-[color:var(--text-primary)]">{eventLabel(event)}</span>
                <span className="block truncate text-xs text-[color:var(--text-tertiary)]">{event.file_scope?.slice(0, 2).join(", ") || event.action_class || group.user}</span>
              </span>
              <span className="truncate text-xs text-[color:var(--text-tertiary)]">{formatOutcome(event.outcome)}</span>
            </div>
          ))}
        </div>

        <div className="mt-3 flex flex-wrap gap-3">
          {group.trigger?.url ? (
            <a className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-1.5 text-sm text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" href={group.trigger.url} rel="noreferrer" target="_blank">
              <ExternalLink className="h-4 w-4" />
              Open {group.trigger.label || "source"}
            </a>
          ) : null}
        </div>
      </div>
    </details>
  );
}

export function LiveFeedPanel({ events, orgId, searchParams, streamKey }: { events: ActivityEvent[]; orgId: string; searchParams: URLSearchParams; streamKey: string }) {
  const [rows, setRows] = useState<ExtendedActivityEvent[]>(events as ExtendedActivityEvent[]);
  const [status, setStatus] = useState(streamKey ? "connecting" : "offline");
  const [viewMode, setViewMode] = useState<ViewMode>("grouped");

  useEffect(() => setRows(events as ExtendedActivityEvent[]), [events]);

  useEffect(() => {
    if (!orgId || !streamKey) return undefined;
    const source = new EventSource(`${API_URL}/v8/orgs/${orgId}/activity/feed/stream?key=${encodeURIComponent(streamKey)}`);
    source.onopen = () => setStatus("live");
    source.onerror = () => setStatus("reconnecting");
    source.onmessage = (message) => {
      const event = JSON.parse(message.data) as ExtendedActivityEvent;
      setRows((current) => [event, ...current.filter((item) => item.id !== event.id)].slice(0, 50));
    };
    return () => source.close();
  }, [orgId, streamKey]);

  const query = useMemo(() => Object.fromEntries(searchParams.entries()), [searchParams]);
  const filterKey = useMemo(() => searchParams.toString(), [searchParams]);
  const chips = useMemo(() => filterChips(searchParams), [searchParams]);
  const groups = useMemo(() => groupEvents(rows), [rows]);
  const chronologicalGroups = useMemo(() => rows.map((event) => buildGroup(`event:${event.id}`, [event])).sort((a, b) => timestampValue(b.latestAt) - timestampValue(a.latestAt)), [rows]);
  const visibleGroups = viewMode === "grouped" ? groups : chronologicalGroups;

  return (
    <section className="mx-auto max-w-[1080px] space-y-3">
      <KpiStrip events={rows} groups={groups} />

      <form className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-2.5" key={filterKey} method="get">
        <div className="grid gap-2 md:grid-cols-[auto_110px_minmax(120px,1fr)_minmax(140px,1fr)_120px_140px_auto] md:items-center">
          <label className="flex items-center gap-2 text-sm font-medium text-[color:var(--text-secondary)]">
            <Filter className="h-4 w-4" />
            Filters
          </label>
          <select className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.hours ?? "168"} name="hours">
            <option value="1">1 hour</option>
            <option value="24">24 hours</option>
            <option value="168">7 days</option>
            <option value="720">30 days</option>
          </select>
          <input className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.agent_provider ?? ""} name="agent_provider" placeholder="Provider" />
          <input className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.repo_id ?? ""} name="repo_id" placeholder="Repo ID" />
          <select className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.risk_band ?? ""} name="risk_band">
            <option value="">All risk</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <select className="min-w-0 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={query.repo_sensitivity_tier ?? ""} name="repo_sensitivity_tier">
            <option value="">All tiers</option>
            <option value="public">Public</option>
            <option value="internal">Internal</option>
            <option value="confidential">Confidential</option>
            <option value="restricted">Restricted</option>
          </select>
          <button className="inline-flex items-center justify-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-medium text-[color:var(--bg-base)]" type="submit">
            <Search className="h-4 w-4" />
            Apply
          </button>
        </div>
        {chips.length ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {chips.map((chip) => (
              <Link className="inline-flex items-center gap-1 rounded-md border border-[rgb(var(--accent-primary-rgb)/0.28)] bg-[rgb(var(--accent-primary-rgb)/0.08)] px-2 py-1 text-xs font-medium text-[color:var(--accent-primary)]" href={chip.href} key={chip.key}>
                {chip.label}: {chip.value}
                <X className="h-3 w-3" />
              </Link>
            ))}
          </div>
        ) : null}
      </form>

      <div className="flex flex-col gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-2.5 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-wrap items-center gap-3 text-sm text-[color:var(--text-secondary)]">
          <span>{groups.length} sessions</span>
          <span className="h-1 w-1 rounded-full bg-[color:var(--text-tertiary)]" />
          <span>{rows.length} events</span>
          <span className="inline-flex items-center gap-2 capitalize">
            <Radio className="h-4 w-4 text-[color:var(--accent-primary)]" />
            {status}
          </span>
        </div>
        <div className="inline-flex rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-1">
          {(["grouped", "chronological"] as ViewMode[]).map((mode) => (
            <button className={`rounded px-3 py-1.5 text-sm font-medium capitalize ${viewMode === mode ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]"}`} key={mode} onClick={() => setViewMode(mode)} type="button">
              {mode}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2.5">
        {visibleGroups.length ? visibleGroups.map((group, index) => <SessionCard defaultOpen={index === 0} group={group} key={group.id} />) : <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center text-sm text-[color:var(--text-secondary)]">No activity matched the current filters.</div>}
      </div>
    </section>
  );
}
