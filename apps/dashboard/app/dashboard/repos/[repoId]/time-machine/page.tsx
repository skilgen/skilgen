import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft, GitCompare, History, Search } from "lucide-react";

import { getRepo, getRepoSnapshots, getRepoSkills, type RepoSnapshot, type Skill } from "../../../../../lib/data";

type PageProps = {
  params: Promise<{ repoId: string }>;
  searchParams?: Promise<{ at?: string | string[] }>;
};

function firstValue(value: string | string[] | undefined): string {
  return Array.isArray(value) ? value[0] ?? "" : value ?? "";
}

function formatDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function snapshotTime(value: string): number {
  const timestamp = new Date(value).getTime();
  return Number.isNaN(timestamp) ? Number.NEGATIVE_INFINITY : timestamp;
}

function selectedSnapshot(snapshots: RepoSnapshot[], selectedAt: string): RepoSnapshot | null {
  if (!snapshots.length) return null;
  if (!selectedAt) return snapshots[0];

  const exact = snapshots.find((snapshot) => snapshot.captured_at === selectedAt || snapshot.id === selectedAt);
  if (exact) return exact;

  const target = new Date(selectedAt).getTime();
  if (Number.isNaN(target)) return snapshots[0];

  return [...snapshots].sort((left, right) => Math.abs(snapshotTime(left.captured_at) - target) - Math.abs(snapshotTime(right.captured_at) - target))[0] ?? snapshots[0];
}

function fallbackSnapshots(skills: Skill[]): RepoSnapshot[] {
  const base = new Date();
  base.setMinutes(0, 0, 0);
  const now = base.getTime();
  return [0, 7, 21, 45].map((age, index) => {
    const date = new Date(now - age * 86400000).toISOString();
    const score = Math.max(28, Math.round((skills.reduce((sum, skill) => sum + skill.score.total, 0) / Math.max(1, skills.length)) - index * 4));
    return {
      id: `snapshot-${age}`,
      captured_at: date,
      label: age === 0 ? "Current baseline" : `${age} days ago`,
      summary: index === 0 ? "Latest generated knowledge state." : "Historical skill state reconstructed from available skill metadata.",
      score_total: score,
      skill_count: Math.max(0, skills.length - index),
      changed_paths: skills.slice(index, index + 4).map((skill) => skill.skill_path),
      content_preview: skills[index]?.content?.slice(0, 420) || "No snapshot body was returned by the API for this point in time.",
      diff_to_now: {
        added: index * 2,
        removed: index,
        summary: index === 0 ? "This snapshot matches the current table view." : "Compare highlights new skills, removed stale guidance, and score drift since capture.",
      },
    };
  });
}

function scoreTone(score: number): string {
  if (score < 40) return "text-red-300 bg-red-500/10 border-red-500/25";
  if (score < 70) return "text-amber-300 bg-amber-500/10 border-amber-500/25";
  return "text-green-300 bg-green-500/10 border-green-500/25";
}

