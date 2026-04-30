"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
type Session = { id: string; repo_id: string; repo_name: string | null; agent_runtime: string; duration_seconds: number | null; skills_loaded: string[]; outcome: string; notes: string | null; code_produced: string | null; created_at: string };
type Replay = { chunk_index: number; code: string; matched_skill: string | null; confidence: number };

export default function SessionDetailPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ repo?: string }> }) {
  const resolvedParams = use(params);
  const resolvedSearchParams = use(searchParams);
  const [apiKey, setApiKey] = useState("");
  const [repoId, setRepoId] = useState(resolvedSearchParams.repo || "");
  const [session, setSession] = useState<Session | null>(null);
  const [tab, setTab] = useState<"overview" | "replay">("overview");
  const [replay, setReplay] = useState<Replay[]>([]);
  const [skills, setSkills] = useState<Record<string, { content: string }>>({});
  const [selected, setSelected] = useState(0);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  useEffect(() => { void bootstrap(); }, []);
  async function bootstrap() {
    const ctx = await fetch("/api/org-context").then((r) => r.json()) as { orgId: string; apiKey: string };
    if (!ctx.orgId || !ctx.apiKey) return;
    const org = { id: ctx.orgId };
    const key = { api_key: ctx.apiKey };
    setApiKey(key.api_key);
    let rid = resolvedSearchParams.repo || repoId;
    if (!rid) {
      const rows = await fetch(`${API_URL}/orgs/${org.id}/sessions`, { headers: { Authorization: `Bearer ${key.api_key}` } }).then((r) => r.json());
      const found = rows.sessions?.find((item: Session) => item.id === resolvedParams.id);
      rid = found?.repo_id || "";
    }
    setRepoId(rid);
    if (rid) {
      const detail = await fetch(`${API_URL}/repos/${rid}/agent-sessions/${resolvedParams.id}`, { headers: { Authorization: `Bearer ${key.api_key}` } }).then((r) => r.json());
      setSession(detail); setCode(detail.code_produced || "");
    }
  }
  async function patch(outcome: string) {
    if (!repoId) return;
    const detail = await fetch(`${API_URL}/repos/${repoId}/sessions/${resolvedParams.id}`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` }, body: JSON.stringify({ outcome, code_produced: code }) }).then((r) => r.json());
    setSession(detail);
  }
  async function loadReplay() {
    if (!repoId) return;
    setLoading(true);
    if (code && code !== session?.code_produced) await patch(session?.outcome || "unknown");
    const body = await fetch(`${API_URL}/repos/${repoId}/sessions/${resolvedParams.id}/replay`, { headers: { Authorization: `Bearer ${apiKey}` } }).then((r) => r.json());
    setReplay(body.replay || []); setSkills(body.skills || {}); setLoading(false);
  }
  return (
    <div className="space-y-6">
      <div className="text-sm text-[color:var(--text-secondary)]"><Link href="/dashboard/sessions">Sessions</Link> &gt; {resolvedParams.id.slice(0, 8)}</div>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[#1A1A2E] p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h1 className="text-xl font-semibold">{session?.agent_runtime || "Agent session"}</h1><p className="mt-1 text-sm text-[color:var(--text-secondary)]">{session?.repo_name} · {session ? new Date(session.created_at).toLocaleString() : ""} · {session?.duration_seconds ?? 0}s · {session?.outcome}</p></div><div className="flex gap-2"><button className="rounded bg-[#ef4444] px-3 py-2 text-sm" onClick={() => void patch("incident")}>Mark as Incident</button><button className="rounded bg-[color:var(--accent-green)] px-3 py-2 text-sm text-black" onClick={() => void patch("success")}>Mark as Success</button></div></div></section>
      <div className="flex gap-4 border-b border-[color:var(--bg-border)]"><button className={tab === "overview" ? "border-b-2 border-[color:var(--accent-primary)] pb-2 text-[color:var(--accent-primary)]" : "pb-2 text-[color:var(--text-tertiary)]"} onClick={() => setTab("overview")}>Overview</button><button className={tab === "replay" ? "border-b-2 border-[color:var(--accent-primary)] pb-2 text-[color:var(--accent-primary)]" : "pb-2 text-[color:var(--text-tertiary)]"} onClick={() => setTab("replay")}>Skill Replay</button></div>
      {tab === "overview" ? <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><h2 className="font-semibold">Skills Loaded</h2><div className="mt-2 flex flex-wrap gap-2">{session?.skills_loaded?.length ? session.skills_loaded.map((skill) => <span className="rounded-full bg-[color:var(--accent-primary)] px-3 py-1 text-xs text-[color:var(--bg-base)]" key={skill}>{skill}</span>) : <span className="text-sm text-[color:var(--text-secondary)]">No skills recorded.</span>}</div><h2 className="mt-5 font-semibold">Notes</h2><textarea className="mt-2 w-full rounded bg-[color:var(--bg-base)] p-3" value={session?.notes || ""} onChange={(e) => setSession(session ? { ...session, notes: e.target.value } : session)} onBlur={() => void patch(session?.outcome || "unknown")} /><h2 className="mt-5 font-semibold">Code Produced</h2><pre className="mt-2 max-h-72 overflow-auto rounded bg-[color:var(--bg-base)] p-3 text-xs">{session?.code_produced || "No code recorded."}</pre></section> : <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">{!session?.code_produced ? <div><p className="mb-2 text-sm text-[color:var(--text-secondary)]">No code recorded for this session.</p><textarea className="min-h-48 w-full rounded bg-[color:var(--bg-base)] p-3 font-mono text-sm" value={code} onChange={(e) => setCode(e.target.value)} /></div> : null}<button className="mt-3 rounded bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]" disabled={loading} onClick={loadReplay}>{loading ? "Generating..." : "Generate Replay"}</button>{replay.length ? <div className="mt-5 grid gap-4 lg:grid-cols-2"><div className="space-y-3">{replay.map((chunk) => <button className="w-full text-left" key={chunk.chunk_index} onClick={() => setSelected(chunk.chunk_index)}><pre className={`overflow-auto rounded border-l-4 ${chunk.matched_skill ? "border-[color:var(--accent-primary)]" : "border-gray-500"} bg-[color:var(--bg-base)] p-3 text-xs`}>{chunk.code}</pre><span className="text-xs text-[color:var(--text-secondary)]">{chunk.matched_skill || "No match"} · {Math.round(chunk.confidence * 100)}%</span></button>)}</div><aside className="rounded bg-[color:var(--bg-base)] p-4"><h3 className="font-semibold">{replay[selected]?.matched_skill || "No match"}</h3><pre className="mt-3 max-h-[520px] overflow-auto whitespace-pre-wrap text-xs text-[color:var(--text-secondary)]">{replay[selected]?.matched_skill ? skills[replay[selected].matched_skill!]?.content : "This chunk did not match a skill. Consider generating or improving coverage."}</pre></aside></div> : null}</section>}
    </div>
  );
}
