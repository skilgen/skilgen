"use client";

import { useState } from "react";
import Link from "next/link";
import { Mail, TrendingDown, TrendingUp } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type Digest = {
  week: string; org_name: string; total_agent_loads: number; loads_last_week: number; loads_trend: "up" | "down" | "flat"; active_repos: number;
  top_skill: { name: string; loads: number }; skill_gap_count: number; roi_multiplier: number | null; top_gaps: { pattern: string; frequency: number }[]; memory_score: number;
};

export function DigestShell({ orgId, apiKey, email, initialDigest }: { orgId: string; apiKey: string; email: string; initialDigest: Digest | null }) {
  const [digest] = useState(initialDigest);
  const [recipient, setRecipient] = useState(email);
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  if (!digest || digest.total_agent_loads === 0) {
    return (
      <div className="space-y-6">
        <Header />
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-center">
          <Mail className="mx-auto h-10 w-10 text-[color:var(--accent-primary)]" />
          <h2 className="mt-4 text-xl font-semibold text-[color:var(--text-primary)]">No agent activity this week yet.</h2>
          <p className="mt-2 text-[color:var(--text-secondary)]">Connect your first agent to start seeing your digest.</p>
          <Link className="mt-5 inline-flex rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]" href="/dashboard/connect">Connect agent</Link>
        </section>
      </div>
    );
  }
  const change = digest.loads_last_week ? Math.round(((digest.total_agent_loads - digest.loads_last_week) / digest.loads_last_week) * 100) : 100;
  const scoreTone = digest.memory_score >= 70 ? "text-[color:var(--accent-green)]" : digest.memory_score >= 40 ? "text-[#f59e0b]" : "text-[#ef4444]";
  async function send(previewOnly = false) {
    setSending(true); setMessage(null);
    try {
      const response = await fetch(`${API_URL}/orgs/${orgId}/digest/send`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` }, body: JSON.stringify({ recipient_email: recipient }) });
      const body = await response.json();
      if (previewOnly) setPreview(body.preview || "");
      setMessage(body.sent ? "Digest sent." : "SMTP not configured. Preview generated.");
    } catch { setMessage("Could not send digest."); } finally { setSending(false); }
  }
  return (
    <div className="space-y-6">
      <Header />
      <div className="grid gap-4 md:grid-cols-4">
        <Metric label="Total Agent Loads" value={digest.total_agent_loads} sub={`${change}% vs last week`} trend={digest.loads_trend} />
        <Metric label="Active Repos" value={digest.active_repos} sub="Loaded this week" />
        <Metric label="ROI Multiplier" value={digest.roi_multiplier ? `${digest.roi_multiplier}x` : "N/A"} sub="High-score task lift" />
        <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><div className="text-xs uppercase text-[color:var(--text-tertiary)]">Memory Score</div><div className={`mt-2 text-4xl font-semibold ${scoreTone}`}>{digest.memory_score}</div><div className="mt-3 h-2 rounded-full bg-white/10"><div className="h-full rounded-full bg-current" style={{ width: `${digest.memory_score}%` }} /></div></article>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><h2 className="font-semibold">Top Skill This Week</h2><div className="mt-4 text-2xl text-[color:var(--text-primary)]">{digest.top_skill.name}</div><div className="mt-3 h-3 rounded-full bg-white/10"><div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${Math.min(100, digest.top_skill.loads * 4)}%` }} /></div><p className="mt-2 text-sm text-[color:var(--text-secondary)]">{digest.top_skill.loads} loads</p></section>
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><h2 className="font-semibold">Top Skill Gaps</h2><div className="mt-3 space-y-2">{digest.top_gaps.length ? digest.top_gaps.map((gap) => <div className="flex justify-between rounded-lg bg-black/10 p-3" key={gap.pattern}><span>{gap.pattern}</span><b className="text-[#f59e0b]">{gap.frequency}</b></div>) : <p className="text-sm text-[color:var(--text-secondary)]">No gaps detected.</p>}</div></section>
      </div>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><h2 className="font-semibold">Send Digest Email</h2><div className="mt-4 flex flex-wrap gap-3"><input className="min-w-[260px] flex-1 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm" value={recipient} onChange={(e) => setRecipient(e.target.value)} /><button className="rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)] disabled:opacity-60" disabled={sending} onClick={() => void send(false)}>{sending ? "Sending..." : "Send Now"}</button><button className="rounded-md border border-[color:var(--bg-border)] px-4 py-2 text-sm" onClick={() => void send(true)}>Preview HTML</button></div>{message ? <p className="mt-3 text-sm text-[color:var(--accent-primary)]">{message}</p> : null}</section>
      {preview ? <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"><div className="max-h-[80vh] max-w-3xl overflow-auto rounded-xl bg-[color:var(--bg-surface)] p-5"><button className="mb-3 text-sm text-[color:var(--accent-primary)]" onClick={() => setPreview(null)}>Close</button><div dangerouslySetInnerHTML={{ __html: preview }} /></div></div> : null}
    </div>
  );
}

function Header() { return <div><h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Weekly AI Readiness Digest</h1><p className="mt-1 text-sm text-[color:var(--text-secondary)]">This week <select className="ml-2 rounded bg-[color:var(--bg-surface)] px-2 py-1"><option>This week</option><option>Last week</option></select></p></div>; }
function Metric({ label, value, sub, trend }: { label: string; value: string | number; sub: string; trend?: string }) { return <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><div className="flex justify-between text-xs uppercase text-[color:var(--text-tertiary)]"><span>{label}</span>{trend === "up" ? <TrendingUp className="h-4 w-4 text-[color:var(--accent-green)]" /> : trend === "down" ? <TrendingDown className="h-4 w-4 text-[#ef4444]" /> : null}</div><div className="mt-2 text-3xl font-semibold">{value}</div><div className="mt-3 text-xs text-[color:var(--text-secondary)]">{sub}</div></article>; }
