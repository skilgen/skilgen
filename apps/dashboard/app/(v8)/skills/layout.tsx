import Link from "next/link";

const tabs = [
  { href: "/skills/registry", label: "Registry" },
  { href: "/skills/score", label: "Score" },
  { href: "/skills/drift", label: "Drift" },
  { href: "/skills/provenance", label: "Provenance" },
  { href: "/skills/skillql", label: "SkillQL" },
  { href: "/skills/repos", label: "Repos" },
] as const;

export default function SkillsLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-[12px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Skillayer v8</div>
        <h1 className="mt-2 text-3xl font-semibold text-[color:var(--text-primary)]">Skills</h1>
      </div>

      <nav className="flex gap-2 overflow-x-auto border-b border-[color:var(--bg-border)] pb-2" aria-label="Skills tabs">
        {tabs.map((tab) => (
          <Link
            className="inline-flex shrink-0 rounded-md px-3 py-1.5 text-[13px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:bg-[color:var(--bg-surface)] hover:text-[color:var(--text-primary)]"
            href={tab.href}
            key={tab.href}
          >
            {tab.label}
          </Link>
        ))}
      </nav>

      {children}
    </div>
  );
}
