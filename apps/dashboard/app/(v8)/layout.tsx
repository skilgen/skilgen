import Link from "next/link";
import { Bell, Building2, ChevronDown, Plus } from "lucide-react";
import { redirect } from "next/navigation";

import { SidebarV8, V8MobileNav } from "../../components/SidebarV8";
import { isDashboardV8Enabled } from "../../lib/flags";
import { getBootstrapOrg, getMyOrg, type Org } from "../../lib/data";
import { mockOrg, mockUser } from "@/lib/mock-data";
import { withAuth } from "@workos-inc/authkit-nextjs";

export const dynamic = "force-dynamic";

type ShellUser = Pick<typeof mockUser, "email" | "firstName" | "lastName">;

async function loadV8ShellOrg(): Promise<Pick<Org, "id" | "name" | "plan">> {
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

async function loadV8ShellUser(): Promise<ShellUser> {
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

export default async function V8Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const shellOrg = await loadV8ShellOrg();
  const isV8Enabled = await isDashboardV8Enabled(shellOrg.id);
  if (!isV8Enabled) {
    redirect("/dashboard");
  }

  const shellUser = await loadV8ShellUser();
  const initials = `${shellUser.firstName[0] ?? "S"}${shellUser.lastName[0] ?? "U"}`;

  return (
    <div className="min-h-screen bg-[color:var(--bg-base)] text-[color:var(--text-primary)]">
      <SidebarV8 initials={initials} user={shellUser} />

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
              href="/skills/repos"
            >
              <Plus className="mr-1.5 h-3.5 w-3.5" />
              <span className="hidden sm:inline">Analyze repo</span>
              <span className="sm:hidden">Analyze</span>
            </Link>
          </div>
        </header>

        <V8MobileNav />

        <main className="min-h-[calc(100vh-52px)] bg-[color:var(--bg-base)] p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
