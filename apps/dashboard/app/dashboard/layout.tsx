import Image from "next/image";
import Link from "next/link";
import {
  Bell,
  BarChart3,
  BookOpen,
  Building2,
  ChevronDown,
  CreditCard,
  Database,
  GitBranch,
  LayoutDashboard,
  LogOut,
  Package,
  Plus,
  Settings,
} from "lucide-react";
import { signOut, withAuth } from "@workos-inc/authkit-nextjs";
import { redirect } from "next/navigation";

import { dashboardNavItems, mockOrg, mockUser } from "@/lib/mock-data";
import { DashboardNavLink } from "@/components/dashboard-nav-link";
import { API_URL, getMyOrg, type Org } from "../../lib/data";

type ShellUser = Pick<typeof mockUser, "email" | "firstName" | "lastName">;

async function handleSignOut() {
  "use server";

  const isWorkOSConfigured = Boolean(
    process.env.WORKOS_API_KEY &&
      process.env.WORKOS_CLIENT_ID &&
      process.env.WORKOS_COOKIE_PASSWORD &&
      process.env.WORKOS_COOKIE_PASSWORD.length >= 32 &&
      (process.env.NEXT_PUBLIC_WORKOS_REDIRECT_URI || process.env.WORKOS_REDIRECT_URI),
  );

  if (!isWorkOSConfigured) {
    redirect("/dashboard");
  }

  await signOut();
}

/**
 * Loads the org used by the dashboard shell and falls back to preview data.
 */
async function loadShellOrg(): Promise<Pick<Org, "name" | "plan">> {
  let accessToken = "";

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Dashboard shell auth unavailable:", error);
  }

  if (accessToken) {
    const org = await getMyOrg(accessToken);
    if (org) return org;
  }

  try {
    const res = await fetch(`${API_URL}/orgs/bootstrap`, { next: { revalidate: 60 } });
    if (res.ok) {
      return ((await res.json()) as Org) || mockOrg;
    }
  } catch (error) {
    console.error("Dashboard shell org bootstrap failed:", error);
  }

  return mockOrg;
}

function deriveShellName(email: string): { firstName: string; lastName: string } {
  const local = email.split("@")[0]?.trim() || "Skillayer User";
  const parts = local
    .split(/[._-]+/)
    .map((part) => part.trim())
    .filter(Boolean);
  const [firstName = "Skillayer", lastName = "User"] = parts;
  return {
    firstName: firstName.charAt(0).toUpperCase() + firstName.slice(1),
    lastName: lastName.charAt(0).toUpperCase() + lastName.slice(1),
  };
}

async function loadShellUser(): Promise<ShellUser> {
  try {
    const session = await withAuth({ ensureSignedIn: false });
    if (session?.user?.email) {
      const fallbackName = deriveShellName(session.user.email);
      return {
        email: session.user.email,
        firstName: session.user.firstName || fallbackName.firstName,
        lastName: session.user.lastName || fallbackName.lastName,
      };
    }
  } catch (error) {
    console.error("Dashboard shell user unavailable:", error);
  }

  return mockUser;
}

export default async function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const icons = {
    LayoutDashboard,
    GitBranch,
    BarChart3,
    BookOpen,
    Package,
    Database,
    Settings,
    CreditCard,
  };
  type IconName = keyof typeof icons;
  type NavItem = {
    href: string;
    label: string;
    icon: IconName;
    badge?: string;
  };
  const shellOrg = await loadShellOrg();
  const shellUser = await loadShellUser();
  const workspaceItems: NavItem[] = dashboardNavItems
    .filter((item) => item.href !== "/dashboard/settings" && item.href !== "/dashboard/upgrade")
    .map((item) => ({ ...item, icon: item.icon as IconName }));
  if (shellOrg.plan === "free") {
    workspaceItems.push({
      href: "/dashboard/upgrade",
      label: "Upgrade",
      icon: "CreditCard",
      badge: "Free",
    });
  }
  const accountItems: NavItem[] = dashboardNavItems
    .filter((item) => item.href === "/dashboard/settings")
    .map((item) => ({ ...item, icon: item.icon as IconName }));
  const initials = `${shellUser.firstName[0] ?? "S"}${shellUser.lastName[0] ?? "U"}`;

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

              return <DashboardNavLink badge={item.badge} key={item.href} href={item.href} icon={<Icon className="h-4 w-4" />} label={item.label} />;
            })}
          </div>

          <div className="mb-2 mt-6 px-2 text-[10px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">ACCOUNT</div>
          <div className="space-y-0.5">
            {accountItems.map((item) => {
              const Icon = icons[item.icon];

              return <DashboardNavLink badge={item.badge} key={item.href} href={item.href} icon={<Icon className="h-4 w-4" />} label={item.label} />;
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
                {shellUser.firstName} {shellUser.lastName}
              </div>
              <div className="truncate text-[11px] text-[color:var(--text-tertiary)]">{shellUser.email}</div>
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
            <span className="text-[14px] font-medium">{shellOrg.name}</span>
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
            <Link
              className="inline-flex items-center rounded-md bg-[color:var(--accent-primary)] px-3 py-1.5 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]"
              href="/dashboard/repos"
            >
              <Plus className="mr-1.5 h-3.5 w-3.5" />
              New analysis
            </Link>
          </div>
        </header>

        <main className="min-h-[calc(100vh-52px)] bg-[color:var(--bg-base)] p-8">{children}</main>
      </div>
    </div>
  );
}
