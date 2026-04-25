import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getDependencyGraph, getMyOrg } from "../../../../lib/data";

export const dynamic = "force-dynamic";

export default async function DependencyGraphPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Dependency graph auth unavailable:", error);
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const graph = org?.id ? await getDependencyGraph(accessToken, org.id) : null;
  const nodes = graph?.nodes ?? [];
  const edges = graph?.edges ?? [];
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Cross-Repo Skill Dependencies</h1>
          <p className="mt-2 text-[15px] text-[color:var(--text-secondary)]">Map which skills depend on upstream knowledge across repositories.</p>
        </div>
        <button className="rounded-full bg-[color:var(--accent-primary)] px-5 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)]" type="button">Scan for Dependencies</button>
      </div>
      {(graph?.stale_upstream_count ?? 0) > 0 ? <div className="rounded-xl border border-[#f59e0b]/30 bg-[#f59e0b]/10 p-4 text-[13px] text-[#f59e0b]">⚠ {graph?.stale_upstream_count} upstream skills are stale — downstream consumers may receive outdated context.</div> : null}
      <section className="relative min-h-[480px] overflow-hidden rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <svg className="absolute inset-0 h-full w-full">
          {edges.map((edge, index) => {
            const sourceIndex = Math.max(0, nodes.findIndex((node) => node.skill_id === edge.source_skill_id));
            const x1 = 100 + (sourceIndex % 4) * 190;
            const y1 = 90 + Math.floor(sourceIndex / 4) * 120;
            const x2 = 180 + (index % 4) * 180;
            const y2 = 160 + Math.floor(index / 4) * 110;
            return <line key={`${edge.source_skill_id}-${edge.target_entry_id}`} stroke="rgba(255,255,255,0.22)" strokeWidth="1.5" x1={x1} x2={x2} y1={y1} y2={y2} />;
          })}
        </svg>
        {nodes.length === 0 ? <div className="relative z-10 flex min-h-[420px] items-center justify-center text-[13px] text-[color:var(--text-secondary)]">No dependencies detected yet.</div> : null}
        {nodes.map((node, index) => {
          const left = 70 + (index % 4) * 190;
          const top = 60 + Math.floor(index / 4) * 120;
          const healthy = (node.score_total ?? 0) >= 70;
          return (
            <div className={`absolute z-10 w-[150px] rounded-xl border bg-[color:var(--bg-base)] p-3 ${healthy ? "border-[color:var(--accent-green)]" : "border-[#ef4444]"}`} key={node.skill_id} style={{ left, top }}>
              <div className="truncate text-[13px] font-semibold text-[color:var(--text-primary)]">{node.domain}</div>
              <div className="mt-1 truncate text-[11px] text-[color:var(--text-tertiary)]">{node.repo_name}</div>
            </div>
          );
        })}
      </section>
      <details className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <summary className="cursor-pointer text-[13px] font-semibold text-[color:var(--text-primary)]">Orphan Skills — no downstream consumers</summary>
        <p className="mt-3 text-[13px] text-[color:var(--text-secondary)]">Dependency scans will list isolated skills here as the graph fills in.</p>
      </details>
    </div>
  );
}
