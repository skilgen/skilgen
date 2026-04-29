"use client";

import { AlertTriangle, ChevronDown, ChevronUp, Loader2, RotateCcw, Send, Settings, Sparkles } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { cn } from "@skillayer/ui";
import type { SkillQLResult, SkillQLSuggestions } from "../../../lib/data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
const MAX_QUERY_LENGTH = 500;

type Props = {
  accessToken: string;
  orgId: string;
  suggestions: SkillQLSuggestions;
};

type SkillQLError = {
  type: "llm_not_configured" | "query_parse_failed" | "network" | "unknown";
  message: string;
};

function stringify(value: unknown): string {
  if (value === null || typeof value === "undefined") return "";
  if (Array.isArray(value)) return value.map((item) => (typeof item === "object" ? JSON.stringify(item) : String(item))).join(", ");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function dateValue(row: Record<string, unknown>): number {
  const raw = row.created_at ?? row.session_start ?? row.opened_at ?? row.merged_at ?? row.last_loaded_at ?? row.updated_at;
  const value = typeof raw === "string" ? new Date(raw).getTime() : 0;
  return Number.isFinite(value) ? value : 0;
}

function formatColumn(column: string): string {
  return column.replaceAll("_", " ");
}

async function askSkillQL(accessToken: string, orgId: string, query: string): Promise<SkillQLResult> {
  const response = await fetch(`${API_URL}/orgs/${orgId}/skillql`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
    body: JSON.stringify({ query }),
    cache: "no-store",
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const error = body && typeof body === "object" ? body as { error?: string; message?: string } : {};
    throw {
      type: error.error === "llm_not_configured" || error.error === "query_parse_failed" ? error.error : "network",
      message: error.message || "SkillQL could not complete the request.",
    } satisfies SkillQLError;
  }
  return body as SkillQLResult;
}

function Thinking() {
  return (
    <div className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 text-center">
      <div className="inline-flex items-center gap-3 text-sm font-semibold text-[color:var(--text-secondary)]">
        <Loader2 className="h-4 w-4 animate-spin text-[color:var(--accent-primary)]" />
        SkillQL is thinking
        <span className="inline-flex gap-1">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[color:var(--accent-primary)]" />
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[color:var(--accent-primary)] [animation-delay:120ms]" />
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[color:var(--accent-primary)] [animation-delay:240ms]" />
        </span>
      </div>
    </div>
  );
}

function ErrorPanel({ error }: { error: SkillQLError }) {
  const llm = error.type === "llm_not_configured";
  return (
    <div className={cn("rounded-[24px] border px-5 py-4", llm ? "border-amber-400/35 bg-amber-400/10" : "border-red-500/30 bg-red-500/10")}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <AlertTriangle className={cn("mt-0.5 h-5 w-5 shrink-0", llm ? "text-amber-200" : "text-red-200")} />
          <div>
            <div className="font-semibold text-[color:var(--text-primary)]">{llm ? "LLM not configured" : error.type === "query_parse_failed" ? "Could not parse that question" : "SkillQL request failed"}</div>
            <p className={cn("mt-1 text-sm", llm ? "text-amber-100/80" : "text-red-100/80")}>{error.message}</p>
          </div>
        </div>
        {llm ? (
          <Link className="inline-flex items-center justify-center rounded-lg border border-amber-200/40 px-3 py-2 text-sm font-semibold text-amber-100 transition-colors hover:bg-amber-400/15" href="/dashboard/settings?tab=llm">
            <Settings className="mr-2 h-4 w-4" /> Settings → LLM
          </Link>
        ) : null}
      </div>
    </div>
  );
}

function SourceBadges({ sources }: { sources: string[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {sources.map((source) => (
        <span className="rounded-full border border-[color:var(--bg-border)] bg-white/5 px-2.5 py-1 text-xs font-semibold text-[color:var(--text-secondary)]" key={source}>
          {source.replaceAll("_", " ")}
        </span>
      ))}
    </div>
  );
}

function TableResult({ result }: { result: SkillQLResult }) {
  const [sort, setSort] = useState<{ column: string; direction: "asc" | "desc" } | null>(null);
  const rows = useMemo(() => {
    if (!sort) return result.rows;
    return [...result.rows].sort((a, b) => {
      const av = stringify(a[sort.column]);
      const bv = stringify(b[sort.column]);
      return sort.direction === "asc" ? av.localeCompare(bv, undefined, { numeric: true }) : bv.localeCompare(av, undefined, { numeric: true });
    });
  }, [result.rows, sort]);

  function toggle(column: string) {
    setSort((current) => current?.column === column && current.direction === "asc" ? { column, direction: "desc" } : { column, direction: "asc" });
  }

  return (
    <div className="max-h-96 overflow-auto rounded-2xl border border-[color:var(--bg-border)] bg-black/10">
      <table className="w-full min-w-[720px] border-collapse text-left text-sm">
        <thead className="sticky top-0 z-10 bg-[color:var(--bg-surface)]">
          <tr>
            {result.columns.map((column) => (
              <th className="border-b border-[color:var(--bg-border)] px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]" key={column}>
                <button className="inline-flex items-center gap-1 text-left transition-colors hover:text-[color:var(--text-primary)]" onClick={() => toggle(column)} type="button">
                  {formatColumn(column)}
                  {sort?.column === column ? <span className="text-[color:var(--accent-primary)]">{sort.direction === "asc" ? "↑" : "↓"}</span> : null}
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr className="border-b border-[color:var(--bg-border)]/70 last:border-b-0" key={index}>
              {result.columns.map((column) => (
                <td className="max-w-[260px] truncate px-4 py-3 text-[color:var(--text-secondary)]" key={column} title={stringify(row[column])}>
                  {stringify(row[column]) || <span className="text-[color:var(--text-tertiary)]">-</span>}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function NumberResult({ result }: { result: SkillQLResult }) {
  const first = result.rows[0] ?? {};
  const value = stringify(Object.values(first)[0] ?? result.row_count);
  return <div className="rounded-2xl border border-[color:var(--bg-border)] bg-black/10 px-6 py-8 text-center text-6xl font-semibold text-[color:var(--text-primary)]">{value}</div>;
}

function ListResult({ result }: { result: SkillQLResult }) {
  const [showAll, setShowAll] = useState(false);
  const rows = showAll ? result.rows : result.rows.slice(0, 50);
  return (
    <div className="space-y-3">
      <div className="rounded-2xl border border-[color:var(--bg-border)] bg-black/10 p-4">
        <ol className="space-y-2">
          {rows.map((row, index) => (
            <li className="rounded-xl bg-white/5 px-3 py-2 text-sm text-[color:var(--text-secondary)]" key={index}>{stringify(row)}</li>
          ))}
        </ol>
      </div>
      {result.rows.length > 50 && !showAll ? (
        <button className="rounded-lg border border-[color:var(--bg-border)] px-3 py-2 text-sm font-semibold text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" onClick={() => setShowAll(true)} type="button">
          Show all
        </button>
      ) : null}
    </div>
  );
}

function TimelineResult({ result }: { result: SkillQLResult }) {
  const rows = [...result.rows].sort((a, b) => dateValue(a) - dateValue(b));
  return (
    <div className="space-y-3">
      {rows.map((row, index) => {
        const when = row.created_at ?? row.session_start ?? row.opened_at ?? row.merged_at ?? row.last_loaded_at ?? row.updated_at;
        return (
          <div className="grid gap-3 rounded-2xl border border-[color:var(--bg-border)] bg-black/10 p-4 sm:grid-cols-[160px_1fr]" key={index}>
            <div className="text-xs font-semibold text-[color:var(--text-tertiary)]">{stringify(when) || "No timestamp"}</div>
            <div className="text-sm text-[color:var(--text-secondary)]">{stringify(row)}</div>
          </div>
        );
      })}
    </div>
  );
}

function ResultPanel({ result, onAsk }: { result: SkillQLResult; onAsk: (query: string) => void }) {
  return (
    <section className="space-y-4 rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="italic text-[color:var(--text-secondary)]">{result.intent}</p>
          <div className="mt-3"><SourceBadges sources={result.data_sources} /></div>
        </div>
        <span className="rounded-full bg-white/5 px-3 py-1 text-xs font-semibold text-[color:var(--text-tertiary)]">{result.row_count} rows</span>
      </div>

      {result.rows.length ? (
        result.result_format === "number" ? <NumberResult result={result} /> : result.result_format === "list" ? <ListResult result={result} /> : result.result_format === "timeline" ? <TimelineResult result={result} /> : <TableResult result={result} />
      ) : (
        <div className="rounded-2xl border border-dashed border-[color:var(--bg-border)] bg-black/10 px-5 py-10 text-center text-sm text-[color:var(--text-secondary)]">No rows matched this question.</div>
      )}

      {result.suggested_followups.length ? (
        <div className="flex flex-wrap gap-2 border-t border-[color:var(--bg-border)] pt-4">
          {result.suggested_followups.map((followup) => (
            <button className="rounded-full border border-[color:var(--bg-border)] bg-white/5 px-3 py-1.5 text-xs font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" key={followup} onClick={() => onAsk(followup)} type="button">
              {followup}
            </button>
          ))}
        </div>
      ) : null}
    </section>
  );
}

export function SkillQLClient({ accessToken, orgId, suggestions }: Props) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<SkillQLResult | null>(null);
  const [error, setError] = useState<SkillQLError | null>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [historyOpen, setHistoryOpen] = useState(false);

  async function submit(nextQuery = query) {
    const trimmed = nextQuery.trim();
    if (!trimmed || trimmed.length > MAX_QUERY_LENGTH || loading) return;
    setQuery(trimmed);
    setLoading(true);
    setError(null);
    try {
      const nextResult = await askSkillQL(accessToken, orgId, trimmed);
      setResult(nextResult);
      setHistory((current) => [trimmed, ...current.filter((item) => item !== trimmed)].slice(0, 5));
    } catch (err) {
      const typed = err as Partial<SkillQLError>;
      setError({ type: typed.type ?? "unknown", message: typed.message ?? "SkillQL could not complete the request." });
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setQuery("");
    setResult(null);
    setError(null);
  }

  const showSuggestions = !query.trim();

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="text-center">
        <div className="inline-flex items-center gap-2 text-5xl font-semibold tracking-[-0.03em]">
          <Sparkles className="h-9 w-9 text-indigo-300" />
          <span className="bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">SkillQL</span>
        </div>
        <p className="mx-auto mt-3 max-w-2xl text-sm text-[color:var(--text-secondary)]">Ask natural-language questions across skills, agent sessions, pull requests, attribution risk, and audit events.</p>
      </div>

      <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <textarea
          className="min-h-[92px] w-full resize-none rounded-2xl border border-[color:var(--bg-border)] bg-black/15 p-4 text-sm text-[color:var(--text-primary)] outline-none placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]"
          maxLength={MAX_QUERY_LENGTH}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
              event.preventDefault();
              void submit();
            }
          }}
          placeholder="Ask about agent risk, stale skills, developer activity, or audit events..."
          rows={3}
          value={query}
        />
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <span className={cn("text-xs", query.length >= MAX_QUERY_LENGTH ? "text-red-200" : "text-[color:var(--text-tertiary)]")}>{query.length}/{MAX_QUERY_LENGTH}</span>
          <div className="flex gap-2">
            {result || error ? (
              <button className="inline-flex items-center gap-2 rounded-lg border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" onClick={reset} type="button">
                <RotateCcw className="h-4 w-4" /> Ask another question
              </button>
            ) : null}
            <button className="inline-flex items-center gap-2 rounded-lg bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-black transition-colors hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-60" disabled={!query.trim() || query.length > MAX_QUERY_LENGTH || loading} onClick={() => void submit()} type="button">
              <Send className="h-4 w-4" /> Ask SkillQL
            </button>
          </div>
        </div>
      </section>

      {history.length ? (
        <section className="rounded-2xl border border-[color:var(--bg-border)] bg-black/10 p-3">
          <button className="flex w-full items-center justify-between text-sm font-semibold text-[color:var(--text-secondary)]" onClick={() => setHistoryOpen((value) => !value)} type="button">
            Query history
            {historyOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
          {historyOpen ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {history.map((item) => (
                <button className="rounded-full border border-[color:var(--bg-border)] px-3 py-1.5 text-xs text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" key={item} onClick={() => { setQuery(item); void submit(item); }} type="button">
                  {item}
                </button>
              ))}
            </div>
          ) : null}
        </section>
      ) : null}

      {showSuggestions ? (
        <div className="grid gap-3 md:grid-cols-2">
          {Object.entries(suggestions).map(([category, items]) => (
            <section className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={category}>
              <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">{category}</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {items.map((item) => (
                  <button className="rounded-full border border-[color:var(--bg-border)] bg-black/15 px-3 py-1.5 text-left text-xs text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" key={item} onClick={() => { setQuery(item); void submit(item); }} type="button">
                    {item}
                  </button>
                ))}
              </div>
            </section>
          ))}
        </div>
      ) : null}

      {loading ? <Thinking /> : null}
      {error ? <ErrorPanel error={error} /> : null}
      {result && !loading ? <ResultPanel result={result} onAsk={(next) => { setQuery(next); void submit(next); }} /> : null}
    </div>
  );
}
