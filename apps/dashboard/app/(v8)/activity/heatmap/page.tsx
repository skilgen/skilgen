import { ActivityHeader } from "../ActivityNav";
import { getActivityHeatmap, getActivityRepos, loadActivityContext, normalizeSearchParams, type HeatmapCell } from "../activity-data";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

function cellClass(cell: HeatmapCell | undefined): string {
  if (!cell) return "bg-[color:var(--bg-base)] text-[color:var(--text-tertiary)]";
  if (cell.risk_band === "high") return "bg-red-500/70 text-white";
  if (cell.risk_band === "medium") return "bg-amber-500/60 text-black";
  return "bg-[color:var(--accent-green)]/55 text-white";
}

export default async function ActivityHeatmapPage({ searchParams }: { searchParams?: PageSearchParams }) {
  const params = await normalizeSearchParams(searchParams);
  if (!params.has("hours")) params.set("hours", "168");
  const context = await loadActivityContext();
  const repos = context.org?.id ? await getActivityRepos(context.accessToken, context.org.id) : [];
  const repoId = params.get("repo_id") || "all";
  const heatmapParams = new URLSearchParams(params);
  heatmapParams.delete("repo_id");
  const payload = context.org?.id ? await getActivityHeatmap(context.accessToken, context.org.id, repoId, heatmapParams) : null;
  const cells = payload?.cells ?? [];
  const repoNames = [...new Map(cells.map((cell) => [cell.repo_id, cell.repo_name])).entries()];
  const hours = Array.from({ length: 24 }, (_, hour) => hour);
  const byCell = new Map(cells.map((cell) => [`${cell.repo_id}:${cell.hour}`, cell]));

  return (
    <div className="space-y-6">
      <ActivityHeader active="heatmap" />

      <form className="grid gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-[minmax(0,1fr)_180px_180px_auto]" method="get">
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={repoId} name="repo_id">
          <option value="all">All repos</option>
          {repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.full_name}</option>)}
        </select>
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("hours") ?? "168"} name="hours">
          <option value="24">24 hours</option>
          <option value="168">7 days</option>
          <option value="720">30 days</option>
        </select>
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={params.get("include_deny_rate") ?? "false"} name="include_deny_rate">
          <option value="false">Volume</option>
          <option value="true">Deny overlay</option>
        </select>
        <button className="rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" type="submit">Apply</button>
      </form>

      <section className="overflow-x-auto rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="grid min-w-[980px] gap-1" style={{ gridTemplateColumns: "180px repeat(24, minmax(30px, 1fr))" }}>
          <div />
          {hours.map((hour) => <div className="py-2 text-center text-[11px] font-semibold text-[color:var(--text-tertiary)]" key={hour}>{hour}</div>)}
          {repoNames.map(([id, name]) => (
            <div className="contents" key={id}>
              <div className="sticky left-0 z-10 truncate bg-[color:var(--bg-surface)] py-2 pr-3 text-sm font-semibold text-[color:var(--text-primary)]">{name}</div>
              {hours.map((hour) => {
                const cell = byCell.get(`${id}:${hour}`);
                return (
                  <div className={`flex h-8 items-center justify-center rounded text-xs font-semibold ${cellClass(cell)}`} key={`${id}-${hour}`} title={`${name} ${hour}:00 - ${cell?.action_count ?? 0} actions`}>
                    {cell?.action_count ?? 0}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
        {repoNames.length === 0 ? <div className="p-8 text-center text-sm text-[color:var(--text-secondary)]">No activity was found for the selected window.</div> : null}
      </section>
    </div>
  );
}
