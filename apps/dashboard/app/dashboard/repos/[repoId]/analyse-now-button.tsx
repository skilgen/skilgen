"use client";

import { useState } from "react";
import { Play } from "lucide-react";

type AnalyseState = "idle" | "queued" | "error";

export function AnalyseNowButton({
  accessToken,
  apiUrl,
  repoId,
}: {
  accessToken: string;
  apiUrl: string;
  repoId: string;
}) {
  const [state, setState] = useState<AnalyseState>("idle");
  const [message, setMessage] = useState("");

  async function handleAnalyse(): Promise<void> {
    setState("idle");
    setMessage("");

    try {
      const response = await fetch(`${apiUrl}/repos/${repoId}/analyse`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({}),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.detail || `Request failed with ${response.status}`);
      }
      setState("queued");
      setMessage(`Queued ${String(data.queued ?? "").slice(0, 8)}`);
    } catch (error) {
      setState("error");
      setMessage(error instanceof Error ? error.message : "Unable to queue analysis");
    }
  }

  return (
    <div className="flex flex-col items-end gap-2">
      <button
        className="inline-flex h-10 items-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-60"
        disabled={state === "queued" || !accessToken}
        onClick={handleAnalyse}
        type="button"
      >
        <Play className="mr-2 h-4 w-4" />
        {state === "queued" ? "Analysis queued" : "Analyse now"}
      </button>
      {message ? (
        <p className={`max-w-[260px] text-right text-[12px] ${state === "error" ? "text-red-400" : "text-[color:var(--accent-green)]"}`}>
          {message}
        </p>
      ) : null}
    </div>
  );
}
