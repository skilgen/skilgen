"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Play } from "lucide-react";

import { captureDashboardEvent } from "@/lib/posthog";

type AnalyseState = "idle" | "queued" | "running" | "complete" | "error" | "needs-auth";
type AnalysisRunSummary = {
  id: string;
  status: string;
};

const POLL_INTERVAL_MS = 5_000;
const POLL_TIMEOUT_MS = 120_000;
const MAX_POLL_ATTEMPTS = POLL_TIMEOUT_MS / POLL_INTERVAL_MS;

function relativeTime(value: string | null | undefined): string {
  if (!value) return "Not analysed yet";

  const timestamp = new Date(value).getTime();
  if (Number.isNaN(timestamp)) return "Not analysed yet";

  const diff = Math.max(0, Date.now() - timestamp);
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (diff < minute) return "Last analysed just now";
  if (diff < hour) {
    const minutes = Math.floor(diff / minute);
    return `Last analysed ${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  }
  if (diff < day) {
    const hours = Math.floor(diff / hour);
    return `Last analysed ${hours} hour${hours === 1 ? "" : "s"} ago`;
  }
  const days = Math.floor(diff / day);
  if (days < 7) {
    return `Last analysed ${days} day${days === 1 ? "" : "s"} ago`;
  }
  return `Last analysed ${new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(timestamp))}`;
}

export function AnalyseNowButton({
  accessToken,
  apiUrl,
  lastAnalysedAt,
  repoId,
}: {
  accessToken: string;
  apiUrl: string;
  lastAnalysedAt?: string | null;
  repoId: string;
}) {
  const router = useRouter();
  const [state, setState] = useState<AnalyseState>("idle");
  const [message, setMessage] = useState("");
  const timeoutRef = useRef<number | null>(null);
  const pollAttemptsRef = useRef(0);

  const stopPolling = useCallback(() => {
    if (timeoutRef.current !== null) {
      window.clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  const checkActiveRun = useCallback(
    async (refreshOnComplete: boolean): Promise<boolean> => {
      try {
        const response = await fetch(`${apiUrl}/repos/${repoId}/runs`, {
          cache: "no-store",
          headers: accessToken
            ? {
                Authorization: `Bearer ${accessToken}`,
              }
            : undefined,
        });
        if (!response.ok) {
          throw new Error(`Unable to load runs (${response.status})`);
        }

        const runs = (await response.json()) as AnalysisRunSummary[];
        const latestRun = runs[0];

        if (!latestRun) {
          setState("idle");
          setMessage("");
          return false;
        }

        if (latestRun.status === "queued") {
          setState("queued");
          setMessage(`Queued ${latestRun.id.slice(0, 8)}`);
          return true;
        }

        if (latestRun.status === "running") {
          setState("running");
          setMessage("Analysis running");
          return true;
        }

        if (refreshOnComplete && latestRun.status === "complete") {
          setState("complete");
          setMessage("Analysis complete. Refreshing…");
          router.refresh();
          return false;
        }

        if (refreshOnComplete && latestRun.status === "failed") {
          setState("error");
          setMessage("Analysis failed. Try again.");
          return false;
        }

        setState("idle");
        setMessage("");
        return false;
      } catch (error) {
        setState("error");
        setMessage(error instanceof Error ? error.message : "Unable to check analysis status");
        return false;
      }
    },
    [accessToken, apiUrl, repoId, router],
  );

  const startPolling = useCallback(() => {
    stopPolling();
    pollAttemptsRef.current = 0;

    const tick = async () => {
      const shouldContinue = await checkActiveRun(true);
      if (!shouldContinue) return;

      if (pollAttemptsRef.current >= MAX_POLL_ATTEMPTS) {
        setState("error");
        setMessage("Still waiting on analysis. Refresh to check again.");
        return;
      }

      pollAttemptsRef.current += 1;
      timeoutRef.current = window.setTimeout(() => {
        void tick();
      }, POLL_INTERVAL_MS);
    };

    void tick();
  }, [checkActiveRun, stopPolling]);

  useEffect(() => {
    void checkActiveRun(false).then((isActive) => {
      if (isActive) {
        startPolling();
      }
    });

    return () => {
      stopPolling();
    };
  }, [checkActiveRun, startPolling, stopPolling]);

  async function handleAnalyse(): Promise<void> {
    if (!accessToken) {
      setState("needs-auth");
      setMessage("Sign in to start an analysis.");
      router.push("/sign-in");
      return;
    }

    setState("idle");
    setMessage("");
    captureDashboardEvent({ name: "repo_analyse_triggered", properties: {} });

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
      startPolling();
    } catch (error) {
      setState("error");
      setMessage(error instanceof Error ? error.message : "Unable to queue analysis");
    }
  }

  const buttonLabel =
    !accessToken
      ? "Sign in to analyse"
      : state === "queued"
        ? "Analysis queued"
        : state === "running"
          ? "Analysis running"
          : "Analyse now";

  const idleText = state === "idle" ? relativeTime(lastAnalysedAt) : null;
  const messageClass =
    state === "error"
      ? "text-red-400"
      : state === "needs-auth"
        ? "text-[color:var(--text-secondary)]"
        : "text-[color:var(--accent-green)]";

  return (
    <div className="flex flex-col items-end gap-2">
      <button
        className="inline-flex h-10 items-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-60"
        disabled={state === "queued" || state === "running"}
        onClick={handleAnalyse}
        type="button"
      >
        <Play className="mr-2 h-4 w-4" />
        {buttonLabel}
      </button>
      {message ? (
        <p className={`max-w-[260px] text-right text-[12px] ${messageClass}`}>
          {message}
        </p>
      ) : idleText ? (
        <p className="max-w-[260px] text-right text-[12px] text-[color:var(--text-secondary)]">{idleText}</p>
      ) : null}
    </div>
  );
}
