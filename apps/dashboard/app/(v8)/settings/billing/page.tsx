import Link from "next/link";
import { AlertTriangle, CheckCircle2, CreditCard, ExternalLink, Gauge, Users } from "lucide-react";

import { Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";

type Billing = {
  plan: string;
  seat_count: number;
  seat_limit: number;
  seat_limit_label: string;
  available_seats: number | null;
  seat_utilization_pct: number;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  stripe_subscription_status: string | null;
  subscription_state: string;
  billing_account_connected: boolean;
  portal_available: boolean;
  needs_attention: boolean;
  next_actions: string[];
};

function label(value: string | null | undefined): string {
  if (!value) return "None";
  return value.slice(0, 1).toUpperCase() + value.slice(1).replaceAll("_", " ");
}

function compactId(value: string | null | undefined): string {
  if (!value) return "Not connected";
  return value.length > 12 ? `${value.slice(0, 6)}...${value.slice(-4)}` : value;
}

function actionLabel(value: string): string {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default async function BillingSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const billing = await v8Fetch<Billing>(accessToken, org.id, "/billing");
  const billingAvailable = billing !== null;
  const fallbackBilling: Billing = {
    plan: org.plan ?? "free",
    seat_count: 0,
    seat_limit: 3,
    seat_limit_label: "3",
    available_seats: null,
    seat_utilization_pct: 0,
    stripe_customer_id: null,
    stripe_subscription_id: null,
    stripe_subscription_status: null,
    subscription_state: "unavailable",
    billing_account_connected: false,
    portal_available: false,
    needs_attention: true,
    next_actions: ["billing_api_unavailable"],
  };
  const current = billing ?? fallbackBilling;
  const plan = current.plan;
  const utilization = current.seat_utilization_pct;
  const needsAttention = current.needs_attention;
  const nextActions = current.next_actions.length ? current.next_actions : ["monitor_usage"];
  const availableSeats = billingAvailable ? current.available_seats ?? "Unlimited" : "Unknown";
  const statusLabel = billingAvailable ? (needsAttention ? "Attention needed" : "Ready") : "Unavailable";
  const usedSeats = billingAvailable ? current.seat_count : "Unknown";
  const seatLimit = billingAvailable ? current.seat_limit_label : "Unknown";
  const utilizationLabel = billingAvailable ? `${utilization}%` : "Unknown";
  const customerReference = billingAvailable ? compactId(current.stripe_customer_id) : "Unavailable";
  const subscriptionReference = billingAvailable ? compactId(current.stripe_subscription_id) : "Unavailable";

  return (
    <SettingsShell active="Billing">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Plan" value={label(plan)} sub={billingAvailable ? (needsAttention ? "Review required" : "Current workspace plan") : "Live billing unavailable"} />
        <Metric label="Seats" value={billingAvailable ? `${current.seat_count}/${current.seat_limit_label}` : "Unavailable"} sub={billingAvailable ? `${utilization}% utilized` : "Waiting for billing API"} />
        <Metric label="Subscription" value={label(current.subscription_state)} sub={billingAvailable ? (current.billing_account_connected ? "Stripe account linked" : "No Stripe customer") : "Live billing unavailable"} />
      </div>

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="border-b border-[color:var(--bg-border)] p-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-start gap-3">
              <CreditCard className="mt-0.5 h-5 w-5 text-[color:var(--accent-primary)]" />
              <div>
                <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Billing readiness</h2>
                <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Plan, seats, and Stripe state for the governance plane.</p>
              </div>
            </div>
            <span className={`inline-flex w-fit items-center gap-2 rounded-full px-3 py-1 text-[12px] font-semibold ${needsAttention ? "bg-amber-500/15 text-amber-100" : "bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]"}`}>
              {needsAttention ? <AlertTriangle className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
              {statusLabel}
            </span>
          </div>
        </div>

        <div className="grid gap-4 p-5 lg:grid-cols-[minmax(0,1fr)_320px]">
          <div className="space-y-4">
            <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2 text-sm font-semibold text-[color:var(--text-primary)]">
                  <Gauge className="h-4 w-4 text-[color:var(--accent-primary)]" />
                  Seat utilization
                </div>
                <span className="text-[12px] font-semibold text-[color:var(--text-tertiary)]">{utilizationLabel}</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-[color:var(--bg-surface)]">
                <div className={needsAttention ? "h-full bg-amber-400" : "h-full bg-[color:var(--accent-primary)]"} style={{ width: `${Math.min(utilization, 100)}%` }} />
              </div>
              <div className="mt-3 grid gap-3 sm:grid-cols-3">
                <div>
                  <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Used</div>
                  <div className="mt-1 text-lg font-semibold text-[color:var(--text-primary)]">{usedSeats}</div>
                </div>
                <div>
                  <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Limit</div>
                  <div className="mt-1 text-lg font-semibold text-[color:var(--text-primary)]">{seatLimit}</div>
                </div>
                <div>
                  <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Available</div>
                  <div className="mt-1 text-lg font-semibold text-[color:var(--text-primary)]">{availableSeats}</div>
                </div>
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-[color:var(--text-primary)]">
                  <Users className="h-4 w-4 text-[color:var(--accent-primary)]" />
                  Subscription
                </div>
                <div className="mt-3 space-y-3 text-sm">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-[color:var(--text-secondary)]">State</span>
                    <span className="font-semibold text-[color:var(--text-primary)]">{label(current.subscription_state)}</span>
                  </div>
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-[color:var(--text-secondary)]">Portal</span>
                    <span className="font-semibold text-[color:var(--text-primary)]">{billingAvailable && current.portal_available ? "Available" : "Unavailable"}</span>
                  </div>
                </div>
              </div>

              <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
                <div className="text-sm font-semibold text-[color:var(--text-primary)]">Stripe references</div>
                <div className="mt-3 space-y-3 text-sm">
                  <div>
                    <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Customer</div>
                    <div className="mt-1 truncate font-mono text-[color:var(--text-primary)]">{customerReference}</div>
                  </div>
                  <div>
                    <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Subscription</div>
                    <div className="mt-1 truncate font-mono text-[color:var(--text-primary)]">{subscriptionReference}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <aside className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
            <div className="text-[12px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Next actions</div>
            <div className="mt-3 space-y-2">
              {nextActions.map((action) => (
                <div className="flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-2 text-sm text-[color:var(--text-primary)]" key={action}>
                  {action === "monitor_usage" ? <CheckCircle2 className="h-4 w-4 text-[color:var(--accent-green)]" /> : <AlertTriangle className="h-4 w-4 text-amber-100" />}
                  <span>{actionLabel(action)}</span>
                </div>
              ))}
            </div>
            <Link className="mt-4 inline-flex h-9 w-full items-center justify-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-primary)]" href="/dashboard/settings?tab=billing" prefetch={false}>
              Billing controls
              <ExternalLink className="h-3.5 w-3.5" />
            </Link>
          </aside>
        </div>
      </section>
    </SettingsShell>
  );
}
