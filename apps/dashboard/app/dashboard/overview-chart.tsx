"use client";

import { useMemo, useState } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { OverviewScoreTrendPoint } from "../../lib/data";

type ChartPoint = OverviewScoreTrendPoint & { index: number };

function tooltipLabel(point: ChartPoint | undefined): string {
  if (!point) return "";
  const direction = point.delta > 0 ? "+" : "";
  return `${point.week} · ${point.score}/100 (${direction}${point.delta})`;
}

function CustomTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: ChartPoint }> }) {
  if (!active || !payload?.length) return null;
  const point = payload[0]?.payload;
  return (
    <div className="max-w-[280px] rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] p-3 shadow-2xl">
      <div className="text-sm font-semibold text-[color:var(--text-primary)]">{tooltipLabel(point)}</div>
      <div className="mt-1 text-xs text-[color:var(--text-secondary)]">{point.repos_changed} repos changed this week</div>
      {point.events.length ? (
        <div className="mt-3 space-y-1">
          {point.events.slice(0, 3).map((event) => (
            <div className="flex items-center justify-between gap-4 text-xs" key={`${event.repo_id}-${event.date}`}>
              <span className="truncate text-[color:var(--text-secondary)]">{event.repo_name}</span>
              <span className="font-semibold text-[color:var(--accent-primary)]">{event.score}/100</span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export function OverviewChart({ points }: { points: OverviewScoreTrendPoint[] }) {
  const data = useMemo<ChartPoint[]>(() => points.map((point, index) => ({ ...point, index })), [points]);
  const [range, setRange] = useState<{ from: number; to: number } | null>(null);
  const [dragStart, setDragStart] = useState<number | null>(null);
  const [selected, setSelected] = useState<ChartPoint | null>(null);
  const visible = range ? data.slice(range.from, range.to + 1) : data;
  const rotateTicks = visible.length > 8;

  function zoomTo(endIndex: number | null) {
    if (dragStart === null || endIndex === null || dragStart === endIndex) {
      setDragStart(null);
      return;
    }
    const from = Math.max(0, Math.min(dragStart, endIndex));
    const to = Math.min(data.length - 1, Math.max(dragStart, endIndex));
    setRange({ from, to });
    setDragStart(null);
  }

  return (
    <section className="relative rounded-[28px] border border-[color:var(--bg-border)] bg-[radial-gradient(circle_at_top,rgba(201,151,58,0.18),rgba(16,16,24,0.96)_50%)] p-6">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Score Trend</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Drag across the chart to zoom. Click a point to inspect what moved the score.</p>
        </div>
        {range ? (
          <button className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs font-semibold text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" onClick={() => setRange(null)} type="button">
            Reset zoom
          </button>
        ) : null}
      </div>

      <div className="h-[280px]">
        <ResponsiveContainer height="100%" width="100%">
          <ComposedChart
            data={visible}
            margin={{ top: 10, right: 18, bottom: rotateTicks ? 42 : 18, left: -10 }}
            onClick={(state) => {
              const payload = (state as unknown as { activePayload?: Array<{ payload?: ChartPoint }> })?.activePayload?.[0]?.payload;
              if (payload) setSelected(payload);
            }}
            onMouseDown={(state) => setDragStart(typeof state?.activeTooltipIndex === "number" ? data.indexOf(visible[state.activeTooltipIndex]) : null)}
            onMouseUp={(state) => zoomTo(typeof state?.activeTooltipIndex === "number" ? data.indexOf(visible[state.activeTooltipIndex]) : null)}
          >
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis
              angle={rotateTicks ? -45 : 0}
              dataKey="week"
              height={rotateTicks ? 56 : 28}
              interval={0}
              stroke="rgba(238,238,245,0.45)"
              textAnchor={rotateTicks ? "end" : "middle"}
              tick={{ fontSize: 11 }}
            />
            <YAxis domain={[0, 100]} stroke="rgba(238,238,245,0.45)" tick={{ fontSize: 11 }} ticks={[0, 25, 50, 75, 100]} />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine label={{ value: "70 target", fill: "#f59e0b", fontSize: 11 }} stroke="#f59e0b" strokeDasharray="6 6" y={70} />
            <Area dataKey="score" fill="#C9973A" fillOpacity={0.1} stroke="none" type="monotone" />
            <Line
              activeDot={{ r: 6 }}
              dataKey="score"
              dot={{ r: 3, fill: "#C9973A" }}
              stroke="#C9973A"
              strokeWidth={2}
              type="monotone"
            />
            {dragStart !== null ? <ReferenceArea fill="#C9973A" fillOpacity={0.12} x1={data[dragStart]?.week} x2={visible[visible.length - 1]?.week} /> : null}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {selected ? (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-[420px] border-l border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-6 shadow-2xl">
          <button className="mb-6 text-sm text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]" onClick={() => setSelected(null)} type="button">
            Close
          </button>
          <h3 className="text-xl font-semibold text-[color:var(--text-primary)]">Week of {selected.date}</h3>
          <p className="mt-2 text-sm text-[color:var(--text-secondary)]">
            Score {selected.score}/100 · {selected.delta >= 0 ? "+" : ""}
            {selected.delta} from prior week
          </p>
          <div className="mt-6 space-y-3">
            {selected.events.length ? selected.events.map((event) => (
              <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3" key={`${event.repo_id}-${event.date}`}>
                <div className="font-semibold text-[color:var(--text-primary)]">{event.repo_name}</div>
                <div className="mt-1 text-sm text-[color:var(--text-secondary)]">Recorded score {event.score}/100</div>
              </article>
            )) : (
              <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 text-sm text-[color:var(--text-secondary)]">
                No individual score events were recorded this week.
              </div>
            )}
          </div>
        </div>
      ) : null}
    </section>
  );
}
