"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ChevronDown, History, Plus, SlidersHorizontal } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
export const dynamic = "force-dynamic";

const AGENT_LABELS: Record<string, string> = {
  claude_code: "Claude Code", codex: "Codex", codex_cli: "Codex CLI",
  cursor: "Cursor", copilot: "GitHub Copilot", gemini_cli: "Gemini CLI",
  devin: "Devin", unidentified_agent: "Codex CLI", unknown: "Unknown",
};
function agentLabel(runtime: string) {
  return AGENT_LABELS[runtime] ?? runtime.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

type SessionSkill = { domain: string; score: number; loaded_at: string };
type Session = {
  session_id: string;
  repo_id: string;
  repo_name: string;
  agent_runtime: string;
  started_at: string;
  ended_at: string;
  duration_minutes: number;
  skills_loaded: SessionSkill[];
  skill_count: number;
  session_context: string;
  quality_signal: "strong" | "mixed" | "weak";
  avg_skill_score: number;
};
type Repo = { id: string; name: string; full_name: string };

function scoreClass(score: number) {
  if (score >= 80) return "border-[color:var(--accent-green)]/40 bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]";
  if (score >= 60) return "border-amber-500/40 bg-amber-500/15 text-amber-200";
  return "border-red-500/40 bg-red-500/15 text-red-200";
}

function qualityCopy(session: Session) {
  if (session.quality_signal === "strong") return "Strong guidance - avg skill score";
  if (session.quality_signal === "mixed") return "Mixed guidance - review output carefully";
  return "Agent loaded low-quality skills - review output";
}

function dateGroup(value: string) {
  const date = new Date(value);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === today.toDateString()) return "Today";
  if (date.toDateString() === yesterday.toDateString()) return "Yesterday";
  return date.toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" });
}

function shortTime(value: string) {
  return new Date(value).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
}

