import { withAuth } from "@workos-inc/authkit-nextjs";
import { Check, Mail, ShieldCheck, Sparkles } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { UpgradeButton } from "@/components/upgrade-button";
import { UpgradePageTracker } from "@/components/upgrade-page-tracker";

export const dynamic = "force-dynamic";

type Plan = {
  name: "Free" | "Team" | "Enterprise";
  price: string;
  caption: string;
  features: string[];
  cta: string;
  badge?: string;
};

const plans: Plan[] = [
  {
    name: "Free",
    price: "$0/month",
    caption: "For solo teams proving out Skilgen.",
    features: ["3 repos", "Basic score", "30d analytics"],
    cta: "Current plan",
  },
  {
    name: "Team",
    price: "$49/mo",
    caption: "Per 10 developers. Built for engineering managers and platform teams.",
    badge: "Most Popular",
    features: ["Unlimited repos", "Team rollup", "Slack alerts", "Policy gates", "Audit log", "Priority support"],
    cta: "Upgrade to Team",
  },
  {
    name: "Enterprise",
    price: "Contact Sales",
    caption: "Security, governance, and deployment flexibility for large organizations.",
    features: ["Everything in Team", "SSO/SAML", "BYOK LLM", "Self-hosted", "SLA"],
    cta: "Contact Sales",
  },
];

const comparisonRows = [
  ["Private repositories", "3 repos", "Unlimited", "Unlimited"],
  ["30-day analytics", "Included", "Included", "Included"],
  ["Team rollup", "—", "Included", "Included"],
  ["Governance policies", "—", "Included", "Advanced"],
  ["Audit log", "—", "Included", "Included + export"],
  ["Slack alerts", "—", "Included", "Included"],
  ["BYOK LLM", "—", "—", "Included"],
  ["Self-hosted", "—", "—", "Included"],
];

function CheckRow({ label, free, team, enterprise }: { label: string; free: string; team: string; enterprise: string }) {
  return (
    <div className="grid grid-cols-[minmax(0,1.3fr)_1fr_1fr_1fr] items-center border-t border-[color:var(--bg-border)] px-4 py-4 text-[13px]">
      <div className="font-medium text-[color:var(--text-primary)]">{label}</div>
      <div className="text-[color:var(--text-secondary)]">{free}</div>
      <div className="text-[color:var(--text-secondary)]">{team}</div>
      <div className="text-[color:var(--text-secondary)]">{enterprise}</div>
    </div>
  );
}

export default async function UpgradePage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }

  return (
    <div className="space-y-8">
      <UpgradePageTracker />
      <section className="rounded-[30px] border border-[color:var(--bg-border)] bg-[radial-gradient(circle_at_top,rgba(201,151,58,0.22),rgba(13,13,20,0.97)_48%)] p-8">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.28)] bg-black/20 px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
            <Sparkles className="h-4 w-4" />
            Pricing
          </div>
          <h1 className="mt-5 text-[40px] font-semibold tracking-[-0.03em] text-[color:var(--text-primary)]">Move from repo-level visibility to enterprise-wide governance.</h1>
          <p className="mt-3 max-w-2xl text-[15px] leading-7 text-[color:var(--text-secondary)]">Free gets you started. Team gives engineering leaders live rollups and policy gates. Enterprise unlocks security, compliance, and deployment control for serious platform programs.</p>
        </div>
      </section>

      <SectionErrorBoundary section="pricing plans">
        <section className="grid gap-5 xl:grid-cols-3">
          {plans.map((plan) => (
            <article
              className={
                plan.name === "Team"
                  ? "relative rounded-[28px] border border-[#C9973A] bg-[linear-gradient(180deg,rgba(201,151,58,0.18),rgba(255,255,255,0.03))] p-6 shadow-[0_28px_80px_rgba(201,151,58,0.18)]"
                  : "rounded-[28px] border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-6"
              }
              key={plan.name}
            >
              {plan.badge ? <span className="absolute right-5 top-5 rounded-full bg-[#C9973A] px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] text-black">{plan.badge}</span> : null}
              <div className="mb-6">
                <h2 className="text-[22px] font-semibold text-[color:var(--text-primary)]">{plan.name}</h2>
                <div className="mt-4 text-[38px] font-semibold leading-none text-white">{plan.price}</div>
                <p className="mt-3 text-[14px] leading-6 text-[color:var(--text-secondary)]">{plan.caption}</p>
              </div>
              <ul className="mb-8 space-y-3">
                {plan.features.map((feature) => (
                  <li className="flex items-start gap-3 text-[14px] text-[color:var(--text-secondary)]" key={feature}>
                    <span className="mt-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-[rgb(var(--accent-primary-rgb)/0.14)]">
                      <Check className="h-3.5 w-3.5 text-[color:var(--accent-primary)]" />
                    </span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              {plan.name === "Free" ? (
                <button className="inline-flex h-12 w-full cursor-not-allowed items-center justify-center rounded-full border border-[color:var(--bg-border)] text-[14px] font-semibold text-[color:var(--text-tertiary)]" disabled type="button">
                  {plan.cta}
                </button>
              ) : null}
              {plan.name === "Team" ? <UpgradeButton accessToken={accessToken} label={plan.cta} plan="team" /> : null}
              {plan.name === "Enterprise" ? (
                <a className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-full border border-[#C9973A]/60 text-[14px] font-semibold text-[#C9973A] hover:bg-[#C9973A]/10" href="mailto:sales@skillayer.com?subject=Skillayer%20Enterprise%20Inquiry">
                  <Mail className="h-4 w-4" />
                  {plan.cta}
                </a>
              ) : null}
            </article>
          ))}
        </section>
      </SectionErrorBoundary>

      <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <div className="mb-5 flex items-center gap-3">
          <ShieldCheck className="h-5 w-5 text-[color:var(--accent-primary)]" />
          <h2 className="text-[22px] font-semibold text-[color:var(--text-primary)]">Feature comparison</h2>
        </div>
        <div className="overflow-hidden rounded-2xl border border-[color:var(--bg-border)]">
          <div className="grid grid-cols-[minmax(0,1.3fr)_1fr_1fr_1fr] bg-black/20 px-4 py-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">
            <span>Capability</span>
            <span>Free</span>
            <span>Team</span>
            <span>Enterprise</span>
          </div>
          {comparisonRows.map(([label, free, team, enterprise]) => (
            <CheckRow enterprise={enterprise} free={free} key={label} label={label} team={team} />
          ))}
        </div>
      </section>
    </div>
  );
}
