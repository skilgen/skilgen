"use client";

import * as d3 from "d3";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
const STANDARD_DOMAINS = [
  "codebase_architecture",
  "code_style",
  "testing_conventions",
  "internal_tools",
  "security_compliance",
  "design_system",
  "data_schema",
  "operational_knowledge",
];

const SHORT: Record<string, string> = {
  codebase_architecture: "arch",
  code_style: "style",
  testing_conventions: "test",
  internal_tools: "api",
  security_compliance: "sec",
  design_system: "design",
  data_schema: "data",
  operational_knowledge: "ops",
};

type ApiSkill = {
  id: string;
  domain: string;
  score_total?: number;
  score?: { total?: number; groundedness?: number; coverage?: number; freshness?: number; structure?: number };
  load_count_30d?: number;
  last_updated_at?: string | null;
};

type NodeDatum = d3.SimulationNodeDatum & {
  id: string;
  domain: string;
  label: string;
  score: number;
  loads: number;
  lastUpdated: string | null;
  missing: boolean;
  skillId?: string;
};

type LinkDatum = d3.SimulationLinkDatum<NodeDatum> & { missing: boolean; color: string };

function colorFor(score: number, missing = false) {
  if (missing) return "#1a1a1a";
  if (score >= 80) return "#1a4a2e";
  if (score >= 60) return "#3d2e00";
  if (score >= 40) return "#3d1a00";
  return "#3d0000";
}

function daysAgo(value: string | null) {
  if (!value) return "Unknown";
  const diff = Date.now() - new Date(value).getTime();
  if (!Number.isFinite(diff)) return "Unknown";
  return `${Math.max(0, Math.round(diff / 86400000))} days ago`;
}

