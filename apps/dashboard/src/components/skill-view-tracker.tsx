"use client";

import type { ReactElement } from "react";
import { useEffect } from "react";

import { captureDashboardEvent } from "@/lib/posthog";

type SkillViewTrackerProps = {
  domain: string;
  repo: string;
};

/** Tracks skill detail page views with domain and repository context. */
export function SkillViewTracker({ domain, repo }: SkillViewTrackerProps): ReactElement | null {
  useEffect(() => {
    captureDashboardEvent({ name: "skill_viewed", properties: { domain, repo } });
  }, [domain, repo]);

  return null;
}
