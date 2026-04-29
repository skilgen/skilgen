"use client";

import { CheckCircle2, Loader2, Play, RefreshCw, XCircle } from "lucide-react";
import { useState } from "react";

import type { AutopilotTask } from "../../../lib/data";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

function headers(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

export function AutopilotActions({ accessToken, orgId, taskId }: { accessToken: string; orgId: string; taskId: string }) {
  const [status, setStatus] = useState<AutopilotTask["status"]>("pending");
  const [working, setWorking] = useState<"approve" | "skip" | null>(null);

  async function act(action: "approve" | "skip") {
    setWorking(action);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/autopilot/tasks/${taskId}/${action}`, {
        method: "POST",
        headers: headers(accessToken),
      });
      if (response.ok) setStatus(action === "approve" ? "approved" : "skipped");
    } finally {
      setWorking(null);
    }
  }

  if (status !== "pending") {
    return <span className="text-[12px] font-semibold text-[color:var(--text-tertiary)]">{status === "approved" ? "Approved" : "Skipped"}</span>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      <button className="inline-flex h-8 items-center rounded-md bg-[color:var(--accent-primary)] px-3 text-[12px] font-semibold text-[color:var(--bg-base)] disabled:cursor-wait disabled:opacity-60" disabled={working !== null} onClick={() => void act("approve")} type="button">
        {working === "approve" ? <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> : <CheckCircle2 className="mr-1.5 h-3.5 w-3.5" />}
        Approve
      </button>
      <button className="inline-flex h-8 items-center rounded-md border border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)] disabled:cursor-wait disabled:opacity-60" disabled={working !== null} onClick={() => void act("skip")} type="button">
        {working === "skip" ? <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> : <XCircle className="mr-1.5 h-3.5 w-3.5" />}
        Skip
      </button>
    </div>
  );
}

export function TriggerAutopilotButton({ accessToken, orgId }: { accessToken: string; orgId: string }) {
  const [working, setWorking] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function trigger() {
    setWorking(true);
    setMessage(null);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/autopilot/trigger`, {
        method: "POST",
        headers: headers(accessToken),
      });
      setMessage(response.ok ? "Drift analysis queued." : "Could not trigger drift analysis.");
    } catch {
      setMessage("Could not trigger drift analysis.");
    } finally {
      setWorking(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-2">
      <button className="inline-flex h-10 items-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] disabled:cursor-wait disabled:opacity-60" disabled={working} onClick={trigger} type="button">
        {working ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
        Run drift analysis
      </button>
      {message ? <span className="text-[12px] text-[color:var(--text-tertiary)]">{message}</span> : null}
    </div>
  );
}
