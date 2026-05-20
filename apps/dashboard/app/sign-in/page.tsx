import { ArrowRight, Building2, Github, Mail, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";

import { selfServeAuthEnvDefault } from "../../lib/flags";

type SignInPageProps = {
  searchParams?: Promise<{
    email?: string;
    error?: string;
    sent?: string;
  }>;
};

function workOSReady(): boolean {
  const redirectUri = process.env.NEXT_PUBLIC_WORKOS_REDIRECT_URI || process.env.WORKOS_REDIRECT_URI || "";

  return Boolean(
    process.env.WORKOS_API_KEY &&
      process.env.WORKOS_CLIENT_ID &&
      process.env.WORKOS_COOKIE_PASSWORD &&
      process.env.WORKOS_COOKIE_PASSWORD.length >= 32 &&
      redirectUri,
  );
}

function AuthOption({
  description,
  disabled = false,
  href,
  icon,
  label,
}: {
  description: string;
  disabled?: boolean;
  href: string;
  icon: React.ReactNode;
  label: string;
}) {
  const className =
    "group flex min-h-[74px] items-center gap-3 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-4 py-3 text-left transition hover:border-[color:var(--accent-primary)] hover:bg-[color:var(--bg-hover)]";

  if (disabled) {
    return (
      <button aria-disabled="true" className={`${className} w-full cursor-not-allowed opacity-55`} disabled type="button">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[8px] bg-[color:var(--bg-elevated)] text-[color:var(--text-secondary)]">
          {icon}
        </span>
        <span>
          <span className="block text-sm font-semibold text-[color:var(--text-primary)]">{label}</span>
          <span className="mt-1 block text-xs leading-5 text-[color:var(--text-secondary)]">{description}</span>
        </span>
      </button>
    );
  }

  return (
    <Link className={className} href={href} prefetch={false}>
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[8px] bg-[color:var(--accent-primary)]/15 text-[color:var(--accent-bright)]">
        {icon}
      </span>
      <span>
        <span className="block text-sm font-semibold text-[color:var(--text-primary)]">{label}</span>
        <span className="mt-1 block text-xs leading-5 text-[color:var(--text-secondary)]">{description}</span>
      </span>
    </Link>
  );
}

export default async function SignInPage({ searchParams }: SignInPageProps) {
  if (!selfServeAuthEnvDefault()) {
    redirect("/dashboard");
  }

  const params = await searchParams;
  const ssoReady = workOSReady();
  const error = params?.error;
  const sent = params?.sent === "magic-link";
  const email = params?.email || "";

  return (
    <main className="min-h-screen bg-[color:var(--bg-base)] px-5 py-6 text-[color:var(--text-primary)] sm:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] w-full max-w-5xl flex-col justify-between gap-10">
        <header className="flex items-center justify-between gap-4">
          <Link className="text-sm font-semibold text-[color:var(--logo-white)]" href="/">
            Skillayer
          </Link>
          <Link className="text-sm font-medium text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]" href="/dashboard" prefetch={false}>
            Preview dashboard
          </Link>
        </header>

        <section className="grid items-center gap-10 lg:grid-cols-[1fr_420px]">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[color:var(--accent-bright)]">
              Enterprise agent coverage
            </p>
            <h1 className="mt-4 max-w-2xl text-4xl font-semibold leading-tight text-[color:var(--text-primary)] sm:text-5xl">
              Sign in to connect local agents and provider compliance sources.
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-[color:var(--text-secondary)]">
              Skillayer turns coding-agent activity into repo attribution, policy evidence, and operational metrics while keeping prompts, chats, diffs, and file contents out of the product.
            </p>
          </div>

          <div>
            <div className="mb-4 flex items-start gap-3">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[8px] bg-[color:var(--accent-primary)]/15 text-[color:var(--accent-bright)]">
                <ShieldCheck className="h-5 w-5" />
              </span>
              <div>
                <h2 className="text-lg font-semibold">Choose a sign-in method</h2>
                <p className="mt-1 text-sm leading-6 text-[color:var(--text-secondary)]">
                  Use SSO, email verification, or GitHub OAuth to start the Connect workflow.
                </p>
              </div>
            </div>

            {error ? (
              <p className="mb-3 rounded-[8px] border border-[color:var(--accent-red)]/40 bg-[color:var(--accent-red)]/10 px-3 py-2 text-sm text-red-100">
                {error === "personal-email"
                  ? "Use a work email so Skillayer can create or join the right enterprise workspace."
                  : error === "email-required"
                    ? "Enter a valid email address to send a magic link."
                    : "Sign-in needs a valid WorkOS configuration before SSO can start."}
              </p>
            ) : null}

            {sent ? (
              <p className="mb-3 rounded-[8px] border border-[color:var(--accent-primary)]/40 bg-[color:var(--accent-primary)]/10 px-3 py-2 text-sm text-[color:var(--text-primary)]">
                Check {email ? <span className="font-semibold">{email}</span> : "your inbox"} for a Skillayer sign-in link.
              </p>
            ) : null}

            <div className="grid gap-3">
              <AuthOption
                description={ssoReady ? "Continue through your company identity provider." : "Local preview falls back to the dashboard until WorkOS env vars are set."}
                href="/api/auth/sso"
                icon={<Building2 className="h-5 w-5" />}
                label="Sign in with work account"
              />
              <form
                action="/api/auth/magic-link/send"
                className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4"
                method="post"
              >
                <div className="flex items-start gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[8px] bg-[color:var(--accent-primary)]/15 text-[color:var(--accent-bright)]">
                    <Mail className="h-5 w-5" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <label className="block text-sm font-semibold text-[color:var(--text-primary)]" htmlFor="magic-link-email">
                      Email magic link
                    </label>
                    <p className="mt-1 text-xs leading-5 text-[color:var(--text-secondary)]">
                      Verify a corporate email and land directly in the Connect experience.
                    </p>
                  </div>
                </div>
                <div className="mt-4 flex flex-col gap-2 sm:flex-row">
                  <input
                    className="min-h-11 flex-1 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] px-3 text-sm text-[color:var(--text-primary)] outline-none transition placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]"
                    id="magic-link-email"
                    name="email"
                    placeholder="you@company.com"
                    type="email"
                    required
                  />
                  <button
                    className="inline-flex min-h-11 items-center justify-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-4 text-sm font-semibold text-black transition hover:bg-[color:var(--accent-bright)]"
                    type="submit"
                  >
                    Send
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </form>
              <AuthOption
                description="OAuth sign-in will reuse the GitHub app without requiring repository install."
                disabled={!ssoReady}
                href="/api/auth/github"
                icon={<Github className="h-5 w-5" />}
                label="Sign in with GitHub"
              />
            </div>
          </div>
        </section>

        <footer className="text-xs text-[color:var(--text-tertiary)]">
          Metadata-only by design: no raw prompts, chats, diffs, tool arguments, or file contents.
        </footer>
      </div>
    </main>
  );
}
