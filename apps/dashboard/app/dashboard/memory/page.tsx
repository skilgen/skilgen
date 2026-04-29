import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowUpRight, Brain, CheckCircle2, TrendingDown, TrendingUp } from "lucide-react";

import { getBootstrapOrg, getKnowledgeVelocity, getMemoryQueue, getOrgMemoryScore, getOrgRedFlags, type KnowledgeVelocity, type MemoryQueueResponse, type MemoryScore, type OrgRedFlags } from "../../../lib/data";
import { MemoryQueueClient } from "./memory-queue-client";

export const dynamic = "force-dynamic";

function emptyQueue(): MemoryQueueResponse {
  return { total: 0, pending_count: 0, items: [] };
}

function emptyVelocity(): KnowledgeVelocity {
  return {
    weekly: Array.from({ length: 8 }, (_, index) => ({ week_start: `Wk ${index + 1}`, discovered: 0, approved: 0 })),
    total_discoveries_all_time: 0,
    approval_rate: null,
  };
}

function fallbackScore(): MemoryScore {
  return {
    score: 0,
    grade: "F",
    trend: "Stable",
    breakdown: { coverage: 0, load_frequency: 0, quality: 0, freshness: 0 },
  };
}

function scoreTone(score: number): string {
  if (score >= 80) return "#22c55e";
  if (score >= 60) return "#f59e0b";
  return "#ef4444";
}

function ScoreDonut({ score, grade }: { score: number; grade: string }) {
  const clamped = Math.max(0, Math.min(100, score));
  const radius = 78;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;
  return (
    <div className="relative h-56 w-56">
      <svg className="h-56 w-56 -rotate-90" viewBox="0 0 200 200">
        <circle cx="100" cy="100" fill="none" r={radius} stroke="rgba(255,255,255,0.08)" strokeWidth="18" />
        <circle cx="100" cy="100" fill="none" r={radius} stroke={scoreTone(clamped)} strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" strokeWidth="18" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-[54px] font-semibold leading-none text-[color:var(--text-primary)]">{clamped}</div>
        <div className="mt-2 rounded-full border border-[color:var(--bg-border)] px-3 py-1 text-[14px] font-semibold text-[color:var(--text-secondary)]">Grade {grade}</div>
      </div>
    </div>
  );
}

function Trend({ label }: { label: string }) {
  const lower = label.toLowerCase();
  const Icon = lower.startsWith("-") ? TrendingDown : lower.includes("stable") ? CheckCircle2 : TrendingUp;
  const tone = lower.startsWith("-") ? "text-red-300" : lower.includes("stable") ? "text-[color:var(--text-secondary)]" : "text-[color:var(--accent-green)]";
  return (
    <div className={`inline-flex items-center gap-2 rounded-full border border-[color:var(--bg-border)] bg-black/20 px-3 py-1 text-[13px] font-semibold ${tone}`}>
      <Icon className="h-4 w-4" />
      {label}
    </div>
  );
}

