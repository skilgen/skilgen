"use client";

import * as d3 from "d3";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { Lightbulb, Loader2, Network, Sparkles, X } from "lucide-react";

import type { CriticalityItem } from "../../../lib/data";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

export type ColoadNode = {
  name: string;
  value: number;
  score?: number;
  status?: "healthy" | "low_score" | "stale" | "never_loaded" | string;
  skill_id?: string;
  display?: string;
  always_together?: boolean;
  children?: ColoadNode[];
};

export type ColoadTree = ColoadNode & {
  uniform_loads: boolean;
  generated_at: string;
};

const riskClass = {
  critical: "bg-red-900/30 text-red-300",
  high: "bg-amber-900/30 text-amber-300",
  medium: "bg-blue-900/30 text-blue-300",
  low: "bg-green-900/30 text-green-300",
};

const runtimeFill = {
  "Codex CLI": "#3b82f6",
  Codex: "#3b82f6",
  "Claude Code": "#8b5cf6",
  Cursor: "#10b981",
  Copilot: "#f59e0b",
  "Gemini CLI": "#06b6d4",
};

const statusFill = {
  healthy: "rgba(16,185,129,0.85)",
  low_score: "rgba(239,68,68,0.75)",
  stale: "rgba(245,158,11,0.75)",
  never_loaded: "rgba(100,116,139,0.5)",
};

function headers(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

function RiskBadge({ risk }: { risk: CriticalityItem["risk_level"] }) {
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${riskClass[risk]}`}>{risk}</span>;
}

function SkillDrawer({
  accessToken,
  item,
  onClose,
  orgId,
}: {
  accessToken: string;
  item: CriticalityItem;
  onClose: () => void;
  orgId: string;
}) {
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  async function loadSuggestions() {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/analytics/improvement-suggestions`, {
        method: "POST",
        headers: headers(accessToken),
        body: JSON.stringify({ skill_id: item.skill_id, risk_reason: item.risk_reason }),
      });
      const body = await response.json().catch(() => ({}));
      if (response.status === 402 || body.code === "llm_not_configured") {
        setMessage("Configure an AI model to generate tailored suggestions.");
        return;
      }
      if (!response.ok) throw new Error(body.detail || "Could not load suggestions.");
      setSuggestions(Array.isArray(body.suggestions) ? body.suggestions : []);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not load suggestions.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/50" onClick={onClose}>
      <aside className="h-full w-full max-w-xl overflow-y-auto border-l border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 shadow-2xl" onClick={(event) => event.stopPropagation()}>
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <div className="mb-2 inline-flex"><RiskBadge risk={item.risk_level} /></div>
            <h2 className="text-xl font-semibold text-[color:var(--text-primary)]">{item.domain}</h2>
            <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{item.repo_name}</p>
          </div>
          <button className="inline-flex h-9 w-9 items-center justify-center rounded-full text-[color:var(--text-tertiary)] hover:bg-white/10 hover:text-[color:var(--text-primary)]" onClick={onClose} type="button">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-lg border border-[color:var(--bg-border)] bg-black/15 p-4">
            <div className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">Loads</div>
            <div className="mt-2 text-2xl font-semibold">{item.load_count_30d}</div>
          </div>
          <div className="rounded-lg border border-[color:var(--bg-border)] bg-black/15 p-4">
            <div className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">Score</div>
            <div className="mt-2 text-2xl font-semibold">{item.score_total}</div>
          </div>
          <div className="rounded-lg border border-[color:var(--bg-border)] bg-black/15 p-4">
            <div className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">Rank</div>
            <div className="mt-2 text-2xl font-semibold">#{item.dependency_rank}</div>
          </div>
        </div>

        <div className="mt-5 rounded-lg border border-[color:var(--bg-border)] bg-black/15 p-4 text-sm leading-6 text-[color:var(--text-secondary)]">
          {item.risk_reason}
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          <button className="inline-flex h-10 items-center rounded-md bg-[color:var(--accent-primary)] px-4 text-sm font-semibold text-[color:var(--bg-base)] disabled:cursor-wait disabled:opacity-60" disabled={loading} onClick={loadSuggestions} type="button">
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
            Generate suggestions
          </button>
          <Link className="inline-flex h-10 items-center rounded-md border border-[color:var(--bg-border)] px-4 text-sm font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href={`/dashboard/repos/${item.repo_id}/skills/${item.skill_id}?tab=edit`}>
            Open skill
          </Link>
        </div>

        {message ? (
          <div className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-200">
            {message} {message.includes("Configure") ? <Link className="font-semibold text-[color:var(--accent-primary)]" href="/dashboard/settings#ai-model">Settings</Link> : null}
          </div>
        ) : null}

        {suggestions.length ? (
          <div className="mt-5 rounded-lg border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[rgb(var(--accent-primary-rgb)/0.08)] p-4">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-[color:var(--accent-primary)]">
              <Lightbulb className="h-4 w-4" />
              Improvement suggestions
            </div>
            <ul className="space-y-2 text-sm leading-6 text-[color:var(--text-secondary)]">
              {suggestions.map((suggestion) => <li key={suggestion}>- {suggestion}</li>)}
            </ul>
          </div>
        ) : null}
      </aside>
    </div>
  );
}

