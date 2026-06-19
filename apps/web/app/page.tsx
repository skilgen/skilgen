import Image from "next/image";
import Link from "next/link";
import { AlertTriangle, BarChart2, CheckCircle2, EyeOff, Github } from "lucide-react";

import HexGrid from "../components/HexGrid";

const problemCards = [
  {
    icon: AlertTriangle,
    iconClassName: "bg-[rgb(var(--accent-red-rgb)/0.1)] text-[color:var(--accent-red)]",
    title: "Skills decay silently",
    body: "CLAUDE.md and .cursorrules are manually maintained, have no quality standard, and go stale the moment code changes.",
  },
  {
    icon: BarChart2,
    iconClassName: "bg-[rgb(var(--accent-primary-rgb)/0.1)] text-[color:var(--accent-primary)]",
    title: "No quality metric",
    body: "There is no Codecov for institutional knowledge. Nobody knows which repos are agent-ready.",
  },
  {
    icon: EyeOff,
    iconClassName: "bg-[rgb(var(--text-secondary-rgb)/0.1)] text-[color:var(--text-secondary)]",
    title: "Zero leadership visibility",
    body: "Engineering leaders have no dashboard showing which teams are behind on AI readiness.",
  },
];

const steps = [
  {
    number: "01",
    title: "Install Skilgen",
    body: "free and open source.",
    code: "pip install skilgen",
  },
  {
    number: "02",
    title: "Analyse your repo",
    body: "AST-based domain detection generates SKILL.md files. No config needed.",
  },
  {
    number: "03",
    title: "Score is computed",
    body: "Skilgen Score out of 100 across Groundedness, Coverage, Freshness, Structure.",
  },
  {
    number: "04",
    title: "Skillayer governs",
    body: "Dashboard, CI gates, team rollup, skill registry, and enterprise policies.",
  },
];

const pricingPlans = [
  {
    name: "Free",
    price: "Free",
    suffix: "",
    description: "For individual developers starting with Skilgen.",
    features: [
      "Skilgen CLI + SDK forever free",
      "Unlimited public repos",
      "3 private repos",
      "Skilgen Score badge",
    ],
    cta: "Start free",
  },
  {
    name: "Team",
    price: "$25",
    suffix: "/dev/month",
    description: "For teams standardizing agent readiness.",
    features: [
      "Everything in Free",
      "Unlimited private repos",
      "Full dashboard + team rollup",
      "90-day score history",
      "Slack alerts",
    ],
    cta: "Get started free",
    featured: true,
  },
  {
    name: "Business",
    price: "$45",
    suffix: "/dev/month",
    description: "For organizations adding governance controls.",
    features: [
      "Everything in Team",
      "Process + data skill generation",
      "BYOK LLM config",
      "API access",
      "Priority support",
    ],
    cta: "Talk to sales",
  },
  {
    name: "Enterprise",
    price: "Custom",
    suffix: "",
    description: "For enterprises with security and rollout needs.",
    features: [
      "Everything in Business",
      "SAML SSO + SCIM",
      "Audit log + SIEM export",
      "Policy enforcement engine",
      "Self-hosted option",
      "Dedicated CSM",
    ],
    cta: "Contact sales",
  },
];

function SectionHeading({ label, title, subtitle }: { label: string; title: string; subtitle?: string }) {
  return (
    <div className="mx-auto max-w-[680px] text-center">
      <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--accent-primary)]">
        {label}
      </div>
      <h2 className="text-[36px] font-semibold leading-[1.12] tracking-[-0.02em] text-[color:var(--text-primary)]">
        {title}
      </h2>
      {subtitle ? <p className="mt-3 text-[16px] leading-[1.7] text-[color:var(--text-secondary)]">{subtitle}</p> : null}
    </div>
  );
}

