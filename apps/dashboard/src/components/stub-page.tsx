import { BookOpen, GitBranch, Package, Settings } from "lucide-react";

type StubPageProps = {
  pageName: "Repos" | "Skills" | "Registry" | "Settings";
};

const icons = {
  Repos: GitBranch,
  Skills: BookOpen,
  Registry: Package,
  Settings,
};

export function StubPage({ pageName }: StubPageProps) {
  const Icon = icons[pageName];

  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <div className="max-w-md rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
        <Icon className="mx-auto mb-3 h-7 w-7 text-[color:var(--bg-border)]" />
        <h1 className="text-[15px] font-medium text-[color:var(--text-secondary)]">{pageName}</h1>
        <p className="mt-2 text-[13px] text-[color:var(--text-tertiary)]">This section is coming soon.</p>
      </div>
    </div>
  );
}
