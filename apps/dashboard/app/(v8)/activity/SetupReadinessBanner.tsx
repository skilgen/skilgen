import Link from "next/link";
import { ArrowRight } from "lucide-react";

import type { SetupStatus } from "../../../lib/data";

export function SetupReadinessBanner({ setupStatus }: { setupStatus: SetupStatus | null }) {
  if (!setupStatus || setupStatus.completion_percent >= 100) return null;

  const percent = Math.max(0, Math.min(100, setupStatus.completion_percent));
  const nextActionUrl = setupStatus.next_action_url ?? "/skills/repos";

  return (
    <section className="rounded-lg border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[rgb(var(--accent-primary-rgb)/0.07)] p-4">
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_260px] lg:items-center">
        <div className="min-w-0">
          <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--accent-primary)]">Setup readiness</div>
          <h2 className="mt-1 text-[18px] font-semibold text-[color:var(--text-primary)]">{setupStatus.next_step_title ?? "Finish setup"}</h2>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-[color:var(--text-secondary)]">
            {setupStatus.next_step_guidance ?? "Complete the next setup step to unlock live governance activity."}
          </p>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-3 text-xs font-semibold text-[color:var(--text-secondary)]">
            <span>{setupStatus.completion_label}</span>
            <span className="text-[color:var(--text-primary)]">{percent}%</span>
          </div>
          <div
            aria-label="Setup readiness completion"
            aria-valuemax={100}
            aria-valuemin={0}
            aria-valuenow={percent}
            className="h-2 overflow-hidden rounded-full bg-black/30"
            role="progressbar"
          >
            <div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${percent}%` }} />
          </div>
          <Link className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]" href={nextActionUrl}>
            Continue setup
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </section>
  );
}
