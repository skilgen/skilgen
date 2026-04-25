"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, ShieldCheck, AlertTriangle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
export const dynamic = "force-dynamic";

type Repo = { id: string; name: string; full_name: string };
type Comment = { file: string; line: number; skill_name: string; anti_pattern: string; message: string; severity: string };

export default function ReviewPage() {
  const [repos, setRepos] = useState<Repo[]>([]);
  const [repoId, setRepoId] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [diff, setDiff] = useState("");
  const [prUrl, setPrUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ comments: Comment[]; skills_checked: number; lines_scanned: number } | null>(null);
  const grouped = useMemo(() => {
    const map = new Map<string, Comment[]>();
    result?.comments.forEach((comment) => map.set(comment.file, [...(map.get(comment.file) ?? []), comment]));
    return [...map.entries()];
  }, [result]);

  async function bootstrap() {
    const org = await fetch(`${API_URL}/orgs/bootstrap`).then((r) => r.json());
    const key = await fetch(`${API_URL}/orgs/${org.id}/api-key`, { headers: { Authorization: "Bearer bootstrap" } }).then((r) => r.json());
    const repoRows = await fetch(`${API_URL}/orgs/${org.id}/repos`, { headers: { Authorization: `Bearer ${key.api_key}` } }).then((r) => r.json());
    setApiKey(key.api_key); setRepos(repoRows); setRepoId(repoRows[0]?.id ?? "");
  }
  useEffect(() => { void bootstrap(); }, []);
  async function scan() {
    setLoading(true);
    const response = await fetch(`${API_URL}/repos/${repoId}/review`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` }, body: JSON.stringify({ diff, pr_url: prUrl || null }) });
    setResult(response.ok ? await response.json() : { comments: [], skills_checked: 0, lines_scanned: 0 });
    setLoading(false);
  }
  const sample = `diff --git a/app.py b/app.py\n@@ -1,2 +1,3 @@\n+sql = "SELECT * FROM users WHERE id=" + user_id\n+print(raw_exception)`;
  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Skill-Aware Code Review</h1><p className="mt-1 text-sm text-[color:var(--text-secondary)]">Check your diff against active skill anti-patterns.</p></div>
      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          {repos.length > 1 ? <select className="mb-3 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-2" value={repoId} onChange={(e) => setRepoId(e.target.value)}>{repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.full_name}</option>)}</select> : null}
          <textarea className="min-h-[300px] w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 font-mono text-sm" placeholder={"Paste your git diff here...\n\ngit diff HEAD~1 HEAD"} value={diff} onChange={(e) => setDiff(e.target.value)} />
          <input className="mt-3 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-2 text-sm" placeholder="PR URL (optional)" value={prUrl} onChange={(e) => setPrUrl(e.target.value)} />
          <div className="mt-4 flex gap-3"><button className="rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)] disabled:opacity-60" disabled={loading || !repoId || !diff} onClick={scan}>{loading ? "Scanning..." : "Scan Diff"}</button><button className="rounded-md border border-[color:var(--bg-border)] px-4 py-2 text-sm" onClick={() => setDiff(sample)}>Try example diff</button></div>
        </section>
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          {loading ? <div className="animate-pulse space-y-3"><div className="h-6 rounded bg-white/10" /><div className="h-32 rounded bg-white/10" /></div> : result ? (
            <div>
              <div className="text-sm text-[color:var(--text-secondary)]">{result.comments.length} issues found | {result.skills_checked} skills checked | {result.lines_scanned} lines scanned</div>
              {result.comments.length === 0 ? <div className="mt-10 text-center"><CheckCircle2 className="mx-auto h-12 w-12 text-[color:var(--accent-green)]" /><h2 className="mt-3 text-lg font-semibold">No anti-pattern violations detected. Clean code!</h2></div> : <div className="mt-4 space-y-4">{grouped.map(([file, comments]) => <div key={file}><div className="rounded-t-md bg-[#1A1A2E] px-3 py-2 font-mono text-sm">{file}</div>{comments.map((comment) => <div className="border border-[color:var(--bg-border)] p-3" key={`${file}-${comment.line}-${comment.anti_pattern}`}><div className="flex gap-2"><span className="rounded bg-white/10 px-2">Line {comment.line}</span><span className="rounded bg-[color:var(--accent-primary)] px-2 text-[color:var(--bg-base)]">{comment.skill_name}</span><AlertTriangle className="h-4 w-4 text-[#f59e0b]" /></div><p className="mt-2 text-sm">{comment.message}</p><p className="mt-2 text-sm text-[#f59e0b]">{comment.anti_pattern}</p></div>)}</div>)}</div>}
              <div className="mt-4 flex gap-2"><button className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm" onClick={() => navigator.clipboard.writeText(JSON.stringify(result, null, 2))}>Copy Report</button><button className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm" onClick={() => setResult(null)}>Clear</button></div>
            </div>
          ) : <div className="grid h-full min-h-[300px] place-items-center text-center text-[color:var(--text-secondary)]"><div><ShieldCheck className="mx-auto h-12 w-12 text-[color:var(--accent-primary)]" /><p className="mt-3">Scan a diff to see skill-aware findings.</p></div></div>}
        </section>
      </div>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><h2 className="font-semibold">Review history</h2><p className="mt-2 text-sm text-[color:var(--text-secondary)]">Recent scans appear here after your first review.</p></section>
    </div>
  );
}