export function CodebaseSkillMap({ repoId, repoName }: { repoId: string; repoName: string }) {
  const router = useRouter();
  const svgRef = useRef<SVGSVGElement | null>(null);
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [skills, setSkills] = useState<ApiSkill[]>([]);
  const [width, setWidth] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedMissing, setSelectedMissing] = useState<NodeDatum | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; node: NodeDatum } | null>(null);

  useEffect(() => {
    if (!wrapRef.current) return;
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width));
    observer.observe(wrapRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(`${API_URL}/repos/${repoId}/skills`, { cache: "no-store" })
      .then((res) => res.json())
      .then((rows) => { if (!cancelled) setSkills(Array.isArray(rows) ? rows : []); })
      .catch(() => { if (!cancelled) setSkills([]); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [repoId]);

  const graph = useMemo(() => {
    const byDomain = new Map(skills.map((skill) => [skill.domain, skill]));
    const center: NodeDatum = { id: "repo", domain: repoName, label: repoName.slice(0, 12), score: 100, loads: 0, lastUpdated: null, missing: false, fx: width / 2, fy: 260 };
    const domainNodes: NodeDatum[] = STANDARD_DOMAINS.map((domain) => {
      const skill = byDomain.get(domain);
      const score = Number(skill?.score_total ?? skill?.score?.total ?? 0);
      return {
        id: domain,
        domain,
        label: SHORT[domain] ?? domain.slice(0, 5),
        score,
        loads: Number(skill?.load_count_30d ?? 0),
        lastUpdated: skill?.last_updated_at ?? null,
        missing: !skill,
        skillId: skill?.id,
      };
    });
    const nodes = [center, ...domainNodes];
    const links: LinkDatum[] = domainNodes.map((node) => ({ source: "repo", target: node.id, missing: node.missing, color: colorFor(node.score, node.missing) }));
    return { nodes, links };
  }, [repoName, skills, width]);

  useEffect(() => {
    if (!svgRef.current || width === 0 || loading) return;
    const svgElement = svgRef.current;
    const height = 520;
    const svg = d3.select(svgElement);
    svg.selectAll("*").remove();
    svg.attr("viewBox", `0 0 ${width} ${height}`);
    const zoomLayer = svg.append("g");
    svg.call(d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.7, 2.2]).on("zoom", (event) => zoomLayer.attr("transform", event.transform)));

    const nodes = graph.nodes.map((node) => ({ ...node }));
    const links = graph.links.map((link) => ({ ...link }));
    const simulation = d3.forceSimulation<NodeDatum>(nodes)
      .force("link", d3.forceLink<NodeDatum, LinkDatum>(links).id((node) => node.id).distance(90))
      .force("charge", d3.forceManyBody().strength(-250))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide<NodeDatum>().radius((node) => node.id === "repo" ? 42 : 28));

    const link = zoomLayer.selectAll("line").data(links).join("line")
      .attr("stroke", (d) => d.missing ? "#333" : d.color)
      .attr("stroke-width", 1.7)
      .attr("stroke-dasharray", (d) => d.missing ? "5 5" : "0");
    const node = zoomLayer.selectAll("g.node").data(nodes).join("g").attr("class", "node").style("cursor", "pointer")
      .on("mouseenter", (event, d) => setTooltip({ x: event.clientX, y: event.clientY, node: d }))
      .on("mouseleave", () => setTooltip(null))
      .on("click", (_event, d) => {
        if (d.id === "repo") return;
        if (d.missing) setSelectedMissing(d);
        else if (d.skillId) router.push(`/dashboard/repos/${repoId}/skills/${d.skillId}`);
      });
    node.append("circle")
      .attr("r", (d) => d.id === "repo" ? 34 : 14 + (d.score / 100) * 14)
      .attr("fill", (d) => d.id === "repo" ? "var(--accent-primary)" : colorFor(d.score, d.missing))
      .attr("stroke", (d) => d.missing ? "#555" : "rgba(255,255,255,0.25)")
      .attr("stroke-dasharray", (d) => d.missing ? "4 4" : "0")
      .attr("stroke-width", 2);
    node.append("text").attr("text-anchor", "middle").attr("dy", "0.35em").attr("font-size", "11px").attr("font-weight", 700).attr("fill", "#f5f5f5").text((d) => d.id === "repo" ? d.label : d.missing ? "Missing" : d.label);
    simulation.on("tick", () => {
      link.attr("x1", (d) => (d.source as NodeDatum).x ?? 0).attr("y1", (d) => (d.source as NodeDatum).y ?? 0).attr("x2", (d) => (d.target as NodeDatum).x ?? 0).attr("y2", (d) => (d.target as NodeDatum).y ?? 0);
      node.attr("transform", (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });
    return () => { simulation.stop(); d3.select(svgElement).selectAll("*").remove(); };
  }, [graph, loading, repoId, router, width]);

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]" ref={wrapRef}>
      <div className="relative rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        {loading ? <div className="h-[520px] animate-pulse rounded-xl bg-white/5" /> : <svg className="h-[520px] w-full" ref={svgRef} />}
        {tooltip ? <div className="fixed z-50 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] p-3 text-xs shadow-xl" style={{ left: tooltip.x + 12, top: tooltip.y + 12 }}>
          <div className="font-semibold">{tooltip.node.domain}</div>
          {tooltip.node.missing ? <div className="mt-1 text-[color:var(--text-secondary)]">Not created yet - click to generate</div> : <><div className="mt-1">Score: {tooltip.node.score}/100</div><div>Loads last 30d: {tooltip.node.loads}</div><div>Last updated: {daysAgo(tooltip.node.lastUpdated)}</div></>}
        </div> : null}
      </div>
      <aside className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        {selectedMissing ? <>
          <h3 className="text-lg font-semibold">Generate {selectedMissing.domain}</h3>
          <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">This domain is missing, so agents have no reliable guidance here. Generate it and the ghost node becomes a scored skill.</p>
          <code className="mt-4 block rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-xs text-[color:var(--accent-primary)]">skilgen analyse --domain {selectedMissing.domain} --project-root .</code>
          <button className="mt-3 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs font-semibold" onClick={() => void navigator.clipboard.writeText(`skilgen analyse --domain ${selectedMissing.domain} --project-root .`)} type="button">Copy command</button>
        </> : <>
          <h3 className="text-lg font-semibold">How to read this map</h3>
          <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">Bigger nodes have higher-quality skills. Ghost nodes are missing domains. Click an existing node to open the skill, or a ghost node to generate the right command.</p>
        </>}
      </aside>
    </div>
  );
}
