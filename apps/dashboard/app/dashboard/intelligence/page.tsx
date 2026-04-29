import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getIntelligenceInsights, getMyOrg, getOrgIntelligence, getOrgSkillHeatmap } from "../../../lib/data";

function tone(type: string): string {
  if (type === "anomaly") return "border-[color:var(--accent-red)]/40 bg-[color:var(--accent-red)]/10";
  if (type === "opportunity") return "border-[color:var(--accent-primary)]/40 bg-[color:var(--accent-primary)]/10";
  if (type === "trend") return "border-sky-500/40 bg-sky-500/10";
  return "border-amber-500/40 bg-amber-500/10";
}

function icon(type: string): string {
  return type === "anomaly" ? "🚨" : type === "opportunity" ? "💡" : type === "trend" ? "📈" : "⚠️";
}

function ringColor(score: number): string {
  if (score >= 70) return "#22c55e";
  if (score >= 40) return "#f59e0b";
  return "#ef4444";
}

function RepoRing({ score }: { score: number }) {
  const radius = 26;
  const c = 2 * Math.PI * radius;
  return (
    <svg className="h-16 w-16 -rotate-90" viewBox="0 0 70 70">
      <circle cx="35" cy="35" fill="none" r={radius} stroke="rgba(255,255,255,.1)" strokeWidth="7" />
      <circle cx="35" cy="35" fill="none" r={radius} stroke={ringColor(score)} strokeDasharray={c} strokeDashoffset={c - (Math.max(0, Math.min(100, score)) / 100) * c} strokeLinecap="round" strokeWidth="7" />
      <text className="rotate-90 fill-[color:var(--text-primary)] text-sm font-semibold" textAnchor="middle" x="35" y="-31">{score}</text>
    </svg>
  );
}

export default async function IntelligencePage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const [insights, intelligence, heatmap] = org?.id ? await Promise.all([getIntelligenceInsights(accessToken, org.id), getOrgIntelligence(accessToken, org.id), getOrgSkillHeatmap(accessToken, org.id)]) : [[], null, null];
  const skills = heatmap?.skills ?? [];
  const maxLoads = Math.max(1, ...skills.map((skill) => skill.loads_30d));
  const always = skills.filter((skill) => skill.loads_30d >= maxLoads * 0.8).slice(0, 5);
  const sometimes = skills.filter((skill) => skill.loads_30d > 0 && skill.loads_30d < maxLoads * 0.8).slice(0, 5);
  const never = skills.filter((skill) => skill.loads_30d === 0).slice(0, 5);

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Intelligence</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Proactive insights about how your agents are using your institutional knowledge.</p>
      </header>

      <section>
        <h2 className="mb-4 text-lg font-semibold">This week's top insights</h2>
        {(insights ?? []).length === 0 ? (
          <div className="rounded-xl border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 p-8 text-center text-[color:var(--accent-green)]">✓ No anomalies detected this week — your org is running smoothly.</div>
        ) : (
          <div className="flex gap-4 overflow-x-auto pb-2">
            {(insights ?? []).slice(0, 6).map((item) => (
              <article className={`min-w-[320px] rounded-xl border p-5 ${tone(item.type)}`} key={`${item.type}-${item.title}`}>
                <div className="text-2xl">{icon(item.type)}</div>
                <h3 className="mt-3 font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">{item.description}</p>
                {item.cta_url ? <Link className="mt-4 inline-flex text-sm font-semibold text-[color:var(--accent-primary)]" href={item.cta_url}>{item.cta_label ?? "Open"} →</Link> : null}
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        {[["Always loaded", always], ["Sometimes loaded", sometimes], ["Never loaded", never]].map(([label, items]) => (
          <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={label as string}>
            <h2 className="font-semibold">{label as string}</h2>
            <div className="mt-4 space-y-3">
              {(items as typeof skills).map((skill) => (
                <div key={skill.skill_id}>
                  <div className="mb-1 flex justify-between text-xs"><span>{skill.domain}</span><span>{skill.loads_30d}</span></div>
                  <div className="h-2 rounded-full bg-white/10"><div className="h-2 rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${Math.max(4, (skill.loads_30d / maxLoads) * 100)}%` }} /></div>
                </div>
              ))}
            </div>
          </article>
        ))}
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold">Repo health at a glance</h2>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {(intelligence?.repos ?? []).map((repo) => (
            <Link className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5 text-center hover:border-[color:var(--accent-primary)]" href={`/dashboard/repos/${repo.id}`} key={repo.id}>
              <div className="flex justify-center"><RepoRing score={repo.score} /></div>
              <h3 className="mt-3 truncate font-semibold">{repo.name}</h3>
              <p className="mt-1 text-xs text-[color:var(--text-secondary)]">{repo.skill_count} skills · last loaded {repo.last_analysed_at ? new Date(repo.last_analysed_at).toLocaleDateString() : "never"}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
