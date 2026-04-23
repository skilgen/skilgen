"use client";

import { useState } from "react";

import { captureDashboardEvent } from "@/lib/posthog";
import { createCheckoutSession } from "../../lib/stripe";

type UpgradeButtonProps = {
  accessToken: string;
  label: string;
  plan: "team" | "business";
};

/**
 * Captures paid plan seat count and redirects the user to Stripe Checkout.
 */
export function UpgradeButton({ accessToken, label, plan }: UpgradeButtonProps) {
  const [seatCount, setSeatCount] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const canUpgrade = accessToken.length > 0;

  async function handleUpgrade() {
    if (!canUpgrade) {
      setError("Sign in is required to start checkout");
      return;
    }

    setError(null);
    setIsLoading(true);
    try {
      captureDashboardEvent({ name: "checkout_started", properties: { plan, seat_count: seatCount } });
      const checkoutUrl = await createCheckoutSession(plan, seatCount, accessToken);
      window.location.assign(checkoutUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to start checkout");
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <label className="block text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">
        Seats
        <input
          aria-label={`Seat count for ${plan}`}
          className="mt-1 w-full rounded-md border border-[color:var(--bg-border)] bg-[#08080d] px-3 py-2 text-[14px] font-semibold text-[color:var(--text-primary)] outline-none transition-colors focus:border-[#C9973A]"
          min={1}
          onChange={(event) => setSeatCount(Math.max(1, Number(event.target.value) || 1))}
          type="number"
          value={seatCount}
        />
      </label>
      <button
        className="inline-flex w-full items-center justify-center rounded-md bg-[#C9973A] px-4 py-2.5 text-[14px] font-semibold text-black transition-colors hover:bg-[#d7aa55] disabled:cursor-not-allowed disabled:opacity-60"
        disabled={isLoading || !canUpgrade}
        onClick={handleUpgrade}
        type="button"
      >
        {isLoading ? "Opening checkout..." : canUpgrade ? label : "Sign in required"}
      </button>
      {error ? <p className="text-[12px] text-red-400">{error}</p> : null}
    </div>
  );
}
