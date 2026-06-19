"use client";

import { useMemo, useState } from "react";
import { Search, X } from "lucide-react";

import type { CompatibilityMatrix, SkillRegistryEntry } from "../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
const RUNTIMES = ["claude-code", "codex", "cursor", "copilot", "gemini-cli"];

type Tab = "org" | "marketplace" | "import" | "compatibility";

export function RegistryShell({
  accessToken,
  activeTab,
  compatibility,
  marketplaceEntries,
  orgEntries,
  orgId,
}: {
  accessToken: string;
  activeTab: Tab;
  compatibility: CompatibilityMatrix | null;
  marketplaceEntries: SkillRegistryEntry[];
  orgEntries: SkillRegistryEntry[];
  orgId: string;
}) {
  const [tab, setTab] = useState<Tab>(activeTab);
  const [entries, setEntries] = useState(orgEntries);
  const [marketplace, setMarketplace] = useState(marketplaceEntries);
  const [selected, setSelected] = useState<SkillRegistryEntry | null>(null);
  const [publishing, setPublishing] = useState(false);
  const [search, setSearch] = useState("");
  const visibleEntries = useMemo(() => entries.filter((entry) => `${entry.name} ${entry.domain} ${entry.description}`.toLowerCase().includes(search.toLowerCase())), [entries, search]);
  const publicCount = entries.filter((entry) => entry.visibility === "public").length;
  const installTotal = entries.reduce((sum, entry) => sum + (entry.install_count ?? 0), 0);
  const avgScore = entries.length ? Math.round(entries.reduce((sum, entry) => sum + (entry.score_total ?? 0), 0) / entries.length) : 0;

  async function install(entry: SkillRegistryEntry) {
    const response = await fetch(`${API_URL}/registry/orgs/${orgId}/entries/${entry.id}/install`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify({ repo_id: null }),
    });
    if (response.ok) {
      setMarketplace(marketplace.map((item) => (item.id === entry.id ? { ...item, install_count: item.install_count + 1 } : item)));
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Skill Registry</h1>
          <p className="mt-2 text-[15px] text-[color:var(--text-secondary)]">Publish, import, install, and govern reusable skills across your organisation.</p>
        </div>
        <button className="rounded-full bg-[color:var(--accent-primary)] px-5 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)]" onClick={() => setPublishing(true)} type="button">
          Publish Skill
        </button>
      </div>

      <div className="flex flex-wrap gap-2 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-1">
        {[
          ["org", "Org Registry"],
          ["marketplace", "Marketplace"],
          ["import", "Import"],
          ["compatibility", "Compatibility"],
        ].map(([key, label]) => (
          <button className={`rounded-lg px-4 py-2 text-[13px] font-semibold ${tab === key ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "text-[color:var(--text-secondary)]"}`} key={key} onClick={() => setTab(key as Tab)} type="button">
            {label}
          </button>
        ))}
      </div>

      {tab === "org" ? (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <Metric label="PUBLISHED SKILLS" value={entries.length} />
            <Metric label="PUBLIC SKILLS" value={publicCount} />
            <Metric label="TOTAL INSTALLS" value={installTotal} />
            <Metric label="AVG REGISTRY SCORE" value={`${avgScore}/100`} score={avgScore} />
          </div>
          <FilterBar search={search} setSearch={setSearch} />
          <CardGrid entries={visibleEntries} onSelect={setSelected} />
        </>
      ) : null}

      {tab === "marketplace" ? (
        <>
          <FilterBar search={search} setSearch={setSearch} />
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Verified Skills</h2>
          <div className="flex gap-4 overflow-x-auto pb-2">
            {marketplace.filter((entry) => entry.is_verified).map((entry) => <SkillCard entry={entry} key={entry.id} onSelect={setSelected} />)}
          </div>
          <CardGrid action={install} actionLabel="Install" entries={marketplace.filter((entry) => `${entry.name} ${entry.domain}`.toLowerCase().includes(search.toLowerCase()))} onSelect={setSelected} />
        </>
      ) : null}

      {tab === "import" ? <ImportPanel accessToken={accessToken} orgId={orgId} onImported={(entry) => setEntries([entry, ...entries])} /> : null}
      {tab === "compatibility" ? <CompatibilityPanel compatibility={compatibility} /> : null}
      {selected ? <EntryDetailDrawer entry={selected} onClose={() => setSelected(null)} /> : null}
      {publishing ? <PublishModal accessToken={accessToken} onClose={() => setPublishing(false)} onPublished={(entry) => setEntries([entry, ...entries])} orgId={orgId} /> : null}
    </div>
  );
}

