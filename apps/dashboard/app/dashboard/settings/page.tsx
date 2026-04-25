import Link from "next/link";
import type { ReactElement } from "react";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { Bell, Brain, CreditCard, Github, RadioTower, Settings, ShieldAlert } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import {
  API_URL,
  getBootstrapOrg,
  getLLMConfig,
  getMyOrg,
  getOrgPolicies,
  getOrgSettings,
  getPolicies,
  getPolicyTemplates,
  runPolicyCheck,
  type GovernancePoliciesResponse,
  type LLMConfig,
  type OrgSettings,
  type PolicyCheckResult,
  type PolicyRule,
} from "../../../lib/data";
import { ManageBillingButton } from "./billing/manage-billing-button";
import { LlmSettingsPanel, PolicySettingsPanel, SiemSettingsPanel } from "./enterprise-settings";
import { SettingsControls } from "./settings-controls";

export const dynamic = "force-dynamic";

type SettingsPageProps = {
  searchParams: Promise<{ tab?: string | string[]; success?: string | string[]; plan?: string | string[] }>;
};

type SubscriptionState = {
  plan: "free" | "team" | "business";
  status: "active" | "past_due" | "canceled" | null;
  seat_count: number;
  seat_limit: number;
  stripe_customer_id: string | null;
};

const tabs = [
  { key: "general", label: "General", icon: Settings },
  { key: "notifications", label: "Notifications", icon: Bell },
  { key: "llm", label: "LLM", icon: Brain },
  { key: "policies", label: "Policies", icon: ShieldAlert },
  { key: "siem", label: "SIEM", icon: RadioTower },
  { key: "github", label: "GitHub App", icon: Github },
  { key: "billing", label: "Billing", icon: CreditCard },
] as const;

type SettingsTab = (typeof tabs)[number]["key"];

/**
 * Loads the current org subscription from the Skillayer API.
 */
async function getSubscription(accessToken: string): Promise<SubscriptionState | null> {
  const res = await fetch(`${API_URL}/stripe/subscription`, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    next: { revalidate: 0 },
  });
  if (!res.ok) return null;
  return res.json();
}

/**
 * Formats settings labels for display.
 */
function label(value: string | null | undefined): string {
  if (!value) return "free";
  return value.slice(0, 1).toUpperCase() + value.slice(1);
}

/**
 * Returns a valid settings tab from the current URL state.
 */
function selectedTab(value: string | string[] | undefined): SettingsTab {
  const tab = Array.isArray(value) ? value[0] : value;
  return tabs.some((item) => item.key === tab) ? (tab as SettingsTab) : "general";
}

/**
 * Builds fallback settings so the page remains useful when preview auth is unavailable.
 */
function fallbackSettings(): OrgSettings {
  return {
    id: "org_01",
    login: "skillayer",
    name: "Skillayer",
    plan: "business",
    score_threshold: 60,
    slack_webhook_url: null,
    notify_on_pr: true,
    notify_on_stale: true,
    github_app_installed: false,
    github_installation_id: null,
    webhook_url: "/webhook/github",
    recent_deliveries: [],
  };
}

/**
 * Renders the unified organization settings surface.
 */
