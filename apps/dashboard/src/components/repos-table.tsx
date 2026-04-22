import Link from "next/link";

import type { Repo } from "../../lib/data";

function scoreBadgeClass(score: number) {
  if (score <= 40) return "bg-red-900/50 text-red-400";
  if (score <= 70) return "bg-amber-900/50 text-amber-400";
  return "bg-green-900/50 text-green-400";
}

export function relativeTime(value: string | null) {
  if (!value) return "—";
  const timestamp = new Date(value).getTime();
  if (Number.isNaN(timestamp)) return "—";
  const diff = Math.max(0, Date.now() - timestamp);
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (diff < minute) return "just now";
  if (diff < hour) {
    const minutes = Math.floor(diff / minute);
    return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  }
  if (diff < day) {
    const hours = Math.floor(diff / hour);
    return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  }
  const days = Math.floor(diff / day);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}

export function ReposTable({ repos }: { repos: Repo[] }) {
  return (
    <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
        <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Repositories</h2>
        <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Live Skilgen readiness from connected repositories.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[700px] border-collapse text-left text-[13px]">
          <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
            <tr className="border-b border-[color:var(--bg-border)]">
              <th className="px-5 py-3 font-semibold">Repository</th>
              <th className="px-5 py-3 font-semibold">Language</th>
              <th className="px-5 py-3 font-semibold">Score</th>
              <th className="px-5 py-3 font-semibold">Skills</th>
              <th className="px-5 py-3 font-semibold">Last analysed</th>
            </tr>
          </thead>
          <tbody>
            {repos.map((repo) => {
              const score = repo.score?.total;
              return (
                <tr key={repo.id} className="cursor-pointer border-b border-[color:var(--bg-elevated)] transition-colors last:border-b-0 hover:bg-white/5">
                  <td className="px-5 py-4">
                    <Link className="block" href={`/dashboard/repos/${repo.id}`}>
                      <span className="font-medium text-[color:var(--text-primary)]">{repo.name}</span>
                      <span className="mt-0.5 block text-[12px] text-[color:var(--text-tertiary)]">{repo.full_name}</span>
                    </Link>
                  </td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{repo.language || "—"}</td>
                  <td className="px-5 py-4">
                    {typeof score === "number" ? (
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreBadgeClass(score)}`}>{score}/100</span>
                    ) : (
                      <span className="text-[color:var(--text-tertiary)]">—</span>
                    )}
                  </td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{repo.skill_count ?? "—"}</td>
                  <td className="px-5 py-4 text-[color:var(--text-secondary)]">{relativeTime(repo.last_analysed_at)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
