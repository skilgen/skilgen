"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { History, Plus } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
export const dynamic = "force-dynamic";

type Session = { id: string; repo_id: string; repo_name: string | null; agent_runtime: string; duration_seconds: number | null; skills_loaded: string[]; outcome: string; created_at: string };
type Repo = { id: string; name: string; full_name: string };

export default function SessionsPage() {
  const [apiKey, setApiKey] = useState("");
  const [repos, setRepos] = useState<Repo[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [repoId, setRepoId] = useState("");
  const [agent, setAgent] = useState("codex");
  const [outcome, setOutcome] = useState("unknown");
  const [code, setCode] = useState("");
  const [notes, setNotes] = useState("");
  useEffect(() => { void bootstrap(); }, []);
  async function bootstrap() {
    const org = await fetch(`${API_URL}/orgs/bootstrap`).then((r) => r.json());
    const key = await fetch(`${API_URL}/orgs/${org.id}/api-key`, { headers: { Authorization: "Bearer bootstrap" } }).then((r) => r.json());
    const repoRows = await fetch(`${API_URL}/orgs/${org.id}/repos`, { headers: { Authorization: `Bearer ${key.api_key}` } }).then((r) => r.json());
    const sessionRows = await fetch(`${API_URL}/orgs/${org.id}/sessions`, { headers: { Authorization: `Bearer ${key.api_key}` } }).then((r) => r.json());
    setApiKey(key.api_key); setRepos(repoRows); setRepoId(repoRows[0]?.id ?? ""); setSessions(sessionRows.sessions ?? []);
  }
  async function save() {
    setSaving(true);
    const created = await fetch(`${API_URL}/repos/${repoId}/sessions`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` }, body: JSON.stringify({ agent_runtime: agent, skills_loaded: [], code_produced: code, outcome, notes }) }).then((r) => r.json());
    if (created.session_id || created.session_db_id) await fetch(`${API_URL}/repos/${repoId}/sessions/${created.session_id || created.session_db_id}`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` }, body: JSON.stringify({ code_produced: code, outcome, notes }) });
    setShowModal(false); setSaving(false); await bootstrap();
  }
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between"><div><h1 className="text-2xl font-semibold">Agent Sessions</h1><p className="mt-1 text-sm text-[color:var(--text-secondary)]">Review agent work, outcomes, and skill replay.</p></div><button className="inline-flex items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]" onClick={() => setShowModal(true)}><Plus className="h-4 w-4" />Log Session</button></div>
      <div className="grid gap-3 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-4"><select className="rounded bg-[color:var(--bg-base)] p-2"><option>All agents</option><option>Codex</option><option>Claude Code</option></select><select className="rounded bg-[color:var(--bg-base)] p-2"><option>All repos</option></select><select className="rounded bg-[color:var(--bg-base)] p-2"><option>All outcomes</option></select><input className="rounded bg-[color:var(--bg-base)] p-2" type="date" /></div>
      <section className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">{sessions.length ? <table className="w-full text-sm"><thead className="bg-[#1A1A2E] text-left"><tr><th className="p-3">Agent</th><th>Repo</th><th>Duration</th><th>Skills Loaded</th><th>Outcome</th><th>Date</th><th>Actions</th></tr></thead><tbody>{sessions.map((s) => <tr className="border-t border-[color:var(--bg-border)]" key={s.id}><td className="p-3">{s.agent_runtime}</td><td>{s.repo_name}</td><td>{s.duration_seconds ? `${Math.floor(s.duration_seconds / 60)}m ${s.duration_seconds % 60}s` : "Open"}</td><td>{s.skills_loaded.length} skills</td><td><span className={s.outcome === "success" ? "text-[color:var(--accent-green)]" : s.outcome === "incident" ? "text-[#ef4444]" : "text-[color:var(--text-tertiary)]"}>{s.outcome}</span></td><td>{new Date(s.created_at).toLocaleDateString()}</td><td><Link className="text-[color:var(--accent-primary)]" href={`/dashboard/sessions/${s.id}?repo=${s.repo_id}`}>Open</Link></td></tr>)}</tbody></table> : <div className="p-10 text-center text-[color:var(--text-secondary)]"><History className="mx-auto h-10 w-10 text-[color:var(--accent-primary)]" /><p className="mt-3">No sessions logged yet.</p></div>}</section>
      {showModal ? <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"><div className="w-full max-w-2xl rounded-xl bg-[color:var(--bg-surface)] p-5"><h2 className="text-lg font-semibold">Log Session</h2><div className="mt-4 grid gap-3"><select className="rounded bg-[color:var(--bg-base)] p-2" value={agent} onChange={(e) => setAgent(e.target.value)}><option value="claude_code">Claude Code</option><option value="codex">Codex</option><option value="cursor">Cursor</option></select><select className="rounded bg-[color:var(--bg-base)] p-2" value={repoId} onChange={(e) => setRepoId(e.target.value)}>{repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.full_name}</option>)}</select><select className="rounded bg-[color:var(--bg-base)] p-2" value={outcome} onChange={(e) => setOutcome(e.target.value)}><option>unknown</option><option>success</option><option>incident</option></select><textarea className="min-h-32 rounded bg-[color:var(--bg-base)] p-2 font-mono" placeholder="Code produced" value={code} onChange={(e) => setCode(e.target.value)} /><textarea className="min-h-24 rounded bg-[color:var(--bg-base)] p-2" placeholder="Notes" value={notes} onChange={(e) => setNotes(e.target.value)} /></div><div className="mt-4 flex justify-end gap-2"><button onClick={() => setShowModal(false)}>Cancel</button><button className="rounded bg-[color:var(--accent-primary)] px-4 py-2 text-[color:var(--bg-base)]" disabled={saving} onClick={save}>{saving ? "Saving..." : "Save Session"}</button></div></div></div> : null}
    </div>
  );
}