function ColoadTreeChart({ data, onSelect }: { data: ColoadTree | null; onSelect: (id: string) => void }) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [width, setWidth] = useState(720);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; text: string } | null>(null);

  useEffect(() => {
    const node = wrapRef.current;
    if (!node) return;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(340, Math.round(entry.contentRect.width))));
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const el = svgRef.current;
    if (!el || !data) return;
    const height = width;
    d3.select(el).selectAll("*").remove();

    const color = d3.scaleOrdinal<string, string>()
      .domain(Object.keys(runtimeFill))
      .range(Object.values(runtimeFill));

    const skillColor = (status: string | undefined) => statusFill[(status ?? "never_loaded") as keyof typeof statusFill] ?? statusFill.never_loaded;

    const treeData: ColoadNode = data;
    const pack = d3.pack<ColoadNode>()
      .size([width, height])
      .padding((d) => (d.depth === 0 ? 24 : d.depth === 1 ? 12 : 4));

    const root = pack(
      d3.hierarchy<ColoadNode>(treeData)
        .sum((d) => Math.max(1, d.value ?? 1))
        .sort((a, b) => (b.value ?? 0) - (a.value ?? 0)),
    );

    const svg = d3.select<SVGSVGElement, unknown>(el)
      .attr("viewBox", `0 0 ${width} ${height}`)
      .style("cursor", "pointer");

    const g = svg.append("g");
    let currentFocus = root;

    const node = g.selectAll<SVGGElement, d3.HierarchyCircularNode<ColoadNode>>("g")
      .data(root.descendants())
      .join("g")
      .attr("transform", (d) => `translate(${d.x},${d.y})`);

    node.append("circle")
      .attr("r", (d) => Math.max(0, d.r))
      .attr("fill", (d) => {
        if (d.depth === 0) return "transparent";
        if (d.depth === 1) return `${color(d.data.name)}22`;
        if (d.depth === 2) return "rgba(255,255,255,0.045)";
        return skillColor(d.data.status);
      })
      .attr("stroke", (d) => {
        if (d.depth === 0) return "none";
        if (d.depth === 1) return color(d.data.name);
        if (d.depth === 2) return "rgba(255,255,255,0.12)";
        return "rgba(255,255,255,0.25)";
      })
      .attr("stroke-width", (d) => (d.depth === 1 ? 1.5 : 0.75));

    node.filter((d) => d.depth === 1 || d.depth === 3)
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em")
      .attr("fill", (d) => (d.depth === 1 ? color(d.data.name) : "rgba(255,255,255,0.9)"))
      .attr("font-size", (d) => {
        const r = d.r;
        if (d.depth === 1) return Math.min(14, Math.max(9, r / 3));
        return Math.min(10, Math.max(7, r * 0.7));
      })
      .attr("font-weight", (d) => (d.depth === 1 ? "700" : "500"))
      .attr("pointer-events", "none")
      .text((d) => {
        const r = d.r;
        const name = d.data.display ?? d.data.name;
        if (r < 8) return "";
        if (r < 16) return name.slice(0, 2);
        if (r < 28) return name.slice(0, 5);
        return name.length > 10 ? `${name.slice(0, 9)}…` : name;
      });

    node.filter((d) => d.depth === 3 && d.r > 18)
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "1.4em")
      .attr("fill", "rgba(255,255,255,0.62)")
      .attr("font-size", 8)
      .attr("pointer-events", "none")
      .text((d) => (d.data.score ? `${d.data.score}/100` : ""));

    function zoomTo(v: [number, number, number]) {
      const k = Math.min(width, height) / v[2];
      g.transition().duration(500).attr("transform", `translate(${width / 2},${height / 2}) scale(${k}) translate(${-v[0]},${-v[1]})`);
    }

    zoomTo([root.x ?? width / 2, root.y ?? height / 2, (root.r ?? width / 2) * 2]);

    node.on("click", (event, d) => {
      event.stopPropagation();
      if (d.depth === 3 && d.data.skill_id) {
        onSelect(d.data.skill_id);
        return;
      }
      if (d === currentFocus && d.parent) currentFocus = d.parent;
      else currentFocus = d;
      zoomTo([currentFocus.x, currentFocus.y, currentFocus.r * 2]);
    });

    node.on("mouseenter", (event, d) => {
      if (d.depth === 0) return;
      const lines = [d.data.display ?? d.data.name];
      if (d.depth === 1) lines.push(`${Math.round(d.value ?? 0)} sessions`);
      if (d.depth === 2) lines.push(d.data.always_together ? "Always loaded together" : "Loaded together often");
      if (d.depth === 3) lines.push(`${Math.round(d.data.value ?? 0)} loads · Score: ${d.data.score ?? "??"}/100`);
      const rect = (event.target as SVGElement).getBoundingClientRect();
      const containerRect = el.getBoundingClientRect();
      setTooltip({ x: rect.left - containerRect.left + rect.width / 2, y: rect.top - containerRect.top - 8, text: lines.join(" · ") });
    });
    node.on("mouseleave", () => setTooltip(null));

    svg.on("click", () => {
      currentFocus = root;
      zoomTo([root.x ?? width / 2, root.y ?? height / 2, (root.r ?? width / 2) * 2]);
    });

    return () => {
      svg.on("click", null);
      d3.select(el).selectAll("*").remove();
    };
  }, [data, onSelect, width]);

  if (!data?.children?.length) {
    return <div className="grid h-[360px] place-items-center rounded-xl border border-dashed border-[color:var(--bg-border)] text-sm text-[color:var(--text-secondary)]">No coload sessions yet.</div>;
  }

  return (
    <div className="relative w-full" ref={wrapRef}>
      <svg ref={svgRef} className="aspect-square w-full rounded-xl border border-[color:var(--bg-border)] bg-black/15" role="img" aria-label="Zoomable circle packing of skill co-loads" />
      {tooltip ? (
        <div
          className="pointer-events-none absolute z-10 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] px-3 py-1.5 text-xs text-[color:var(--text-secondary)] shadow-xl"
          style={{ left: tooltip.x, top: tooltip.y, transform: "translateX(-50%) translateY(-100%)" }}
        >
          {tooltip.text}
        </div>
      ) : null}
      <div className="mt-4 flex flex-wrap items-center gap-4 text-[12px] text-[color:var(--text-secondary)]">
        {Object.entries(runtimeFill).slice(0, 5).map(([runtime, color]) => <span className="inline-flex items-center gap-2" key={runtime}><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />{runtime}</span>)}
        {Object.entries(statusFill).map(([status, color]) => <span className="inline-flex items-center gap-2" key={status}><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />{status.replace("_", " ")}</span>)}
        <span className="text-[color:var(--text-tertiary)]">Click any circle to zoom in · Click center or background to zoom out</span>
      </div>
    </div>
  );
}

