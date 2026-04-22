"use client";

import { useState } from "react";

import { createPortalSession } from "../../../../lib/stripe";

type ManageBillingButtonProps = {
  accessToken: string;
  disabled?: boolean;
};

export function ManageBillingButton({ accessToken, disabled = false }: ManageBillingButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setError(null);
    setIsLoading(true);
    try {
      const portalUrl = await createPortalSession(accessToken);
      window.location.assign(portalUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to open billing portal");
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-2">
      <button
        className="inline-flex items-center rounded-md bg-[#C9973A] px-4 py-2 text-sm font-semibold text-black transition-colors hover:bg-[#d7aa55] disabled:cursor-not-allowed disabled:opacity-50"
        disabled={disabled || isLoading}
        onClick={handleClick}
        type="button"
      >
        {isLoading ? "Opening..." : "Manage billing"}
      </button>
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
    </div>
  );
}
