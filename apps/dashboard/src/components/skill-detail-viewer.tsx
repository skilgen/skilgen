"use client";

import { useState } from "react";

import { CopySkillButton } from "@/components/copy-skill-button";

type SkillVersionSummary = {
  id: string;
  version_number: number;
  is_latest: boolean;
  content_hash: string;
  created_at: string;
  run_id: string;
};

type SkillVersion = {
  id: string;
  version_number: number;
  content: string;
  content_hash: string;
  created_at: string;
  is_latest: boolean;
};

type SkillSnapshot = {
  id: string;
  content: string | null;
  content_hash: string | null;
  load_count_30d: number;
  last_loaded_at: string | null;
  version_count: number;
  latest_version_number: number | null;
};

type SkillDetailViewerProps = {
  accessToken: string;
  skill: SkillSnapshot;
  versions: SkillVersionSummary[];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

/** Format a timestamp into compact relative copy for dashboard metadata. */
function formatRelativeTime(value: string | null): string {
  if (!value) return "Never loaded";
  const date = new Date(value);
  const timestamp = date.getTime();
  if (Number.isNaN(timestamp)) return "Unknown";

  const seconds = Math.max(0, Math.floor((Date.now() - timestamp) / 1000));
  const minutes = Math.floor(seconds / 60);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;

  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} day${days === 1 ? "" : "s"} ago`;

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

/** Format a timestamp for version history rows. */
function formatVersionDate(value: string): string {
  return formatRelativeTime(value);
}

/** Return a short hash label for compact version rows. */
function contentHashLabel(hash: string | null | undefined): string {
  return hash ? hash.slice(0, 8) : "No hash";
}

/** Fetch a specific skill version directly from the Skillayer API. */
async function fetchSkillVersion(skillId: string, versionId: string, accessToken: string): Promise<SkillVersion> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_URL}/skills/${skillId}/versions/${versionId}`, {
    headers,
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Unable to load skill version");
  }
  return response.json();
}

/** Render raw skill content, client-side version switching, and usage metadata. */
export function SkillDetailViewer({ accessToken, skill, versions }: SkillDetailViewerProps) {
  const currentContent = skill.content ?? "No SKILL.md content is available for this skill yet.";
  const [content, setContent] = useState(currentContent);
  const [activeVersionId, setActiveVersionId] = useState<string | null>(null);
  const [activeVersionNumber, setActiveVersionNumber] = useState<number | null>(skill.latest_version_number);
  const [activeVersionDate, setActiveVersionDate] = useState<string | null>(null);
  const [isLoadingVersion, setIsLoadingVersion] = useState(false);
  const [versionError, setVersionError] = useState<string | null>(null);

  /** Restore the latest generated SKILL.md content. */
  function showCurrentContent() {
    setContent(currentContent);
    setActiveVersionId(null);
    setActiveVersionNumber(skill.latest_version_number);
    setActiveVersionDate(null);
    setVersionError(null);
  }

  /** Load and display a historical skill version without navigating away. */
  async function showVersion(version: SkillVersionSummary) {
    setIsLoadingVersion(true);
    setVersionError(null);
    try {
      const loadedVersion = await fetchSkillVersion(skill.id, version.id, accessToken);
      setContent(loadedVersion.content);
      setActiveVersionId(loadedVersion.id);
      setActiveVersionNumber(loadedVersion.version_number);
      setActiveVersionDate(loadedVersion.created_at);
    } catch {
      setVersionError("Version unavailable");
    } finally {
      setIsLoadingVersion(false);
    }
  }

  const showVersionHistory = skill.version_count > 1 || versions.length > 1;

  return (
    <div className={showVersionHistory ? "grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]" : "grid gap-6"}>
      <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="flex items-center justify-between gap-4 border-b border-[color:var(--bg-border)] px-5 py-4">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">SKILL.md — what agents receive</h2>
              {activeVersionNumber ? (
                <span className="rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-2 py-0.5 text-[11px] font-semibold text-[color:var(--accent-primary)]">
                  v{activeVersionNumber}
                </span>
              ) : null}
              {isLoadingVersion ? <span className="text-[12px] text-[color:var(--text-tertiary)]">Loading...</span> : null}
              {versionError ? <span className="rounded-full bg-amber-900/40 px-2 py-0.5 text-[11px] font-semibold text-amber-300">{versionError}</span> : null}
            </div>
            <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">
              {activeVersionDate ? `Viewing historical version from ${formatVersionDate(activeVersionDate)}` : "Viewing current generated content"}
            </p>
          </div>
          <CopySkillButton content={content} />
        </div>

        <pre className="max-h-[680px] overflow-auto whitespace-pre-wrap break-words bg-[#07070c] p-5 font-mono text-sm leading-6 text-gray-300">
          {content}
        </pre>
      </section>

      <aside className="space-y-6">
        {showVersionHistory ? (
          <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
            <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
              <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Version history</h2>
              <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">
                {versions.length || skill.version_count} stored version{(versions.length || skill.version_count) === 1 ? "" : "s"}
              </p>
            </div>

            <div className="divide-y divide-[color:var(--bg-elevated)]">
              <button
                className={`block w-full px-5 py-4 text-left transition-colors hover:bg-white/5 ${
                  activeVersionId ? "text-[color:var(--text-secondary)]" : "bg-[rgb(var(--accent-primary-rgb)/0.08)] text-[color:var(--text-primary)]"
                }`}
                onClick={showCurrentContent}
                type="button"
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="text-[13px] font-semibold">Current SKILL.md</span>
                  {!activeVersionId ? <span className="rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] px-2 py-0.5 text-[11px] font-semibold text-[color:var(--accent-primary)]">Viewing</span> : null}
                </div>
                <div className="mt-1 font-mono text-[11px] text-[color:var(--text-tertiary)]">{contentHashLabel(skill.content_hash)}</div>
              </button>

              {versions.map((version) => {
                const isSelected = activeVersionId === version.id;

                return (
                  <button
                    className={`block w-full px-5 py-4 text-left transition-colors hover:bg-white/5 ${
                      isSelected ? "bg-[rgb(var(--accent-primary-rgb)/0.08)] text-[color:var(--text-primary)]" : "text-[color:var(--text-secondary)]"
                    }`}
                    key={version.id}
                    onClick={() => showVersion(version)}
                    type="button"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-[13px] font-semibold">v{version.version_number}</span>
                      {version.is_latest ? <span className="rounded-full bg-[rgb(var(--accent-green-rgb)/0.12)] px-2 py-0.5 text-[11px] font-semibold text-[color:var(--accent-green)]">Latest</span> : null}
                    </div>
                    <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{formatVersionDate(version.created_at)}</div>
                    <div className="mt-1 font-mono text-[11px] text-[color:var(--text-tertiary)]">{contentHashLabel(version.content_hash)}</div>
                  </button>
                );
              })}
            </div>
          </section>
        ) : null}

        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Usage stats</h2>
          <div className="mt-4 space-y-3 text-[13px] font-semibold text-[color:var(--text-primary)]">
            <div>{skill.load_count_30d} loads in last 30 days</div>
            <div>{skill.last_loaded_at ? `Last loaded ${formatRelativeTime(skill.last_loaded_at)}` : "Never loaded"}</div>
          </div>
        </section>
      </aside>
    </div>
  );
}