export default function SessionsPage() {
  const [apiKey, setApiKey] = useState("");
  const [repos, setRepos] = useState<Repo[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [repoId, setRepoId] = useState("");
  const [agent, setAgent] = useState("codex");
  const [outcome, setOutcome] = useState("unknown");
  const [code, setCode] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => { void bootstrap(); }, []);

  async function bootstrap() {
    const ctx = await fetch("/api/org-context").then((r) => r.json()) as { orgId: string; apiKey: string; accessToken?: string };
    const token = ctx.apiKey || ctx.accessToken || "";
    if (!ctx.orgId || !token) return;
    const auth = { Authorization: `Bearer ${token}` };
    const [repoRows, sessionRows] = await Promise.all([
      fetch(`${API_URL}/orgs/${ctx.orgId}/repos`, { headers: auth }).then((r) => r.json()),
      fetch(`${API_URL}/orgs/${ctx.orgId}/sessions`, { headers: auth }).then((r) => r.json()),
    ]);
    setApiKey(token);
    setRepos(repoRows);
    setRepoId(repoRows[0]?.id ?? "");
    setSessions(sessionRows.sessions ?? []);
  }

  async function save() {
    setSaving(true);
    const created = await fetch(`${API_URL}/repos/${repoId}/sessions`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` }, body: JSON.stringify({ agent_runtime: agent, skills_loaded: [], code_produced: code, outcome, notes }) }).then((r) => r.json());
    if (created.session_id || created.session_db_id) await fetch(`${API_URL}/repos/${repoId}/sessions/${created.session_id || created.session_db_id}`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` }, body: JSON.stringify({ code_produced: code, outcome, notes }) });
    setShowModal(false);
    setSaving(false);
    await bootstrap();
  }

  const grouped = useMemo(() => sessions.reduce<Record<string, Session[]>>((acc, session) => {
    const key = dateGroup(session.started_at);
    acc[key] = [...(acc[key] ?? []), session];
    return acc;
  }, {}), [sessions]);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Agent Sessions</h1>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Every skill load grouped into a real agent timeline: what the agent loaded, in what order, and whether the guidance was strong.</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]" onClick={() => setShowModal(true)} type="button"><Plus className="h-4 w-4" />Log Session</button>
      </div>

      <button className="inline-flex items-center gap-2 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-2 text-sm text-[color:var(--text-secondary)]" onClick={() => setShowFilters((value) => !value)} type="button">
        <SlidersHorizontal className="h-4 w-4" /> Filters <ChevronDown className="h-3.5 w-3.5" />
      </button>
      {showFilters ? <div className="grid gap-3 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:grid-cols-4"><select className="rounded bg-[color:var(--bg-base)] p-2"><option>All agents</option><option>Codex</option><option>Claude Code</option></select><select className="rounded bg-[color:var(--bg-base)] p-2"><option>All repos</option></select><select className="rounded bg-[color:var(--bg-base)] p-2"><option>All quality levels</option></select><input className="rounded bg-[color:var(--bg-base)] p-2" type="date" /></div> : null}

      {sessions.length ? (
        <section className="space-y-8">
          {Object.entries(grouped).map(([day, rows]) => (
            <div key={day}>
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{day}</h2>
              <div className="space-y-4 border-l border-[color:var(--bg-border)] pl-5">
                {rows.map((session) => (
                  <article className="relative rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={`${session.session_id}-${session.repo_id}`}>
                    <div className="absolute -left-[29px] top-6 h-3 w-3 rounded-full bg-[color:var(--accent-primary)] shadow-[0_0_0_4px_var(--bg-base)]" />
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <div className="text-xs text-[color:var(--text-tertiary)]">{shortTime(session.started_at)}</div>
                        <h3 className="mt-1 text-lg font-semibold">{agentLabel(session.agent_runtime)} · {session.repo_name}</h3>
                      </div>
                      <div className="text-right text-sm text-[color:var(--text-secondary)]">{session.session_context} · {session.duration_minutes || 1} min</div>
                    </div>
                    <div className="mt-5">
                      <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Skills loaded in sequence</div>
                      <div className="flex flex-wrap items-center gap-2">
                        {session.skills_loaded.map((skill, index) => (
                          <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${scoreClass(skill.score)}`} key={`${skill.domain}-${skill.loaded_at}`} title={`${skill.domain} skill · score ${skill.score}/100 · loaded ${shortTime(skill.loaded_at)}`}>
                            {skill.score < 50 ? "⚠ " : ""}{skill.domain}{index < session.skills_loaded.length - 1 ? " →" : ""}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className={`mt-5 rounded-lg border p-3 text-sm ${session.quality_signal === "strong" ? "border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : session.quality_signal === "mixed" ? "border-amber-500/30 bg-amber-500/10 text-amber-200" : "border-red-500/30 bg-red-500/10 text-red-200"}`}>
                      {qualityCopy(session)} {session.avg_skill_score}/100
                    </div>
                    <Link className="mt-4 inline-flex text-sm font-semibold text-[color:var(--accent-primary)]" href={`/dashboard/sessions/${session.session_id}?repo=${session.repo_id}`}>View session details →</Link>
                  </article>
                ))}
              </div>
            </div>
          ))}
        </section>
      ) : (
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
          <History className="mx-auto h-10 w-10 text-[color:var(--accent-primary)]" />
          <h2 className="mt-4 text-xl font-semibold">No agent sessions recorded yet</h2>
          <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-[color:var(--text-secondary)]">Sessions appear here automatically when Claude Code or Codex loads skills from your repos. The hook fires on every agent startup.</p>
          <Link className="mt-5 inline-flex rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]" href="/dashboard/connect">Set up Connect Agent →</Link>
        </section>
      )}

      {showModal ? <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"><div className="w-full max-w-2xl rounded-xl bg-[color:var(--bg-surface)] p-5"><h2 className="text-lg font-semibold">Log Session</h2><div className="mt-4 grid gap-3"><select className="rounded bg-[color:var(--bg-base)] p-2" value={agent} onChange={(e) => setAgent(e.target.value)}><option value="claude_code">Claude Code</option><option value="codex">Codex</option><option value="cursor">Cursor</option></select><select className="rounded bg-[color:var(--bg-base)] p-2" value={repoId} onChange={(e) => setRepoId(e.target.value)}>{repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.full_name}</option>)}</select><select className="rounded bg-[color:var(--bg-base)] p-2" value={outcome} onChange={(e) => setOutcome(e.target.value)}><option>unknown</option><option>success</option><option>incident</option></select><textarea className="min-h-32 rounded bg-[color:var(--bg-base)] p-2 font-mono" placeholder="Code produced" value={code} onChange={(e) => setCode(e.target.value)} /><textarea className="min-h-24 rounded bg-[color:var(--bg-base)] p-2" placeholder="Notes" value={notes} onChange={(e) => setNotes(e.target.value)} /></div><div className="mt-4 flex justify-end gap-2"><button onClick={() => setShowModal(false)} type="button">Cancel</button><button className="rounded bg-[color:var(--accent-primary)] px-4 py-2 text-[color:var(--bg-base)]" disabled={saving} onClick={save} type="button">{saving ? "Saving..." : "Save Session"}</button></div></div></div> : null}
    </div>
  );
}
