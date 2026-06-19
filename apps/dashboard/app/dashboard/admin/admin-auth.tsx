import "server-only";

import { withAuth } from "@workos-inc/authkit-nextjs";

export async function requireAdmin() {
  let email = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    email = session?.user?.email || "";
  } catch {
    email = "";
  }
  const adminEmails = (process.env.NEXT_PUBLIC_ADMIN_EMAILS || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
  return {
    isAdmin: Boolean(email && adminEmails.includes(email)),
    email,
    adminSecret: process.env.ADMIN_SECRET || "",
  };
}

export function ForbiddenAdmin() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="max-w-md rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10 text-red-300">403</div>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Admin access required</h1>
        <p className="mt-2 text-sm text-[color:var(--text-secondary)]">Your email is not listed in NEXT_PUBLIC_ADMIN_EMAILS for this deployment.</p>
      </div>
    </div>
  );
}
