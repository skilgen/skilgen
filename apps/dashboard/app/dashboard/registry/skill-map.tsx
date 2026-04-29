"use client";

import * as d3 from "d3";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronRight, Maximize2, Minimize2, Sparkles, X } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type RepoRow = { id: string; name: string; score?: { total?: number } | null };
type SkillNode = {
  name: string;
  type: "repo" | "domain" | "skill";
  children?: SkillNode[];
  _children?: SkillNode[];
  skill_id?: string;
  score?: number;
  path?: string;
  load_count?: number;
  last_updated?: string | null;
  status?: "healthy" | "low_score" | "stale" | "never_loaded";
  content_preview?: string;
  skill_count?: number;
  avg_score?: number;
};

function headers(accessToken: string): HeadersInit {
  return { "Content-Type": "application/json", ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) };
}

function statusClass(status?: string): string {
  if (status === "healthy") return "border-[color:var(--accent-green)] bg-green-500/10 text-green-200";
  if (status === "stale") return "border-amber-500/50 bg-amber-500/10 text-amber-200";
  if (status === "low_score") return "border-red-500/50 bg-red-500/10 text-red-200";
  return "border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] text-[color:var(--text-secondary)]";
}

export function RegistrySkillMap({ accessToken, orgId }: { accessToken: string; orgId: string }) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [repos, setRepos] = useState<RepoRow[]>([]);
  const [repoId, setRepoId] = useState("");
  const [tree, setTree] = useState<SkillNode | null>(null);
  const [selected, setSelected] = useState<SkillNode | null>(null);
  const [collapsed, setCollapsed] = useState(false);
  const [width, setWidth] = useState(900);

  useEffect(() => {
    async function loadRepos() {
      const response = await fetch(`${API_URL}/orgs/${orgId}/repos`, { headers: headers(accessToken) });
      if (!response.ok) return;
      const body = (await response.json()) as RepoRow[];
      setRepos(body);
      setRepoId((current) => current || body[0]?.id || "");
    }
    if (orgId) void loadRepos();
  }, [accessToken, orgId]);

  useEffect(() => {
    async function loadTree() {
      const response = await fetch(`${API_URL}/registry/orgs/${orgId}/skill-tree?repo_id=${repoId}`, { headers: headers(accessToken) });
      if (!response.ok) return;
      setTree((await response.json()) as SkillNode);
      setCollapsed(false);
    }
    if (repoId) void loadTree();
  }, [accessToken, orgId, repoId]);

  useEffect(() => {
    const node = wrapRef.current;
    if (!node) return;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(640, entry.contentRect.width)));
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const summary = useMemo(() => {
    const domains = tree?.children ?? [];
    const covered = domains.length;
    const all = 8;
    return { domains, covered, missing: Math.max(0, all - covered) };
  }, [tree]);

  useEffect(() => {
    const svgEl = svgRef.current;
    if (!svgEl) return;
    const svg = d3.select<SVGSVGElement, unknown>(svgEl);
    svg.selectAll("*").remove();
    if (!tree) return;
    const height = Math.max(520, (tree.children ?? []).reduce((sum, domain) => sum + Math.max(1, domain.children?.length ?? 1), 0) * 56);
    const root = d3.hierarchy(tree as SkillNode);
    if (collapsed) {
      root.children?.forEach((child) => {
        child.children = undefined;
      });
    }
    d3.tree<SkillNode>().nodeSize([46, 230])(root);
    const g = svg.attr("viewBox", [-180, -40, width, height].join(" ")).append("g");
    svg.call(d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.4, 4]).on("zoom", (event) => g.attr("transform", event.transform.toString())));
    g.selectAll("path")
      .data(root.links())
      .join("path")
      .attr("fill", "none")
      .attr("stroke", "var(--bg-border)")
      .attr("stroke-width", 1.5)
      .attr("d", d3.linkHorizontal<d3.HierarchyLink<SkillNode>, d3.HierarchyNode<SkillNode>>().x((d) => d.y ?? 0).y((d) => d.x ?? 0));
    const node = g.selectAll("g.node").data(root.descendants()).join("g").attr("class", "node").attr("transform", (d) => `translate(${d.y},${d.x})`).style("cursor", "pointer");
    node.append("rect")
      .attr("x", (d) => (d.data.type === "repo" ? -60 : d.data.type === "domain" ? -50 : -64))
      .attr("y", (d) => (d.data.type === "repo" ? -18 : -14))
      .attr("width", (d) => (d.data.type === "repo" ? 120 : d.data.type === "domain" ? 112 : 150))
      .attr("height", (d) => (d.data.type === "repo" ? 36 : 28))
      .attr("rx", 8)
      .attr("fill", (d) => (d.data.type === "repo" ? "var(--accent-primary)" : d.data.type === "domain" ? "var(--bg-elevated)" : d.data.status === "healthy" ? "rgba(34,197,94,0.14)" : d.data.status === "stale" ? "rgba(245,158,11,0.14)" : d.data.status === "low_score" ? "rgba(239,68,68,0.16)" : "var(--bg-border)"))
      .attr("stroke", (d) => (d.data.type === "repo" ? "var(--accent-primary)" : d.data.status === "healthy" ? "var(--accent-green)" : d.data.status === "stale" ? "#f59e0b" : d.data.status === "low_score" ? "#ef4444" : "var(--bg-border)"))
      .on("click", (_event, d) => {
        if (d.data.type === "skill") setSelected(d.data);
      });
    node.append("text")
      .attr("dy", 4)
      .attr("x", (d) => (d.data.type === "skill" ? -56 : 0))
      .attr("text-anchor", (d) => (d.data.type === "skill" ? "start" : "middle"))
      .attr("fill", "var(--text-primary)")
      .attr("font-size", 11)
      .attr("font-weight", 700)
      .text((d) => (d.data.name.length > 18 ? `${d.data.name.slice(0, 18)}...` : d.data.name));
    node.filter((d) => d.data.type === "skill").append("text").attr("x", 76).attr("dy", 4).attr("text-anchor", "end").attr("fill", "var(--text-tertiary)").attr("font-size", 10).text((d) => `${d.data.score ?? 0}`);
    return () => {
      svg.selectAll("*").remove();
    };
  }, [collapsed, tree, width]);

  return (
    <section className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
      <aside className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <h2 className="font-semibold text-[color:var(--text-primary)]">Select a repo</h2>
        <div className="mt-3 max-h-[320px] space-y-2 overflow-y-auto">
          {repos.map((repo) => <button className={`flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left text-[13px] ${repo.id === repoId ? "border-[color:var(--accent-primary)] bg-[rgb(var(--accent-primary-rgb)/0.10)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-base)]"}`} key={repo.id} onClick={() => setRepoId(repo.id)} type="button"><span>{repo.name}</span><ChevronRight className="h-3.5 w-3.5" /></button>)}
        </div>
        <div className="mt-5 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-[13px] text-[color:var(--text-secondary)]">
          <div className="font-semibold text-[color:var(--text-primary)]">Domain summary</div>
          <div className="mt-2">{summary.domains.length} domains · {summary.covered} covered · {summary.missing} missing</div>
          <div className="mt-3 flex flex-wrap gap-1.5">{summary.domains.map((domain) => <button className="rounded-full bg-green-500/15 px-2 py-0.5 text-[11px] text-green-300" key={domain.name} type="button">{domain.name}</button>)}</div>
        </div>
      </aside>
      <div className="relative rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" ref={wrapRef}>
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-[color:var(--text-primary)]">Interactive skill tree</h2>
            <p className="text-[12px] text-[color:var(--text-secondary)]">Root is the repo, branches are domains, leaves are SKILL.md files.</p>
          </div>
          <div className="flex gap-2">
            <button className="rounded-md border border-[color:var(--bg-border)] p-2 text-[color:var(--text-secondary)]" onClick={() => setCollapsed(false)} type="button"><Maximize2 className="h-4 w-4" /></button>
            <button className="rounded-md border border-[color:var(--bg-border)] p-2 text-[color:var(--text-secondary)]" onClick={() => setCollapsed(true)} type="button"><Minimize2 className="h-4 w-4" /></button>
          </div>
        </div>
        {tree ? <svg className="h-[560px] w-full rounded-lg bg-[color:var(--bg-base)]" ref={svgRef} /> : <div className="flex h-[560px] items-center justify-center rounded-lg bg-[color:var(--bg-base)] text-sm text-[color:var(--text-secondary)]">Select a repo from the left to see its skill tree.</div>}
        <div className="mt-3 flex flex-wrap gap-3 text-[12px] text-[color:var(--text-secondary)]"><span>Healthy</span><span>Low score</span><span>Stale</span><span>Never loaded</span></div>
      </div>
      {selected ? <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-[400px] border-l border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-6 shadow-2xl"><button className="mb-4 rounded-lg p-2 text-[color:var(--text-secondary)] hover:bg-[color:var(--bg-surface)]" onClick={() => setSelected(null)} type="button"><X className="h-4 w-4" /></button><h2 className="text-xl font-semibold text-[color:var(--text-primary)]">{selected.name}</h2><div className={`mt-3 inline-flex rounded-full border px-2.5 py-1 text-[12px] font-semibold ${statusClass(selected.status)}`}>{selected.status?.replaceAll("_", " ")}</div><div className="mt-5 text-sm text-[color:var(--text-secondary)]">Score {selected.score}/100 · {selected.load_count} loads in 30d</div><div className="mt-2 font-mono text-[12px] text-[color:var(--text-tertiary)]">{selected.path}</div><pre className="mt-5 max-h-[260px] overflow-auto whitespace-pre-wrap rounded-lg bg-[color:var(--bg-surface)] p-3 text-[11px] leading-5 text-[color:var(--text-secondary)]">{selected.content_preview || "No preview available."}</pre><div className="mt-5 flex flex-wrap gap-2">{selected.status === "healthy" ? <Link className="rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-[12px] font-semibold text-[color:var(--bg-base)]" href={`/dashboard/skills?domain=${selected.name}`}>View full skill</Link> : <Link className="inline-flex items-center rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-[12px] font-semibold text-[color:var(--bg-base)]" href={`/dashboard/autopilot?skill=${selected.skill_id}`}><Sparkles className="mr-1.5 h-3.5 w-3.5" />Improve with AI</Link>}</div></aside> : null}
    </section>
  );
}
