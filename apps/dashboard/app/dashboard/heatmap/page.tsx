import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getMyOrg, getOrgRepos, getOrgSkillHeatmap, type SkillHeatmapSkill } from "../../../lib/data";

function cellColor(score: number | null): string {
  if (score === null) return "#1a1a1a";
  if (score >= 80) return "#1a4a2e";
  if (score >= 60) return "#3d2e00";
  if (score >= 40) return "#3d1a00";
  return "#3d0000";
}

function relative(value: string | null): string {
  if (!value) return "Never";
  const hours = Math.max(1, Math.round((Date.now() - new Date(value).getTime()) / 3600000));
  return hours < 24 ? `${hours} hours ago` : `${Math.round(hours / 24)} days ago`;
}

export default async function HeatmapPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const [heatmap, repos] = org?.id ? await Promise.all([getOrgSkillHeatmap(accessToken, org.id), getOrgRepos(accessToken, org.id)]) : [null, []];
  const skills = heatmap?.skills ?? [];
  const repoList = repos ?? [];
  const domains = [...new Set(skills.map((skill) => skill.domain))].sort((a, b) => {
    const avg = (domain: string) => {
      const values = skills.filter((skill) => skill.domain === domain).map((skill) => skill.score_total);
      return values.reduce((sum, value) => sum + value, 0) / Math.max(1, values.length);
    };
    return avg(b) - avg(a);
  });
  const byCell = new Map(skills.map((skill) => [`${skill.domain}:${skill.repo_id}`, skill]));
  const lastActivity = skills.map((skill) => skill.last_loaded_at).filter(Boolean).sort().at(-1) ?? null;
  const hotspots = [...skills].sort((a, b) => b.score_total - a.score_total).slice(0, 3);
  const coldExisting = skills.filter((skill) => skill.score_total < 40).sort((a, b) => a.score_total - b.score_total);
  const missing = domains.flatMap((domain) => repoList.filter((repo) => !byCell.has(`${domain}:${repo.id}`)).map((repo) => ({ domain, repo_name: repo.name }))).slice(0, 3);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Heatmap</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Where knowledge is hot, cold, missing, or stale across repos and domains.</p>
      </header>

      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-5 py-4 text-sm text-[color:var(--text-secondary)]">
        {heatmap?.summary.total_skills ?? 0} skills across {repoList.length} repos · {heatmap?.summary.stale_but_active ?? 0} stale · Last activity: {relative(lastActivity)}
      </section>

      <section className="overflow-x-auto rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="grid min-w-max gap-2" style={{ gridTemplateColumns: `180px repeat(${repoList.length}, minmax(64px, 1fr))` }}>
          <div />
          {repoList.map((repo) => <div className="truncate px-2 py-2 text-center text-xs font-semibold text-[color:var(--text-tertiary)]" key={repo.id}>{repo.name.slice(0, 12)}</div>)}
          {domains.map((domain) => (
            <div className="contents" key={domain}>
              <div className="sticky left-0 z-10 bg-[color:var(--bg-surface)] px-2 py-3 text-sm font-semibold text-[color:var(--text-primary)]">{domain}</div>
              {repoList.map((repo) => {
                const skill = byCell.get(`${domain}:${repo.id}`) as SkillHeatmapSkill | undefined;
                return (
                  <Link
                    className="group relative flex min-h-12 min-w-16 items-center justify-center rounded-md border border-white/5 text-sm font-semibold text-white"
                    href={skill ? `/dashboard/repos/${repo.id}/skills/${skill.skill_id}` : `/dashboard/repos/${repo.id}`}
                    key={`${domain}-${repo.id}`}
                    style={{ backgroundColor: cellColor(skill?.score_total ?? null) }}
                  >
                    {skill ? <><span>{skill.score_total}</span><span className={`absolute right-2 top-2 h-2 w-2 rounded-full ${skill.is_stale ? "bg-red-400" : "bg-[color:var(--accent-green)]"}`} /></> : "—"}
                    <span className="pointer-events-none absolute left-1/2 top-full z-20 mt-2 hidden w-56 -translate-x-1/2 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] p-3 text-left text-xs font-normal text-[color:var(--text-secondary)] shadow-xl group-hover:block">
                      <b className="block text-[color:var(--text-primary)]">{domain} · {repo.name}</b>
                      {skill ? <>Score {skill.score_total}/100 · {skill.loads_30d} loads<br />View skill →</> : <>Not covered<br />Run skilgen analyse --domain {domain}</>}
                    </span>
                  </Link>
                );
              })}
            </div>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-4 text-xs text-[color:var(--text-secondary)]">
          <span>● Excellent (≥80)</span><span>● Good (60-79)</span><span>● Needs work (40-59)</span><span>● At risk (&lt;40)</span><span>■ Not covered</span>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-xl border border-[color:var(--accent-green)]/35 bg-[color:var(--bg-surface)] p-5">
          <h2 className="text-lg font-semibold text-[color:var(--accent-green)]">Hotspots</h2>
          <div className="mt-4 space-y-3">
            {hotspots.map((skill) => <Link className="block rounded-md bg-[color:var(--bg-base)] p-3 text-sm" href={`/dashboard/repos/${skill.repo_id}/skills/${skill.skill_id}`} key={skill.skill_id}>{skill.domain} · {skill.repo_name} · {skill.score_total}/100</Link>)}
          </div>
        </article>
        <article className="rounded-xl border border-[color:var(--accent-red)]/35 bg-[color:var(--bg-surface)] p-5">
          <h2 className="text-lg font-semibold text-[color:var(--accent-red)]">Cold spots</h2>
          <div className="mt-4 space-y-3">
            {[...missing.map((item) => ({ label: `${item.domain} · ${item.repo_name} · missing`, domain: item.domain })), ...coldExisting.map((skill) => ({ label: `${skill.domain} · ${skill.repo_name} · ${skill.score_total}/100`, domain: skill.domain }))].slice(0, 3).map((item) => <div className="rounded-md bg-[color:var(--bg-base)] p-3 text-sm" key={item.label}>{item.label}<code className="mt-2 block text-xs text-[color:var(--text-tertiary)]">skilgen analyse --domain {item.domain}</code></div>)}
          </div>
        </article>
      </section>
    </div>
  );
}
