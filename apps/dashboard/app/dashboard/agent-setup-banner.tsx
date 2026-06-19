"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, X, Zap } from "lucide-react";

const DISMISS_KEY = "skillayer-agent-setup-banner-dismissed";

export function AgentSetupBanner() {
  const [dismissed, setDismissed] = useState(true);

  useEffect(() => {
    setDismissed(localStorage.getItem(DISMISS_KEY) === "true");
  }, []);

  if (dismissed) return null;

  return (
    <section className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div className="flex gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-amber-500/30 bg-amber-500/10 text-amber-200">
            <Zap className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-[17px] font-semibold text-[color:var(--text-primary)]">Connect your AI agent to unlock usage analytics</h2>
            <p className="mt-1 max-w-3xl text-[14px] leading-6 text-[color:var(--text-secondary)]">
              Skills are generated but no agent loads have been tracked. Once connected, you&apos;ll see which skills agents rely on, which are dangerously stale, and your AI productivity trend.
            </p>
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <Link className="inline-flex items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-[13px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]" href="/dashboard/connect">
            Connect agent
            <ArrowRight className="h-4 w-4" />
          </Link>
          <button
            aria-label="Dismiss connect agent banner"
            className="inline-flex h-9 w-9 items-center justify-center rounded-md text-[color:var(--text-tertiary)] hover:bg-white/5 hover:text-[color:var(--text-primary)]"
            onClick={() => {
              localStorage.setItem(DISMISS_KEY, "true");
              setDismissed(true);
            }}
            type="button"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </section>
  );
}