export default async function SettingsPage({ searchParams }: SettingsPageProps): Promise<ReactElement> {
  const resolvedSearchParams = await searchParams;
  const tab = selectedTab(resolvedSearchParams.tab);
  const success = (Array.isArray(resolvedSearchParams.success) ? resolvedSearchParams.success[0] : resolvedSearchParams.success) === "true";
  const upgradedPlan = Array.isArray(resolvedSearchParams.plan) ? resolvedSearchParams.plan[0] : resolvedSearchParams.plan;
  let accessToken = "";
  let settings = fallbackSettings();
  let subscription: SubscriptionState | null = null;
  let policies: GovernancePoliciesResponse = { policies: [] };
  let policyRules: PolicyRule[] = [];
  let policyTemplates: PolicyRule[] = [];
  let policyCheck: PolicyCheckResult | null = null;
  let llmConfig: LLMConfig | null = null;

  try {
    const session = await withAuth({ ensureSignedIn: true });
    accessToken = session.accessToken || "";
    const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
    if (org) {
      settings = (await getOrgSettings(accessToken, org.id)) ?? { ...settings, ...org };
      policies = (await getOrgPolicies(accessToken, org.id)) ?? policies;
      policyRules = await getPolicies(accessToken, org.id);
      policyTemplates = await getPolicyTemplates(accessToken, org.id);
      policyCheck = await runPolicyCheck(accessToken, org.id);
      llmConfig = await getLLMConfig(accessToken, org.id);
    }
    subscription = await getSubscription(accessToken);
  } catch {
    const org = await getBootstrapOrg();
    if (org) {
      settings = (await getOrgSettings("", org.id)) ?? { ...settings, ...org };
      policies = (await getOrgPolicies("", org.id)) ?? policies;
      policyRules = await getPolicies("", org.id);
      policyTemplates = await getPolicyTemplates("", org.id);
      llmConfig = await getLLMConfig("", org.id);
    }
    subscription = null;
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Settings</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Manage workspace quality gates, notifications, integrations, and billing.</p>
      </div>

      <div className="mb-6 flex flex-wrap gap-2 border-b border-[color:var(--bg-border)] pb-2">
        {tabs.map((item) => {
          const Icon = item.icon;
          const active = item.key === tab;
          return (
            <Link
              className={
                active
                  ? "inline-flex h-9 items-center rounded-md bg-[#C9973A] px-3 text-[13px] font-semibold text-black"
                  : "inline-flex h-9 items-center rounded-md px-3 text-[13px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:bg-[color:var(--bg-surface)] hover:text-[color:var(--text-primary)]"
              }
              href={`/dashboard/settings?tab=${item.key}`}
              key={item.key}
            >
              <Icon className="mr-2 h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </div>

      <SectionErrorBoundary section={`${tab} settings`}>
        {tab === "general" || tab === "notifications" ? (
          <SettingsControls accessToken={accessToken} initialPolicies={policies.policies} initialSettings={settings} orgId={settings.id} tab={tab} />
        ) : null}
        {tab === "llm" ? <LlmSettingsPanel accessToken={accessToken} initialConfig={llmConfig} orgId={settings.id} /> : null}
        {tab === "policies" ? <PolicySettingsPanel accessToken={accessToken} initialCheck={policyCheck} initialPolicies={policyRules} orgId={settings.id} templates={policyTemplates} /> : null}
        {tab === "siem" ? <SiemSettingsPanel accessToken={accessToken} orgId={settings.id} /> : null}
        {tab === "github" ? <GitHubSettingsPanel settings={settings} /> : null}
        {tab === "billing" ? <BillingPanel accessToken={accessToken} success={success} subscription={subscription} upgradedPlan={upgradedPlan} /> : null}
      </SectionErrorBoundary>
    </div>
  );
}

/**
 * Renders GitHub App installation and webhook delivery state.
 */
function GitHubSettingsPanel({ settings }: { settings: OrgSettings }): ReactElement {
  return (
    <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">GitHub App</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Installation health and incoming webhook activity.</p>
        </div>
        <span className={settings.github_app_installed ? "rounded-full bg-[#3dd68c]/15 px-3 py-1 text-[13px] font-semibold text-[#3dd68c]" : "rounded-full bg-[color:var(--bg-border)] px-3 py-1 text-[13px] font-semibold text-[color:var(--text-tertiary)]"}>
          {settings.github_app_installed ? "Installed" : "Not installed"}
        </span>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[#08080d] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Installation ID</div>
          <div className="mt-2 font-mono text-[14px] text-white">{settings.github_installation_id ?? "None"}</div>
        </div>
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[#08080d] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Webhook URL</div>
          <div className="mt-2 truncate font-mono text-[13px] text-[color:var(--text-secondary)]">{settings.webhook_url}</div>
        </div>
      </div>

      <div className="mt-6 overflow-hidden rounded-lg border border-[color:var(--bg-border)]">
        <div className="grid grid-cols-[1fr_110px_150px] bg-[#08080d] px-4 py-3 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">
          <span>Delivery</span>
          <span>Status</span>
          <span>Received</span>
        </div>
        {settings.recent_deliveries.length ? (
          settings.recent_deliveries.map((delivery) => (
            <div className="grid grid-cols-[1fr_110px_150px] border-t border-[color:var(--bg-border)] px-4 py-3 text-[13px]" key={delivery.id}>
              <span className="font-mono text-[color:var(--text-secondary)]">{delivery.trigger}</span>
              <span className="text-[color:var(--text-primary)]">{label(delivery.status)}</span>
              <span className="truncate text-[color:var(--text-tertiary)]">{delivery.created_at ? new Date(delivery.created_at).toLocaleString() : "Unknown"}</span>
            </div>
          ))
        ) : (
          <div className="border-t border-[color:var(--bg-border)] px-4 py-5 text-[13px] text-[color:var(--text-tertiary)]">No recent deliveries.</div>
        )}
      </div>
    </section>
  );
}

/**
 * Renders billing state and plan management actions.
 */
function BillingPanel({
  accessToken,
  success,
  subscription,
  upgradedPlan,
}: {
  accessToken: string;
  success: boolean;
  subscription: SubscriptionState | null;
  upgradedPlan: string | undefined;
}): ReactElement {
  const plan = subscription?.plan ?? "free";
  const status = subscription?.status ?? null;
  const seatCount = subscription?.seat_count ?? 0;
  const seatLimit = subscription?.seat_limit ?? 3;

  return (
    <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      {success ? (
        <div className="mb-6 rounded-lg border border-[#C9973A]/40 bg-[#C9973A]/10 px-5 py-4 text-[14px] font-medium text-[#f3d28e]">
          Welcome to {label(upgradedPlan || plan)}! Your plan has been upgraded.
        </div>
      ) : null}

      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Billing</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Billing details update automatically after Stripe events are processed.</p>
        </div>
        <span className="rounded-full bg-[#C9973A]/15 px-3 py-1 text-[13px] font-semibold text-[#C9973A]">{label(plan)}</span>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[#08080d] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Seats</div>
          <div className="mt-2 text-[24px] font-bold text-white">
            {seatCount}
            <span className="text-[13px] font-medium text-[color:var(--text-tertiary)]"> / {seatLimit >= 999999 ? "unlimited" : seatLimit}</span>
          </div>
        </div>
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[#08080d] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Status</div>
          <div className="mt-2 text-[24px] font-bold text-white">{status ? label(status) : "None"}</div>
        </div>
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[#08080d] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Billing account</div>
          <div className="mt-2 truncate font-mono text-[13px] text-[color:var(--text-secondary)]">{subscription?.stripe_customer_id ?? "Not connected"}</div>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <ManageBillingButton accessToken={accessToken} disabled={!subscription?.stripe_customer_id} />
        <Link className="inline-flex items-center rounded-md bg-[#C9973A] px-4 py-2 text-sm font-semibold text-black transition-colors hover:bg-[#d7aa55]" href="/dashboard/upgrade">
          Upgrade plan
        </Link>
      </div>
    </section>
  );
}