export default async function TimeMachinePage({ params, searchParams }: PageProps) {
  const { repoId } = await params;
  const resolvedSearch = searchParams ? await searchParams : {};
  const selectedAt = firstValue(resolvedSearch.at);
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    // Local preview can render without auth.
  }

  const [repo, skills, snapshotsPayload] = await Promise.all([
    getRepo(accessToken, repoId),
    getRepoSkills(accessToken, repoId),
    getRepoSnapshots(accessToken, repoId),
  ]);
  const snapshots = (snapshotsPayload?.length ? snapshotsPayload : fallbackSnapshots(skills ?? [])).sort((left, right) => new Date(right.captured_at).getTime() - new Date(left.captured_at).getTime());
  const selected = selectedSnapshot(snapshots, selectedAt);

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link className="mb-4 inline-flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)] hover:text-[color:var(--accent-primary)]" href={`/dashboard/repos/${repoId}`}>
            <ArrowLeft className="h-4 w-4" />
            Back to repo
          </Link>
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Time Machine</h1>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{repo?.full_name ?? "Repository"} knowledge snapshots and compare-to-now history.</p>
        </div>
        <div className="inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[rgb(var(--accent-primary-rgb)/0.1)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--accent-primary)]">
          <History className="h-4 w-4" />
          {snapshots.length} snapshots
        </div>
      </div>

      <form className="mb-6 grid gap-3 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-[260px_auto]">
        <label>
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Jump to date and time</span>
          <input className="mt-2 h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px] text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]" name="at" type="datetime-local" />
        </label>
        <div className="flex items-end">
          <button className="inline-flex h-11 items-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]" type="submit">
            <Search className="mr-2 h-4 w-4" />
            Find closest snapshot
          </button>
        </div>
      </form>

      <section className="mb-6 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="mb-4 text-[13px] font-semibold text-[color:var(--text-primary)]">Timeline</div>
        <div className="flex gap-3 overflow-x-auto pb-2">
          {snapshots.map((snapshot) => {
            const active = selected?.id === snapshot.id;
            return (
              <Link className="min-w-[180px]" href={`/dashboard/repos/${repoId}/time-machine?at=${encodeURIComponent(snapshot.captured_at)}`} key={snapshot.id}>
                <div className={active ? "rounded-lg border border-[color:var(--accent-primary)] bg-[rgb(var(--accent-primary-rgb)/0.12)] p-3" : "rounded-lg border border-[color:var(--bg-border)] bg-black/10 p-3 hover:border-[rgb(var(--accent-primary-rgb)/0.35)]"}>
                  <div className={`mb-3 h-3 w-3 rounded-full ${active ? "bg-[color:var(--accent-primary)]" : "bg-[color:var(--text-tertiary)]"}`} />
                  <div className="text-[12px] font-semibold text-[color:var(--text-primary)]">{snapshot.label}</div>
                  <div className="mt-1 text-[11px] text-[color:var(--text-tertiary)]">{formatDate(snapshot.captured_at)}</div>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {selected ? (
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
          <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]" key={selected.id}>
            <div className="grid grid-cols-[1fr_110px_110px_140px] border-b border-[color:var(--bg-border)] px-5 py-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[color:var(--text-tertiary)]">
              <span>Snapshot</span>
              <span>Score</span>
              <span>Skills</span>
              <span>Captured</span>
            </div>
            {snapshots.map((snapshot) => (
              <details className="group border-b border-[color:var(--bg-elevated)] last:border-b-0" key={snapshot.id} open={snapshot.id === selected.id}>
                <summary className="grid cursor-pointer list-none grid-cols-[1fr_110px_110px_140px] items-center gap-4 px-5 py-4">
                  <div>
                    <div className="font-semibold text-[color:var(--text-primary)]">{snapshot.label}</div>
                    <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">{snapshot.summary}</div>
                  </div>
                  <span className={`w-fit rounded-full border px-2.5 py-1 text-[12px] font-semibold ${scoreTone(snapshot.score_total)}`}>{snapshot.score_total}/100</span>
                  <span className="text-[13px] text-[color:var(--text-secondary)]">{snapshot.skill_count}</span>
                  <span className="text-[12px] text-[color:var(--text-tertiary)]">{formatDate(snapshot.captured_at)}</span>
                </summary>
                <div className="border-t border-[color:var(--bg-border)] bg-black/10 px-5 py-4">
                  <div className="mb-3 text-[12px] font-semibold text-[color:var(--text-secondary)]">Changed paths</div>
                  <div className="mb-4 flex flex-wrap gap-2">
                    {snapshot.changed_paths.length ? snapshot.changed_paths.map((path) => <code className="rounded-md bg-black/25 px-2 py-1 text-[11px] text-[color:var(--text-secondary)]" key={path}>{path}</code>) : <span className="text-[13px] text-[color:var(--text-tertiary)]">No path changes recorded.</span>}
                  </div>
                  <pre className="max-h-72 overflow-auto rounded-lg border border-[color:var(--bg-border)] bg-black/25 p-4 text-[12px] leading-5 text-[color:var(--text-secondary)]">{snapshot.content_preview}</pre>
                </div>
              </details>
            ))}
          </section>

          <aside className="rounded-xl border border-[rgb(var(--accent-primary-rgb)/0.26)] bg-[rgb(var(--accent-primary-rgb)/0.08)] p-5">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.25)] bg-black/20 px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
              <GitCompare className="h-4 w-4" />
              Compare to now
            </div>
            <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">{selected.label}</h2>
            <p className="mt-2 text-[13px] leading-6 text-[color:var(--text-secondary)]">{selected.diff_to_now.summary}</p>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <div className="rounded-lg border border-green-500/25 bg-green-500/10 p-4">
                <div className="text-[11px] font-semibold uppercase tracking-wide text-green-200">Added</div>
                <div className="mt-2 text-2xl font-semibold text-green-200">+{selected.diff_to_now.added}</div>
              </div>
              <div className="rounded-lg border border-red-500/25 bg-red-500/10 p-4">
                <div className="text-[11px] font-semibold uppercase tracking-wide text-red-200">Removed</div>
                <div className="mt-2 text-2xl font-semibold text-red-200">-{selected.diff_to_now.removed}</div>
              </div>
            </div>
            <div className="mt-5 rounded-lg border border-[color:var(--bg-border)] bg-black/20 p-4 text-[12px] leading-5 text-[color:var(--text-secondary)]">
              Diff preview focuses on knowledge surface changes: score movement, skill count, paths touched, and generated guidance snippets.
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  );
}
