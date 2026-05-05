import Link from "next/link";
import { CreditCard } from "lucide-react";

import { Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";

type Billing = {
  plan: string;
  seat_count: number;
  seat_limit: number;
  stripe_customer_id: string | null;
  stripe_subscription_status: string | null;
};

function label(value: string | null | undefined): string {
  if (!value) return "None";
  return value.slice(0, 1).toUpperCase() + value.slice(1).replaceAll("_", " ");
}

export default async function BillingSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const billing = await v8Fetch<Billing>(accessToken, org.id, "/billing");
  const plan = billing?.plan ?? org.plan ?? "free";

  return (
    <SettingsShell active="Billing">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Plan" value={label(plan)} sub="Existing billing behavior preserved" />
        <Metric label="Seats" value={`${billing?.seat_count ?? 0}/${billing?.seat_limit ?? 3}`} sub="Usage display only" />
        <Metric label="Subscription" value={label(billing?.stripe_subscription_status)} sub="Stripe state from org fields" />
      </div>

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-start gap-3">
            <CreditCard className="mt-0.5 h-5 w-5 text-[color:var(--accent-primary)]" />
            <div>
              <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Billing</h2>
              <p className="mt-1 text-sm text-[color:var(--text-secondary)]">This v8 route composes the existing billing state without editing billing handlers.</p>
            </div>
          </div>
          <Link className="inline-flex items-center justify-center rounded-[8px] border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold text-[color:var(--text-primary)]" href="/dashboard/settings?tab=billing">
            Open legacy billing controls
          </Link>
        </div>
        <div className="mt-5 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Stripe customer</div>
          <div className="mt-2 truncate font-mono text-sm text-[color:var(--text-primary)]">{billing?.stripe_customer_id ?? "Not connected"}</div>
        </div>
      </section>
    </SettingsShell>
  );
}
