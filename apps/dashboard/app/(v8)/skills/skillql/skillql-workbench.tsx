"use client";

import { AlertTriangle, ChevronDown, ChevronUp, Loader2, MessageSquareText, RotateCcw, Search, Send, Table2 } from "lucide-react";
import { useMemo, useState } from "react";

import { cn } from "@skillayer/ui";
import type { SkillQLResult, SkillQLSuggestions } from "../../../../lib/data";

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

function formatColumn(column: string): string {
  return column.replaceAll("_", " ");
}

function dateValue(row: Record<string, unknown>): number {
  const raw = row.created_at ?? row.session_start ?? row.opened_at ?? row.merged_at ?? row.last_loaded_at ?? row.updated_at;
  const value = typeof raw === "string" ? new Date(raw).getTime() : 0;
  return Number.isFinite(value) ? value : 0;
}

async function askSkillQL(accessToken: string, orgId: string, query: string): Promise<SkillQLResult> {
  const response = await fetch(`${API_URL}/v8/orgs/${orgId}/skills/skillql`, {
    body: JSON.stringify({ query }),
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
    method: "POST",
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

function Metric({ label, value, detail }: { label: string; value: string | number; detail: string }) {
  return (
    <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-3 text-[30px] font-semibold text-[color:var(--text-primary)]">{value}</div>
      <p className="mt-2 text-xs leading-5 text-[color:var(--text-secondary)]">{detail}</p>
    </article>
  );
}

function ErrorPanel({ error }: { error: SkillQLError }) {
  const llm = error.type === "llm_not_configured";
  return (
    <section className={cn("rounded-[8px] border px-5 py-4", llm ? "border-amber-400/35 bg-amber-400/10" : "border-red-500/30 bg-red-500/10")}>
      <div className="flex items-start gap-3">
        <AlertTriangle className={cn("mt-0.5 h-5 w-5 shrink-0", llm ? "text-amber-200" : "text-red-200")} />
        <div>
          <div className="font-semibold text-[color:var(--text-primary)]">{llm ? "LLM not configured" : error.type === "query_parse_failed" ? "Could not parse that question" : "SkillQL request failed"}</div>
          <p className={cn("mt-1 text-sm", llm ? "text-amber-100/80" : "text-red-100/80")}>{error.message}</p>
        </div>
      </div>
    </section>
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
    <>
      <div className="space-y-3 md:hidden">
        {rows.map((row, index) => (
          <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-black/10 p-4" key={index}>
            <div className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Row {index + 1}</div>
            <dl className="mt-3 space-y-3">
              {result.columns.map((column) => (
                <div className="grid gap-1" key={column}>
                  <dt className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{formatColumn(column)}</dt>
                  <dd className="break-words text-sm text-[color:var(--text-primary)]">{stringify(row[column]) || <span className="text-[color:var(--text-tertiary)]">-</span>}</dd>
                </div>
              ))}
            </dl>
          </article>
        ))}
      </div>
      <div className="hidden max-h-96 overflow-auto rounded-[8px] border border-[color:var(--bg-border)] bg-black/10 md:block">
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead className="sticky top-0 z-10 bg-[color:var(--bg-surface)]">
            <tr>
              {result.columns.map((column) => (
                <th className="border-b border-[color:var(--bg-border)] px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]" key={column}>
                  <button className="inline-flex items-center gap-1 text-left transition-colors hover:text-[color:var(--text-primary)]" onClick={() => toggle(column)} type="button">
                    {formatColumn(column)}
                    {sort?.column === column ? <span className="text-[color:var(--accent-primary)]">{sort.direction === "asc" ? "up" : "down"}</span> : null}
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
    </>
  );
}

function NumberResult({ result }: { result: SkillQLResult }) {
  const first = result.rows[0] ?? {};
  const value = stringify(Object.values(first)[0] ?? result.row_count);
  return <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-black/10 px-6 py-8 text-center text-5xl font-semibold text-[color:var(--text-primary)]">{value}</div>;
}

function ListResult({ result }: { result: SkillQLResult }) {
  const [showAll, setShowAll] = useState(false);
  const rows = showAll ? result.rows : result.rows.slice(0, 50);
  return (
    <div className="space-y-3">
      <ol className="space-y-2 rounded-[8px] border border-[color:var(--bg-border)] bg-black/10 p-4">
        {rows.map((row, index) => (
          <li className="rounded-md bg-white/5 px-3 py-2 text-sm text-[color:var(--text-secondary)]" key={index}>{stringify(row)}</li>
        ))}
      </ol>
      {result.rows.length > 50 && !showAll ? (
        <button className="rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm font-semibold text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" onClick={() => setShowAll(true)} type="button">
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
          <div className="grid gap-3 rounded-[8px] border border-[color:var(--bg-border)] bg-black/10 p-4 sm:grid-cols-[160px_1fr]" key={index}>
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
    <section className="space-y-4 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="italic text-[color:var(--text-secondary)]">{result.intent}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {result.data_sources.map((source) => (
              <span className="rounded-md border border-[color:var(--bg-border)] bg-white/5 px-2.5 py-1 text-xs font-semibold text-[color:var(--text-secondary)]" key={source}>
                {source.replaceAll("_", " ")}
              </span>
            ))}
          </div>
        </div>
        <span className="rounded-md bg-white/5 px-3 py-1 text-xs font-semibold text-[color:var(--text-tertiary)]">{result.row_count} rows</span>
      </div>

      {result.answer ? <div className="rounded-[8px] border border-[color:var(--accent-primary)]/25 bg-[color:var(--accent-primary)]/10 p-4 text-sm leading-6 text-[color:var(--text-primary)]">{result.answer}</div> : null}

      {result.rows.length ? (
        result.result_format === "number" ? <NumberResult result={result} /> : result.result_format === "list" ? <ListResult result={result} /> : result.result_format === "timeline" ? <TimelineResult result={result} /> : <TableResult result={result} />
      ) : (
        <div className="rounded-[8px] border border-dashed border-[color:var(--bg-border)] bg-black/10 px-5 py-10 text-center text-sm text-[color:var(--text-secondary)]">No rows matched this question.</div>
      )}

      {result.suggested_followups.length ? (
        <div className="flex flex-wrap gap-2 border-t border-[color:var(--bg-border)] pt-4">
          {result.suggested_followups.map((followup) => (
            <button className="rounded-md border border-[color:var(--bg-border)] bg-white/5 px-3 py-1.5 text-xs font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" key={followup} onClick={() => onAsk(followup)} type="button">
              {followup}
            </button>
          ))}
        </div>
      ) : null}
    </section>
  );
}

export function SkillQLWorkbench({ accessToken, orgId, suggestions }: Props) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<SkillQLResult | null>(null);
  const [error, setError] = useState<SkillQLError | null>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [historyOpen, setHistoryOpen] = useState(false);

  const categories = Object.entries(suggestions);
  const suggestedQueryCount = categories.reduce((total, [, items]) => total + items.length, 0);
  const showSuggestions = !query.trim();

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

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">SkillQL</h1>
          <p className="mt-2 max-w-3xl text-[15px] leading-6 text-[color:var(--text-secondary)]">Ask governed, natural-language questions across generated skills, agent sessions, developer activity, audit events, and policy risk.</p>
        </div>
        <div className="inline-flex w-fit items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs font-semibold text-[color:var(--text-secondary)]">
          <MessageSquareText className="h-4 w-4 text-[color:var(--accent-primary)]" />
          v8 Skills API
        </div>
      </div>

      <section className="grid gap-4 md:grid-cols-3">
        <Metric detail="Question groups returned by the v8 SkillQL suggestions endpoint." label="Prompt groups" value={categories.length} />
        <Metric detail="Starter prompts grounded in the governance data model." label="Suggested asks" value={suggestedQueryCount} />
        <Metric detail="Maximum query size enforced by the SkillQL contract." label="Query limit" value={`${MAX_QUERY_LENGTH} chars`} />
      </section>

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <label className="mb-3 flex items-center gap-2 text-sm font-semibold text-[color:var(--text-primary)]" htmlFor="skillql-query">
          <Search className="h-4 w-4 text-[color:var(--accent-primary)]" />
          Ask SkillQL
        </label>
        <textarea
          className="min-h-[104px] w-full resize-none rounded-[8px] border border-[color:var(--bg-border)] bg-black/15 p-4 text-sm text-[color:var(--text-primary)] outline-none placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]"
          id="skillql-query"
          maxLength={MAX_QUERY_LENGTH}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
              event.preventDefault();
              void submit();
            }
          }}
          placeholder="Show stale skills in restricted repos, agent sessions with policy violations, or developer activity with high risk."
          rows={3}
          value={query}
        />
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <span className={cn("text-xs", query.length >= MAX_QUERY_LENGTH ? "text-red-200" : "text-[color:var(--text-tertiary)]")}>{query.length}/{MAX_QUERY_LENGTH}</span>
          <div className="flex flex-wrap gap-2">
            {result || error ? (
              <button className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-4 py-2 text-sm font-semibold text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" onClick={reset} type="button">
                <RotateCcw className="h-4 w-4" /> Ask another
              </button>
            ) : null}
            <button className="inline-flex items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-60" disabled={!query.trim() || query.length > MAX_QUERY_LENGTH || loading} onClick={() => void submit()} type="button">
              <Send className="h-4 w-4" /> Run query
            </button>
          </div>
        </div>
      </section>

      {history.length ? (
        <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
          <button className="flex w-full items-center justify-between text-sm font-semibold text-[color:var(--text-secondary)]" onClick={() => setHistoryOpen((value) => !value)} type="button">
            Query history
            {historyOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
          {historyOpen ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {history.map((item) => (
                <button className="rounded-md border border-[color:var(--bg-border)] px-3 py-1.5 text-xs text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" key={item} onClick={() => { setQuery(item); void submit(item); }} type="button">
                  {item}
                </button>
              ))}
            </div>
          ) : null}
        </section>
      ) : null}

      {showSuggestions ? (
        <section className="grid gap-3 md:grid-cols-2">
          {categories.map(([category, items]) => (
            <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={category}>
              <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">{category}</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {items.map((item) => (
                  <button className="rounded-md border border-[color:var(--bg-border)] bg-black/15 px-3 py-1.5 text-left text-xs text-[color:var(--text-secondary)] transition-colors hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]" key={item} onClick={() => { setQuery(item); void submit(item); }} type="button">
                    {item}
                  </button>
                ))}
              </div>
            </article>
          ))}
          {!categories.length ? (
            <article className="rounded-[8px] border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-sm text-[color:var(--text-secondary)]">
              SkillQL suggestions will appear here when the v8 Skills API is reachable.
            </article>
          ) : null}
        </section>
      ) : null}

      {loading ? (
        <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 text-center">
          <div className="inline-flex items-center gap-3 text-sm font-semibold text-[color:var(--text-secondary)]">
            <Loader2 className="h-4 w-4 animate-spin text-[color:var(--accent-primary)]" />
            SkillQL is querying governed evidence
          </div>
        </section>
      ) : null}
      {error ? <ErrorPanel error={error} /> : null}
      {result && !loading ? <ResultPanel result={result} onAsk={(next) => { setQuery(next); void submit(next); }} /> : null}

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex items-start gap-3">
          <Table2 className="mt-0.5 h-4 w-4 shrink-0 text-[color:var(--accent-primary)]" />
          <p className="text-sm leading-6 text-[color:var(--text-secondary)]">Results preserve the SkillQL contract: intent, answer, result format, columns, rows, row count, data sources, and suggested follow-ups are rendered without leaving the migrated Skillayer Skills surface.</p>
        </div>
      </section>
    </div>
  );
}