function BreakdownCard({ label, description, value, weight }: { label: string; description: string; value: number; weight: number }) {
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100);
  return (
    <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-[13px] font-semibold text-[color:var(--text-primary)]">{label}</div>
          <p className="mt-1 min-h-[40px] text-[12px] leading-5 text-[color:var(--text-secondary)]">{description}</p>
        </div>
        <span className="rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-2.5 py-1 text-[11px] font-semibold text-[color:var(--accent-primary)]">x{weight}</span>
      </div>
      <div className="mt-4 flex items-center gap-3">
        <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-white/10">
          <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${pct}%` }} />
        </div>
        <span className="w-10 text-right text-[13px] font-semibold text-[color:var(--text-primary)]">{pct}%</span>
      </div>
    </article>
  );
}

function suggestions(score: MemoryScore): Array<{ title: string; detail: string; points: string }> {
  const entries = [
    { key: "coverage", value: score.breakdown.coverage, title: "Add missing domain skills", detail: "Add Security, Data Schema, or Operations skills to repos with coverage gaps.", points: "+8 points" },
    { key: "load_frequency", value: score.breakdown.load_frequency, title: "Get agents loading skills", detail: "Add SKILL.md references to CLAUDE.md or AGENTS.md for active repos.", points: "+6 points" },
    { key: "quality", value: score.breakdown.quality, title: "Improve low quality skills", detail: "Add anti-patterns, code examples, and specific file references to weak skills.", points: "+7 points" },
    { key: "freshness", value: score.breakdown.freshness, title: "Refresh stale skills", detail: "Re-analyse repos with freshness below 15/25 and add Last verified dates.", points: "+5 points" },
  ];
  return entries.sort((left, right) => left.value - right.value).slice(0, 3);
}

function HistoricalTrend({ velocity, score }: { velocity: KnowledgeVelocity; score: number }) {
  const weeks = velocity.weekly.length ? velocity.weekly : emptyVelocity().weekly;
  const max = Math.max(1, ...weeks.map((week) => week.discovered + week.approved), score);
  return (
    <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-5">
        <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Historical trend</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Last 8 weeks of memory discoveries and approvals.</p>
      </div>
      <svg className="h-[180px] w-full" preserveAspectRatio="none" viewBox="0 0 640 180">
        {weeks.map((week, index) => {
          const x = index * 80 + 18;
          const discoveredHeight = Math.max(5, (week.discovered / max) * 120);
          const approvedHeight = Math.max(5, (week.approved / max) * 120);
          return (
            <g key={`${week.week_start}-${index}`}>
              <rect fill="rgba(201,151,58,0.9)" height={discoveredHeight} rx="4" width="22" x={x} y={140 - discoveredHeight} />
              <rect fill="rgba(34,197,94,0.9)" height={approvedHeight} rx="4" width="22" x={x + 28} y={140 - approvedHeight} />
              <text fill="rgba(238,238,245,0.5)" fontSize="11" textAnchor="middle" x={x + 25} y="168">W{index + 1}</text>
            </g>
          );
        })}
      </svg>
    </section>
  );
}

export default async function MemoryPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Memory auth unavailable:", error);
  }
  const org = await getBootstrapOrg();
  const [memoryScore, queue, velocity, redFlags] = org?.id
    ? await Promise.all([
        getOrgMemoryScore(accessToken, org.id),
        getMemoryQueue(accessToken, org.id, { status: "pending" }),
        getKnowledgeVelocity(accessToken, org.id),
        getOrgRedFlags(accessToken, org.id, "critical"),
      ])
    : [null, null, null, null];
  const safeScore = memoryScore ?? fallbackScore();
  const safeQueue = queue ?? emptyQueue();
  const safeVelocity = velocity ?? emptyVelocity();
  const safeRedFlags: OrgRedFlags = redFlags ?? { critical_count: 0, high_count: 0, medium_count: 0, flags: [] };
  const breakdown = [
    { label: "Coverage", value: safeScore.breakdown.coverage, weight: 30, description: "How many knowledge domains are documented" },
    { label: "Load Frequency", value: safeScore.breakdown.load_frequency, weight: 30, description: "How often agents pull your skills" },
    { label: "Quality", value: safeScore.breakdown.quality, weight: 25, description: "Average skill score across all repos" },
    { label: "Freshness", value: safeScore.breakdown.freshness, weight: 15, description: "% of skills with up-to-date content" },
  ];

  return (
    <div>
      <nav className="mb-6 flex flex-wrap items-center gap-2 text-[13px] text-[color:var(--text-tertiary)]">
        <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">Overview</Link>
        <span>/</span>
        <span className="text-[color:var(--text-secondary)]">Memory Score</span>
      </nav>

      <section className="mb-8 rounded-[30px] border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[radial-gradient(circle_at_top_left,rgb(var(--accent-primary-rgb)/0.18),rgb(var(--bg-surface-rgb)/0.96)_48%)] p-7">
        <div className="grid gap-8 lg:grid-cols-[260px_minmax(0,1fr)] lg:items-center">
          <ScoreDonut grade={safeScore.grade} score={safeScore.score} />
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
              <Brain className="h-4 w-4" />
              Organisational Memory
            </div>
            <h1 className="text-3xl font-semibold text-[color:var(--text-primary)]">Memory Score</h1>
            <p className="mt-3 max-w-3xl text-[15px] leading-7 text-[color:var(--text-secondary)]">A board-level metric quantifying how well your organisation's knowledge is codified and actively used by AI agents.</p>
            <div className="mt-5 flex flex-wrap items-center gap-3">
              <Trend label={safeScore.trend} />
              {safeQueue.pending_count > 0 ? <span className="rounded-full bg-amber-500/15 px-3 py-1 text-[13px] font-semibold text-amber-300">{safeQueue.pending_count} memory items pending</span> : null}
              {safeRedFlags.critical_count > 0 ? <span className="rounded-full bg-red-500/15 px-3 py-1 text-[13px] font-semibold text-red-300">{safeRedFlags.critical_count} critical flags</span> : null}
            </div>
          </div>
        </div>
      </section>

      <section className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {breakdown.map((item) => <BreakdownCard key={item.label} {...item} />)}
      </section>

      <section className="mb-8">
        <div className="mb-4">
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">What moves your score</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Actions ranked by the weakest sub-score first.</p>
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          {suggestions(safeScore).map((item) => (
            <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={item.title}>
              <div className="flex items-start justify-between gap-3">
                <h3 className="text-[15px] font-semibold text-[color:var(--text-primary)]">{item.title}</h3>
                <span className="rounded-full bg-[rgb(var(--accent-green-rgb)/0.14)] px-2.5 py-1 text-[11px] font-semibold text-[color:var(--accent-green)]">{item.points}</span>
              </div>
              <p className="mt-3 text-[13px] leading-6 text-[color:var(--text-secondary)]">{item.detail}</p>
              <Link className="mt-4 inline-flex items-center gap-2 text-[12px] font-semibold text-[color:var(--accent-primary)]" href="/dashboard/skills">
                Improve skills
                <ArrowUpRight className="h-3.5 w-3.5" />
              </Link>
            </article>
          ))}
        </div>
      </section>

      <div className="mb-8">
        <HistoricalTrend score={safeScore.score} velocity={safeVelocity} />
      </div>

      <section>
        <div className="mb-4">
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Memory capture queue</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Agent-discovered knowledge waiting to be merged into skills.</p>
        </div>
        <MemoryQueueClient accessToken={accessToken} initialQueue={safeQueue} orgId={org?.id ?? ""} />
      </section>
    </div>
  );
}
