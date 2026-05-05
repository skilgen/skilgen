import Image from "next/image";
import Link from "next/link";
import {
  Activity,
  BarChart3,
  BookOpen,
  LogOut,
  ScrollText,
  Settings,
  ShieldCheck,
} from "lucide-react";

import { DashboardNavLink } from "../src/components/dashboard-nav-link";

export const v8NavItems = [
  { href: "/activity", label: "Activity", icon: Activity },
  { href: "/policy", label: "Policy", icon: ShieldCheck },
  { href: "/audit", label: "Audit", icon: ScrollText },
  { href: "/skills", label: "Skills", icon: BookOpen },
  { href: "/insights", label: "Insights", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
] as const;

type SidebarV8Props = {
  handleSignOut?: () => Promise<void>;
  initials?: string;
  user?: {
    email: string;
    firstName: string;
    lastName: string;
  };
};

export function SidebarV8({ handleSignOut, initials = "SU", user }: SidebarV8Props) {
  return (
    <aside className="fixed inset-y-0 left-0 z-50 hidden w-[220px] border-r border-[color:var(--bg-surface)] bg-[color:var(--bg-base)] md:block">
      <div className="px-4 pb-4 pt-5">
        <Link className="inline-flex items-center" href="/activity">
          <Image src="/skillayer-logo.png" alt="Skillayer" width={36} height={28} className="object-contain" />
          <span className="ml-2 text-[15px] font-bold tracking-[-0.01em] text-[color:var(--text-primary)]">Skillayer</span>
        </Link>
      </div>

      <nav className="mt-3 max-h-[calc(100vh-132px)] overflow-y-auto px-3 pb-3" aria-label="v8 primary navigation">
        <div>
          <div className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">GOVERNANCE</div>
          <div className="space-y-0.5">
            {v8NavItems.map((item) => (
              <DashboardNavLink key={item.href} href={item.href} icon={<item.icon className="h-4 w-4" />} label={item.label} />
            ))}
          </div>
        </div>
      </nav>

      <div className="absolute bottom-0 left-0 right-0 border-t border-[color:var(--bg-surface)] p-3">
        <div className="flex items-center gap-3">
          <div className="flex h-[30px] w-[30px] items-center justify-center rounded-full border border-[color:var(--bg-border)] bg-[linear-gradient(135deg,var(--accent-dim),var(--bg-surface))] text-[12px] font-semibold text-[color:var(--accent-primary)]">
            {initials}
          </div>
          {user ? (
            <div className="min-w-0 flex-1">
              <div className="truncate text-[13px] font-medium text-[color:var(--text-primary)]">
                {user.firstName} {user.lastName}
              </div>
              <div className="truncate text-[11px] text-[color:var(--text-tertiary)]">{user.email}</div>
            </div>
          ) : null}
          {handleSignOut ? (
            <form action={handleSignOut}>
              <button
                aria-label="Sign out"
                className="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-md text-[color:var(--text-tertiary)] transition-colors hover:bg-[color:var(--bg-surface)] hover:text-[color:var(--accent-red)]"
                title="Sign out"
                type="submit"
              >
                <LogOut className="h-[15px] w-[15px]" />
              </button>
            </form>
          ) : null}
        </div>
      </div>
    </aside>
  );
}

export function V8MobileNav() {
  return (
    <nav className="sticky top-[52px] z-30 border-b border-[color:var(--bg-surface)] bg-[color:var(--bg-base)] px-3 py-2 md:hidden">
      <div className="flex gap-2 overflow-x-auto pb-1">
        {v8NavItems.map((item) => (
          <Link
            className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-1.5 text-xs font-semibold text-[color:var(--text-secondary)]"
            href={item.href}
            key={`mobile-${item.href}`}
          >
            <item.icon className="h-3.5 w-3.5" />
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}

export function V8PlaceholderPage({ surface }: { surface: string }) {
  return (
    <section className="mx-auto flex min-h-[calc(100vh-140px)] max-w-5xl flex-col justify-center">
      <div className="text-[12px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Skillayer v8</div>
      <h1 className="mt-3 text-3xl font-semibold text-[color:var(--text-primary)]">{surface}</h1>
      <p className="mt-4 text-[15px] text-[color:var(--text-secondary)]">Coming soon — v8 surface</p>
    </section>
  );
}