function scoreTone(score: number) {
  if (score >= 70) return "text-[color:var(--accent-green)]";
  if (score >= 40) return "text-[#f59e0b]";
  return "text-[#ef4444]";
}

function Metric({ label, value, score }: { label: string; value: string | number; score?: number }) {
  return <div className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div><div className={`mt-3 text-[32px] font-semibold ${score === undefined ? "text-[color:var(--text-primary)]" : scoreTone(score)}`}>{value}</div></div>;
}

function FilterBar({ search, setSearch }: { search: string; setSearch: (value: string) => void }) {
  return <div className="flex flex-wrap items-center gap-3 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4"><Search className="h-4 w-4 text-[color:var(--text-tertiary)]" /><input className="h-10 flex-1 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px] outline-none focus:border-[color:var(--accent-primary)]" onChange={(event) => setSearch(event.target.value)} placeholder="Search registry skills, tags, domains..." value={search} /><select className="h-10 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px]"><option>All visibility</option><option>Private</option><option>Org</option><option>Public</option></select></div>;
}

function CardGrid({ entries, onSelect, action, actionLabel }: { entries: SkillRegistryEntry[]; onSelect: (entry: SkillRegistryEntry) => void; action?: (entry: SkillRegistryEntry) => void; actionLabel?: string }) {
  if (!entries.length) return <div className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[13px] text-[color:var(--text-secondary)]">No registry skills yet.</div>;
  return <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{entries.map((entry) => <SkillCard action={action} actionLabel={actionLabel} entry={entry} key={entry.id} onSelect={onSelect} />)}</section>;
}

function SkillCard({ entry, onSelect, action, actionLabel }: { entry: SkillRegistryEntry; onSelect: (entry: SkillRegistryEntry) => void; action?: (entry: SkillRegistryEntry) => void; actionLabel?: string }) {
  return (
    <article className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5 transition-colors hover:border-[color:var(--accent-primary)]">
      <button className="block w-full text-left" onClick={() => onSelect(entry)} type="button">
        <div className="flex items-start justify-between gap-3"><div><h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">{entry.domain}</h2><p className="mt-1 font-mono text-[12px] text-[color:var(--text-tertiary)]">{entry.name}</p></div><span className={`rounded-full px-2 py-0.5 text-[12px] font-semibold ${scoreTone(entry.score_total)}`}>{Math.round(entry.score_total)}/100</span></div>
        <p className="mt-4 line-clamp-2 min-h-[42px] text-[13px] leading-5 text-[color:var(--text-secondary)]">{entry.description}</p>
        <div className="mt-4 flex flex-wrap gap-2"><span className="rounded-full bg-[color:var(--bg-elevated)] px-2 py-0.5 text-[11px] text-[color:var(--text-secondary)]">{entry.visibility}</span>{entry.is_verified ? <span className="rounded-full bg-green-500/15 px-2 py-0.5 text-[11px] text-green-300">✓ Verified</span> : null}{entry.tags.slice(0, 3).map((tag) => <span className="rounded-full bg-[color:var(--bg-elevated)] px-2 py-0.5 text-[11px] text-[color:var(--text-tertiary)]" key={tag}>{tag}</span>)}</div>
        <div className="mt-4 flex flex-wrap gap-1 text-[11px] text-[color:var(--text-tertiary)]">{entry.compatible_runtimes.map((runtime) => <span className="rounded-md border border-[color:var(--bg-border)] px-1.5 py-0.5" key={runtime}>{runtime}</span>)}</div>
        <div className="mt-5 flex items-center justify-between border-t border-[color:var(--bg-border)] pt-4 text-[12px] text-[color:var(--text-tertiary)]"><span>↓ {entry.install_count} installs</span>{(entry.predicted_decay_days ?? 99) < 7 ? <span className="text-[#f59e0b]">⚠ Decays in {Math.round(entry.predicted_decay_days ?? 0)}d</span> : null}</div>
      </button>
      {action ? <button className="mt-4 rounded-full bg-[color:var(--accent-primary)] px-4 py-2 text-[12px] font-semibold text-[color:var(--bg-base)]" onClick={() => action(entry)} type="button">{actionLabel}</button> : null}
    </article>
  );
}

