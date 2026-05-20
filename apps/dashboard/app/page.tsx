import { ArrowRight, CheckCircle2, DatabaseZap, LockKeyhole, TerminalSquare } from "lucide-react";
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[color:var(--bg-base)] text-[color:var(--text-primary)]">
      <section className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 py-6 sm:px-8">
        <nav className="flex items-center justify-between gap-4">
          <Link className="text-sm font-semibold text-[color:var(--logo-white)]" href="/">
            Skillayer
          </Link>
          <Link className="inline-flex items-center gap-2 rounded-[8px] border border-[color:var(--bg-border)] px-3 py-2 text-sm font-medium text-[color:var(--text-secondary)] transition hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" href="/sign-in">
            Sign in
            <ArrowRight className="h-4 w-4" />
          </Link>
        </nav>

        <div className="grid flex-1 items-center gap-12 py-12 lg:grid-cols-[1.05fr_0.95fr]">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[color:var(--accent-bright)]">
              Enterprise coding-agent telemetry
            </p>
            <h1 className="mt-4 max-w-3xl text-4xl font-semibold leading-tight text-[color:var(--text-primary)] sm:text-6xl">
              Skillayer connects every coding agent to repo, policy, and compliance evidence.
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-[color:var(--text-secondary)] sm:text-lg">
              Developers can sign in, connect local agent sessions or provider compliance APIs, and populate Activity, Insights, Policy, Audit, and Skills without uploading prompts, chats, diffs, or file contents.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link className="inline-flex min-h-11 items-center justify-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-5 py-3 text-sm font-semibold text-black transition hover:bg-[color:var(--accent-bright)]" href="/sign-in">
                Sign in
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link className="inline-flex min-h-11 items-center justify-center rounded-[8px] border border-[color:var(--bg-border)] px-5 py-3 text-sm font-semibold text-[color:var(--text-primary)] transition hover:border-[color:var(--accent-primary)]" href="/dashboard" prefetch={false}>
                Open local preview
              </Link>
            </div>
          </div>

          <div>
            <div className="grid gap-3">
              {[
                {
                  icon: <TerminalSquare className="h-5 w-5" />,
                  label: "Local agent capture",
                  detail: "Codex Desktop, Codex CLI, Claude Code, Cursor, and Windsurf metadata import.",
                },
                {
                  icon: <DatabaseZap className="h-5 w-5" />,
                  label: "Provider compliance pull",
                  detail: "Anthropic and OpenAI admin APIs normalize events into the same metric surface.",
                },
                {
                  icon: <LockKeyhole className="h-5 w-5" />,
                  label: "Metadata-only contract",
                  detail: "Repo, tokens, cost, tools, files touched, runtime, and policy state only.",
                },
              ].map((item) => (
                <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={item.label}>
                  <div className="flex items-start gap-3">
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[8px] bg-[color:var(--accent-primary)]/15 text-[color:var(--accent-bright)]">
                      {item.icon}
                    </span>
                    <div>
                      <h2 className="text-base font-semibold">{item.label}</h2>
                      <p className="mt-1 text-sm leading-6 text-[color:var(--text-secondary)]">{item.detail}</p>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            <div className="mt-4 rounded-[8px] border border-[color:var(--accent-primary)]/30 bg-[color:var(--accent-primary)]/10 p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-[color:var(--accent-bright)]">
                <CheckCircle2 className="h-4 w-4" />
                Enterprise end-to-end milestone
              </div>
              <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">
                Public entry, SSO redirect, local preview, and metadata-only posture are visible before the authenticated dashboard.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
