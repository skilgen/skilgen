"use client";

import posthog from "posthog-js";

type AnalyticsEvent =
  | { name: "upgrade_page_viewed"; properties?: Record<string, never> }
  | { name: "checkout_started"; properties: { plan: "team" | "business"; seat_count: number } }
  | { name: "skill_viewed"; properties: { domain: string; repo: string } }
  | { name: "skill_content_copied"; properties: { domain: string } }
  | { name: "repo_analyse_triggered"; properties?: Record<string, never> };

let initialized = false;

/** Initialize PostHog only for production browser sessions with a configured key. */
export function initPostHog(): void {
  if (initialized || process.env.NODE_ENV !== "production") return;

  const key = process.env.NEXT_PUBLIC_POSTHOG_KEY;
  if (!key) return;

  posthog.init(key, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://app.posthog.com",
    capture_pageview: false,
  });
  initialized = true;
}

/** Capture a typed dashboard analytics event when PostHog is active. */
export function captureDashboardEvent(event: AnalyticsEvent): void {
  if (!initialized) return;
  posthog.capture(event.name, event.properties);
}
