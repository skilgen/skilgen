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
  Inbox,
  LayoutDashboard,
  Package,
  Plug,
  Plus,
  Mail,
  Settings,
  ShieldCheck,
  Sparkles,
  ScrollText,
  AlertTriangle,
  ShieldAlert,
  Timer,
  Trophy,
  User,
  Users2,
  Zap,
} from "lucide-react";
import { signOut, withAuth } from "@workos-inc/authkit-nextjs";
import { redirect } from "next/navigation";
import { cache } from "react";

import { mockOrg, mockUser } from "@/lib/mock-data";
import { SidebarLegacy, type LegacyNavGroup } from "../../components/SidebarLegacy";
import { SidebarV8, V8MobileNav } from "../../components/SidebarV8";
import { isDashboardV8Enabled } from "../../lib/flags";
import { API_URL, getAuditLogStats, getAutopilotQueue, getBootstrapOrg, getEvalSkillGaps, getMemoryQueue, getMyOrg, getOrgRedFlags, getOrgSetupStatus, type Org } from "../../lib/data";

export const dynamic = "force-dynamic";

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

  try {
    await signOut();
  } catch {
    redirect("/sign-in");
  }
}

/**
 * Loads the org used by the dashboard shell and falls back to preview data.
 */
async function loadShellOrg(): Promise<Pick<Org, "id" | "name" | "plan">> {
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

const loadNavBadges = cache(async (): Promise<{ memory: boolean; redFlags: boolean; audit: boolean; agentLoads: boolean; skillGapCount: number; pendingAutopilotCount: number }> => {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    // Auth can be unavailable in local preview; badges fall back below.
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  if (!org?.id) return { memory: false, redFlags: false, audit: false, agentLoads: true, skillGapCount: 0, pendingAutopilotCount: 0 };
  const [memory, redFlags, auditStats, setupStatus, skillGaps, autopilotQueue] = await Promise.all([
    getMemoryQueue(accessToken, org.id, { status: "pending", limit: 1 }),
    getOrgRedFlags(accessToken, org.id, "critical"),
    getAuditLogStats(accessToken, org.id),
    getOrgSetupStatus(accessToken, org.id, 300),
    getEvalSkillGaps(accessToken, org.id, "open"),
    getAutopilotQueue(accessToken, org.id),
  ]);
  return {
    memory: (memory?.pending_count ?? 0) > 0,
    redFlags: (redFlags?.critical_count ?? 0) > 0,
    audit: (auditStats?.critical_events_7d ?? 0) > 0,
    agentLoads: setupStatus?.has_agent_loads ?? true,
    skillGapCount: skillGaps?.length ?? 0,
    pendingAutopilotCount: (autopilotQueue ?? []).filter((task) => task.status === "pending").length,
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
    Trophy,
    User,
    Settings,
    Mail,
    History,
    Inbox,
    ShieldCheck,
    Sparkles,
    FlaskConical,
    Zap,
  };
  const shellOrg = await loadShellOrg();
  const shellUser = await loadShellUser();
  const initials = `${shellUser.firstName[0] ?? "S"}${shellUser.lastName[0] ?? "U"}`;
  const isV8Enabled = await isDashboardV8Enabled(shellOrg.id);
  try {
    const session = await withAuth({ ensureSignedIn: false });
    const token = session?.accessToken || "";
    if (token && shellOrg.id && shellUser.email) {
      const login = shellUser.email.split("@")[0] || shellUser.email;
      void fetch(`${API_URL}/orgs/${shellOrg.id}/auth/login-event`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_login: login, user_email: shellUser.email }),
        cache: "no-store",
      }).catch(() => undefined);
    }
  } catch {
    // Login telemetry must never block dashboard rendering.
  }
  const adminEmails = (process.env.NEXT_PUBLIC_ADMIN_EMAILS || "")
    .split(",")
    .map((email) => email.trim())
    .filter(Boolean);
  const isAdmin = adminEmails.includes(shellUser.email || "");
  const navBadges = isV8Enabled
    ? { memory: false, redFlags: false, audit: false, agentLoads: true, skillGapCount: 0, pendingAutopilotCount: 0 }
    : await loadNavBadges();
  const navGroups: LegacyNavGroup[] = [
    {
      label: "PRODUCT",
      items: [
        { href: "/dashboard", label: "Overview", icon: "LayoutDashboard" },
        { href: "/dashboard/my-code-today", label: "My Code Today", icon: "User" },
        { href: "/dashboard/agent-prs", label: "PR Inbox", icon: "Inbox" },
        { href: "/dashboard/leaderboard", label: "Leaderboard", icon: "Trophy" },
        { href: "/dashboard/skills", label: "Skills", icon: "BookOpen" },
        { href: "/dashboard/registry", label: "Registry", icon: "Package" },
        { href: "/dashboard/repos", label: "Repos", icon: "GitBranch" },
      ],
    },
    {
      label: "ANALYTICS",
      items: [
        { href: "/dashboard/agent-scorecard", label: "Agent Scorecard", icon: "BarChart3" },
        { href: "/dashboard/eval", label: "Agent Performance", icon: "BarChart2" },
        { href: "/dashboard/heatmap", label: "Heatmap", icon: "BarChart3" },
        { href: "/dashboard/intelligence", label: "Intelligence", icon: "BarChart2" },
        { href: "/dashboard/ai-readiness", label: "AI Readiness", icon: "Brain" },
        { href: "/dashboard/skillql", label: "SkillQL", icon: "Sparkles" },
      ],
    },
    {
      label: "QUALITY",
      items: [
        { href: "/dashboard/eval/gaps", label: "Skill Gaps", icon: "AlertTriangle", badge: navBadges.skillGapCount ? `${navBadges.skillGapCount} open gaps` : undefined, badgeVariant: "dot" },
        { href: "/dashboard/debt", label: "Skill Debt", icon: "AlertTriangle" },
        { href: "/dashboard/knowledge-risk", label: "Knowledge Risk", icon: "Users2" },
        { href: "/dashboard/red-flags", label: "Red Flags", icon: "ShieldAlert", badge: navBadges.redFlags ? "Critical red flags" : undefined, badgeVariant: "dot" },
        { href: "/dashboard/eval/ab-tests", label: "A/B Tests", icon: "FlaskConical" },
        { href: "/dashboard/review", label: "Code Review", icon: "ShieldCheck" },
      ],
    },
    {
      label: "OPERATIONS",
      items: [
        { href: "/dashboard/sessions", label: "Sessions", icon: "History" },
        { href: "/dashboard/digest", label: "Digest", icon: "Mail" },
        { href: "/dashboard/autopilot", label: "Autopilot", icon: "Zap", badge: navBadges.pendingAutopilotCount > 0 ? `${navBadges.pendingAutopilotCount} pending` : undefined, badgeVariant: "dot" },
        { href: "/dashboard/sources", label: "Sources", icon: "Database" },
        { href: "/dashboard/sla", label: "Coverage SLA", icon: "ClipboardList" },
        { href: "/dashboard/half-life", label: "Half-life", icon: "Timer" },
        { href: "/dashboard/registry/dependency-graph", label: "Dependency Graph", icon: "GitFork" },
      ],
    },
    {
      label: "SETUP & CONFIG",
      items: [
        { href: "/dashboard/connect", label: "Connect Agent", icon: "Plug", badge: navBadges.agentLoads ? undefined : "No agent loads", badgeVariant: "dot" },
        { href: "/dashboard/teams", label: "Teams", icon: "Users2" },
      ],
    },
    {
      label: "ACCOUNT",
      items: [
        { href: "/dashboard/audit", label: "Audit", icon: "ScrollText", badge: navBadges.audit ? "Critical audit events" : undefined, badgeVariant: "dot" },
        { href: "/dashboard/settings", label: "Settings", icon: "Settings" },
        ...(isAdmin ? [{ href: "/dashboard/admin", label: "Admin", icon: "ShieldCheck" as const }] : []),
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-[color:var(--bg-base)] text-[color:var(--text-primary)]">
      {isV8Enabled ? (
        <SidebarV8 handleSignOut={handleSignOut} initials={initials} user={shellUser} />
      ) : (
        <SidebarLegacy handleSignOut={handleSignOut} icons={icons} initials={initials} navGroups={navGroups} orgId={shellOrg.id} user={shellUser} />
      )}

      <div className="md:pl-[220px]">
        <header className="sticky top-0 z-40 flex h-[52px] items-center justify-between border-b border-[color:var(--bg-surface)] bg-[color:var(--bg-base)] px-4 md:px-6">
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
              <span className="hidden sm:inline">New analysis</span>
              <span className="sm:hidden">New</span>
            </Link>
          </div>
        </header>

        {isV8Enabled ? (
          <V8MobileNav />
        ) : (
          <nav className="sticky top-[52px] z-30 border-b border-[color:var(--bg-surface)] bg-[color:var(--bg-base)] px-3 py-2 md:hidden">
            <div className="flex gap-2 overflow-x-auto pb-1">
              {navGroups.flatMap((group) => group.items).slice(0, 12).map((item) => {
                const Icon = icons[item.icon];
                return (
                  <Link
                    className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-1.5 text-xs font-semibold text-[color:var(--text-secondary)]"
                    href={item.href}
                    key={`mobile-${item.href}`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </nav>
        )}

        <main className="min-h-[calc(100vh-52px)] bg-[color:var(--bg-base)] p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
