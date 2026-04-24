import Link from "next/link";
import { ArrowRight, BookOpen, Github, Sparkles } from "lucide-react";

export const dynamic = "force-dynamic";

export default function OnboardingPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">How to add a new skill</h1>
        <p className="mt-1 max-w-2xl text-sm text-[color:var(--text-secondary)]">
          Skillayer turns connected repositories into a working knowledge library. This page is the shortest path from zero to your first useful skill.
        </p>
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[color:var(--accent-primary)]">
            <Github className="h-6 w-6" />
          </div>
          <p className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Step 1</p>
          <h2 className="mt-2 text-[18px] font-semibold text-[color:var(--text-primary)]">Connect a repo</h2>
          <p className="mt-2 text-[14px] leading-6 text-[color:var(--text-secondary)]">
            Install the Skillayer GitHub App. Once it is installed, your repositories appear in the Repos tab automatically.
          </p>
          <Link
            className="mt-5 inline-flex h-10 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]"
            href="https://github.com/apps/skillayer/installations/new"
          >
            Install GitHub App
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </section>

        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[color:var(--accent-primary)]">
            <Sparkles className="h-6 w-6" />
          </div>
          <p className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Step 2</p>
          <h2 className="mt-2 text-[18px] font-semibold text-[color:var(--text-primary)]">Run an analysis</h2>
          <p className="mt-2 text-[14px] leading-6 text-[color:var(--text-secondary)]">
            Open any repo and click <span className="font-semibold text-[color:var(--text-primary)]">Analyse now</span>. Skillayer analyses your code and generates SKILL.md files for each domain.
          </p>
          <Link
            className="mt-5 inline-flex h-10 items-center justify-center rounded-md border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-primary)] hover:bg-[color:var(--bg-elevated)]"
            href="/dashboard/repos"
          >
            Go to Repos
          </Link>
        </section>

        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[color:var(--accent-primary)]">
            <BookOpen className="h-6 w-6" />
          </div>
          <p className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Step 3</p>
          <h2 className="mt-2 text-[18px] font-semibold text-[color:var(--text-primary)]">Browse your skills</h2>
          <p className="mt-2 text-[14px] leading-6 text-[color:var(--text-secondary)]">
            Skills appear in the Skills tab with scores, categories, freshness, and source types. Publish your best skills to the Registry to share them with your team.
          </p>
          <div className="mt-5 flex gap-3">
            <Link
              className="inline-flex h-10 items-center justify-center rounded-md border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-primary)] hover:bg-[color:var(--bg-elevated)]"
              href="/dashboard/skills"
            >
              Open Skills
            </Link>
            <Link
              className="inline-flex h-10 items-center justify-center rounded-md border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-primary)] hover:bg-[color:var(--bg-elevated)]"
              href="/dashboard/registry"
            >
              Open Registry
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
