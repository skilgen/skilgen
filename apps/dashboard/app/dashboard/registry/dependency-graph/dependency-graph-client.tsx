"use client";

import * as d3 from "d3";
import { useCallback, useEffect, useRef, useState } from "react";
import { Loader2, Play, Sparkles } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type Repo = { id: string; name: string };
type GraphNode = {
  id: string;
  label?: string;
  repo_name?: string;
  score?: number;
  load_count?: number;
  status?: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
};
type GraphEdge = { source: string; target: string; weight?: number; relationship?: string; shared_files?: string[] };
type Graph = { nodes: GraphNode[]; edges: GraphEdge[]; opportunities: Record<string, unknown>[]; computed_at: string | null };

function headers(accessToken: string): HeadersInit {
  return { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) };
}

function color(node: GraphNode): string {
  if (node.status === "healthy" || (node.score ?? 0) > 70) return "var(--accent-green)";
  if (node.status === "stale") return "#f59e0b";
  if (node.status === "low_score" || (node.score ?? 0) < 50) return "#ef4444";
  return "var(--bg-border)";
}

function ForceGraph({ graph, crossRepo }: { graph: Graph; crossRepo?: boolean }) {
  const ref = useRef<SVGSVGElement | null>(null);
  const wrap = useRef<HTMLDivElement | null>(null);
  const [selected, setSelected] = useState<GraphNode | null>(null);

  useEffect(() => {
    const svgEl = ref.current;
    if (!svgEl) return;
    const svg = d3.select<SVGSVGElement, unknown>(svgEl);
    svg.selectAll("*").remove();
    const width = wrap.current?.clientWidth ?? 900;
    const height = 560;
    const nodes: GraphNode[] = graph.nodes.map((node) => ({ ...node }));
    const links: GraphEdge[] = graph.edges.map((edge) => ({ ...edge }));
    const g = svg.attr("viewBox", `0 0 ${width} ${height}`).append("g");
    svg.call(d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.3, 5]).on("zoom", (event) => g.attr("transform", event.transform.toString())));
    const simulation = d3.forceSimulation(nodes as d3.SimulationNodeDatum[])
      .force("link", d3.forceLink(links).id((d) => (d as GraphNode).id).distance((d) => 140 / Math.max(0.5, Number((d as GraphEdge).weight ?? 1))).strength(0.35))
      .force("charge", d3.forceManyBody().strength(-220))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide(34));
    const link = g.selectAll<SVGLineElement, GraphEdge>("line").data(links).join("line").attr("stroke", (d) => crossRepo && d.relationship === "same_domain" ? "var(--accent-primary)" : "#f59e0b").attr("stroke-dasharray", crossRepo ? "6,3" : null).attr("stroke-opacity", 0.55).attr("stroke-width", (d) => 1 + Number(d.weight ?? 1) * 1.5);
    const dragBehavior = d3.drag<SVGGElement, GraphNode>().on("start", (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }).on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; }).on("end", (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; });
    const node = g.selectAll<SVGGElement, GraphNode>("g.node").data(nodes).join("g").attr("class", "node").call(dragBehavior);
    node.append("circle").attr("r", (d) => 16 + Math.min(14, Number(d.load_count ?? 0) / 3)).attr("fill", color).attr("fill-opacity", 0.78).attr("stroke", "rgba(255,255,255,0.35)").on("click", (_event, d) => setSelected(d));
    node.append("text").attr("text-anchor", "middle").attr("dy", 38).attr("fill", "var(--text-secondary)").attr("font-size", 11).text((d) => String(d.label ?? "").slice(0, 12));
    simulation.on("tick", () => {
      link.attr("x1", (d) => (d.source as d3.SimulationNodeDatum).x ?? 0).attr("y1", (d) => (d.source as d3.SimulationNodeDatum).y ?? 0).attr("x2", (d) => (d.target as d3.SimulationNodeDatum).x ?? 0).attr("y2", (d) => (d.target as d3.SimulationNodeDatum).y ?? 0);
      node.attr("transform", (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });
    return () => {
      simulation.stop();
      svg.selectAll("*").remove();
    };
  }, [crossRepo, graph]);

  return <div className="relative" ref={wrap}><svg className="h-[560px] w-full rounded-xl bg-[color:var(--bg-base)]" ref={ref} />{selected ? <aside className="absolute right-4 top-4 w-[280px] rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 shadow-xl"><div className="font-semibold text-[color:var(--text-primary)]">{selected.label}</div><div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">{selected.repo_name}</div><div className="mt-3 text-[13px] text-[color:var(--text-secondary)]">Score {selected.score ?? 0}/100 · {selected.load_count ?? 0} loads</div><button className="mt-3 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-[12px] text-[color:var(--accent-primary)]" onClick={() => setSelected(null)} type="button">Close</button></aside> : null}</div>;
}

