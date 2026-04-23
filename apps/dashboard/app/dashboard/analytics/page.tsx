import { withAuth } from "@workos-inc/authkit-nextjs";

import { SectionFallback } from "@/components/section-fallback";
import { getMyOrg, getOrgAnalytics, type AnalyticsSkill, type OrgAnalytics } from "../../../lib/data";

export const dynamic = "force-dynamic";

function MetricPanel({ label, value, sub }: { label: string; value: string | number; sub: string }) {
  return (
    <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
      <div className="text-[28px] font-bold leading-none text-[color:var(--text-primary)]">{value}</div>
      <div className="mt-4 border-t border-[color:var(--bg-elevated)] pt-3 text-[12px] text-[color:var(--text-tertiary)]">{sub}</div>
    </article>
  );
}

function Sparkline({ points }: { points: OrgAnalytics["daily_loads"] }) {
  const width = 600;
  const height = 120;
  const maxLoads = Math.max(1, ...points.map((point) => point.loads));
  const coordinates = points.map((point, index) => {
    const x = points.length <= 1 ? 0 : (index / (points.length - 1)) * width;
    const y = height - (point.loads / maxLoads) * height;
    return `${x},${y}`;
  });

  return (
    <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-4">
        <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">30-day activity</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Daily skill loads recorded by connected agents.</p>
      </div>
      <svg aria-label="30-day skill usage sparkline" className="h-[120px] w-full" preserveAspectRatio="none" viewBox={`0 0 ${width} ${height}`}>
        <polyline fill="none" points={coordinates.join(" ")} stroke="#C9973A" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
      </svg>
    </section>
  );
}

function TopSkillsChart({ skills }: { skills: AnalyticsSkill[] }) {
  const maxLoads = Math.max(1, ...skills.map((skill) => skill.loads ?? 0));
  return (
    <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-5">
        <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Top skills</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Most loaded skills in the last 30 days.</p>
      </div>
      <div className="space-y-4">
        {skills.length === 0 ? (
          <div className="rounded-lg border border-dashed border-[color:var(--bg-border)] p-6 text-[13px] text-[color:var(--text-secondary)]">No skill loads recorded yet.</div>
        ) : (
          skills.map((skill) => {
            const loads = skill.loads ?? 0;
            const width = `${Math.max(4, (loads / maxLoads) * 100)}%`;
            return (
              <div key={skill.id}>
                <div className="mb-1 flex items-center justify-between gap-4 text-[13px]">
                  <div className="min-w-0">
                    <div className="truncate font-medium text-[color:var(--text-primary)]">{skill.domain}</div>
                    <div className="truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{skill.repo_full_name}</div>
                  </div>
                  <span className="font-semibold text-[color:var(--accent-primary)]">{loads}</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white/10">
                  <div className="h-full rounded-full bg-[#C9973A]" style={{ width }} />
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}

function NeverLoadedList({ skills }: { skills: AnalyticsSkill[] }) {
  return (
    <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-5">
        <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Never loaded</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Skills that have not been used by agents in the current 30-day window.</p>
      </div>
      <div className="space-y-3">
        {skills.length === 0 ? (
          <div className="rounded-lg border border-dashed border-[color:var(--bg-border)] p-6 text-[13px] text-[color:var(--text-secondary)]">Every tracked skill has usage.</div>
        ) : (
          skills.slice(0, 10).map((skill) => (
            <div className="flex items-center justify-between gap-3 rounded-lg border border-[color:var(--bg-border)] px-3 py-2" key={skill.id}>
              <div className="min-w-0">
                <div className="truncate text-[13px] font-medium text-[color:var(--text-primary)]">{skill.domain}</div>
                <div className="truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{skill.skill_path}</div>
              </div>
              <span className="shrink-0 rounded-full bg-red-900/30 px-2 py-0.5 text-[11px] font-semibold text-red-400">No loads</span>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

export default async function AnalyticsPage() {
  let analytics: OrgAnalytics | null = null;
  try {
    const session = await withAuth({ ensureSignedIn: true });
    const accessToken = session.accessToken || "";
    const org = await getMyOrg(accessToken);
    if (org) {
      analytics = await getOrgAnalytics(accessToken, org.id);
    }
  } catch (error) {
    console.error("Unable to load analytics:", error);
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Analytics</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Skill usage, agent activity, and adoption gaps.</p>
      </div>

      {analytics ? (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <MetricPanel label="Total loads" value={analytics.total_loads_30d} sub="Last 30 days" />
            <MetricPanel label="Most active repo" value={analytics.most_active_repo?.name ?? "-"} sub={`${analytics.most_active_repo?.loads ?? 0} loads`} />
            <MetricPanel label="Most loaded skill" value={analytics.most_loaded_skill?.domain ?? "-"} sub={`${analytics.most_loaded_skill?.loads ?? 0} loads`} />
          </div>
          <Sparkline points={analytics.daily_loads} />
          <div className="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(320px,0.75fr)]">
            <TopSkillsChart skills={analytics.top_skills} />
            <NeverLoadedList skills={analytics.never_loaded} />
          </div>
        </div>
      ) : (
        <SectionFallback section="analytics" />
      )}
    </div>
  );
}