export function AnalyticsRiskWorkbench({ accessToken, criticality, orgId, tree }: { accessToken: string; criticality: CriticalityItem[]; orgId: string; tree: ColoadTree | null }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [highlight, setHighlight] = useState<{ summary: string; highlights: string[] } | null>(null);
  const [highlightLoading, setHighlightLoading] = useState(false);
  const selected = useMemo(() => criticality.find((item) => item.skill_id === selectedId) ?? null, [criticality, selectedId]);
  const allLow = criticality.length > 0 && criticality.every((item) => item.risk_level === "low");

  async function loadHighlights() {
    setHighlightLoading(true);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/analytics/highlight-risks`, { headers: headers(accessToken) });
      const body = await response.json().catch(() => ({}));
      if (response.ok) setHighlight({ summary: body.summary, highlights: body.highlights ?? [] });
      else setHighlight({ summary: body.detail || "Could not highlight risks.", highlights: body.code === "llm_not_configured" ? ["Configure an AI model in Settings to enable AI risk highlights."] : [] });
    } finally {
      setHighlightLoading(false);
    }
  }

  return (
    <section className="space-y-6">
      <article className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[rgb(var(--accent-primary-rgb)/0.08)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
              <Network className="h-4 w-4" />
              Co-load tree
            </div>
            <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Skills agents load together</h2>
            <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Click any agent to zoom in · Click a skill to see risk details and improve it.</p>
          </div>
          {tree?.uniform_loads ? <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-[12px] font-semibold text-amber-200">Uniform setup loads detected</span> : null}
        </div>
        {tree?.uniform_loads ? (
          <div className="mb-4 rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-sm leading-6 text-amber-100">
            All skills were loaded uniformly during Codex's initial setup. Circle sizes will differentiate after real coding sessions generate varied skill load patterns. The clusters you see represent how Codex grouped your skills architecturally.
          </div>
        ) : null}
        <ColoadTreeChart data={tree} onSelect={setSelectedId} />
      </article>

      <article className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Skill Risk Register</h2>
            <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Skills your agents depend on most, sorted by risk.</p>
          </div>
          <button className="inline-flex h-9 items-center rounded-md border border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-primary)] disabled:cursor-wait disabled:opacity-60" disabled={highlightLoading} onClick={loadHighlights} type="button">
            {highlightLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
            Highlight risks
          </button>
        </div>

        {allLow ? <div className="mb-4 rounded-xl border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 p-4 text-sm text-[color:var(--accent-green)]">All high-use skills are currently low risk.</div> : null}
        {highlight ? (
          <div className="mb-4 rounded-xl border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[rgb(var(--accent-primary-rgb)/0.08)] p-4 text-sm text-[color:var(--text-secondary)]">
            <div className="font-semibold text-[color:var(--text-primary)]">{highlight.summary}</div>
            {highlight.highlights.length ? <ul className="mt-2 space-y-1">{highlight.highlights.map((item) => <li key={item}>- {item}</li>)}</ul> : null}
          </div>
        ) : null}

        <div className="overflow-hidden rounded-xl border border-[color:var(--bg-border)]">
          <div className="grid grid-cols-[70px_1.1fr_1fr_110px_2fr_90px] gap-3 bg-black/20 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">
            <span>Rank</span><span>Domain</span><span>Repo</span><span>Risk</span><span>Why</span><span>Action</span>
          </div>
          {criticality.slice(0, 12).map((item) => (
            <button className="grid w-full grid-cols-[70px_1.1fr_1fr_110px_2fr_90px] gap-3 border-t border-[color:var(--bg-border)] px-4 py-3 text-left text-sm transition-colors hover:bg-white/5" key={item.skill_id} onClick={() => setSelectedId(item.skill_id)} type="button">
              <span className="font-semibold text-[color:var(--text-secondary)]">#{item.dependency_rank}</span>
              <span className="font-medium text-[color:var(--text-primary)]">{item.domain}</span>
              <span className="text-[color:var(--text-secondary)]">{item.repo_name}</span>
              <RiskBadge risk={item.risk_level} />
              <span className="text-[color:var(--text-secondary)]">{item.risk_reason}</span>
              <span className="font-semibold text-[color:var(--accent-primary)]">Inspect →</span>
            </button>
          ))}
        </div>
      </article>

      {selected ? <SkillDrawer accessToken={accessToken} item={selected} onClose={() => setSelectedId(null)} orgId={orgId} /> : null}
    </section>
  );
}
