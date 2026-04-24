"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Loader2, X } from "lucide-react";

type SourceType = "claude_md" | "agents_md" | "cursorrules";
type Step = "paste" | "configure" | "success";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type ImportSkillModalProps = {
  orgId: string;
  accessToken: string;
  onClose: () => void;
};

type ImportResponse = {
  id: string;
  score_total: number;
};

type ErrorResponse = {
  detail?: string | { detail?: string };
};

const sourceLabels: Record<SourceType, string> = {
  claude_md: "CLAUDE.md",
  agents_md: "AGENTS.md",
  cursorrules: ".cursorrules",
};

function deriveName(content: string): string {
  const match = content.match(/^#\s+(.+)$/m);
  return match?.[1]?.trim() || "";
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function ImportSkillModal({ orgId: _orgId, accessToken, onClose }: ImportSkillModalProps) {
  const [step, setStep] = useState<Step>("paste");
  const [sourceType, setSourceType] = useState<SourceType>("claude_md");
  const [content, setContent] = useState("");
  const [name, setName] = useState("");
  const [domain, setDomain] = useState("");
  const [tags, setTags] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ImportResponse | null>(null);

  const canContinue = content.trim().length >= 20;
  const autoDomain = useMemo(() => slugify(name || deriveName(content)), [content, name]);

  function handleNext() {
    const derivedName = deriveName(content);
    if (!name && derivedName) setName(derivedName);
    if (!domain) setDomain(autoDomain);
    setError("");
    setStep("configure");
  }

  async function handleSubmit() {
    if (!accessToken) {
      setError("Sign in to import a skill file.");
      return;
    }
    setSubmitting(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/registry/import-skill-file`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          name,
          domain,
          content,
          source_type: sourceType,
          is_public: isPublic,
          tags: tags
            .split(",")
            .map((tag) => tag.trim())
            .filter(Boolean),
        }),
      });
      const data = (await response.json().catch(() => null)) as ImportResponse | ErrorResponse | null;
      if (!response.ok || !data || !("id" in data)) {
        const apiError = data as ErrorResponse | null;
        const detail =
          typeof apiError?.detail === "string"
            ? apiError.detail
            : typeof apiError?.detail === "object" && apiError.detail && "detail" in apiError.detail
              ? String(apiError.detail.detail)
              : "Unable to import skill file.";
        throw new Error(detail);
      }
      setResult(data);
      setStep("success");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to import skill file.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="w-full max-w-lg rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] shadow-2xl">
          <div className="flex items-start justify-between border-b border-[color:var(--bg-border)] px-6 py-5">
            <div>
              <h2 className="text-[22px] font-semibold text-[color:var(--text-primary)]">
                {step === "success" ? "Imported to Registry" : "Import existing skill file"}
              </h2>
              <p className="mt-1 text-[14px] text-[color:var(--text-secondary)]">
                {step === "success"
                  ? "Your imported skill is now available in the private registry."
                  : "Paste your CLAUDE.md, AGENTS.md, or .cursorrules. Skillayer scores it and adds it to your private registry."}
              </p>
            </div>
            <button className="rounded-md p-1 text-[color:var(--text-tertiary)] hover:bg-[color:var(--bg-elevated)] hover:text-[color:var(--text-primary)]" onClick={onClose} type="button">
              <X className="h-4 w-4" />
            </button>
          </div>

          {step === "paste" ? (
            <div className="space-y-5 px-6 py-6">
              <div className="flex flex-wrap gap-2">
                {(Object.keys(sourceLabels) as SourceType[]).map((value) => (
                  <button
                    className={`rounded-full px-3 py-1.5 text-[13px] font-semibold transition-colors ${
                      sourceType === value
                        ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]"
                        : "border border-[color:var(--bg-border)] text-[color:var(--text-secondary)]"
                    }`}
                    key={value}
                    onClick={() => setSourceType(value)}
                    type="button"
                  >
                    {sourceLabels[value]}
                  </button>
                ))}
              </div>
              <textarea
                className="min-h-[220px] w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 font-mono text-[13px] leading-6 text-[color:var(--text-secondary)] outline-none transition-colors placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]"
                onChange={(event) => setContent(event.target.value)}
                placeholder="# Paste your file content here…"
                value={content}
              />
              <div className="flex justify-end">
                <button
                  className="inline-flex h-10 items-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={!canContinue}
                  onClick={handleNext}
                  type="button"
                >
                  Next →
                </button>
              </div>
            </div>
          ) : null}

          {step === "configure" ? (
            <div className="space-y-4 px-6 py-6">
              <button className="text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" onClick={() => setStep("paste")} type="button">
                ← Back
              </button>
              <label className="block text-[13px] font-medium text-[color:var(--text-primary)]">
                Name
                <input
                  className="mt-2 h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] outline-none focus:border-[color:var(--accent-primary)]"
                  onChange={(event) => setName(event.target.value)}
                  value={name}
                />
              </label>
              <label className="block text-[13px] font-medium text-[color:var(--text-primary)]">
                Domain
                <input
                  className="mt-2 h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] outline-none focus:border-[color:var(--accent-primary)]"
                  onChange={(event) => setDomain(slugify(event.target.value))}
                  value={domain}
                />
              </label>
              <label className="block text-[13px] font-medium text-[color:var(--text-primary)]">
                Tags
                <input
                  className="mt-2 h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] outline-none focus:border-[color:var(--accent-primary)]"
                  onChange={(event) => setTags(event.target.value)}
                  value={tags}
                />
              </label>
              <div>
                <div className="mb-2 text-[13px] font-medium text-[color:var(--text-primary)]">Visibility</div>
                <div className="flex gap-2">
                  {[
                    { label: "Public", value: true },
                    { label: "Org only", value: false },
                  ].map((option) => (
                    <button
                      className={`rounded-full px-3 py-1.5 text-[13px] font-semibold ${
                        isPublic === option.value
                          ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]"
                          : "border border-[color:var(--bg-border)] text-[color:var(--text-secondary)]"
                      }`}
                      key={option.label}
                      onClick={() => setIsPublic(option.value)}
                      type="button"
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
              {error ? <div className="rounded-md border border-red-500/30 bg-red-500/10 px-3 py-2 text-[13px] text-red-300">{error}</div> : null}
              <div className="flex justify-end">
                <button
                  className="inline-flex h-10 items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-60"
                  disabled={submitting || name.trim().length < 1 || domain.trim().length < 1}
                  onClick={() => void handleSubmit()}
                  type="button"
                >
                  {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                  Import to Registry
                </button>
              </div>
            </div>
          ) : null}

          {step === "success" && result ? (
            <div className="space-y-4 px-6 py-6">
              <div className="rounded-xl border border-green-500/30 bg-green-500/10 px-4 py-4 text-green-300">
                Imported! Score: {result.score_total}/100
              </div>
              <Link className="inline-flex text-[14px] font-semibold text-[color:var(--accent-primary)] hover:text-[color:var(--accent-bright)]" href={`/dashboard/registry/${result.id}`} onClick={onClose}>
                View in Registry →
              </Link>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
