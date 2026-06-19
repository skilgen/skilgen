"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ArrowLeft, Clock3, GitCompare, RotateCcw } from "lucide-react";
import { useRouter } from "next/navigation";

import type { Repo, Skill, SkillRollbackResult, SkillSnapshot } from "../../../../../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type TimeMachineClientProps = {
  accessToken: string;
  repo: Repo | null;
  repoId: string;
  skill: Skill;
  skillId: string;
  currentContent: string;
  initialSnapshots: SkillSnapshot[];
  initialSelectedSnapshot: SkillSnapshot | null;
  initialDiff: string;
};

type Tab = "diff" | "content";
type Toast = { tone: "success" | "error"; message: string } | null;

function formatDate(value: string | null): string {
  if (!value) return "Unknown date";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function relativeTime(value: string | null): string {
  if (!value) return "Unknown";
  const then = new Date(value).getTime();
  if (Number.isNaN(then)) return "Unknown";
  const seconds = Math.max(0, Math.round((Date.now() - then) / 1000));
  if (seconds < 60) return "Just now";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 48) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  return `${days}d ago`;
}

function typeTone(type: string): string {
  if (type === "manual") return "border-blue-400/25 bg-blue-400/10 text-blue-200";
  if (type === "pre_edit") return "border-amber-400/25 bg-amber-400/10 text-amber-200";
  return "border-[color:var(--bg-border)] bg-black/15 text-[color:var(--text-secondary)]";
}

