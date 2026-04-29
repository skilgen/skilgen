import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowUpRight, Brain } from "lucide-react";

import { getBootstrapOrg, getKnowledgeVelocity, getMemoryQueue, getOrgMemoryScore, getOrgRepos } from "../../../lib/data";

function gradeCopy(score: number): string {
  if (score >= 80) return "AI-Native — agents write code like your best engineers";
  if (score >= 60) return "AI-Ready — agents follow your patterns most of the time";
  if (score >= 40) return "Getting there — agents need more guidance";
  return "Early stage — high value in improving skill coverage";
}

function ScoreDonut({ score, grade }: { score: number; grade: string }) {
  const radius = 78;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? "#22c55e" : score >= 60 ? "#f59e0b" : "#ef4444";
  return (
    <div className="relative h-56 w-56">
      <svg className="h-56 w-56 -rotate-90" viewBox="0 0 200 200">
        <circle cx="100" cy="100" fill="none" r={radius} stroke="rgba(255,255,255,.08)" strokeWidth="18" />
        <circle cx="100" cy="100" fill="none" r={radius} stroke={color} strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" strokeWidth="18" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center"><span className="text-5xl font-semibold">{score}</span><span className="mt-2 rounded-full border border-[color:var(--bg-border)] px-3 py-1 text-sm">Grade {grade}</span></div>
    </div>
  );
}

