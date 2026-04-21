import { BarChart2, BookOpen, GitBranch, Zap } from "lucide-react";

import type { OrgStats } from "@skillayer/types";

type OverviewMetricCardsProps = {
  stats: OrgStats | null;
};

const metricCards = [
  {
    title: "Repos monitored",
    icon: GitBranch,
    context: "Connected repos",
    getValue: (stats: OrgStats) => String(stats.repoCount),
    delta: "↑ +12 this week",
  },
  {
    title: "Avg Skilgen Score",
    icon: BarChart2,
    context: "Org readiness",
    getValue: (stats: OrgStats) => `${stats.avgScore}/100`,
    delta: "↑ +4 this week",
  },
  {
    title: "Skills generated",
    icon: BookOpen,
    context: "Published skills",
    getValue: (stats: OrgStats) => String(stats.skillCount),
    delta: "↑ +28 this week",
  },
  {
    title: "Active agents",
    icon: Zap,
    context: "Live sessions",
    getValue: (stats: OrgStats) => String(stats.activeAgentSessions),
    delta: "↑ +3 this week",
  },
];

export function OverviewMetricCards({ stats }: OverviewMetricCardsProps) {
  return (
    <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {metricCards.map((metric) => {
        const Icon = metric.icon;
        const value = stats ? metric.getValue(stats) : null;

        return (
          <article
            key={metric.title}
            className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5 transition-colors hover:border-[color:var(--bg-hover)]"
          >
            <div className="mb-3 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{metric.title}</div>
            <div className="flex items-baseline gap-2">
              <div
                className={
                  value
                    ? "text-[28px] font-bold leading-none text-[color:var(--text-primary)]"
                    : "text-[28px] font-bold leading-none text-[color:var(--bg-border)]"
                }
              >
                {value ?? "—"}
              </div>
            </div>

            {value ? (
              <div className="mt-3 inline-flex rounded-full bg-[rgb(var(--accent-green-rgb)/0.1)] px-2 py-0.5 text-[12px] text-[color:var(--accent-green)]">
                {metric.delta}
              </div>
            ) : null}

            <div className="mt-4 flex items-center gap-2 border-t border-[color:var(--bg-elevated)] pt-3 text-[12px] text-[color:var(--text-tertiary)]">
              <Icon className={value ? "h-3.5 w-3.5 text-[color:var(--accent-primary)]" : "h-3.5 w-3.5"} />
              <span>{metric.context}</span>
            </div>
          </article>
        );
      })}
    </div>
  );
}
