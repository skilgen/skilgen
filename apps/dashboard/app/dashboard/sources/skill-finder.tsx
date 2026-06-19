"use client";

import Link from "next/link";
import * as d3 from "d3";
import { useEffect, useRef, useState } from "react";

type Leaf = { name: string; type: "leaf"; skill: string; label: string; description: string; command: string; color: string };
type Branch = { name: string; type: "root" | "question"; children: TreeNode[] };
type TreeNode = Branch | Leaf;

const treeData: Branch = {
  name: "What is your agent struggling with?",
  type: "root",
  children: [
    { name: "Getting the database schema wrong", type: "question", children: [
      { name: "SQL database (Postgres, MySQL, SQLite)", type: "leaf", skill: "data_schema", label: "SQL Schema Skill", description: "Teaches agents your exact table names, column types, foreign keys, and query patterns. Agents stop guessing schema — they load it.", command: "skilgen analyse --source sql-schema --file schema.sql --domain data_schema", color: "#3b82f6" },
      { name: "NoSQL / other (Mongo, Dynamo, Redis)", type: "leaf", skill: "data_schema", label: "Data Schema Skill", description: "Documents your collection structure, index design, and data access patterns so agents use your real data model.", command: "skilgen analyse --domain data_schema --project-root .", color: "#3b82f6" },
    ] },
    { name: "Calling the wrong API endpoints", type: "question", children: [
      { name: "We have an OpenAPI / Swagger spec", type: "leaf", skill: "internal_tools", label: "API Patterns Skill (from OpenAPI)", description: "Generated directly from your spec — agents learn your real endpoints, request shapes, and authentication patterns. Zero guessing.", command: "skilgen analyse --source openapi --file openapi.yaml --domain internal_tools", color: "#8b5cf6" },
      { name: "No spec — agents just guess endpoint names", type: "leaf", skill: "internal_tools", label: "Internal Tools Skill", description: "Document your API conventions so agents stop inventing endpoint names. Covers base URLs, auth headers, common patterns.", command: "skilgen analyse --domain internal_tools --project-root .", color: "#8b5cf6" },
    ] },
    { name: "Wrong code style or architecture", type: "question", children: [
      { name: "Formatting, naming, import order", type: "leaf", skill: "code_style", label: "Code Style Skill", description: "Captures your naming conventions, file structure rules, and formatting preferences. Agents write code that passes your linter first time.", command: "skilgen analyse --domain code_style --project-root .", color: "#f59e0b" },
      { name: "Module structure, layers, how things are organised", type: "leaf", skill: "codebase_architecture", label: "Architecture Skill", description: "Teaches agents how your codebase is structured — where controllers go, how services are layered, what the module boundaries are.", command: "skilgen analyse --domain codebase_architecture --project-root .", color: "#f59e0b" },
    ] },
    { name: "Writing bad tests or using wrong test patterns", type: "leaf", skill: "testing_conventions", label: "Testing Conventions Skill", description: "Your test structure, assertion style, mocking approach, and coverage targets. Agents write tests that match your actual test suite.", command: "skilgen analyse --domain testing_conventions --project-root .", color: "#10b981" },
    { name: "Missing security checks or exposing secrets", type: "question", children: [
      { name: "We have SARIF / SAST scan output", type: "leaf", skill: "security_compliance", label: "Security Skill (from scan results)", description: "Generated from your security scan findings — agents learn the exact vulnerabilities your scanner flags and how to avoid them.", command: "skilgen analyse --source sarif --file results.sarif --domain security_compliance", color: "#ef4444" },
      { name: "No scan — agents just make security mistakes", type: "leaf", skill: "security_compliance", label: "Security Compliance Skill", description: "Documents your auth patterns, secret handling rules, and input validation conventions. Agents stop introducing the same security mistakes.", command: "skilgen analyse --domain security_compliance --project-root .", color: "#ef4444" },
    ] },
    { name: "Infrastructure or deployment errors", type: "question", children: [
      { name: "Terraform", type: "leaf", skill: "operational_knowledge", label: "Infrastructure Skill (Terraform)", description: "Resource naming, module patterns, and tagging conventions extracted from your Terraform. Agents write infra code that matches your setup.", command: "skilgen analyse --source terraform --dir infra/ --domain operational_knowledge", color: "#6366f1" },
      { name: "Kubernetes", type: "leaf", skill: "operational_knowledge", label: "Infrastructure Skill (Kubernetes)", description: "Deployment patterns, resource limits, namespace naming, and health check conventions from your K8s manifests.", command: "skilgen analyse --source kubernetes --dir k8s/ --domain operational_knowledge", color: "#6366f1" },
      { name: "Other / general ops knowledge", type: "leaf", skill: "operational_knowledge", label: "Operational Knowledge Skill", description: "Runbooks, deployment steps, environment configuration, and on-call patterns your agents need to understand.", command: "skilgen analyse --domain operational_knowledge --project-root .", color: "#6366f1" },
    ] },
    { name: "Using wrong UI components or design tokens", type: "leaf", skill: "design_system", label: "Design System Skill", description: "Component names, prop patterns, colour tokens, and spacing rules from your design system. Agents stop inventing components that already exist.", command: "skilgen analyse --domain design_system --project-root .", color: "#ec4899" },
  ],
};