export default async function AIReadinessPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }
  const org = await getBootstrapOrg();
  const [score, velocity, queue, repos] = org?.id ? await Promise.all([getOrgMemoryScore(accessToken, org.id), getKnowledgeVelocity(accessToken, org.id), getMemoryQueue(accessToken, org.id, { status: "pending" }), getOrgRepos(accessToken, org.id)]) : [null, null, null, []];
  const safe = score ?? { score: 0, grade: "F" as const, trend: "Stable", trend_7d: 0, trend_30d: 0, computed_at: "", breakdown: { coverage: 0, load_frequency: 0, compliance: 0, quality: 0, freshness: 0 } };
  const totalSkills = (repos ?? []).reduce((sum, repo) => sum + (repo.skill_count ?? 0), 0);
  const compliance = safe.breakdown.compliance ?? safe.breakdown.quality ?? 0;
  const needsWork = Math.max(0, Math.round(totalSkills * (1 - compliance)));
  const loads = Math.round(safe.breakdown.load_frequency * 1000);
  const repoId = repos?.[0]?.id ?? "<repo-id>";
  const points = velocity?.weekly ?? [];

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">AI Readiness Score</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">How ready is your organisation for AI-assisted development? Measured across 4 dimensions.</p>
      </header>

      <section className="rounded-[28px] border border-[color:var(--accent-primary)]/25 bg-[color:var(--bg-surface)] p-7">
        <div className="grid gap-8 lg:grid-cols-[260px_1fr] lg:items-center">
          <ScoreDonut grade={safe.grade} score={safe.score} />
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-[color:var(--accent-primary)]/10 px-3 py-1 text-xs font-semibold text-[color:var(--accent-primary)]"><Brain className="h-4 w-4" /> {gradeCopy(safe.score)}</div>
            <p className="mt-5 max-w-3xl text-base leading-7 text-[color:var(--text-secondary)]">Your agents are currently working with {safe.score}% of the institutional knowledge they could have. Improving to 80+ means agents write code that passes review first time.</p>
            <p className="mt-3 text-sm text-[color:var(--text-tertiary)]">{safe.trend ?? `${safe.trend_7d >= 0 ? "+" : ""}${safe.trend_7d} this week`}</p>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          ["Coverage", safe.breakdown.coverage, "How many knowledge domains are documented", `${Math.round(safe.breakdown.coverage * 100)}% of your repos' knowledge is captured in skills`],
          ["Load Frequency", safe.breakdown.load_frequency, "How often agents pull your skills", `${loads} loads this month · target: 1000+`],
          ["Compliance", compliance, "How consistently PRs follow skill guidance", `${Math.round(compliance * 100)}/100 compliance · ${needsWork} skills need improvement`],
          ["Freshness", safe.breakdown.freshness, "% of skills with up-to-date content", `${Math.round(safe.breakdown.freshness * 100)}% fresh · add '## Last verified' dates to improve`],
        ].map(([label, value, description, context]) => (
          <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={label as string}>
            <div className="font-semibold">{label as string} <span className="text-xs text-[color:var(--text-tertiary)]">×{label === "Freshness" ? 15 : label === "Quality" ? 25 : 30}</span></div>
            <p className="mt-1 min-h-10 text-xs text-[color:var(--text-secondary)]">{description as string}</p>
            <div className="mt-4 h-2 rounded-full bg-white/10"><div className="h-2 rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${Math.round(Number(value) * 100)}%` }} /></div>
            <p className="mt-3 text-xs text-[color:var(--text-tertiary)]">{context as string}</p>
            {label === "Load Frequency" && loads < 100 ? <p className="mt-2 text-xs font-semibold text-amber-300">Low agent adoption — check CLAUDE.md setup</p> : null}
          </article>
        ))}
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold">What moves your score</h2>
        <div className="grid gap-4 lg:grid-cols-3">
          {[
            ["Add missing skills", "Skillayer finds missing domains and generates draft skills for review.", "/dashboard/debt?tab=gaps"],
            ["Upload agent loads", "Confirm your agents are connected and sending skill load events.", "/dashboard/connect"],
            ["Refresh stale skills", "Review stale skills and regenerate them with AI before agents rely on outdated guidance.", "/dashboard/debt?tab=stale"],
          ].map(([title, description, href]) => (
            <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={title}>
              <h3 className="font-semibold">{title}</h3>
              <p className="mt-4 min-h-12 rounded-md bg-[color:var(--bg-base)] p-3 text-xs leading-5 text-[color:var(--text-secondary)]">{description}</p>
              <Link className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-[color:var(--accent-primary)]" href={href}>Act now <ArrowUpRight className="h-3.5 w-3.5" /></Link>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        {points.length < 2 ? (
          <div className="text-center"><div className="text-3xl">📊</div><h2 className="mt-3 text-lg font-semibold">Historical trend will appear after your second weekly digest</h2><p className="mt-2 text-sm text-[color:var(--text-secondary)]">Your baseline score has been set at {safe.score}. Come back next week to see progress.</p></div>
        ) : (
          <svg className="h-44 w-full" viewBox="0 0 640 180" preserveAspectRatio="none">{points.slice(-8).map((point, index) => <rect fill="#C9973A" height={Math.max(5, point.discovered * 10)} key={point.week_start} rx="4" width="42" x={index * 78 + 20} y={150 - Math.max(5, point.discovered * 10)} />)}</svg>
        )}
      </section>

      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <h2 className="text-lg font-semibold">Skill Gap Inbox</h2>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">When agents encounter patterns not covered by any skill, they appear here. Requires skilgen watch mode.</p>
        {(queue?.items ?? []).length === 0 ? (
          <div className="mt-6 rounded-lg border border-dashed border-[color:var(--bg-border)] p-6 text-center"><div className="text-3xl">📭</div><h3 className="mt-3 font-semibold">No skill gaps captured yet</h3><p className="mt-2 text-sm text-[color:var(--text-secondary)]">Start skilgen watch mode to automatically detect knowledge gaps as agents work:</p><code className="mt-4 block rounded-md bg-[color:var(--bg-base)] p-3 text-xs text-[color:var(--text-tertiary)]">SKILLAYER_API_KEY=sk-... skilgen watch --repo-id {repoId}</code><p className="mt-3 text-xs text-[color:var(--text-tertiary)]">Each gap is a pattern your agents encountered with no matching skill — prime candidates for your next skilgen deliver run.</p></div>
        ) : (
          <div className="mt-5 grid gap-3">
            {(queue?.items ?? []).map((item) => {
              const href = item.skill_id ? `/dashboard/repos/${item.repo_id}/skills/${item.skill_id}` : `/dashboard/debt?tab=gaps&domain=${encodeURIComponent(item.domain)}`;
              return <Link className="rounded-md border border-[color:var(--bg-border)] p-4 text-sm" href={href} key={item.id}>{item.title} · {item.repo_name} →</Link>;
            })}
          </div>
        )}
      </section>
    </div>
  );
}
