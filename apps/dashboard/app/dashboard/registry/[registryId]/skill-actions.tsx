"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";

type SkillActionsProps = {
  registryId: string;
  accessToken: string;
  skillPath: string | null;
};
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type ImportResponse = {
  skill_path: string | null;
};

type ErrorResponse = {
  detail?: string | { detail?: string };
};

export function SkillActions({ registryId, accessToken, skillPath }: SkillActionsProps) {
  const [importState, setImportState] = useState<"idle" | "loading" | "success">("idle");
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");
  const [importedPath, setImportedPath] = useState(skillPath);

  async function copyPath() {
    if (!importedPath) return;
    await navigator.clipboard.writeText(importedPath);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  async function importSkill() {
    if (!accessToken) {
      setError("Sign in to import this skill.");
      return;
    }
    setImportState("loading");
    setError("");
    try {
      const response = await fetch(`${API_URL}/registry/${registryId}/import`, {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = (await response.json().catch(() => null)) as ImportResponse | ErrorResponse | null;
      if (!response.ok || !data || !("skill_path" in data)) {
        const apiError = data as ErrorResponse | null;
        const detail =
          typeof apiError?.detail === "string"
            ? apiError.detail
            : typeof apiError?.detail === "object" && apiError.detail && "detail" in apiError.detail
              ? String(apiError.detail.detail)
              : "Unable to import this skill.";
        throw new Error(detail);
      }
      setImportedPath(data.skill_path);
      setImportState("success");
    } catch (importError) {
      setError(importError instanceof Error ? importError.message : "Unable to import this skill.");
      setImportState("idle");
    }
  }

  return (
    <div className="mt-6">
      <div className="flex flex-wrap items-center gap-3">
        <button
          className="inline-flex h-10 items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-60"
          disabled={importState === "loading"}
          onClick={() => void importSkill()}
          type="button"
        >
          {importState === "loading" ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          {importState === "success" ? "Imported!" : "Import this skill"}
        </button>
        <button
          className="inline-flex h-10 items-center rounded-md border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-primary)] transition-colors hover:bg-[color:var(--bg-elevated)]"
          onClick={() => void copyPath()}
          type="button"
        >
          {copied ? "Copied!" : "Copy path"}
        </button>
      </div>
      {importState === "success" && importedPath ? (
        <div className="mt-3 flex flex-wrap items-center gap-2 rounded-lg border border-green-500/30 bg-green-500/10 px-3 py-2 text-[13px] text-green-300">
          <span>Imported! Copy path:</span>
          <span className="rounded-md bg-black/20 px-2 py-1 font-mono text-[12px] text-green-200">{importedPath}</span>
        </div>
      ) : null}
      {error ? <div className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-[13px] text-red-300">{error}</div> : null}
    </div>
  );
}

export function CopyValueButton({ label, value }: { label: string; value: string | null }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!value) return;
    await navigator.clipboard.writeText(value);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  return (
    <button
      className="inline-flex h-9 items-center rounded-md border border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-primary)] transition-colors hover:bg-[color:var(--bg-elevated)]"
      onClick={() => void handleCopy()}
      type="button"
    >
      {copied ? "Copied!" : label}
    </button>
  );
}
