import { withAuth } from "@workos-inc/authkit-nextjs";
import { Mail } from "lucide-react";

import { UpgradeButton } from "@/components/upgrade-button";

export const dynamic = "force-dynamic";

const plans = [
  {
    name: "Free",
    price: "$0",
    cadence: "",
    features: ["Skilgen CLI forever free", "Unlimited public repos", "3 private repos", "Skilgen Score badge"],
  },
  {
    name: "Team",
    price: "$25",
    cadence: "/dev/month",
    highlighted: true,
    features: [
      "Everything in Free",
      "Unlimited private repos",
      "Full dashboard + team rollup",
      "90-day score history",
      "PR comment engine",
      "Slack alerts",
    ],
  },
  {
    name: "Business",
    price: "$45",
    cadence: "/dev/month",
    features: ["Everything in Team", "Process + data skill generation", "BYOK LLM config", "API access", "Priority support"],
  },
  {
    name: "Enterprise",
    price: "Custom",
    cadence: "",
    features: [
      "Everything in Business",
      "SAML SSO + SCIM",
      "Audit log + SIEM export",
      "Policy enforcement engine",
      "Self-hosted option",
      "Dedicated CSM",
    ],
  },
];

/**
 * Renders the self-serve pricing page inside the authenticated dashboard.
 */
export default async function UpgradePage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: true });
    accessToken = session.accessToken || "";
  } catch {
    accessToken = "";
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Upgrade</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Choose the plan that matches your team&apos;s AI-readiness workflow.</p>
      </div>

      <div className="grid gap-5 xl:grid-cols-4">
        {plans.map((plan) => (
          <article
            className={
              plan.highlighted
                ? "rounded-xl border border-[#C9973A] bg-[linear-gradient(180deg,rgba(201,151,58,0.14),rgba(255,255,255,0.03))] p-5 shadow-[0_0_28px_rgba(201,151,58,0.16)]"
                : "rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"
            }
            key={plan.name}
          >
            <div className="mb-5">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">{plan.name}</h2>
                {plan.highlighted ? <span className="rounded-full bg-[#C9973A] px-2 py-0.5 text-[11px] font-bold text-black">Best fit</span> : null}
              </div>
              <div className="mt-4 flex items-end gap-1">
                <span className="text-[34px] font-bold leading-none text-white">{plan.price}</span>
                {plan.cadence ? <span className="text-[13px] text-[color:var(--text-tertiary)]">{plan.cadence}</span> : null}
              </div>
            </div>

            <ul className="mb-6 space-y-3 text-[13px] leading-5 text-[color:var(--text-secondary)]">
              {plan.features.map((feature) => (
                <li className="flex gap-2" key={feature}>
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-[#C9973A]" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>

            {plan.name === "Free" ? (
              <button
                className="w-full cursor-not-allowed rounded-md border border-[color:var(--bg-border)] px-4 py-2.5 text-[14px] font-semibold text-[color:var(--text-tertiary)]"
                disabled
                type="button"
              >
                Current plan
              </button>
            ) : plan.name === "Team" ? (
              <UpgradeButton accessToken={accessToken} label="Upgrade to Team" plan="team" />
            ) : plan.name === "Business" ? (
              <UpgradeButton accessToken={accessToken} label="Upgrade to Business" plan="business" />
            ) : (
              <a
                className="inline-flex w-full items-center justify-center rounded-md border border-[#C9973A]/60 px-4 py-2.5 text-[14px] font-semibold text-[#C9973A] transition-colors hover:bg-[#C9973A]/10"
                href="mailto:sales@skillayer.com"
              >
                <Mail className="mr-2 h-4 w-4" />
                Contact sales
              </a>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}
