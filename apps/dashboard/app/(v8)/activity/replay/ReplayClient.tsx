"use client";

import { Download } from "lucide-react";
import { useMemo, useState } from "react";

import type { ActivityComplianceEvent, ActivitySession, ReplayStep } from "../activity-data";

function riskClass(band: ReplayStep["risk_band"]): string {
  if (band === "high") return "text-red-200";
  if (band === "medium") return "text-amber-200";
  return "text-[color:var(--accent-green)]";
}

function compactNumber(value: number | null | undefined): string {
  const safe = Number(value ?? 0);
  if (safe >= 1_000_000) return `${(safe / 1_000_000).toFixed(safe >= 10_000_000 ? 0 : 1)}M`;
  if (safe >= 1_000) return `${(safe / 1_000).toFixed(safe >= 10_000 ? 0 : 1)}K`;
  return String(safe);
}

function formatMoney(value: number | null | undefined): string {
  const safe = Number(value ?? 0);
  return safe > 0 ? `$${safe.toFixed(safe >= 1 ? 2 : 4)}` : "$0.00";
}

export function ReplayClient({ complianceEvents = [], exportHtml, session, timeline }: { complianceEvents?: ActivityComplianceEvent[]; exportHtml: string | null | undefined; session: ActivitySession; timeline?: ReplayStep[] | null }) {
  const steps = timeline ?? [];
  const [index, setIndex] = useState(0);
  const active = steps[Math.min(index, Math.max(0, steps.length - 1))];
  const exportHref = useMemo(() => `data:text/html;charset=utf-8,${encodeURIComponent(exportHtml ?? "")}`, [exportHtml]);
  const metrics = session.activity_metrics ?? {};
  const details = session.activity_details ?? {};
  const editedFiles = details.edited_files?.length ? details.edited_files : session.files_touched;
  const exploredFiles = details.explored_files ?? [];
  const searches = details.searches ?? [];
  const commands = details.commands ?? [];
  const tools = details.tools?.length ? details.tools : session.mcp_tools ?? [];

  if (!active) {
    return <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-sm text-[color:var(--text-secondary)]">No replay timeline is available for this session.</div>;
  }

  return (
    <section className="space-y-4">
      <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">{session.agent} - {session.repo_name}</h2>
            <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{session.session_id} - {session.user}</p>
            <p className="mt-1 text-xs text-[color:var(--text-tertiary)]">{session.model ?? "model unknown"}{session.intelligence_tier ? ` · ${session.intelligence_tier}` : ""} · {compactNumber(session.tokens_total)} tokens · {formatMoney(session.cost_usd)} · {session.outcome.replaceAll("_", " ")}</p>
          </div>
          <a className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)]" download={`skillayer-replay-${session.session_id}.html`} href={exportHref}>
            <Download className="h-4 w-4" />
            Export HTML
          </a>
        </div>
        <input
          aria-label="Replay step"
          className="mt-5 w-full accent-[color:var(--accent-primary)]"
          max={Math.max(0, steps.length - 1)}
          min={0}
          onChange={(event) => setIndex(Number(event.target.value))}
          type="range"
          value={index}
        />
        <div className="mt-2 flex justify-between text-xs text-[color:var(--text-tertiary)]">
          <span>Step {active.index + 1}</span>
          <span>{steps.length} steps</span>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-4 xl:grid-cols-6">
        <Metric href="#activity-edited" label="Edited" value={metrics.edited_files ?? session.files_touched.length} />
        <Metric href="#activity-explored" label="Explored" value={metrics.explored_files ?? 0} />
        <Metric href="#activity-searches" label="Searches" value={metrics.searches ?? 0} />
        <Metric href="#activity-commands" label="Commands" value={metrics.commands ?? 0} />
        <Metric href="#activity-tools" label="Tools" value={metrics.tool_calls ?? session.mcp_tools?.length ?? 0} />
        <Metric label="Risk" value={`${session.risk_band} ${session.risk_score}`} />
      </div>
      {session.risk_reasons?.length ? (
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 text-sm text-[color:var(--text-secondary)]">
          <span className="font-semibold text-[color:var(--text-primary)]">Why this risk score:</span> {session.risk_reasons.join(" · ")}
        </div>
      ) : null}

      <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div>
          <h3 className="font-semibold text-[color:var(--text-primary)]">Run Activity Details</h3>
          <p className="mt-1 text-xs text-[color:var(--text-secondary)]">Click any metric above to jump to its evidence for this run.</p>
        </div>
        <div className="mt-4 grid gap-4 xl:grid-cols-2">
          <DetailPanel id="activity-edited" title="Edited files" items={editedFiles} empty="No edited files captured for this run." />
          <DetailPanel expectedCount={metrics.explored_files ?? 0} id="activity-explored" title="Explored files" items={exploredFiles} empty="No explored file paths captured for this run." />
          <DetailPanel expectedCount={metrics.searches ?? 0} id="activity-searches" title="Searches" items={searches} empty="No search commands captured for this run." />
          <DetailPanel expectedCount={metrics.commands ?? 0} id="activity-commands" title="Commands" items={commands} empty="No shell commands captured for this run." />
          <DetailPanel expectedCount={metrics.tool_calls ?? 0} id="activity-tools" title="Tools" items={tools} empty="No tool calls captured for this run." />
        </div>
      </article>

      <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="font-semibold text-[color:var(--text-primary)]">Compliance Events For This Run</h3>
            <p className="mt-1 text-xs text-[color:var(--text-secondary)]">Metadata-only evidence linked to the selected live-feed run.</p>
          </div>
          <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs font-semibold text-[color:var(--text-secondary)]">{complianceEvents.length} events</span>
        </div>
        {complianceEvents.length ? (
          <div className="mt-4 divide-y divide-[color:var(--bg-border)]">
            {complianceEvents.map((event) => (
              <div className="grid gap-3 py-3 text-sm md:grid-cols-[1.2fr_1fr_1fr_120px]" key={event.id}>
                <div>
                  <div className="font-semibold text-[color:var(--text-primary)]">{event.summary}</div>
                  <div className="mt-1 text-xs text-[color:var(--text-tertiary)]">{event.timestamp ? new Date(event.timestamp).toLocaleString() : "time unknown"} · {event.actor_login ?? "unknown actor"}</div>
                </div>
                <div className="text-[color:var(--text-secondary)]">{event.model ?? "model unknown"}{event.intelligence_tier ? ` · ${event.intelligence_tier}` : ""}</div>
                <div className="text-[color:var(--text-secondary)]">{event.access_scope ?? "scope unknown"} · {event.policy_decision ?? "no policy decision"}</div>
                <div className={`font-semibold capitalize ${riskClass(event.risk_band)}`}>{event.risk_band} {event.risk_score}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-[color:var(--text-secondary)]">No compliance metadata has been attached to this run yet.</p>
        )}
      </article>

      <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-xs text-[color:var(--text-tertiary)]">{active.timestamp}</div>
            <h3 className="mt-1 text-xl font-semibold capitalize text-[color:var(--text-primary)]">{active.action}</h3>
          </div>
          <span className={`text-sm font-semibold capitalize ${riskClass(active.risk_band)}`}>{active.risk_band} risk - {active.risk_score}</span>
        </div>
        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <div className="rounded-md border border-[color:var(--bg-border)] p-3">
            <div className="text-xs font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Policy</div>
            <div className="mt-2 text-sm capitalize text-[color:var(--text-primary)]">{active.policy_decision}</div>
          </div>
          <div className="rounded-md border border-[color:var(--bg-border)] p-3">
            <div className="text-xs font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Action</div>
            <div className="mt-2 text-sm capitalize text-[color:var(--text-primary)]">{active.action_class}</div>
          </div>
          <div className="rounded-md border border-[color:var(--bg-border)] p-3">
            <div className="text-xs font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Result</div>
            <div className="mt-2 truncate text-sm text-[color:var(--text-primary)]">{JSON.stringify(active.result)}</div>
          </div>
        </div>
        {active.reasoning ? <p className="mt-4 text-sm text-[color:var(--text-secondary)]">{active.reasoning}</p> : null}
        <pre className="mt-4 max-h-[420px] overflow-auto rounded-md bg-black/30 p-4 text-xs leading-5 text-[color:var(--text-secondary)]">{active.file_diff || JSON.stringify(active.tool_call, null, 2)}</pre>
      </article>
    </section>
  );
}

function Metric({ href, label, value }: { href?: string; label: string; value: number | string }) {
  const content = (
    <>
      <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-1 text-lg font-semibold text-[color:var(--text-primary)]">{value}</div>
      {href ? <div className="mt-2 text-xs font-semibold text-[color:var(--accent-primary)]">View details</div> : null}
    </>
  );
  const className = "rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3";
  return href ? (
    <a className={`${className} block hover:border-[color:var(--accent-primary)]/70`} href={href}>
      {content}
    </a>
  ) : (
    <div className={className}>{content}</div>
  );
}

function DetailPanel({ empty, expectedCount, id, items, title }: { empty: string; expectedCount?: number; id: string; items: string[]; title: string }) {
  const count = Math.max(items.length, Number(expectedCount ?? 0));
  return (
    <section className="scroll-mt-24 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4" id={id}>
      <div className="flex items-center justify-between gap-3">
        <h4 className="font-semibold text-[color:var(--text-primary)]">{title}</h4>
        <span className="rounded-md border border-[color:var(--bg-border)] px-2 py-1 text-xs font-semibold text-[color:var(--text-secondary)]">{count}</span>
      </div>
      {items.length ? (
        <div className="mt-3 max-h-64 space-y-2 overflow-auto pr-1">
          {items.map((item, index) => (
            <div className="break-all rounded border border-[color:var(--bg-border)] bg-black/20 px-3 py-2 font-mono text-xs leading-5 text-[color:var(--text-secondary)]" key={`${id}-${index}-${item}`}>
              {item}
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-3 text-sm text-[color:var(--text-secondary)]">{count > 0 ? `${count} event${count === 1 ? "" : "s"} counted, but this provider record did not include item-level details.` : empty}</p>
      )}
    </section>
  );
}