export default function HomePage() {
  return (
    <main className="bg-[color:var(--bg-base)] text-[color:var(--text-primary)]">
      <header className="fixed left-0 right-0 top-0 z-50 h-[60px] bg-[linear-gradient(to_bottom,rgb(var(--bg-base-rgb)/0.9)_0%,rgb(var(--bg-base-rgb)/0)_100%)] px-4 sm:px-8">
        <div className="mx-auto flex h-full max-w-[1100px] items-center justify-between">
          <Link href="/" className="inline-flex items-center" aria-label="Skillayer home">
            <Image src="/skillayer-logo.png" alt="Skillayer" width={36} height={28} className="object-contain" />
            <span className="ml-2 text-[15px] font-bold tracking-[-0.01em] text-[color:var(--text-primary)]">Skillayer</span>
          </Link>

          <nav aria-label="Primary navigation" className="hidden items-center gap-8 md:flex">
            {["Features", "Pricing", "Docs"].map((item) => (
              <Link
                key={item}
                href={`#${item.toLowerCase()}`}
                className="text-[13px] text-[color:var(--text-secondary)] transition-colors hover:text-[color:var(--text-primary)]"
              >
                {item}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-4">
            <Link
              className="text-[13px] text-[color:var(--text-secondary)] transition-colors hover:text-[color:var(--text-primary)]"
              href="https://app.skillayer.com/sign-in"
            >
              Sign in
            </Link>
            <Link
              className="rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]"
              href="https://app.skillayer.com/sign-in"
            >
              Get started free
            </Link>
          </div>
        </div>
      </header>

      <section className="relative h-screen overflow-hidden bg-[color:var(--bg-base)]">
        <HexGrid />
        <div className="absolute inset-0 z-[1] bg-[radial-gradient(ellipse_80%_60%_at_50%_50%,transparent_30%,var(--bg-base)_100%)]" />
        <div className="absolute bottom-0 left-0 right-0 z-[1] h-48 bg-[linear-gradient(to_bottom,rgb(var(--bg-base-rgb)/0),var(--bg-base))]" />

        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center px-6 text-center">
          <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.2)] bg-[rgb(var(--bg-surface-rgb)/0.8)] px-4 py-1.5 text-[12px] text-[color:var(--text-secondary)] backdrop-blur-sm">
            <span className="h-1.5 w-1.5 rounded-full bg-[color:var(--accent-bright)] shadow-[0_0_8px_rgb(var(--accent-bright-rgb)/0.4)]" />
            <span>Now in beta · pip install skilgen</span>
          </div>

          <h1 className="max-w-[820px] text-center text-[clamp(40px,6vw,68px)] font-bold leading-[1.05] tracking-[-0.03em] text-[color:var(--text-primary)] [text-shadow:0_0_80px_rgb(var(--accent-primary-rgb)/0.15)]">
            The institutional knowledge OS
            <br />
            for AI <span className="text-[color:var(--accent-bright)]">agents</span>
          </h1>

          <p className="mt-5 max-w-[520px] text-center text-[18px] leading-[1.7] text-[color:var(--text-secondary)]">
            Generate, score, and govern the skills your agents need to do real work — built from your actual codebase.
          </p>

          <div className="mt-9 flex flex-col justify-center gap-4 sm:flex-row">
            <Link
              className="inline-flex items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-6 py-3 text-[14px] font-bold text-[color:var(--bg-base)] shadow-[0_0_24px_rgb(var(--accent-primary-rgb)/0.25)] transition-colors hover:bg-[color:var(--accent-bright)]"
              href="https://app.skillayer.com/sign-in"
            >
              <Github className="mr-2 h-4 w-4 text-[color:var(--bg-base)]" />
              Start free with GitHub
            </Link>
            <Link
              className="inline-flex items-center justify-center rounded-md border border-[rgb(var(--accent-primary-rgb)/0.25)] bg-transparent px-6 py-3 text-[14px] text-[color:var(--text-secondary)] transition-colors hover:border-[rgb(var(--accent-primary-rgb)/0.5)] hover:text-[color:var(--text-primary)]"
              href="#docs"
            >
              Read the docs
            </Link>
          </div>

          <div className="mt-12 grid w-full max-w-[860px] gap-3 md:grid-cols-3">
            <div className="flex items-center gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[rgb(var(--bg-surface-rgb)/0.6)] px-4 py-2.5 text-left backdrop-blur-sm">
              <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-[color:var(--accent-bright)] shadow-[0_0_6px_var(--accent-bright)]" />
              <div>
                <div className="text-[13px] font-medium text-[color:var(--text-primary)]">38 domains analysed</div>
                <div className="text-[12px] text-[color:var(--text-secondary)]">
                  avg Skilgen Score <span className="text-[color:var(--accent-bright)]">87/100</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[rgb(var(--bg-surface-rgb)/0.6)] px-4 py-2.5 text-left backdrop-blur-sm">
              <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-[color:var(--accent-bright)] shadow-[0_0_6px_var(--accent-bright)]" />
              <div>
                <div className="text-[13px] font-medium text-[color:var(--text-primary)]">Works with 5 agent runtimes</div>
                <div className="text-[12px] text-[color:var(--text-secondary)]">Claude Code · Codex · Cursor · Copilot · Gemini</div>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-lg border border-[color:var(--bg-border)] bg-[rgb(var(--bg-surface-rgb)/0.6)] px-4 py-2.5 text-left backdrop-blur-sm">
              <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-[color:var(--accent-bright)] shadow-[0_0_6px_var(--accent-bright)]" />
              <div>
                <div className="text-[13px] font-medium text-[color:var(--text-primary)]">Open source</div>
                <div className="text-[12px] text-[color:var(--text-secondary)]">pip install skilgen · MIT license</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="bg-[color:var(--bg-base)] px-4 py-24 sm:px-6">
        <div className="mx-auto max-w-[1100px]">
          <SectionHeading label="THE PROBLEM" title="Agents fail without institutional context" />

          <div className="mt-12 grid gap-5 lg:grid-cols-3">
            {problemCards.map((card) => {
              const Icon = card.icon;

              return (
                <article
                  key={card.title}
                  className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 transition-colors hover:border-[color:var(--bg-hover)]"
                >
                  <div className={`mb-4 flex h-10 w-10 items-center justify-center rounded-lg ${card.iconClassName}`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <h3 className="mb-2 text-[15px] font-semibold text-[color:var(--text-primary)]">{card.title}</h3>
                  <p className="text-[14px] leading-[1.6] text-[color:var(--text-secondary)]">{card.body}</p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="bg-[color:var(--bg-base)] px-4 py-24 sm:px-6">
        <div className="mx-auto max-w-[1100px]">
          <SectionHeading label="HOW IT WORKS" title="From codebase to agent-ready in minutes" />

          <div className="mt-12 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {steps.map((step) => (
              <article key={step.number} className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
                <div className="mb-2 text-[40px] font-bold leading-none text-[color:var(--bg-border)]">{step.number}</div>
                <h3 className="mb-2 text-[15px] font-semibold text-[color:var(--text-primary)]">{step.title}</h3>
                <p className="text-[14px] leading-[1.6] text-[color:var(--text-secondary)]">
                  {step.code ? (
                    <>
                      <span className="mr-1 inline-flex rounded border border-[rgb(var(--accent-primary-rgb)/0.3)] bg-[color:var(--bg-surface)] px-2 py-0.5 font-mono text-[12px] text-[color:var(--accent-bright)]">
                        {step.code}
                      </span>
                      {step.body}
                    </>
                  ) : (
                    step.body
                  )}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="pricing" className="bg-[color:var(--bg-base)] px-4 py-24 sm:px-6">
        <div className="mx-auto max-w-[1100px]">
          <SectionHeading
            label="PRICING"
            title="Simple per-developer pricing"
            subtitle="Start free. Scale when your team grows."
          />

          <div className="mt-12 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {pricingPlans.map((plan) => (
              <article
                key={plan.name}
                className={
                  plan.featured
                    ? "relative rounded-xl border border-[rgb(var(--accent-primary-rgb)/0.3)] bg-[linear-gradient(135deg,var(--pricing-gradient-start)_0%,var(--pricing-gradient-end)_100%)] p-6 shadow-[0_0_40px_rgb(var(--accent-primary-rgb)/0.06)]"
                    : "rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6"
                }
              >
                {plan.featured ? (
                  <div className="absolute right-4 top-4 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.3)] bg-[rgb(var(--accent-primary-rgb)/0.15)] px-2.5 py-1 text-[11px] font-semibold tracking-wide text-[color:var(--accent-primary)]">
                    Most popular
                  </div>
                ) : null}

                <div
                  className={
                    plan.featured
                      ? "text-[13px] font-semibold uppercase tracking-wide text-[color:var(--accent-primary)]"
                      : "text-[13px] font-semibold uppercase tracking-wide text-[color:var(--text-secondary)]"
                  }
                >
                  {plan.name}
                </div>
                <div className="mt-2 text-[36px] font-bold leading-tight text-[color:var(--text-primary)]">
                  {plan.price}
                  {plan.suffix ? <span className="text-[14px] font-normal text-[color:var(--text-secondary)]">{plan.suffix}</span> : null}
                </div>
                <p className="mt-2 min-h-11 text-[14px] leading-[1.6] text-[color:var(--text-secondary)]">{plan.description}</p>

                <div className="my-5 h-px bg-[color:var(--bg-border)]" />

                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2">
                      <CheckCircle2
                        className={plan.featured ? "h-[15px] w-[15px] text-[color:var(--accent-primary)]" : "h-[15px] w-[15px] text-[color:var(--accent-green)]"}
                      />
                      <span className="text-[14px] text-[color:var(--text-primary)]">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  className={
                    plan.featured
                      ? "mt-6 inline-flex w-full items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-[14px] font-bold text-[color:var(--bg-base)] shadow-[0_0_16px_rgb(var(--accent-primary-rgb)/0.2)] transition-colors hover:bg-[color:var(--accent-bright)]"
                      : "mt-6 inline-flex w-full items-center justify-center rounded-md border border-[color:var(--bg-border)] px-4 py-2 text-[14px] font-medium text-[color:var(--text-secondary)] transition-colors hover:bg-[color:var(--bg-hover)] hover:text-[color:var(--text-primary)]"
                  }
                  href="https://app.skillayer.com/sign-in"
                >
                  {plan.cta}
                </Link>
              </article>
            ))}
          </div>
        </div>
      </section>

      <footer id="docs" className="border-t border-[color:var(--bg-surface)] bg-[color:var(--bg-base)] px-4 pb-12 pt-16 text-[color:var(--text-tertiary)] sm:px-6">
        <div className="mx-auto max-w-[1100px]">
          <div className="flex flex-col justify-between gap-12 md:flex-row">
            <div>
              <div className="inline-flex items-center">
                <Image src="/skillayer-logo.png" alt="Skillayer" width={36} height={28} className="object-contain" />
                <span className="ml-2 text-[15px] font-bold tracking-[-0.01em] text-[color:var(--text-primary)]">Skillayer</span>
              </div>
              <p className="mt-1 max-w-[280px] text-[13px] leading-[1.6] text-[color:var(--text-tertiary)]">
                The institutional knowledge OS for AI agents
              </p>
            </div>

            <div className="flex gap-16">
              <div>
                <div className="mb-4 text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-primary)]">Product</div>
                {["Features", "Pricing", "Docs", "Changelog"].map((link) => (
                  <Link
                    key={link}
                    className="mb-2 block text-[14px] text-[color:var(--text-tertiary)] transition-colors hover:text-[color:var(--text-secondary)]"
                    href={`#${link.toLowerCase()}`}
                  >
                    {link}
                  </Link>
                ))}
              </div>
              <div>
                <div className="mb-4 text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-primary)]">Company</div>
                {["About", "Blog", "Security", "Privacy"].map((link) => (
                  <Link
                    key={link}
                    className="mb-2 block text-[14px] text-[color:var(--text-tertiary)] transition-colors hover:text-[color:var(--text-secondary)]"
                    href={`#${link.toLowerCase()}`}
                  >
                    {link}
                  </Link>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-12 flex flex-col justify-between gap-4 border-t border-[color:var(--bg-surface)] pt-8 text-[13px] text-[color:var(--text-tertiary)] sm:flex-row">
            <span>© 2026 Skillayer, Inc.</span>
            <span>Built on Skilgen — pip install skilgen</span>
          </div>
        </div>
      </footer>
    </main>
  );
}
