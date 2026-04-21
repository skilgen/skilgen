import Image from "next/image";
import {
  Bell,
  BookOpen,
  Building2,
  ChevronDown,
  GitBranch,
  LayoutDashboard,
  LogOut,
  Package,
  Plus,
  Settings,
} from "lucide-react";
import { signOut } from "@workos-inc/authkit-nextjs";
import { redirect } from "next/navigation";

import { dashboardNavItems, mockOrg, mockUser } from "@/lib/mock-data";
import { DashboardNavLink } from "@/components/dashboard-nav-link";

async function handleSignOut() {
  "use server";

  const isWorkOSConfigured = Boolean(
    process.env.WORKOS_API_KEY &&
      process.env.WORKOS_CLIENT_ID &&
      process.env.WORKOS_COOKIE_PASSWORD &&
      process.env.WORKOS_COOKIE_PASSWORD.length >= 32 &&
      (process.env.NEXT_PUBLIC_WORKOS_REDIRECT_URI ?? process.env.WORKOS_REDIRECT_URI),
  );

  if (!isWorkOSConfigured) {
    redirect("/dashboard");
  }

  await signOut();
}

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const icons = {
    LayoutDashboard,
    GitBranch,
    BookOpen,
    Package,
    Settings,
  };
  const workspaceItems = dashboardNavItems.filter((item) => item.href !== "/dashboard/settings");
  const accountItems = dashboardNavItems.filter((item) => item.href === "/dashboard/settings");
  const initials = `${mockUser.firstName[0]}${mockUser.lastName[0]}`;

  return (
    <div className="min-h-screen bg-[color:var(--bg-base)] text-[color:var(--text-primary)]">
      <aside className="fixed inset-y-0 left-0 z-50 w-[220px] border-r border-[color:var(--bg-surface)] bg-[color:var(--bg-base)]">
        <div className="px-4 pb-4 pt-5">
          <div className="inline-flex items-center">
            <Image src="/skillayer-logo.png" alt="Skillayer" width={36} height={28} className="object-contain" />
            <span className="ml-2 text-[15px] font-bold tracking-[-0.01em] text-[color:var(--text-primary)]">Skillayer</span>
          </div>
        </div>

        <nav className="mt-6 px-3">
          <div className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">WORKSPACE</div>
          <div className="space-y-0.5">
            {workspaceItems.map((item) => {
              const Icon = icons[item.icon];

              return <DashboardNavLink key={item.href} href={item.href} icon={<Icon className="h-4 w-4" />} label={item.label} />;
            })}
          </div>

          <div className="mb-2 mt-6 px-2 text-[10px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">ACCOUNT</div>
          <div className="space-y-0.5">
            {accountItems.map((item) => {
              const Icon = icons[item.icon];

              return <DashboardNavLink key={item.href} href={item.href} icon={<Icon className="h-4 w-4" />} label={item.label} />;
            })}
          </div>
        </nav>

        <div className="absolute bottom-0 left-0 right-0 border-t border-[color:var(--bg-surface)] p-3">
          <div className="flex items-center gap-3">
            <div className="flex h-[30px] w-[30px] items-center justify-center rounded-full border border-[color:var(--bg-border)] bg-[linear-gradient(135deg,var(--accent-dim),var(--bg-surface))] text-[12px] font-semibold text-[color:var(--accent-primary)]">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-[13px] font-medium text-[color:var(--text-primary)]">
                {mockUser.firstName} {mockUser.lastName}
              </div>
              <div className="truncate text-[11px] text-[color:var(--text-tertiary)]">{mockUser.email}</div>
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

      <div className="pl-[220px]">
        <header className="sticky top-0 z-40 flex h-[52px] items-center justify-between border-b border-[color:var(--bg-surface)] bg-[color:var(--bg-base)] px-6">
          <button className="flex cursor-pointer items-center gap-2 text-[color:var(--text-primary)] transition-colors hover:text-[color:var(--text-secondary)]" type="button">
            <Building2 className="h-4 w-4 text-[color:var(--text-secondary)]" />
            <span className="text-[14px] font-medium">{mockOrg.name}</span>
            <ChevronDown className="h-3.5 w-3.5 text-[color:var(--text-tertiary)]" />
          </button>

          <div className="flex items-center gap-3">
            <button
              aria-label="Notifications"
              className="inline-flex h-8 w-8 items-center justify-center rounded-full text-[color:var(--text-secondary)] transition-colors hover:bg-[color:var(--bg-surface)] hover:text-[color:var(--text-primary)]"
              type="button"
            >
              <Bell className="h-4 w-4" />
            </button>
            <div className="h-5 w-px bg-[color:var(--bg-surface)]" />
            <button
              className="inline-flex items-center rounded-md bg-[color:var(--accent-primary)] px-3 py-1.5 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]"
              type="button"
            >
              <Plus className="mr-1.5 h-3.5 w-3.5" />
              New analysis
            </button>
          </div>
        </header>

        <main className="min-h-[calc(100vh-52px)] bg-[color:var(--bg-base)] p-8">{children}</main>
      </div>
    </div>
  );
}
