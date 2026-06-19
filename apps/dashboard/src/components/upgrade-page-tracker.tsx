"use client";

import type { ReactElement } from "react";
import { useEffect } from "react";

import { captureDashboardEvent } from "@/lib/posthog";

/** Tracks upgrade page impressions after the dashboard analytics client is ready. */
export function UpgradePageTracker(): ReactElement | null {
  useEffect(() => {
    captureDashboardEvent({ name: "upgrade_page_viewed", properties: {} });
  }, []);

  return null;
}
