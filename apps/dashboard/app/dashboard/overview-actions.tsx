"use client";

import Link from "next/link";
import { ArrowRight, BookOpen, GitBranch, Play, TrendingUp, X } from "lucide-react";
import { useMemo, useState } from "react";

import type { Repo } from "../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

export function AnalyseRepoButton({ accessToken, orgId, repo }: { accessToken: string; orgId: string; repo: Repo }) {
  const [status, setStatus] = useState<"idle" | "running" | "done" | "error">("idle");
  const [score, setScore] = useState(repo.score?.total ?? 0);

  async function analyse() {
    setStatus("running");
    try {
      const response = await fetch(`${API_URL}/orgs/${orgId}/repos/${repo.id}/analyse`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
      });
      if (!response.ok) throw new Error("Analysis failed");
      const payload = (await response.json()) as { score?: number };
      if (typeof payload.score === "number") setScore(payload.score);
      setStatus("done");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <button
        className="inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.28)] px-3 py-1.5 text-[12px] font-semibold text-[color:var(--accent-primary)] hover:bg-[rgb(var(--accent-primary-rgb)/0.08)] disabled:cursor-wait disabled:opacity-60"
        disabled={status === "running"}
        onClick={analyse}
        type="button"
      >
        {status === "running" ? "Analysing..." : status === "done" ? `Queued · ${score}/100` : "Analyse now"}
        <ArrowRight className="h-3.5 w-3.5" />
      </button>
      {status === "error" ? <span className="text-[11px] text-red-300">Could not queue analysis.</span> : null}
    </div>
  );
}

function Modal({ children, onClose, title }: { children: React.ReactNode; onClose: () => void; title: string }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="w-full max-w-lg rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-5 shadow-2xl">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">{title}</h2>
          <button className="rounded-md p-2 text-[color:var(--text-secondary)] hover:bg-white/5 hover:text-[color:var(--text-primary)]" onClick={onClose} type="button">
            <X className="h-4 w-4" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function QuickActions({ accessToken, orgId, repos }: { accessToken: string; orgId: string; repos: Repo[] }) {
  const [modal, setModal] = useState<"connect" | "analysis" | null>(null);
  const [repoUrl, setRepoUrl] = useState("");
  const [selectedRepo, setSelectedRepo] = useState(repos[0]?.id ?? "");
  const selected = useMemo(() => repos.find((repo) => repo.id === selectedRepo), [repos, selectedRepo]);

  const actions = [
    { label: "Connect Repo", icon: GitBranch, onClick: () => setModal("connect") },
    { label: "New Analysis", icon: Play, onClick: () => setModal("analysis") },
    { label: "View Skills", icon: BookOpen, href: "/dashboard/skills" },
    { label: "Analytics", icon: TrendingUp, href: "/dashboard/analytics" },
  ];

  return (
    <>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {actions.map((action) => {
          const Icon = action.icon;
          const content = (
            <>
              <div className="flex items-center justify-between gap-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-[rgb(var(--accent-primary-rgb)/0.22)] bg-[rgb(var(--accent-primary-rgb)/0.08)]">
                  <Icon className="h-5 w-5 text-[color:var(--accent-primary)]" />
                </div>
                <ArrowRight className="h-4 w-4 text-[color:var(--text-tertiary)] transition-transform group-hover:translate-x-0.5" />
              </div>
              <div className="mt-5 text-[16px] font-semibold text-[color:var(--text-primary)]">{action.label}</div>
            </>
          );
          const className = "group rounded-[22px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5 text-left transition-transform hover:-translate-y-0.5 hover:border-[rgb(var(--accent-primary-rgb)/0.32)]";
          return action.href ? (
            <Link className={className} href={action.href} key={action.label}>{content}</Link>
          ) : (
            <button className={className} key={action.label} onClick={action.onClick} type="button">{content}</button>
          );
        })}
      </section>
      {modal === "connect" ? (
        <Modal onClose={() => setModal(null)} title="Connect a repository">
          <p className="mt-3 text-sm text-[color:var(--text-secondary)]">Paste a GitHub repository URL. Skillayer will route you into the GitHub connection flow with the repo prefilled.</p>
          <input className="mt-5 w-full rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-2 text-sm text-[color:var(--text-primary)]" onChange={(event) => setRepoUrl(event.target.value)} placeholder="https://github.com/acme/service" value={repoUrl} />
          <div className="mt-5 flex justify-end">
            <Link className="rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-black" href={`/dashboard/repos?connect=${encodeURIComponent(repoUrl)}`}>Continue</Link>
          </div>
        </Modal>
      ) : null}
      {modal === "analysis" ? (
        <Modal onClose={() => setModal(null)} title="Run a new analysis">
          <p className="mt-3 text-sm text-[color:var(--text-secondary)]">Choose a repo to queue a fresh Skilgen analysis.</p>
          <select className="mt-5 w-full rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-2 text-sm" onChange={(event) => setSelectedRepo(event.target.value)} value={selectedRepo}>
            {repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.full_name}</option>)}
          </select>
          <div className="mt-5 flex justify-end">
            {selected ? <AnalyseRepoButton accessToken={accessToken} orgId={orgId} repo={selected} /> : null}
          </div>
        </Modal>
      ) : null}
    </>
  );
}