function authHeaders(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

async function fetchSnapshot(accessToken: string, repoId: string, skillId: string, snapshotId: string): Promise<SkillSnapshot | null> {
  const response = await fetch(`${API_URL}/repos/${repoId}/skills/${skillId}/snapshots/${snapshotId}`, {
    headers: authHeaders(accessToken),
    cache: "no-store",
  });
  return response.ok ? ((await response.json()) as SkillSnapshot) : null;
}

async function fetchDiff(accessToken: string, repoId: string, skillId: string, snapshotId: string): Promise<string> {
  const response = await fetch(`${API_URL}/repos/${repoId}/skills/${skillId}/snapshots/${snapshotId}/diff`, {
    headers: authHeaders(accessToken),
    cache: "no-store",
  });
  return response.ok ? response.text() : "";
}

async function postSnapshot(accessToken: string, repoId: string, skillId: string, label: string): Promise<SkillSnapshot | null> {
  const response = await fetch(`${API_URL}/repos/${repoId}/skills/${skillId}/snapshots`, {
    method: "POST",
    headers: authHeaders(accessToken),
    body: JSON.stringify({ label: label.trim() || null }),
  });
  return response.ok ? ((await response.json()) as SkillSnapshot) : null;
}

async function postRollback(accessToken: string, repoId: string, skillId: string, snapshotId: string): Promise<SkillRollbackResult | null> {
  const response = await fetch(`${API_URL}/repos/${repoId}/skills/${skillId}/rollback/${snapshotId}`, {
    method: "POST",
    headers: authHeaders(accessToken),
  });
  return response.ok ? ((await response.json()) as SkillRollbackResult) : null;
}

function DiffViewer({ diff }: { diff: string }) {
  const lines = useMemo(() => diff.split("\n").filter((line, index, all) => index < all.length - 1 || line.length > 0), [diff]);
  let oldLine = 0;
  let newLine = 0;
  return (
    <div className="overflow-auto rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] font-mono text-[12px] leading-5">
      {lines.map((line, index) => {
        const isMeta = line.startsWith("@@") || line.startsWith("---") || line.startsWith("+++");
        const isAdded = line.startsWith("+") && !line.startsWith("+++");
        const isRemoved = line.startsWith("-") && !line.startsWith("---");
        if (line.startsWith("@@")) {
          const match = /-(\d+).* \+(\d+)/.exec(line);
          oldLine = match ? Number(match[1]) : oldLine;
          newLine = match ? Number(match[2]) : newLine;
        } else if (!isMeta) {
          if (isAdded) newLine += 1;
          else if (isRemoved) oldLine += 1;
          else {
            oldLine += 1;
            newLine += 1;
          }
        }
        const tone = isAdded
          ? "bg-green-500/10 text-green-100"
          : isRemoved
            ? "bg-red-500/10 text-red-100"
            : isMeta
              ? "bg-black/25 text-[color:var(--text-tertiary)]"
              : "text-[color:var(--text-secondary)]";
        return (
          <div className={`grid grid-cols-[52px_52px_minmax(0,1fr)] ${tone}`} key={`${index}-${line}`}>
            <span className="select-none border-r border-white/5 px-2 text-right text-[color:var(--text-tertiary)]">{isAdded || isMeta ? "" : oldLine}</span>
            <span className="select-none border-r border-white/5 px-2 text-right text-[color:var(--text-tertiary)]">{isRemoved || isMeta ? "" : newLine}</span>
            <pre className="overflow-visible whitespace-pre-wrap px-3 py-0.5">{line}</pre>
          </div>
        );
      })}
    </div>
  );
}

export function TimeMachineClient({
  accessToken,
  currentContent,
  initialDiff,
  initialSelectedSnapshot,
  initialSnapshots,
  repo,
  repoId,
  skill,
  skillId,
}: TimeMachineClientProps) {
  const router = useRouter();
  const [snapshots, setSnapshots] = useState(initialSnapshots);
  const [selected, setSelected] = useState<SkillSnapshot | null>(initialSelectedSnapshot);
  const [diff, setDiff] = useState(initialDiff);
  const [tab, setTab] = useState<Tab>("diff");
  const [label, setLabel] = useState("");
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState<Toast>(null);

  async function selectSnapshot(snapshot: SkillSnapshot) {
    setLoadingId(snapshot.id);
    const [full, nextDiff] = await Promise.all([
      fetchSnapshot(accessToken, repoId, skillId, snapshot.id),
      fetchDiff(accessToken, repoId, skillId, snapshot.id),
    ]);
    setSelected(full ?? snapshot);
    setDiff(nextDiff);
    setTab("diff");
    setLoadingId(null);
  }

  async function createSnapshot() {
    if (busy) return;
    setBusy(true);
    setToast(null);
    const snapshot = await postSnapshot(accessToken, repoId, skillId, label);
    if (snapshot) {
      setSnapshots((current) => [snapshot, ...current.filter((item) => item.id !== snapshot.id)]);
      setLabel("");
      setToast({ tone: "success", message: "Snapshot created." });
      await selectSnapshot(snapshot);
    } else {
      setToast({ tone: "error", message: "Unable to create snapshot." });
    }
    setBusy(false);
  }

  async function restoreSelected() {
    if (!selected || busy) return;
    const confirmed = window.confirm("Restore this snapshot over the current skill content?");
    if (!confirmed) return;
    setBusy(true);
    setToast(null);
    const result = await postRollback(accessToken, repoId, skillId, selected.id);
    if (result?.ok) {
      setToast({ tone: "success", message: "Skill restored. Refreshing current version." });
      router.refresh();
    } else {
      setToast({ tone: "error", message: "Unable to restore snapshot." });
    }
    setBusy(false);
  }

  return (
    <div>
      {toast ? (
        <div className={`fixed right-5 top-5 z-50 rounded-md border px-4 py-3 text-sm shadow-xl ${toast.tone === "success" ? "border-green-400/25 bg-green-950 text-green-100" : "border-red-400/25 bg-red-950 text-red-100"}`}>
          {toast.message}
        </div>
      ) : null}

      <div className="mb-6">
        <Link className="mb-4 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}/skills/${skillId}`}>
          <ArrowLeft className="h-4 w-4" />
          Back to skill
        </Link>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Time Machine — {skill.domain}</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{repo?.full_name ?? skill.repo_name} · {skill.skill_path}</p>
      </div>

      <div className="grid min-h-[680px] gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="border-r border-[color:var(--bg-border)] pr-4">
          <div className="mb-4 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
            <label className="text-[12px] font-semibold text-[color:var(--text-secondary)]" htmlFor="snapshot-label">
              Create snapshot
            </label>
            <input
              className="mt-2 h-10 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px] outline-none focus:border-[color:var(--accent-primary)]"
              id="snapshot-label"
              onChange={(event) => setLabel(event.target.value)}
              placeholder="Optional label"
              value={label}
            />
            <button className="mt-2 h-9 w-full rounded-md bg-[color:var(--accent-primary)] text-[12px] font-semibold text-[color:var(--bg-base)] disabled:opacity-50" disabled={busy} onClick={createSnapshot} type="button">
              Create snapshot
            </button>
          </div>

          <div className="space-y-2">
            {snapshots.map((snapshot) => {
              const active = selected?.id === snapshot.id;
              return (
                <button
                  className={`w-full rounded-md border p-3 text-left transition-colors ${active ? "border-[color:var(--accent-primary)] bg-[rgb(var(--accent-primary-rgb)/0.12)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] hover:border-[rgb(var(--accent-primary-rgb)/0.35)]"}`}
                  disabled={loadingId === snapshot.id}
                  key={snapshot.id}
                  onClick={() => void selectSnapshot(snapshot)}
                  type="button"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${typeTone(snapshot.snapshot_type)}`}>{snapshot.snapshot_type}</span>
                    <span className="text-[11px] text-[color:var(--text-tertiary)]">{relativeTime(snapshot.created_at)}</span>
                  </div>
                  <div className="mt-2 truncate text-[13px] font-semibold text-[color:var(--text-primary)]">{snapshot.label || formatDate(snapshot.created_at)}</div>
                  <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">Score {snapshot.score_total ?? "n/a"}</div>
                </button>
              );
            })}
          </div>
        </aside>

        <main>
          {!selected ? (
            <div className="flex min-h-[520px] items-center justify-center rounded-md border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] text-center">
              <div>
                <Clock3 className="mx-auto h-10 w-10 text-[color:var(--text-tertiary)]" />
                <div className="mt-3 text-sm font-semibold text-[color:var(--text-primary)]">Select a snapshot</div>
              </div>
            </div>
          ) : (
            <section className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
              <div className="flex flex-wrap items-start justify-between gap-3 border-b border-[color:var(--bg-border)] p-4">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`rounded-full border px-2.5 py-1 text-[12px] font-semibold ${typeTone(selected.snapshot_type)}`}>{selected.snapshot_type}</span>
                    <span className="text-sm font-semibold text-[color:var(--text-primary)]">{formatDate(selected.created_at)}</span>
                    <span className="text-sm text-[color:var(--text-secondary)]">Score {selected.score_total ?? "n/a"}</span>
                  </div>
                  {selected.label ? <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{selected.label}</p> : null}
                </div>
                <button className="inline-flex h-10 items-center gap-2 rounded-md border border-amber-400/35 bg-amber-400/10 px-3 text-[13px] font-semibold text-amber-200 disabled:opacity-50" disabled={busy} onClick={restoreSelected} type="button">
                  <RotateCcw className="h-4 w-4" />
                  Restore this version
                </button>
              </div>

              <div className="flex border-b border-[color:var(--bg-border)] px-4 pt-3">
                {(["diff", "content"] as const).map((item) => (
                  <button className={`border-b-2 px-4 py-2 text-sm font-semibold ${tab === item ? "border-[color:var(--accent-primary)] text-[color:var(--accent-primary)]" : "border-transparent text-[color:var(--text-secondary)]"}`} key={item} onClick={() => setTab(item)} type="button">
                    {item === "diff" ? "Diff" : "Full Content"}
                  </button>
                ))}
              </div>

              <div className="p-4">
                {tab === "diff" ? (
                  <div>
                    <div className="mb-3 inline-flex items-center gap-2 text-[12px] font-semibold text-[color:var(--text-secondary)]">
                      <GitCompare className="h-4 w-4" />
                      Snapshot to current
                    </div>
                    <DiffViewer diff={diff} />
                  </div>
                ) : (
                  <pre className="max-h-[680px] overflow-auto rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 text-[12px] leading-5 text-[color:var(--text-secondary)]">{selected.content ?? currentContent}</pre>
                )}
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
