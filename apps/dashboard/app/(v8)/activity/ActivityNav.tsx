import Link from "next/link";

const tabs = [
  { href: "/activity/live-feed", label: "Live feed" },
  { href: "/activity/compliance-events", label: "Compliance events" },
  { href: "/activity/sessions", label: "Sessions" },
  { href: "/activity/replay", label: "Replay" },
  { href: "/activity/heatmap", label: "Heatmap" },
] as const;

export function ActivityNav({ active }: { active: "live-feed" | "compliance-events" | "sessions" | "replay" | "heatmap" }) {
  return (
    <div className="border-b border-[color:var(--bg-border)]">
      <nav aria-label="Activity tabs" className="flex flex-wrap gap-1">
        {tabs.map((tab) => {
          const isActive = tab.href.endsWith(active);
          return (
            <Link
              className={`border-b-2 px-3 py-2 text-sm font-semibold ${isActive ? "border-[color:var(--accent-primary)] text-[color:var(--text-primary)]" : "border-transparent text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]"}`}
              href={tab.href}
              key={tab.href}
            >
              {tab.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}

export function ActivityHeader({ active }: { active: "live-feed" | "compliance-events" | "sessions" | "replay" | "heatmap" }) {
  return (
    <header className="space-y-4">
      <div>
        <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Governance plane</div>
        <h1 className="mt-2 text-3xl font-semibold text-[color:var(--text-primary)]">Activity</h1>
      </div>
      <ActivityNav active={active} />
    </header>
  );
}
