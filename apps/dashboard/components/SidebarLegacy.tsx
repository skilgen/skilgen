import Image from "next/image";
import { LogOut } from "lucide-react";

import { DashboardNavLink } from "../src/components/dashboard-nav-link";

type IconName =
  | "LayoutDashboard"
  | "GitBranch"
  | "GitFork"
  | "BarChart3"
  | "BarChart2"
  | "Brain"
  | "BookOpen"
  | "Package"
  | "Plug"
  | "Database"
  | "Users2"
  | "ClipboardList"
  | "AlertTriangle"
  | "ShieldAlert"
  | "ScrollText"
  | "Timer"
  | "Trophy"
  | "User"
  | "Settings"
  | "Mail"
  | "History"
  | "Inbox"
  | "ShieldCheck"
  | "Sparkles"
  | "FlaskConical"
  | "Zap";

export type LegacyNavItem = {
  href: string;
  label: string;
  icon: IconName;
  badge?: string;
  badgeVariant?: "label" | "dot";
};

export type LegacyNavGroup = {
  label: string;
  items: LegacyNavItem[];
};

type SidebarLegacyProps = {
  handleSignOut: () => Promise<void>;
  icons: Record<IconName, React.ComponentType<{ className?: string }>>;
  initials: string;
  navGroups: LegacyNavGroup[];
  orgId: string;
  user: {
    email: string;
    firstName: string;
    lastName: string;
  };
};

export function SidebarLegacy({ handleSignOut, icons, initials, navGroups, orgId, user }: SidebarLegacyProps) {
  return (
    <aside className="fixed inset-y-0 left-0 z-50 hidden w-[220px] border-r border-[color:var(--bg-surface)] bg-[color:var(--bg-base)] md:block">
      <div className="px-4 pb-4 pt-5">
        <div className="inline-flex items-center">
          <Image src="/skillayer-logo.png" alt="Skillayer" width={36} height={28} className="object-contain" />
          <span className="ml-2 text-[15px] font-bold tracking-[-0.01em] text-[color:var(--text-primary)]">Skillayer</span>
        </div>
      </div>

      <nav className="mt-3 max-h-[calc(100vh-132px)] overflow-y-auto px-3 pb-3">
        {navGroups.map((group, index) => (
          <div className={index === 0 ? "" : "mt-5"} key={group.label}>
            <div className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">{group.label}</div>
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const Icon = icons[item.icon];

                return (
                  <DashboardNavLink
                    badge={item.badge}
                    badgeVariant={item.badgeVariant}
                    key={item.href}
                    href={item.href}
                    icon={<Icon className="h-4 w-4" />}
                    label={item.label}
                    unreadStorageKey={item.href === "/dashboard/agent-prs" && orgId ? `skillayer.agentPrInbox.unreadCount.${orgId}` : undefined}
                  />
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 border-t border-[color:var(--bg-surface)] p-3">
        <div className="flex items-center gap-3">
          <div className="flex h-[30px] w-[30px] items-center justify-center rounded-full border border-[color:var(--bg-border)] bg-[linear-gradient(135deg,var(--accent-dim),var(--bg-surface))] text-[12px] font-semibold text-[color:var(--accent-primary)]">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <div className="truncate text-[13px] font-medium text-[color:var(--text-primary)]">
              {user.firstName} {user.lastName}
            </div>
            <div className="truncate text-[11px] text-[color:var(--text-tertiary)]">{user.email}</div>
          </div>
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
        </div>
      </div>
    </aside>
  );
}
