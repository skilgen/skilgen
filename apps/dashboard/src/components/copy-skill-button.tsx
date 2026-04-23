"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";

import { captureDashboardEvent } from "@/lib/posthog";

/** Copy the raw SKILL.md content and briefly confirm the action. */
export function CopySkillButton({ content, domain }: { content: string; domain: string }) {
  const [copied, setCopied] = useState(false);

  /** Write the skill content to the clipboard and reset the success state. */
  async function handleCopy() {
    await navigator.clipboard.writeText(content);
    captureDashboardEvent({ name: "skill_content_copied", properties: { domain } });
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  }

  return (
    <button
      className="inline-flex items-center rounded-md border border-[rgb(var(--accent-primary-rgb)/0.35)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--accent-primary)] transition-colors hover:border-[color:var(--accent-primary)] hover:bg-[rgb(var(--accent-primary-rgb)/0.08)]"
      onClick={handleCopy}
      type="button"
    >
      {copied ? <Check className="mr-1.5 h-3.5 w-3.5" /> : <Copy className="mr-1.5 h-3.5 w-3.5" />}
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}
