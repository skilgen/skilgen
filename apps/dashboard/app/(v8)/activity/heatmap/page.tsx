import Link from "next/link";
import { redirect } from "next/navigation";

import { ActivityHeader } from "../ActivityNav";
import { SetupReadinessBanner } from "../SetupReadinessBanner";
import { getActivityHeatmap, getActivityRepos, getActivitySetupStatus, loadActivityContext, normalizeSearchParams, type HeatmapCell, type HeatmapModel, type HeatmapTrend } from "../activity-data";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

function cellClass(cell: HeatmapCell | undefined): string {
  if (!cell) return "bg-[#303030] text-[#777]";
  if (cell.risk_band === "high") return "bg-red-500/70 text-white";
  if (cell.risk_band === "medium") return "bg-[#9f6a1d] text-black";
  return "bg-[#7ea7ee] text-black";
}

function compactNumber(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(value >= 10_000_000 ? 0 : 1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(value >= 10_000 ? 0 : 1)}K`;
  return String(value);
}

function formatMoney(value: number | null | undefined): string {
  const safe = Number(value ?? 0);
  return safe > 0 ? `$${safe.toFixed(safe >= 1 ? 2 : 4)}` : "$0.00";
}

function hourLabel(hour: number | null | undefined): string {
  if (hour === null || hour === undefined) return "-";
  if (hour === 0) return "12 AM";
  if (hour < 12) return `${hour} AM`;
  if (hour === 12) return "12 PM";
  return `${hour - 12} PM`;
}

function dayLabel(value: string): string {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(new Date(`${value}T12:00:00`));
}

function heatmapHref(repoId: string, hours: string, view: string, includeDenyRate: string): string {
  const query = new URLSearchParams({ repo_id: repoId, hours, view });
  if (includeDenyRate === "true") query.set("include_deny_rate", "true");
  return `/activity/heatmap?${query.toString()}`;
}

export default async function ActivityHeatmapPage({ searchParams }: { searchParams?: PageSearchParams }) {
  const params = await normalizeSearchParams(searchParams);
  if (!params.has("hours")) {
    redirect("/activity/heatmap?repo_id=all&hours=168&view=overview");
  }
  const context = await loadActivityContext();
  const repos = context.org?.id ? await getActivityRepos(context.accessToken, context.org.id) : [];
  const repoId = params.get("repo_id") || "all";
  const heatmapParams = new URLSearchParams(params);
  heatmapParams.delete("repo_id");
  const payload = context.org?.id ? await getActivityHeatmap(context.accessToken, context.org.id, repoId, heatmapParams) : null;
  const setupStatus = context.org?.id ? await getActivitySetupStatus(context.accessToken, context.org.id) : null;
  const cells = payload?.cells ?? [];
  const rowNames = [...new Map(cells.map((cell) => [cell.repo_id, cell.repo_name])).entries()];
  const hours = Array.from({ length: 24 }, (_, hour) => hour);
  const byCell = new Map(cells.map((cell) => [`${cell.repo_id}:${cell.hour}`, cell]));
  const summary = payload?.summary;
  const models = payload?.models ?? [];
  const trend = payload?.trend ?? [];
  const view = params.get("view") === "models" ? "models" : "overview";
  const selectedHours = params.get("hours") ?? "168";
  const includeDenyRate = params.get("include_deny_rate") ?? "false";
  const actionCount = cells.reduce((sum, cell) => sum + cell.action_count, 0);
  const busiest = cells.reduce<HeatmapCell | null>((current, cell) => (current === null || cell.action_count > current.action_count ? cell : current), null);
  const isPlatformView = payload?.group_by === "platform" || repoId === "all";

  return (
    <div className="space-y-6">
      <ActivityHeader active="heatmap" />
      <SetupReadinessBanner setupStatus={setupStatus} />

      <section className="grid gap-3 md:grid-cols-4">
        <Metric label="Sessions" value={summary?.sessions ?? actionCount} />
        <Metric label="Messages" value={compactNumber(summary?.messages ?? cells.reduce((sum, cell) => sum + (cell.messages ?? cell.action_count), 0))} />
        <Metric label="Total tokens" value={compactNumber(summary?.tokens_total ?? cells.reduce((sum, cell) => sum + (cell.tokens_total ?? 0), 0))} />
        <Metric label="Cost" value={formatMoney(summary?.cost_usd)} />
        <Metric label="Current streak" value={summary?.active_days ? `${summary.active_days}d` : "0d"} />
        <Metric label="Platforms" value={summary?.platforms ?? rowNames.length} />
        <Metric label="Peak hour" value={hourLabel(summary?.peak_hour ?? busiest?.hour)} />
        <Metric label="Favorite model" value={summary?.favorite_model ?? busiest?.favorite_model ?? "-"} />
      </section>

      <form className="grid gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-[minmax(0,1fr)_180px_180px_auto]" method="get">
        <input name="view" type="hidden" value={view} />
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={repoId} name="repo_id">
          <option value="all">All platforms</option>
          {repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.full_name}</option>)}
        </select>
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={selectedHours} name="hours">
          <option value="24">24 hours</option>
          <option value="168">7 days</option>
          <option value="720">30 days</option>
          <option value="2160">All</option>
        </select>
        <select className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" defaultValue={includeDenyRate} name="include_deny_rate">
          <option value="false">Volume</option>
          <option value="true">Deny overlay</option>
        </select>
        <button className="rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" type="submit">Apply</button>
      </form>

      <section className="overflow-x-auto rounded-lg border border-[color:var(--bg-border)] bg-[#262626] p-4">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div className="inline-flex rounded-md bg-[#333] p-1 text-sm">
            <Link className={`rounded px-3 py-1 ${view === "overview" ? "bg-[#444] text-white" : "text-[#aaa] hover:text-white"}`} href={heatmapHref(repoId, selectedHours, "overview", includeDenyRate)}>Overview</Link>
            <Link className={`rounded px-3 py-1 ${view === "models" ? "bg-[#444] text-white" : "text-[#aaa] hover:text-white"}`} href={heatmapHref(repoId, selectedHours, "models", includeDenyRate)}>Models</Link>
          </div>
          <div className="inline-flex rounded-md bg-[#333] p-1 text-sm">
            <Link className={`rounded px-3 py-1 ${selectedHours === "2160" ? "bg-[#444] text-white" : "text-[#aaa] hover:text-white"}`} href={heatmapHref(repoId, "2160", view, includeDenyRate)}>All</Link>
            <Link className={`rounded px-3 py-1 ${selectedHours === "720" ? "bg-[#444] text-white" : "text-[#aaa] hover:text-white"}`} href={heatmapHref(repoId, "720", view, includeDenyRate)}>30d</Link>
            <Link className={`rounded px-3 py-1 ${selectedHours === "168" ? "bg-[#444] text-white" : "text-[#aaa] hover:text-white"}`} href={heatmapHref(repoId, "168", view, includeDenyRate)}>7d</Link>
          </div>
        </div>
        {view === "models" ? (
          <ModelBars models={models} total={models.reduce((sum, model) => sum + model.tokens_total, 0)} />
        ) : isPlatformView && trend.length ? (
          <TrendGrid hours={selectedHours} trend={trend} />
        ) : (
        <div className="grid min-w-[980px] gap-1" style={{ gridTemplateColumns: "180px repeat(24, minmax(30px, 1fr))" }}>
          <div />
          {hours.map((hour) => <div className="py-2 text-center text-[11px] font-semibold text-[color:var(--text-tertiary)]" key={hour}>{hour}</div>)}
          {rowNames.map(([id, name]) => (
            <div className="contents" key={id}>
              <div className="sticky left-0 z-10 truncate bg-[#262626] py-2 pr-3 text-sm font-semibold text-[color:var(--text-primary)]">{name}</div>
              {hours.map((hour) => {
                const cell = byCell.get(`${id}:${hour}`);
                return (
                  <div className={`flex h-8 items-center justify-center rounded text-xs font-semibold ${cellClass(cell)}`} key={`${id}-${hour}`} title={`${name} ${hour}:00 - ${cell?.tokens_total ? compactNumber(cell.tokens_total) + " tokens" : `${cell?.action_count ?? 0} actions`}`}>
                    {cell ? (isPlatformView ? compactNumber(cell.tokens_total ?? cell.action_count) : cell.action_count) : ""}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
        )}
        {rowNames.length === 0 ? (
          <div className="p-8 text-center text-sm text-[color:var(--text-secondary)]">
            <p>No activity was found for the selected window.</p>
            {setupStatus?.next_action_url ? (
              <Link className="mt-3 inline-flex rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-[13px] font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href={setupStatus.next_action_url}>
                {setupStatus.next_step_title ?? "Continue setup"}
              </Link>
            ) : null}
          </div>
        ) : null}
        {summary?.tokens_total ? <p className="mt-4 text-sm text-[#aaa]">Coding agents used {compactNumber(summary.tokens_total)} tokens and {formatMoney(summary.cost_usd)} across {summary.platforms} platform{summary.platforms === 1 ? "" : "s"} in this window.</p> : null}
      </section>
    </div>
  );
}

function TrendGrid({ hours, trend }: { hours: string; trend: HeatmapTrend[] }) {
  const platforms = [...new Set(trend.map((item) => item.platform))];
  const allDates = [...new Set(trend.map((item) => item.date))];
  const activeDates = allDates.filter((date) => trend.some((item) => item.date === date && (item.tokens_total > 0 || item.sessions > 0 || item.messages > 0)));
  const dates = hours === "2160" && activeDates.length ? activeDates : allDates;
  const byCell = new Map(trend.map((item) => [`${item.platform}:${item.date}`, item]));
  const maxTokens = Math.max(...trend.map((item) => item.tokens_total), 1);
  return (
    <div className="grid min-w-[760px] gap-1" style={{ gridTemplateColumns: `180px repeat(${dates.length}, minmax(56px, 1fr))` }}>
      <div />
      {dates.map((date) => <div className="py-2 text-center text-[11px] font-semibold text-[color:var(--text-tertiary)]" key={date}>{dayLabel(date)}</div>)}
      {platforms.map((platform) => (
        <div className="contents" key={platform}>
          <div className="sticky left-0 z-10 truncate bg-[#262626] py-2 pr-3 text-sm font-semibold text-[color:var(--text-primary)]">{platform}</div>
          {dates.map((date) => {
            const cell = byCell.get(`${platform}:${date}`);
            const tokens = cell?.tokens_total ?? 0;
            const intensity = tokens / maxTokens;
            const tone = tokens === 0 ? "bg-[#303030] text-[#777]" : intensity > 0.66 ? "bg-red-500/70 text-white" : intensity > 0.33 ? "bg-[#9f6a1d] text-black" : "bg-[#7ea7ee] text-black";
            return (
              <div className={`flex h-10 items-center justify-center rounded px-1 text-xs font-semibold ${tone}`} key={`${platform}-${date}`} title={`${platform} ${dayLabel(date)} - ${compactNumber(tokens)} tokens, ${cell?.sessions ?? 0} sessions`}>
                {tokens ? compactNumber(tokens) : ""}
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

function ModelBars({ models, total }: { models: HeatmapModel[]; total: number }) {
  const max = Math.max(...(models ?? []).map((model) => model.tokens_total), 1);
  return (
    <div className="min-w-[760px] space-y-4">
      {(models ?? []).map((model) => (
        <div className="grid gap-3 md:grid-cols-[180px_minmax(0,1fr)_220px]" key={`${model.platform}-${model.model}`}>
          <div>
            <div className="text-sm font-semibold text-white">{model.model}</div>
            <div className="text-xs text-[#aaa]">{model.platform}</div>
          </div>
          <div className="h-9 overflow-hidden rounded bg-[#333]">
            <div className="h-full rounded bg-[#4f82df]" style={{ width: `${Math.max(4, (model.tokens_total / max) * 100)}%` }} />
          </div>
          <div className="text-sm text-[#ddd]">
            <span className="font-semibold">{compactNumber(model.tokens_total)}</span>
            <span className="text-[#999]"> · {formatMoney(model.cost_usd)} · {model.sessions} sessions · {total ? Math.round((model.tokens_total / total) * 100) : 0}%</span>
          </div>
        </div>
      ))}
      {models?.length ? null : <div className="p-8 text-center text-sm text-[#aaa]">No model metadata found for this window.</div>}
    </div>
  );
}

function Metric({ label, value, detail }: { label: string; value: number | string; detail?: string }) {
  return (
    <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-[color:var(--text-primary)]">{value}</div>
      {detail ? <div className="mt-1 text-xs text-[color:var(--text-secondary)]">{detail}</div> : null}
    </div>
  );
}
