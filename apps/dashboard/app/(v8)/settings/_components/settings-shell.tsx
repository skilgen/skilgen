import Link from "next/link";
import { Bell, Building2, CreditCard, ListChecks, LockKeyhole, Plug, ShieldCheck } from "lucide-react";

const tabs = [
  { href: "/settings/teams", label: "Teams", icon: Building2 },
  { href: "/settings/rbac", label: "RBAC", icon: LockKeyhole },
  { href: "/settings/sso", label: "SSO", icon: ShieldCheck },
  { href: "/settings/connectors", label: "Connectors", icon: Plug },
  { href: "/settings/admin-audit", label: "Admin audit", icon: ListChecks },
  { href: "/settings/billing", label: "Billing", icon: CreditCard },
  { href: "/settings/notifications", label: "Notifications", icon: Bell },
] as const;

export function SettingsShell({ active, children }: { active: string; children: React.ReactNode }) {
  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Skillayer v8</div>
          <h1 className="mt-2 text-2xl font-semibold text-[color:var(--text-primary)]">Settings</h1>
          <p className="mt-1 max-w-3xl text-sm text-[color:var(--text-secondary)]">Access, integrations, notifications, and commercial configuration for the governance plane.</p>
        </div>
      </header>

      <nav className="flex gap-2 overflow-x-auto border-b border-[color:var(--bg-border)] pb-2" aria-label="Settings sections">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = active === tab.label;
          return (
            <Link
              className={
                isActive
                  ? "inline-flex h-9 shrink-0 items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 text-[13px] font-semibold text-[color:var(--bg-base)]"
                  : "inline-flex h-9 shrink-0 items-center gap-2 rounded-md px-3 text-[13px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:bg-[color:var(--bg-surface)] hover:text-[color:var(--text-primary)]"
              }
              href={tab.href}
              key={tab.href}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </Link>
          );
        })}
      </nav>

      {children}
    </div>
  );
}

export function Metric({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-2 text-[24px] font-semibold text-[color:var(--text-primary)]">{value}</div>
      {sub ? <div className="mt-2 text-[12px] text-[color:var(--text-secondary)]">{sub}</div> : null}
    </div>
  );
}

export function EmptyPanel({ title, detail, icon }: { title: string; detail: string; icon?: React.ReactNode }) {
  return (
    <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center">
      {icon ? <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-[color:var(--bg-base)] text-[color:var(--text-tertiary)]">{icon}</div> : null}
      <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">{title}</h2>
      <p className="mx-auto mt-2 max-w-2xl text-sm text-[color:var(--text-secondary)]">{detail}</p>
    </section>
  );
}
