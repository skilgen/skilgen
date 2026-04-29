"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, ClipboardList, GitBranch, History, Loader2, Settings, ShieldCheck } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type Tab = "history" | "paste" | "settings";
type Repo = { id: string; name: string; full_name: string };
type Finding = {
  id?: string | null;
  file_path: string;
  line_number: number | null;
  severity: string;
  title: string;
  message: string;
  skill_name?: string | null;
  rule_id?: string | null;
  suggestion?: string | null;
};
type PRReview = {
  id: string;
  repo_id: string;
  repo_name: string | null;
  pr_url: string | null;
  pr_number: number | null;
  title: string | null;
  summary: string | null;
  model_used: string | null;
  findings_count: number;
  skills_checked: number;
  lines_scanned: number;
  created_at: string;
  findings: Finding[];
};
type ScanJobResponse = { job_id?: string; id?: string; status?: string; detail?: string };
type ScanStatusResponse = {
  status?: string;
  state?: string;
  done?: boolean;
  error?: string;
  detail?: string;
  message?: string;
  reviews_created?: number;
  scanned_prs?: number;
  scanned?: number;
  queued?: number;
  skipped?: number;
};

export default function ReviewPage() {
  const [tab, setTab] = useState<Tab>("history");
  const [orgId, setOrgId] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [repos, setRepos] = useState<Repo[]>([]);
  const [repoId, setRepoId] = useState("");
  const [history, setHistory] = useState<PRReview[]>([]);
  const [selected, setSelected] = useState<PRReview | null>(null);
  const [diff, setDiff] = useState("");
  const [prUrl, setPrUrl] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [scanAllLoading, setScanAllLoading] = useState(false);
  const [scanAllStatus, setScanAllStatus] = useState("");

  async function bootstrap() {
    const org = await fetch(`${API_URL}/orgs/bootstrap`).then((response) => response.json());
    const key = await fetch(`${API_URL}/orgs/${org.id}/api-key`, { headers: { Authorization: "Bearer bootstrap" } }).then((response) => response.json());
    const repoRows = await fetch(`${API_URL}/orgs/${org.id}/repos`, { headers: { Authorization: `Bearer ${key.api_key}` } }).then((response) => response.json());
    setOrgId(org.id);
    setApiKey(key.api_key);
    setRepos(repoRows);
    setRepoId(repoRows[0]?.id ?? "");
    await loadHistory(org.id, key.api_key);
  }

  async function loadHistory(nextOrgId = orgId, nextApiKey = apiKey) {
    if (!nextOrgId || !nextApiKey) return;
    const response = await fetch(`${API_URL}/orgs/${nextOrgId}/review/history`, { headers: { Authorization: `Bearer ${nextApiKey}` } });
    if (response.ok) {
      const body = (await response.json()) as { reviews: PRReview[] };
      setHistory(body.reviews);
      setSelected((current) => (body.reviews.some((review) => review.id === current?.id) ? current : body.reviews[0] ?? null));
    }
  }

  useEffect(() => {
    void bootstrap();
  }, []);

  async function scan() {
    if (!orgId || !apiKey || !repoId || !diff.trim()) return;
    setLoading(true);
    setStatus("Scanning diff...");
    const response = await fetch(`${API_URL}/orgs/${orgId}/review/scan-diff`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({ repo_id: repoId, diff, pr_url: prUrl || null, title: title || null }),
    });
    if (response.ok) {
      const review = (await response.json()) as PRReview;
      setHistory((current) => [review, ...current.filter((item) => item.id !== review.id)]);
      setSelected(review);
      setTab("history");
      setStatus("Review saved");
    } else {
      setStatus("Could not scan diff");
    }
    setLoading(false);
  }

  async function scanAllRepos() {
    if (!orgId || !apiKey || repos.length === 0) return;
    setScanAllLoading(true);
    setScanAllStatus("Loading PRs from connected repos...");
    try {
      const response = await fetch(`${API_URL}/orgs/${orgId}/review/scan-repo-prs`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      });
      const body = (await response.json().catch(() => ({}))) as ScanJobResponse;
      if (!response.ok) throw new Error(body.detail || "Could not start PR scan.");
      const jobId = body.job_id ?? body.id;
      if (!jobId) {
        await loadHistory();
        setScanAllStatus("PR scan finished.");
        return;
      }

      for (let attempt = 0; attempt < 45; attempt += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, attempt < 6 ? 1200 : 2500));
        const pollResponse = await fetch(`${API_URL}/orgs/${orgId}/review/scan-status/${jobId}`, {
          headers: { Authorization: `Bearer ${apiKey}` },
        });
        const pollBody = (await pollResponse.json().catch(() => ({}))) as ScanStatusResponse;
        if (!pollResponse.ok) throw new Error(pollBody.detail || "Could not check PR scan status.");
        const nextStatus = pollBody.status ?? pollBody.state ?? "";
        if (pollBody.error || nextStatus === "failed" || nextStatus === "error") {
          throw new Error(pollBody.error || pollBody.detail || pollBody.message || "PR scan failed.");
        }
        const scanned = pollBody.scanned ?? pollBody.scanned_prs;
        const queued = pollBody.queued ?? pollBody.reviews_created;
        setScanAllStatus(scanned !== undefined || queued !== undefined ? `Scanning PRs... ${scanned ?? 0} scanned · ${queued ?? 0} loaded` : "Scanning PRs...");
        if (pollBody.done || ["complete", "completed", "succeeded", "success"].includes(nextStatus)) {
          await loadHistory();
          setScanAllStatus("PR history refreshed.");
          return;
        }
      }
      await loadHistory();
      setScanAllStatus("Scan is still running. Refreshed current history.");
    } catch (error) {
      setScanAllStatus(error instanceof Error ? error.message : "Could not load PRs.");
    } finally {
      setScanAllLoading(false);
    }
  }

  const selectedFindings = useMemo(() => selected?.findings ?? [], [selected]);
  const sample = `diff --git a/app.py b/app.py
@@ -1,2 +1,3 @@
+sql = "SELECT * FROM users WHERE id=" + user_id
+print(raw_exception)`;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Code Review</h1>
          <p className="mt-2 text-[15px] text-[color:var(--text-secondary)]">PR-level review history powered by your repository skills.</p>
        </div>
        <button className="rounded-full bg-[color:var(--accent-primary)] px-5 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)]" onClick={() => setTab("paste")} type="button">
          Scan Diff
        </button>
      </div>

      <div className="flex flex-wrap gap-2 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-1">
        {[
          ["history", History, "History"],
          ["paste", ClipboardList, "Paste diff"],
          ["settings", Settings, "Settings"],
        ].map(([key, Icon, label]) => {
          const TabIcon = Icon as typeof History;
          return (
            <button className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-[13px] font-semibold ${tab === key ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "text-[color:var(--text-secondary)] hover:bg-[color:var(--bg-elevated)]"}`} key={key as string} onClick={() => setTab(key as Tab)} type="button">
              <TabIcon className="h-4 w-4" />
              {label as string}
            </button>
          );
        })}
      </div>

      {tab === "history" ? (
        <div className="grid gap-5 lg:grid-cols-[360px_1fr]">
          <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Recent PR Reviews</h2>
              <button className="text-[12px] text-[color:var(--accent-primary)]" onClick={() => void loadHistory()} type="button">Refresh</button>
            </div>
            <div className="space-y-2">
              {history.length ? history.map((review) => (
                <button className={`block w-full rounded-lg border p-3 text-left ${selected?.id === review.id ? "border-[color:var(--accent-primary)] bg-[color:var(--bg-elevated)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-base)]"}`} key={review.id} onClick={() => setSelected(review)} type="button">
                  <div className="flex items-center justify-between gap-3">
                    <div className="truncate text-[13px] font-semibold text-[color:var(--text-primary)]">{review.title || review.pr_url || "Pasted diff review"}</div>
                    <span className={review.findings_count ? "text-[12px] font-semibold text-[#f59e0b]" : "text-[12px] font-semibold text-[color:var(--accent-green)]"}>{review.findings_count}</span>
                  </div>
                  <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{review.repo_name || review.repo_id} · {new Date(review.created_at).toLocaleString()}</div>
                </button>
              )) : repos.length ? (
                <ReviewHistoryEmptyState loading={scanAllLoading} onScanAll={scanAllRepos} status={scanAllStatus} />
              ) : (
                <ConnectRepoEmptyState />
              )}
            </div>
          </section>
          <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
            {selected ? (
              <>
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">{selected.title || "PR Review"}</h2>
                    <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{selected.summary || "No summary available."}</p>
                    {selected.pr_url ? <a className="mt-2 inline-block text-[13px] font-semibold text-[color:var(--accent-primary)]" href={selected.pr_url} rel="noreferrer" target="_blank">Open PR</a> : null}
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <MiniMetric label="Findings" value={selected.findings_count} />
                    <MiniMetric label="Skills" value={selected.skills_checked} />
                    <MiniMetric label="Lines" value={selected.lines_scanned} />
                  </div>
                </div>
                <div className="mt-5 space-y-3">
                  {selectedFindings.length ? selectedFindings.map((finding, index) => (
                    <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4" key={finding.id ?? `${finding.file_path}-${index}`}>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="rounded bg-[color:var(--bg-elevated)] px-2 py-0.5 font-mono text-[12px]">{finding.file_path}{finding.line_number ? `:${finding.line_number}` : ""}</span>
                        <span className={finding.severity === "error" ? "rounded bg-red-500/15 px-2 py-0.5 text-[12px] text-red-300" : "rounded bg-[#f59e0b]/15 px-2 py-0.5 text-[12px] text-[#f59e0b]"}>{finding.severity}</span>
                        {finding.skill_name ? <span className="rounded bg-[color:var(--accent-primary)] px-2 py-0.5 text-[12px] text-[color:var(--bg-base)]">{finding.skill_name}</span> : null}
                      </div>
                      <h3 className="mt-3 text-[14px] font-semibold text-[color:var(--text-primary)]">{finding.title}</h3>
                      <p className="mt-2 text-[13px] leading-6 text-[color:var(--text-secondary)]">{finding.message}</p>
                      {finding.suggestion ? <pre className="mt-3 overflow-auto rounded-lg bg-[color:var(--bg-elevated)] p-3 font-mono text-[12px] leading-5 text-[color:var(--text-secondary)]">{finding.suggestion}</pre> : null}
                    </article>
                  )) : <div className="py-12 text-center"><CheckCircle2 className="mx-auto h-12 w-12 text-[color:var(--accent-green)]" /><h3 className="mt-3 text-[16px] font-semibold">No findings in this review.</h3></div>}
                </div>
              </>
            ) : history.length ? <EmptyState title="Select a review" text="Review details and findings will appear here." /> : <EmptyState title="No PR reviews loaded" text={repos.length ? "Load PRs from your connected repos or paste a diff to create a review." : "Connect a repo to scan PRs against your skills."} />}
          </section>
        </div>
      ) : null}

      {tab === "paste" ? (
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          <div className="grid gap-3 md:grid-cols-3">
            <select className="h-11 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px]" value={repoId} onChange={(event) => setRepoId(event.target.value)}>
              {repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.full_name}</option>)}
            </select>
            <input className="h-11 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px]" onChange={(event) => setPrUrl(event.target.value)} placeholder="PR URL (optional)" value={prUrl} />
            <input className="h-11 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px]" onChange={(event) => setTitle(event.target.value)} placeholder="Review title (optional)" value={title} />
          </div>
          <textarea className="mt-4 min-h-[360px] w-full rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 font-mono text-[13px] leading-6" onChange={(event) => setDiff(event.target.value)} placeholder="Paste a git diff here..." value={diff} />
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <button className="rounded-full bg-[color:var(--accent-primary)] px-5 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)] disabled:opacity-60" disabled={loading || !repoId || !diff.trim()} onClick={scan} type="button">{loading ? "Scanning..." : "Scan and Save"}</button>
            <button className="rounded-full border border-[color:var(--bg-border)] px-5 py-2.5 text-[13px] font-semibold text-[color:var(--text-primary)]" onClick={() => setDiff(sample)} type="button">Try sample</button>
            {status ? <span className="text-[13px] text-[color:var(--text-secondary)]">{status}</span> : null}
          </div>
        </section>
      ) : null}

      {tab === "settings" ? (
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-1 h-5 w-5 text-[color:var(--accent-primary)]" />
            <div>
              <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Review Settings</h2>
              <p className="mt-2 max-w-2xl text-[13px] leading-6 text-[color:var(--text-secondary)]">Diff scans use configured org LLM settings when available and fall back to deterministic skill anti-pattern checks. Results are saved as PR-level history for audit and follow-up.</p>
              <div className="mt-5 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 text-[13px] text-[color:var(--text-secondary)]">
                <div className="font-semibold text-[color:var(--text-primary)]">Current scope</div>
                <div className="mt-2">Organization: {orgId || "loading"} · Repositories: {repos.length}</div>
              </div>
            </div>
          </div>
        </section>
      ) : null}
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: number }) {
  return <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-4 py-3"><div className="text-[18px] font-semibold text-[color:var(--text-primary)]">{value}</div><div className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div></div>;
}

function EmptyState({ title, text }: { title: string; text: string }) {
  return <div className="grid min-h-[220px] place-items-center text-center text-[color:var(--text-secondary)]"><div><AlertTriangle className="mx-auto h-10 w-10 text-[color:var(--text-tertiary)]" /><h3 className="mt-3 text-[15px] font-semibold text-[color:var(--text-primary)]">{title}</h3><p className="mt-1 text-[13px]">{text}</p></div></div>;
}

function ReviewHistoryEmptyState({ loading, onScanAll, status }: { loading: boolean; onScanAll: () => void; status: string }) {
  return (
    <div className="grid min-h-[260px] place-items-center text-center text-[color:var(--text-secondary)]">
      <div>
        <History className="mx-auto h-10 w-10 text-[color:var(--text-tertiary)]" />
        <h3 className="mt-3 text-[15px] font-semibold text-[color:var(--text-primary)]">No PRs scanned yet</h3>
        <p className="mx-auto mt-1 max-w-[280px] text-[13px]">Load PRs from connected repos to seed review history.</p>
        <button className="mt-4 inline-flex items-center gap-2 rounded-full bg-[color:var(--accent-primary)] px-4 py-2 text-[13px] font-semibold text-[color:var(--bg-base)] disabled:cursor-wait disabled:opacity-60" disabled={loading} onClick={onScanAll} type="button">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ClipboardList className="h-4 w-4" />}
          Load PRs from all repos
        </button>
        {status ? <p className="mt-3 text-[12px] text-[color:var(--text-tertiary)]">{status}</p> : null}
      </div>
    </div>
  );
}

function ConnectRepoEmptyState() {
  return (
    <div className="grid min-h-[260px] place-items-center text-center text-[color:var(--text-secondary)]">
      <div>
        <GitBranch className="mx-auto h-10 w-10 text-[color:var(--text-tertiary)]" />
        <h3 className="mt-3 text-[15px] font-semibold text-[color:var(--text-primary)]">Connect a repo to scan PRs</h3>
        <p className="mx-auto mt-1 max-w-[280px] text-[13px]">Review history appears after Skillayer can see a repository.</p>
        <a className="mt-4 inline-flex items-center rounded-full border border-[color:var(--bg-border)] px-4 py-2 text-[13px] font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href="/dashboard/sources">
          Connect repo
        </a>
      </div>
    </div>
  );
}
