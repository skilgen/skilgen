import { withAuth } from "@workos-inc/authkit-nextjs";
import { CheckCircle2, KeyRound, ShieldCheck, TerminalSquare } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import { API_URL } from "../../lib/data";

export const dynamic = "force-dynamic";

type DevicePageProps = {
  searchParams?: Promise<{
    approved?: string;
    error?: string;
    user_code?: string;
  }>;
};

function cleanReturnTo(userCode: string): string {
  const params = new URLSearchParams();
  if (userCode) params.set("user_code", userCode);
  return `/device${params.toString() ? `?${params.toString()}` : ""}`;
}

function signInHref(source: "github" | "sso", userCode: string): string {
  const params = new URLSearchParams({ returnTo: cleanReturnTo(userCode) });
  return `/api/auth/${source}?${params.toString()}`;
}

async function approveDevice(formData: FormData) {
  "use server";

  const userCode = String(formData.get("user_code") ?? "").trim().toUpperCase();
  if (!userCode) {
    redirect("/device?error=missing-code");
  }

  let accessToken = "";
  let actorEmail = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
    actorEmail = session?.user?.email || "";
  } catch {
    accessToken = "";
    actorEmail = "";
  }

  if (!accessToken || !actorEmail) {
    redirect(cleanReturnTo(userCode));
  }

  const adminSecret = process.env.ADMIN_SECRET || "";
  const response = await fetch(`${API_URL}/v1/device/approve`, {
    method: "POST",
    headers: {
      ...(adminSecret ? { "X-Admin-Secret": adminSecret, "X-Skillayer-Actor-Email": actorEmail } : { Authorization: `Bearer ${accessToken}` }),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_code: userCode }),
    cache: "no-store",
  });

  if (!response.ok) {
    let detail = "approval-failed";
    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail || detail;
    } catch {
      // Keep a stable fallback for query rendering.
    }
    const params = new URLSearchParams({ user_code: userCode, error: detail });
    redirect(`/device?${params.toString()}`);
  }

  const params = new URLSearchParams({ user_code: userCode, approved: "1" });
  redirect(`/device?${params.toString()}`);
}

export default async function DevicePage({ searchParams }: DevicePageProps) {
  const params = await searchParams;
  const userCode = String(params?.user_code ?? "").trim().toUpperCase();
  const approved = params?.approved === "1";
  const error = params?.error;
  let signedIn = false;

  try {
    const session = await withAuth({ ensureSignedIn: false });
    signedIn = Boolean(session?.accessToken);
  } catch {
    signedIn = false;
  }

  return (
    <main className="min-h-screen bg-[color:var(--bg-base)] px-5 py-6 text-[color:var(--text-primary)] sm:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] w-full max-w-4xl flex-col">
        <header className="flex items-center justify-between gap-4">
          <Link className="text-sm font-semibold text-[color:var(--logo-white)]" href="/">
            Skillayer
          </Link>
          <Link className="text-sm font-medium text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]" href="/dashboard/connect" prefetch={false}>
            Connect dashboard
          </Link>
        </header>

        <section className="grid flex-1 place-items-center py-12">
          <div className="w-full max-w-xl rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 shadow-2xl shadow-black/20">
            <div className="flex items-start gap-3">
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[8px] bg-[color:var(--accent-primary)]/15 text-[color:var(--accent-bright)]">
                {approved ? <CheckCircle2 className="h-5 w-5" /> : <TerminalSquare className="h-5 w-5" />}
              </span>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--accent-bright)]">Device connection</p>
                <h1 className="mt-2 text-2xl font-semibold">{approved ? "Skillayer agent connected" : "Approve Skillayer CLI"}</h1>
                <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">
                  {approved ? "Return to your terminal. The local helper will receive its tenant key and start syncing coding-agent metadata." : "Approve this machine so the local helper can upload metadata-only Codex, Claude Code, Cursor, and Windsurf activity."}
                </p>
              </div>
            </div>

            <div className="mt-6 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
              <div className="flex items-center justify-between gap-4">
                <span className="text-sm text-[color:var(--text-secondary)]">Device code</span>
                <span className="font-mono text-lg font-semibold tracking-wider text-[color:var(--text-primary)]">{userCode || "Missing"}</span>
              </div>
            </div>

            {error ? (
              <p className="mt-4 rounded-[8px] border border-[color:var(--accent-red)]/40 bg-[color:var(--accent-red)]/10 px-3 py-2 text-sm text-red-100">
                {decodeURIComponent(error)}
              </p>
            ) : null}

            {!userCode ? (
              <p className="mt-4 text-sm text-[color:var(--text-secondary)]">Run `skillayer connect` again to generate a fresh device code.</p>
            ) : approved ? (
              <div className="mt-5 flex items-center gap-2 rounded-[8px] border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 px-3 py-2 text-sm text-[color:var(--accent-green)]">
                <ShieldCheck className="h-4 w-4" />
                Approved. You can close this browser tab.
              </div>
            ) : signedIn ? (
              <form action={approveDevice} className="mt-5">
                <input name="user_code" type="hidden" value={userCode} />
                <button className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[color:var(--accent-bright)]" type="submit">
                  <KeyRound className="h-4 w-4" />
                  Approve this machine
                </button>
              </form>
            ) : (
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <Link className="inline-flex min-h-11 items-center justify-center rounded-[8px] bg-[color:var(--accent-primary)] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[color:var(--accent-bright)]" href={signInHref("sso", userCode)} prefetch={false}>
                  Sign in with SSO
                </Link>
                <Link className="inline-flex min-h-11 items-center justify-center rounded-[8px] border border-[color:var(--bg-border)] px-4 py-3 text-sm font-semibold text-[color:var(--text-primary)] transition hover:border-[color:var(--accent-primary)]" href={signInHref("github", userCode)} prefetch={false}>
                  Sign in with GitHub
                </Link>
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