function EntryDetailDrawer({ entry, onClose }: { entry: SkillRegistryEntry; onClose: () => void }) {
  return <div className="fixed inset-0 z-50 bg-black/50"><aside className="ml-auto h-full w-full max-w-[480px] overflow-y-auto border-l border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-6"><button className="mb-5 rounded-lg p-2 text-[color:var(--text-tertiary)] hover:bg-[color:var(--bg-surface)]" onClick={onClose} type="button"><X className="h-4 w-4" /></button>{entry.is_deprecated ? <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-[13px] text-red-300">Deprecated — {entry.deprecation_message}</div> : null}<h2 className="text-[22px] font-semibold text-[color:var(--text-primary)]">{entry.name}</h2><p className="mt-2 text-[13px] text-[color:var(--text-secondary)]">{entry.description}</p><div className="mt-6 space-y-3">{[["Groundedness", entry.score_groundedness], ["Coverage", entry.score_coverage], ["Freshness", entry.score_freshness], ["Structure", entry.score_structure]].map(([label, value]) => <div key={label as string}><div className="mb-1 flex justify-between text-[12px] text-[color:var(--text-secondary)]"><span>{label}</span><span>{Math.round(Number(value))}/25</span></div><div className="h-1.5 rounded-full bg-white/10"><div className="h-full rounded-full bg-[color:var(--accent-primary)]" style={{ width: `${Math.min(100, Number(value) * 4)}%` }} /></div></div>)}</div><pre className="mt-6 max-h-[300px] overflow-auto rounded-xl bg-[color:var(--bg-surface)] p-4 font-mono text-[12px] leading-6 text-[color:var(--text-secondary)]">{entry.content_preview}</pre><div className="mt-6 rounded-xl border border-[color:var(--bg-border)] p-4 text-[13px] text-[color:var(--text-secondary)]"><div className="font-semibold text-[color:var(--text-primary)]">Half-life</div><div className="mt-2">Decay in {entry.predicted_decay_days == null ? "unknown" : `${Math.round(entry.predicted_decay_days)}d`} · confidence {Math.round((entry.decay_confidence ?? 0) * 100)}%</div>{entry.regen_queued ? <div className="mt-2 text-[color:var(--accent-green)]">Pre-emptive regen queued</div> : null}</div></aside></div>;
}

function PublishModal({ accessToken, orgId, onClose, onPublished }: { accessToken: string; orgId: string; onClose: () => void; onPublished: (entry: SkillRegistryEntry) => void }) {
  const [skillId, setSkillId] = useState("");
  const [description, setDescription] = useState("");
  const [visibility, setVisibility] = useState("private");
  const [tags, setTags] = useState("");
  const [status, setStatus] = useState("");
  async function submit() {
    setStatus("Publishing...");
    const response = await fetch(`${API_URL}/registry/orgs/${orgId}/publish`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` }, body: JSON.stringify({ skill_id: skillId, version: "1.0.0", visibility, tags: tags.split(",").map((tag) => tag.trim()).filter(Boolean), description, compatible_runtimes: RUNTIMES }) });
    if (response.ok) { const entry = (await response.json()) as SkillRegistryEntry; onPublished(entry); onClose(); } else { setStatus("Could not publish skill"); }
  }
  return <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"><div className="w-full max-w-lg rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6"><h2 className="text-[18px] font-semibold">Publish Skill</h2><input className="mt-4 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px]" onChange={(event) => setSkillId(event.target.value)} placeholder="Skill UUID" value={skillId} /><textarea className="mt-3 min-h-[100px] w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-[13px]" onChange={(event) => setDescription(event.target.value)} placeholder="Description" value={description} /><input className="mt-3 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px]" onChange={(event) => setTags(event.target.value)} placeholder="tags, comma, separated" value={tags} /><select className="mt-3 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px]" onChange={(event) => setVisibility(event.target.value)} value={visibility}><option value="private">Private</option><option value="org">Org</option><option value="public">Public</option></select><div className="mt-5 flex justify-end gap-3"><button className="px-4 py-2 text-[13px]" onClick={onClose} type="button">Cancel</button><button className="rounded-full bg-[color:var(--accent-primary)] px-5 py-2 text-[13px] font-semibold text-[color:var(--bg-base)]" onClick={submit} type="button">Submit</button></div>{status ? <p className="mt-3 text-[12px] text-[#ef4444]">{status}</p> : null}</div></div>;
}

function ImportPanel({ accessToken, orgId, onImported }: { accessToken: string; orgId: string; onImported: (entry: SkillRegistryEntry) => void }) {
  const [content, setContent] = useState("");
  const [name, setName] = useState("");
  const [repoId, setRepoId] = useState("");
  const [result, setResult] = useState<SkillRegistryEntry | null>(null);
  async function submit() {
    const response = await fetch(`${API_URL}/registry/orgs/${orgId}/import`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` }, body: JSON.stringify({ content, source: "custom", repo_id: repoId, name }) });
    if (response.ok) { const body = (await response.json()) as { entry: SkillRegistryEntry }; setResult(body.entry); onImported(body.entry); }
  }
  return <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6"><h2 className="text-[18px] font-semibold">Import Skill</h2><textarea className="mt-4 min-h-[260px] w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 font-mono text-[13px]" onChange={(event) => setContent(event.target.value)} placeholder="Paste your CLAUDE.md, AGENTS.md, or .cursorrules content here" value={content} /><div className="mt-3 grid gap-3 md:grid-cols-2"><input className="h-11 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px]" onChange={(event) => setName(event.target.value)} placeholder="Name" value={name} /><input className="h-11 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px]" onChange={(event) => setRepoId(event.target.value)} placeholder="Repo UUID" value={repoId} /></div><button className="mt-4 rounded-full bg-[color:var(--accent-primary)] px-5 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)]" onClick={submit} type="button">Analyse & Import</button>{result ? <div className="mt-5 rounded-xl border border-[color:var(--bg-border)] p-4"><div className={`text-[22px] font-semibold ${scoreTone(result.score_total)}`}>{Math.round(result.score_total)}/100</div><p className="mt-2 text-[13px] text-[color:var(--text-secondary)]">Imported as private registry entry.</p></div> : null}</section>;
}