function isLeaf(node: TreeNode): node is Leaf {
  return node.type === "leaf";
}

function ResultPanel({ leaf, onReset }: { leaf: Leaf | null; onReset: () => void }) {
  const [copied, setCopied] = useState(false);
  if (!leaf) return <aside className="rounded-xl border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 text-sm text-[color:var(--text-secondary)]">Select a leaf node to see the exact skill and command to generate it.</aside>;
  return (
    <aside className="translate-x-0 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 transition-transform">
      <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-full" style={{ backgroundColor: leaf.color }} /><h3 className="text-xl font-semibold">{leaf.label}</h3></div>
      <p className="mt-4 text-sm leading-6 text-[color:var(--text-secondary)]">{leaf.description}</p>
      <div className="my-5 border-t border-[color:var(--bg-border)]" />
      <div className="text-sm font-semibold">Generate this skill:</div>
      <code className="mt-3 block rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] p-3 font-mono text-[12px] leading-5 text-[color:var(--accent-primary)]">$ {leaf.command}</code>
      <button className="mt-3 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm" onClick={() => { void navigator.clipboard.writeText(leaf.command); setCopied(true); window.setTimeout(() => setCopied(false), 2000); }} type="button">{copied ? "Copied!" : "Copy command"}</button>
      <div className="my-5 border-t border-[color:var(--bg-border)]" />
      <h4 className="font-semibold">What this does:</h4>
      <p className="mt-2 text-sm leading-6 text-[color:var(--text-secondary)]">Analyses your codebase and writes a SKILL.md file to .skillayer/{leaf.skill}.md. Your agents load this automatically in every coding session.</p>
      <div className="mt-5 flex flex-wrap gap-3"><Link className="text-sm font-semibold text-[color:var(--accent-primary)]" href={`/dashboard/skills?domain=${leaf.skill}`}>View existing {leaf.skill} skills →</Link><button className="text-sm font-semibold text-[color:var(--text-secondary)]" onClick={onReset} type="button">Start over ↺</button></div>
    </aside>
  );
}

function MobileTree({ onSelect }: { onSelect: (leaf: Leaf) => void }) {
  return <div className="space-y-3">{treeData.children.map((child) => isLeaf(child) ? <button className="w-full rounded-lg border border-[color:var(--bg-border)] p-3 text-left" key={child.name} onClick={() => onSelect(child)}>{child.name}</button> : <details className="rounded-lg border border-[color:var(--bg-border)] p-3" key={child.name}><summary className="cursor-pointer font-semibold">{child.name}</summary><div className="mt-3 space-y-2">{child.children.map((leaf) => <button className="block w-full rounded-md bg-black/20 p-3 text-left text-sm" key={leaf.name} onClick={() => isLeaf(leaf) ? onSelect(leaf) : undefined}>{leaf.name}</button>)}</div></details>)}</div>;
}