export function DependencyGraphClient({ accessToken, orgId, repos }: { accessToken: string; orgId: string; repos: Repo[] }) {
  const [tab, setTab] = useState<"repo" | "cross">("repo");
  const [repoId, setRepoId] = useState(repos[0]?.id ?? "");
  const [graph, setGraph] = useState<Graph | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async (nextTab = tab, nextRepo = repoId) => {
    const path = nextTab === "repo" ? `/orgs/${orgId}/dependency-graph/repo/${nextRepo}` : `/orgs/${orgId}/dependency-graph/cross-repo`;
    const response = await fetch(`${API_URL}${path}`, { headers: headers(accessToken) });
    if (response.ok) setGraph((await response.json()) as Graph);
  }, [accessToken, orgId, repoId, tab]);

  useEffect(() => {
    if (orgId && (tab === "cross" || repoId)) void load(tab, repoId);
  }, [load, orgId, repoId, tab]);

  async function compute() {
    setBusy(true);
    try {
      await fetch(`${API_URL}/orgs/${orgId}/dependency-graph/compute`, { method: "POST", headers: headers(accessToken) });
      await load(tab, repoId);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4 md:flex-row md:items-center md:justify-between">
        <div><div className="font-semibold text-[color:var(--text-primary)]">{graph?.computed_at ? `Computed ${new Date(graph.computed_at).toLocaleString()}` : "Skillayer has not mapped dependencies yet."}</div><p className="text-sm text-[color:var(--text-secondary)]">Compute shared file references and cross-repo skill opportunities without leaving the browser.</p></div>
        <button className="inline-flex items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)] disabled:opacity-60" disabled={busy} onClick={compute} type="button">{busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}Compute dependency graph</button>
      </div>
      <div className="flex flex-wrap gap-2"><button className={`rounded-full px-4 py-2 text-sm font-semibold ${tab === "repo" ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "border border-[color:var(--bg-border)] text-[color:var(--text-secondary)]"}`} onClick={() => setTab("repo")} type="button">Repo-level</button><button className={`rounded-full px-4 py-2 text-sm font-semibold ${tab === "cross" ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]" : "border border-[color:var(--bg-border)] text-[color:var(--text-secondary)]"}`} onClick={() => setTab("cross")} type="button">Cross-repo</button></div>
      {tab === "repo" ? <select className="h-10 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 text-sm" onChange={(event) => setRepoId(event.target.value)} value={repoId}>{repos.map((repo) => <option key={repo.id} value={repo.id}>{repo.name}</option>)}</select> : null}
      {graph && graph.nodes.length ? <ForceGraph crossRepo={tab === "cross"} graph={graph} /> : <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center"><div className="text-lg font-semibold text-[color:var(--text-primary)]">No skill dependencies found yet.</div><p className="mt-2 text-sm text-[color:var(--text-secondary)]">Run a dependency analysis to see shared file references and cross-repo opportunities.</p><button className="mt-5 inline-flex items-center rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-[color:var(--bg-base)]" onClick={compute} type="button"><Sparkles className="mr-2 h-4 w-4" />Compute graph</button></section>}
      {tab === "cross" && graph?.opportunities?.length ? <aside className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><h2 className="font-semibold text-[color:var(--text-primary)]">Cross-repo opportunities</h2><div className="mt-3 grid gap-3 md:grid-cols-2">{graph.opportunities.slice(0, 8).map((opp, index) => <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-sm text-[color:var(--text-secondary)]" key={index}>💡 {String(opp.recommendation ?? "Generate an adapted skill for this repo.")}</div>)}</div></aside> : null}
    </div>
  );
}
