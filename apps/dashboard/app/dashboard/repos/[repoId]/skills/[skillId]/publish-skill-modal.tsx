"use client";

import { useState } from "react";
import Link from "next/link";
import { Loader2, X } from "lucide-react";

type PublishSkillModalProps = {
  skillId: string;
  domain: string;
  accessToken: string;
  onClose: () => void;
};
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type PublishResponse = {
  id: string;
  skill_id: string;
  name: string;
};

type ErrorResponse = {
  detail?: string | { detail?: string };
};

export function PublishSkillModal({ skillId, domain, accessToken, onClose }: PublishSkillModalProps) {
  const [name, setName] = useState(domain);
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState("");
  const [isPublic, setIsPublic] = useState(true);
  const [status, setStatus] = useState<"idle" | "submitting" | "success">("idle");
  const [error, setError] = useState("");
  const [result, setResult] = useState<PublishResponse | null>(null);

  async function handleSubmit() {
    if (!accessToken) {
      setError("Sign in to publish this skill.");
      return;
    }
    setStatus("submitting");
    setError("");
    try {
      const response = await fetch(`${API_URL}/registry/publish`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          skill_id: skillId,
          name,
          description,
          is_public: isPublic,
          tags: tags
            .split(",")
            .map((tag) => tag.trim())
            .filter(Boolean)
            .slice(0, 10),
        }),
      });
      const data = (await response.json().catch(() => null)) as PublishResponse | ErrorResponse | null;
      if (!response.ok || !data || !("id" in data)) {
        const apiError = data as ErrorResponse | null;
        const detail =
          typeof apiError?.detail === "string"
            ? apiError.detail
            : typeof apiError?.detail === "object" && apiError.detail && "detail" in apiError.detail
              ? String(apiError.detail.detail)
              : "Unable to publish this skill.";
        throw new Error(detail);
      }
      setResult(data);
      setStatus("success");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to publish this skill.");
      setStatus("idle");
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="w-full max-w-lg rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] shadow-2xl">
          <div className="flex items-start justify-between border-b border-[color:var(--bg-border)] px-6 py-5">
            <h2 className="text-[22px] font-semibold text-[color:var(--text-primary)]">Publish to Registry</h2>
            <button className="rounded-md p-1 text-[color:var(--text-tertiary)] hover:bg-[color:var(--bg-elevated)] hover:text-[color:var(--text-primary)]" onClick={onClose} type="button">
              <X className="h-4 w-4" />
            </button>
          </div>

          {status === "success" && result ? (
            <div className="space-y-4 px-6 py-6">
              <div className="rounded-xl border border-green-500/30 bg-green-500/10 px-4 py-4 text-green-300">✓ Published to Registry</div>
              <Link className="inline-flex text-[14px] font-semibold text-[color:var(--accent-primary)] hover:text-[color:var(--accent-bright)]" href={`/dashboard/registry/${result.id}`} onClick={onClose}>
                View in Registry →
              </Link>
              <div className="rounded-md bg-black/20 px-3 py-2 font-mono text-[12px] text-[color:var(--text-secondary)]">{`.skilgen/skills/${domain}/SKILL.md`}</div>
            </div>
          ) : (
            <div className="space-y-4 px-6 py-6">
              <label className="block text-[13px] font-medium text-[color:var(--text-primary)]">
                Skill name
                <input
                  className="mt-2 h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] outline-none focus:border-[color:var(--accent-primary)]"
                  onChange={(event) => setName(event.target.value)}
                  value={name}
                />
              </label>
              <label className="block text-[13px] font-medium text-[color:var(--text-primary)]">
                Description
                <textarea
                  className="mt-2 min-h-[100px] w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-3 text-[14px] outline-none focus:border-[color:var(--accent-primary)]"
                  minLength={20}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder="Describe what this skill covers and when an agent should load it"
                  value={description}
                />
              </label>
              <label className="block text-[13px] font-medium text-[color:var(--text-primary)]">
                Tags
                <input
                  className="mt-2 h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[14px] outline-none focus:border-[color:var(--accent-primary)]"
                  onChange={(event) => setTags(event.target.value)}
                  placeholder="e.g. payments, typescript, auth"
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
              <div className="flex items-center justify-between">
                <button className="text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]" onClick={onClose} type="button">
                  Cancel
                </button>
                <button
                  className="inline-flex h-10 items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-60"
                  disabled={status === "submitting" || name.trim().length < 1 || description.trim().length < 20}
                  onClick={() => void handleSubmit()}
                  type="button"
                >
                  {status === "submitting" ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                  Publish
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
