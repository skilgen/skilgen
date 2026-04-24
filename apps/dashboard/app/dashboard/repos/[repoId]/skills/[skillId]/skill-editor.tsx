"use client";

import { useMemo, useRef, useState } from "react";

import type { Score } from "../../../../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type SavingState = "idle" | "saving" | "saved" | "error";

type SkillEditorProps = {
  skillId: string;
  repoId: string;
  initialContent: string;
  accessToken: string;
  onSaved: (newScore: Score, newVersionNumber: number) => void;
  onContentSaved?: (content: string) => void;
};

type SkillContentUpdateResult = {
  updated: boolean;
  version_number: number;
  score: Score;
};

function countWords(value: string): number {
  return value.trim().split(/\s+/).filter(Boolean).length;
}

export function SkillEditor({ skillId, repoId, initialContent, accessToken, onSaved, onContentSaved }: SkillEditorProps) {
  const savedContentRef = useRef(initialContent);
  const savedTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [content, setContent] = useState(initialContent);
  const [saving, setSaving] = useState<SavingState>("idle");
  const [error, setError] = useState<string | null>(null);

  const isDirty = content !== savedContentRef.current;
  const wordCount = useMemo(() => countWords(content), [content]);
  const wordCountTone = wordCount < 100 ? "text-amber-400" : "text-[color:var(--text-tertiary)]";

  async function saveContent() {
    if (!isDirty || saving === "saving") return;

    setSaving("saving");
    setError(null);
    if (savedTimeoutRef.current) {
      clearTimeout(savedTimeoutRef.current);
      savedTimeoutRef.current = null;
    }

    try {
      const response = await fetch(`${API_URL}/repos/${repoId}/skills/${skillId}/content`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ content }),
      });

      if (!response.ok) {
        const message = response.status === 401 ? "You need to sign in again before saving." : "Unable to save skill content.";
        throw new Error(message);
      }

      const result = (await response.json()) as SkillContentUpdateResult;
      savedContentRef.current = content;
      onContentSaved?.(content);
      onSaved(result.score, result.version_number);
      setSaving("saved");
      savedTimeoutRef.current = setTimeout(() => setSaving("idle"), 2000);
    } catch (saveError) {
      setSaving("error");
      setError(saveError instanceof Error ? saveError.message : "Unable to save skill content.");
    }
  }

  function discardChanges() {
    setContent(savedContentRef.current);
    setError(null);
    setSaving("idle");
  }

  const buttonLabel = saving === "saving" ? "Saving…" : saving === "saved" ? "Saved ✓" : "Save changes";

  return (
    <section className="mt-6 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Skill Content</h2>
        <div className="flex flex-wrap items-center gap-3">
          <span className={`rounded-full border border-[color:var(--bg-border)] px-2.5 py-1 text-[12px] font-semibold ${wordCountTone}`}>
            {wordCount} words
          </span>
          <button
            className="rounded-full bg-[color:var(--accent-primary)] px-4 py-2 text-[12px] font-semibold text-[color:var(--bg-base)] transition-opacity disabled:cursor-not-allowed disabled:opacity-45"
            disabled={!isDirty || saving === "saving"}
            onClick={saveContent}
            type="button"
          >
            {buttonLabel}
          </button>
        </div>
      </div>

      <textarea
        className="min-h-[480px] w-full resize-y rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 font-mono text-[13px] leading-6 text-[color:var(--text-primary)] outline-none transition-colors placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]"
        onChange={(event) => {
          setContent(event.target.value);
          if (saving === "error") {
            setSaving("idle");
            setError(null);
          }
        }}
        placeholder="Write your skill content in Markdown…"
        value={content}
      />

      {isDirty ? (
        <div className="mt-3 flex items-center justify-between gap-3">
          <span className="text-[12px] font-semibold text-amber-400">● Unsaved changes</span>
          <button className="text-[12px] font-semibold text-[color:var(--text-tertiary)] transition-colors hover:text-[color:var(--text-primary)]" onClick={discardChanges} type="button">
            Discard
          </button>
        </div>
      ) : null}

      {error ? <p className="mt-3 text-[12px] font-semibold text-red-300">{error}</p> : null}
    </section>
  );
}
