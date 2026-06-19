"use client";

import type { ReactElement } from "react";
import { useEffect } from "react";

import { SectionFallback } from "./section-fallback";

type DashboardRouteErrorProps = {
  error: Error & { digest?: string };
  reset: () => void;
  section: string;
};

/** Route-segment error UI for dashboard pages. */
export function DashboardRouteError({ error, reset, section }: DashboardRouteErrorProps): ReactElement {
  useEffect(() => {
    console.error(
      JSON.stringify({
        scope: "dashboard.route",
        event: "render_error",
        section,
        message: error.message,
        digest: error.digest ?? null,
      }),
    );
  }, [error, section]);

  return (
    <div className="space-y-4">
      <SectionFallback section={section} />
      <button
        className="inline-flex rounded-md border border-[rgb(var(--accent-primary-rgb)/0.45)] px-4 py-2 text-sm font-semibold text-[color:var(--accent-primary)] transition-colors hover:bg-[rgb(var(--accent-primary-rgb)/0.12)]"
        onClick={reset}
        type="button"
      >
        Try again
      </button>
    </div>
  );
}
