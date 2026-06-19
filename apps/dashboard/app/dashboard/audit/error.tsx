"use client";

import { DashboardRouteError } from "@/components/dashboard-route-error";

export default function AuditError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <DashboardRouteError error={error} reset={reset} section="audit" />;
}
