"use client";

import type { ReactElement } from "react";
import { useEffect } from "react";

import { initPostHog } from "@/lib/posthog";

/** Initializes production-only PostHog tracking from the root layout. */
export function PostHogProvider(): ReactElement | null {
  useEffect(() => {
    initPostHog();
  }, []);

  return null;
}
