import Image from "next/image";
import Link from "next/link";
import {
  Bell,
  BarChart2,
  BarChart3,
  BookOpen,
  Brain,
  Building2,
  ChevronDown,
  ClipboardList,
  Database,
  GitFork,
  GitBranch,
  FlaskConical,
  History,
  LayoutDashboard,
  LogOut,
  Package,
  Plug,
  Plus,
  Mail,
  Settings,
  ShieldCheck,
  ScrollText,
  AlertTriangle,
  ShieldAlert,
  Timer,
  Users2,
} from "lucide-react";
import { signOut, withAuth } from "@workos-inc/authkit-nextjs";
import { redirect } from "next/navigation";
import { cache } from "react";

import { mockOrg, mockUser } from "@/lib/mock-data";
import { DashboardNavLink } from "@/components/dashboard-nav-link";
import { getAuditLogStats, getBootstrapOrg, getEvalSkillGaps, getMemoryQueue, getMyOrg, getOrgRedFlags, getOrgSetupStatus, type Org } from "../../lib/data";

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
  } catch {
    // Auth can be unavailable in local preview; fall back to bootstrap data.
  }

  if (accessToken) {
    const org = await getMyOrg(accessToken);
    if (org) return org;
  }

  try {
    const org = await getBootstrapOrg();
    if (org) return org;
  } catch {
    // Bootstrap may be offline during local preview.
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
  } catch {
    // Auth can be unavailable in local preview; use mock user data.
  }

  return mockUser;
}

const loadNavBadges = cache(async (): Promise<{ memory: boolean; redFlags: boolean; audit: boolean; agentLoads: boolean; skillGapCount: number }> => {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    // Auth can be unavailable in local preview; badges fall back below.
  }
  const org = await getBootstrapOrg();
  if (!org?.id) return { memory: false, redFlags: false, audit: false, agentLoads: true, skillGapCount: 0 };
  const [memory, redFlags, auditStats, setupStatus, skillGaps] = await Promise.all([
    getMemoryQueue(accessToken, org.id, { status: "pending", limit: 1 }),
    getOrgRedFlags(accessToken, org.id, "critical"),
    getAuditLogStats(accessToken, org.id),
    getOrgSetupStatus(accessToken, org.id, 300),
    getEvalSkillGaps(accessToken, org.id, "open"),
  ]);
  return {
    memory: (memory?.pending_count ?? 0) > 0,
    redFlags: (redFlags?.critical_count ?? 0) > 0,
    audit: (auditStats?.critical_events_7d ?? 0) > 0,
    agentLoads: setupStatus?.has_agent_loads ?? true,
    skillGapCount: skillGaps?.length ?? 0,
  };
});

export default async function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const icons = {
    LayoutDashboard,
    GitBranch,
    GitFork,
    BarChart3,
    BarChart2,
    Brain,
    BookOpen,
    Package,
    Plug,
    Database,
    Users2,
    ClipboardList,
    AlertTriangle,
    ShieldAlert,
    ScrollText,
    Timer,
    Settings,
    Mail,
    History,
    ShieldCheck,
    FlaskConical,
  };
  type IconName = keyof typeof icons;
  type NavItem = {
    href: string;
    label: string;
    icon: IconName;
    badge?: string;
    badgeVariant?: "label" | "dot";
  };
  const shellOrg = await loadShellOrg();
  const shellUser = await loadShellUser();
  const navBadges = await loadNavBadges();
  const navGroups: Array<{ label: string; items: NavItem[] }> = [
    {
      label: "WORKSPACE",
      items: [
        { href: "/dashboard", label: "Overview", icon: "LayoutDashboard" },
        { href: "/dashboard/repos", label: "Repos", icon: "GitBranch" },
        { href: "/dashboard/skills", label: "Skills", icon: "BookOpen" },
        { href: "/dashboard/sources", label: "Sources", icon: "Database" },
      ],
    },
    {
      label: "ANALYTICS",
      items: [
        { href: "/dashboard/heatmap", label: "Heatmap", icon: "BarChart3" },
        { href: "/dashboard/intelligence", label: "Intelligence", icon: "BarChart2" },
        { href: "/dashboard/analytics", label: "Analytics", icon: "ClipboardList" },
        { href: "/dashboard/eval", label: "Agent Performance", icon: "BarChart2" },
        { href: "/dashboard/eval/gaps", label: "Skill Gaps", icon: "AlertTriangle", badge: navBadges.skillGapCount ? `${navBadges.skillGapCount} open gaps` : undefined, badgeVariant: "dot" },
        { href: "/dashboard/eval/ab-tests", label: "A/B Tests", icon: "FlaskConical" },
      ],
    },
    {
      label: "INSIGHTS",
      items: [
        { href: "/dashboard/digest", label: "Digest", icon: "Mail" },
        { href: "/dashboard/sessions", label: "Sessions", icon: "History" },
      ],
    },
    {
      label: "TOOLS",
      items: [
        { href: "/dashboard/review", label: "Code Review", icon: "ShieldCheck" },
      ],
    },
    {
      label: "QUALITY",
      items: [
        { href: "/dashboard/debt", label: "Skill Debt", icon: "AlertTriangle" },
        { href: "/dashboard/red-flags", label: "Red Flags", icon: "ShieldAlert", badge: navBadges.redFlags ? "Critical red flags" : undefined, badgeVariant: "dot" },
        { href: "/dashboard/half-life", label: "Half-life", icon: "Timer" },
      ],
    },
    {
      label: "DISTRIBUTION",
      items: [
        { href: "/dashboard/registry", label: "Registry", icon: "Package" },
        { href: "/dashboard/registry/dependency-graph", label: "Dependency Graph", icon: "GitFork" },
      ],
    },
    {
      label: "SETUP & CONFIG",
      items: [
        { href: "/dashboard/connect", label: "Connect Agent", icon: "Plug", badge: navBadges.agentLoads ? undefined : "No agent loads", badgeVariant: "dot" },
        { href: "/dashboard/teams", label: "Teams", icon: "Users2" },
        { href: "/dashboard/memory", label: "Memory", icon: "Brain", badge: navBadges.memory ? "Pending memory" : undefined, badgeVariant: "dot" },
      ],
    },
    {
      label: "ACCOUNT",
      items: [
        { href: "/dashboard/audit", label: "Audit", icon: "ScrollText", badge: navBadges.audit ? "Critical audit events" : undefined, badgeVariant: "dot" },
        { href: "/dashboard/settings", label: "Settings", icon: "Settings" },
      ],
    },
  ];
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

        <nav className="mt-3 max-h-[calc(100vh-132px)] overflow-y-auto px-3 pb-3">
          {navGroups.map((group, index) => (
            <div className={index === 0 ? "" : "mt-5"} key={group.label}>
              <div className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">{group.label}</div>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const Icon = icons[item.icon];

                  return <DashboardNavLink badge={item.badge} badgeVariant={item.badgeVariant} key={item.href} href={item.href} icon={<Icon className="h-4 w-4" />} label={item.label} />;
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
