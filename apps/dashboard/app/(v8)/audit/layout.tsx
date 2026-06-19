import Link from "next/link";

const tabs = [
  { href: "/audit/event-log", label: "Event log" },
  { href: "/audit/agent-compliance", label: "Agent compliance" },
  { href: "/audit/reports", label: "Reports" },
  { href: "/audit/exports", label: "Exports" },
  { href: "/audit/worm-roots", label: "WORM roots" },
  { href: "/audit/evidence-packages", label: "Evidence packages" },
];

export default function AuditLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-4 border-b border-[color:var(--bg-border)] pb-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="text-[12px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Skillayer v8</div>
          <h1 className="mt-2 text-[30px] font-semibold text-[color:var(--text-primary)]">Audit</h1>
        </div>
        <nav className="flex flex-wrap gap-2" aria-label="Audit tabs">
          {tabs.map((tab) => (
            <Link
              className="inline-flex h-9 shrink-0 items-center rounded-md border border-[color:var(--bg-border)] px-3 text-[13px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--accent-primary)]"
              href={tab.href}
              key={tab.href}
            >
              {tab.label}
            </Link>
          ))}
        </nav>
      </div>
      {children}
    </section>
  );
}