function CompatibilityPanel({ compatibility }: { compatibility: CompatibilityMatrix | null }) {
  if (!compatibility) return <div className="text-[13px] text-[color:var(--text-secondary)]">No compatibility data yet.</div>;
  return <div className="overflow-x-auto rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]"><table className="w-full min-w-[800px] text-left text-[13px]"><thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]"><tr><th className="px-5 py-3">Skill</th>{compatibility.runtimes.map((runtime) => <th className="px-5 py-3" key={runtime}>{runtime}</th>)}</tr></thead><tbody>{compatibility.skills.map((skill) => <tr className="border-t border-[color:var(--bg-border)]" key={skill.skill_id}><td className="px-5 py-4 font-medium">{skill.domain}</td>{compatibility.runtimes.map((runtime) => { const state = compatibility.matrix[skill.skill_id]?.[runtime] ?? "untested"; return <td className={state === "compatible" ? "px-5 py-4 text-[color:var(--accent-green)]" : state === "incompatible" ? "px-5 py-4 text-[#ef4444]" : "px-5 py-4 text-[#f59e0b]"} key={runtime}>{state === "compatible" ? "✓ Compatible" : state === "incompatible" ? "✗ Incompatible" : "~ Untested"}</td>; })}</tr>)}</tbody></table></div>;
}
