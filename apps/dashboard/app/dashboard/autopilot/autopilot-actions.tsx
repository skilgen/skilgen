"use client";

import { CheckCircle2, GitPullRequest, Loader2, Play, RefreshCw, Sparkles, XCircle } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";

import type { AutopilotTask } from "../../../lib/data";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

function headers(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

export function GenerateImprovementButton({ accessToken, orgId, taskId }: { accessToken: string; orgId: string; taskId: string }) {
  const router = useRouter();
  const [working, setWorking] = useState(false);

  async function generate() {
    setWorking(true);
    try {
      await fetch(`${CLIENT_API_URL}/orgs/${orgId}/autopilot/${taskId}/generate-improvement`, {
        method: "POST",
        headers: headers(accessToken),
      });
      router.refresh();
    } finally {
      setWorking(false);
    }
  }

  return (
    <button className="inline-flex h-8 items-center rounded-md bg-[color:var(--accent-primary)] px-3 text-[12px] font-semibold text-[color:var(--bg-base)] disabled:cursor-wait disabled:opacity-60" disabled={working} onClick={generate} type="button">
      {working ? <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> : <Sparkles className="mr-1.5 h-3.5 w-3.5" />}
      Generate
    </button>
  );
}

export function ReviewActions({ accessToken, orgId, task }: { accessToken: string; orgId: string; task: AutopilotTask }) {
  const router = useRouter();
  const [content, setContent] = useState(task.final_content || task.generated_content || "");
  const [createPr, setCreatePr] = useState(false);
  const [working, setWorking] = useState<"approve" | "reject" | null>(null);

  async function approve() {
    setWorking("approve");
    try {
      await fetch(`${CLIENT_API_URL}/orgs/${orgId}/autopilot/${task.id}/approve`, {
        method: "POST",
        headers: headers(accessToken),
        body: JSON.stringify({ final_content: content, create_skill_pr: createPr }),
      });
      router.refresh();
    } finally {
      setWorking(null);
    }
  }

  async function reject() {
    setWorking("reject");
    try {
      await fetch(`${CLIENT_API_URL}/orgs/${orgId}/autopilot/${task.id}/reject`, {
        method: "POST",
        headers: headers(accessToken),
        body: JSON.stringify({ reason: "Rejected from Autopilot review" }),
      });
      router.refresh();
    } finally {
      setWorking(null);
    }
  }

  return (
    <div className="grid gap-3">
      <textarea
        className="min-h-[220px] w-full resize-y rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 font-mono text-[12px] leading-5 text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]"
        onChange={(event) => setContent(event.target.value)}
        value={content}
      />
      <label className="inline-flex items-center gap-2 text-[12px] font-medium text-[color:var(--text-secondary)]">
        <input checked={createPr} className="h-4 w-4 accent-[color:var(--accent-primary)]" onChange={(event) => setCreatePr(event.target.checked)} type="checkbox" />
        Create GitHub PR
      </label>
      <div className="flex flex-wrap gap-2">
        <button className="inline-flex h-9 items-center rounded-md bg-[color:var(--accent-primary)] px-3 text-[12px] font-semibold text-[color:var(--bg-base)] disabled:cursor-wait disabled:opacity-60" disabled={working !== null || content.trim().length === 0} onClick={approve} type="button">
          {working === "approve" ? <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> : createPr ? <GitPullRequest className="mr-1.5 h-3.5 w-3.5" /> : <CheckCircle2 className="mr-1.5 h-3.5 w-3.5" />}
          Approve
        </button>
        <button className="inline-flex h-9 items-center rounded-md border border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)] disabled:cursor-wait disabled:opacity-60" disabled={working !== null} onClick={reject} type="button">
          {working === "reject" ? <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> : <XCircle className="mr-1.5 h-3.5 w-3.5" />}
          Reject
        </button>
      </div>
    </div>
  );
}

export function TriggerAutopilotButton({ accessToken, orgId }: { accessToken: string; orgId: string }) {
  const router = useRouter();
  const [working, setWorking] = useState(false);

  async function trigger() {
    setWorking(true);
    try {
      await fetch(`${CLIENT_API_URL}/orgs/${orgId}/autopilot/trigger`, {
        method: "POST",
        headers: headers(accessToken),
      });
      router.refresh();
    } finally {
      setWorking(false);
    }
  }

  return (
    <button className="inline-flex h-9 items-center rounded-md bg-[color:var(--accent-primary)] px-3 text-[12px] font-semibold text-[color:var(--bg-base)] disabled:cursor-wait disabled:opacity-60" disabled={working} onClick={trigger} type="button">
      {working ? <RefreshCw className="mr-1.5 h-3.5 w-3.5 animate-spin" /> : <Play className="mr-1.5 h-3.5 w-3.5" />}
      Refresh queue
    </button>
  );
}