export function SkillFinder() {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [selectedLeaf, setSelectedLeaf] = useState<Leaf | null>(null);
  const [activePath, setActivePath] = useState<string[]>([]);
  const [width, setWidth] = useState(0);
  const [tooltip, setTooltip] = useState<{ text: string; x: number; y: number } | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width));
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!svgRef.current || width < 640) return;
    const svgElement = svgRef.current;
    const svg = d3.select(svgElement);
    svg.selectAll("*").remove();
    const chartWidth = Math.max(620, width * 0.6);
    const height = 520;
    const margin = { top: 20, right: 40, bottom: 20, left: 180 };
    const root = d3.hierarchy<TreeNode>(treeData);
    d3.tree<TreeNode>().size([height - margin.top - margin.bottom, chartWidth - margin.left - margin.right])(root);
    const pointRoot = root as d3.HierarchyPointNode<TreeNode>;
    const group = svg.attr("viewBox", `0 0 ${chartWidth} ${height}`).append("g").attr("transform", `translate(${margin.left},${margin.top})`);
    const pathIds = new Set(activePath);
    const linkPath = d3.linkHorizontal<d3.HierarchyPointLink<TreeNode>, d3.HierarchyPointNode<TreeNode>>().x((d) => d.y).y((d) => d.x);
    group.selectAll(".link").data(pointRoot.links()).join("path").attr("fill", "none").attr("stroke", (d) => pathIds.has(d.source.data.name) && pathIds.has(d.target.data.name) ? "var(--accent-primary)" : "var(--bg-border)").attr("stroke-width", 1.5).attr("opacity", (d) => activePath.length === 0 || pathIds.has(d.source.data.name) || pathIds.has(d.target.data.name) ? 1 : 0.25).attr("d", (d) => linkPath(d) ?? "");
    const node = group.selectAll(".node").data(pointRoot.descendants()).join("g").attr("transform", (d) => `translate(${d.y},${d.x})`).style("cursor", "pointer").on("click", (_event, d) => {
      const path = d.ancestors().map((item) => item.data.name);
      setActivePath(path);
      if (isLeaf(d.data)) setSelectedLeaf(d.data);
    });
    node.append("circle").attr("r", (d) => d.data.type === "leaf" ? 10 : 7).attr("fill", (d) => d.data.type === "leaf" ? (d.data as Leaf).color : pathIds.has(d.data.name) ? "var(--accent-primary)" : d.data.type === "root" ? "var(--accent-primary)" : "var(--bg-surface)").attr("stroke", (d) => d.data.type === "leaf" ? (d.data as Leaf).color : "var(--accent-primary)").attr("stroke-width", 2);
    node.append("text").attr("dy", "0.32em").attr("x", (d) => d.children ? -12 : 14).attr("text-anchor", (d) => d.children ? "end" : "start").attr("fill", "var(--text-primary)").attr("font-size", "12px").text((d) => d.data.name.length > 36 ? `${d.data.name.slice(0, 36)}…` : d.data.name).on("mouseenter", (event, d) => d.data.name.length > 36 ? setTooltip({ text: d.data.name, x: event.clientX, y: event.clientY }) : null).on("mouseleave", () => setTooltip(null));
    return () => { d3.select(svgElement).selectAll("*").remove(); };
  }, [activePath, width]);

  function reset() {
    setSelectedLeaf(null);
    setActivePath([]);
  }

  return (
    <section className="space-y-5" ref={containerRef}>
      <header><h2 className="text-xl font-semibold">What skill do I need?</h2><p className="mt-1 text-sm text-[color:var(--text-secondary)]">Answer two questions to find the right skill type and the exact command to generate it.</p></header>
      <div className="grid gap-5 lg:grid-cols-[minmax(0,3fr)_minmax(320px,2fr)]">
        <div className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          {width === 0 ? <div className="h-[520px] animate-pulse rounded-lg bg-white/5" /> : width < 640 ? <MobileTree onSelect={setSelectedLeaf} /> : <svg className="h-[520px] w-full" ref={svgRef} />}
          <button className="mt-3 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm" onClick={reset} type="button">Start over</button>
        </div>
        <ResultPanel leaf={selectedLeaf} onReset={reset} />
      </div>
      {tooltip ? <div className="fixed z-50 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] px-3 py-2 text-xs text-[color:var(--text-primary)]" style={{ left: tooltip.x + 12, top: tooltip.y + 12 }}>{tooltip.text}</div> : null}
    </section>
  );
}
