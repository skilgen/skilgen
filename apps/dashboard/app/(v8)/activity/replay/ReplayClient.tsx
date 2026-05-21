"use client";

import * as d3 from "d3";
import { AlertTriangle, ChevronDown, ChevronLeft, ChevronRight, Copy, Download, Flag, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";

import type { ActivitySession, ReplayStep } from "../activity-data";

type RiskBand = ActivitySession["risk_band"];
type LooseRecord = Record<string, unknown>;
type ReplayStepV2 = ReplayStep & {
  type?: string | null;
  label?: string | null;
  target?: string | null;
  detail?: unknown;
  risk_flag?: string | boolean | null;
};
type ActivitySessionV2 = ActivitySession & {
  risk_contributors?: unknown;
  skill_coverage?: unknown;
};
type RiskContributor = {
  label: string;
  value: number;
  detail: string;
};
type DangerFinding = {
  severity: "critical" | "high" | "medium";
  title: string;
  reason: string;
  matchedPattern: string;
  command: string;
  step: number;
};
type FlowNode = {
  id: string;
  type: string;
  label: string;
  target: string;
  count: number;
  steps: ReplayStepV2[];
  firstIndex: number;
  riskScore: number;
  riskBand: RiskBand;
  destructive: boolean;
  x: number;
  y: number;
};
type FindingGroup = {
  key: string;
  severity: DangerFinding["severity"];
  title: string;
  reason: string;
  findings: DangerFinding[];
};

function bandTone(band: RiskBand): string {
  if (band === "high") return "border-red-500/40 bg-red-500/10 text-red-200";
  if (band === "medium") return "border-amber-500/40 bg-amber-500/10 text-amber-200";
  return "border-[color:var(--accent-green)]/40 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]";
}

function bandText(band: RiskBand): string {
  if (band === "high") return "High risk";
  if (band === "medium") return "Medium risk";
  return "Low risk";
}

function formatTime(value: string | null): string {
  if (!value) return "Time unavailable";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(date);
}

function compactId(value: string): string {
  if (value.length <= 18) return value;
  return `${value.slice(0, 8)}...${value.slice(-6)}`;
}

function humanize(value: string | null | undefined): string {
  if (!value) return "Unknown";
  if (value.startsWith("{") || value.startsWith("[")) {
    try {
      const parsed = JSON.parse(value) as unknown;
      if (isRecord(parsed)) return humanize(stringField(parsed, ["type", "mode", "policy", "name"]) || "configured");
    } catch {
      return "Configured";
    }
  }
  return value.replaceAll("_", " ").replaceAll("-", " ");
}

function isRecord(value: unknown): value is LooseRecord {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function stringField(record: LooseRecord | null | undefined, keys: string[]): string | null {
  if (!record) return null;
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" && value.trim()) return value;
    if (typeof value === "number") return String(value);
  }
  return null;
}

function stringValue(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function readableValue(value: unknown): string | null {
  if (value == null) return null;
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) {
    const values = value.map(readableValue).filter(Boolean);
    return values.length ? values.join(", ") : null;
  }
  if (isRecord(value)) {
    const picked = [
      stringField(value, ["label", "name", "title", "path", "file", "target", "command", "query", "url", "endpoint"]),
      stringField(value, ["method", "status", "decision", "outcome", "message", "summary", "detail"]),
    ].filter(Boolean);
    return picked.length ? picked.join(" - ") : null;
  }
  return null;
}

function stepTitle(step: ReplayStepV2): string {
  return step.label || humanize(step.action) || humanize(step.type);
}

function stepTarget(step: ReplayStepV2): string {
  return step.target || stringField(step.tool_call, ["target", "path", "file", "command", "query", "url", "endpoint"]) || stringField(isRecord(step.detail) ? step.detail : null, ["target", "path", "file", "command", "query", "url", "endpoint"]) || "Run context";
}

function commandForStep(step: ReplayStepV2): string {
  if ((step.type || step.action).toLowerCase() === "command") return stepTarget(step);
  const value = stringField(step.tool_call, ["command", "cmd", "input"]) || stringField(step.result, ["command", "cmd"]);
  return value || "";
}

function stepDetail(step: ReplayStepV2): string {
  return readableValue(step.detail) || stringField(step.result, ["summary", "message", "outcome", "status", "path", "file", "command"]) || stringField(step.tool_call, ["name", "tool", "command", "query", "path", "url"]) || step.reasoning || humanize(step.action_class);
}

function isRiskFlagged(step: ReplayStepV2): boolean {
  const flag: unknown = step.risk_flag;
  return flag === true || (typeof flag === "string" && flag.trim().length > 0) || step.risk_band === "high";
}

function inferEvidenceKind(step: ReplayStepV2): string | null {
  const haystack = [step.type, step.action, step.action_class, step.label, step.target, stringField(step.tool_call, ["name", "tool", "command"]), step.file_diff ? "diff edit" : ""].filter(Boolean).join(" ").toLowerCase();
  if (haystack.match(/\b(api|http|fetch|request|webhook)\b/)) return "api";
  if (haystack.match(/\b(shell|terminal|bash|command|exec)\b/)) return "shell";
  if (haystack.match(/\b(search|grep|rg|find)\b/)) return "searches";
  if (step.file_diff || haystack.match(/\b(edit|write|patch|modified|created|delete)\b/)) return "edited";
  if (haystack.match(/\b(read|open|explore|inspect|view|cat)\b/)) return "explored";
  if (step.tool_call) return "tools";
  return null;
}

function findingsForStep(step: ReplayStepV2, index: number): DangerFinding[] {
  const command = commandForStep(step);
  const raw = isRecord(step.result) && Array.isArray(step.result.danger_findings) ? step.result.danger_findings : [];
  const backend = raw.filter(isRecord).map((item) => ({
    severity: item.severity === "critical" || item.severity === "high" || item.severity === "medium" ? item.severity : "medium",
    title: String(item.title || "Flagged command"),
    reason: String(item.reason || "Matched the command danger policy."),
    matchedPattern: String(item.matchedPattern || "policy-match"),
    command: String(item.command || command),
    step: index + 1,
  })) as DangerFinding[];
  const byKey = new Map<string, DangerFinding>();
  for (const finding of backend) byKey.set(`${finding.severity}:${finding.title}:${finding.command}`, finding);
  return [...byKey.values()];
}

function detailTarget(step: ReplayStepV2): string {
  const command = commandForStep(step);
  const target = stepTarget(step);
  const detail = stepDetail(step);
  if (command) return command;
  if (target && target !== "Run context") return target;
  if (detail && !["read", "write", "exec", "tool"].includes(detail.toLowerCase())) return detail;
  return stepTitle(step);
}

function shortNodeLabel(step: ReplayStepV2): string {
  const type = (step.type || step.action || step.action_class || "").toLowerCase();
  const command = commandForStep(step);
  if (command) {
    const match = command.match(/\b(rm\s+-rf|rm\s+-r|npm\s+install|npm\s+run|git\s+push|curl|wget|python|pytest|rg|sed|sqlite3|uvicorn|playwright|sudo|cat|cp|scp|rsync)\b/i);
    return match ? match[0] : command.split(/\s+/).slice(0, 2).join(" ");
  }
  if (type.includes("session")) return "Session";
  if (type.includes("search")) return "Search";
  if (type.includes("explore") || type.includes("read")) return "Explore";
  if (type.includes("edit") || type.includes("write")) return "Edit";
  if (type.includes("finish")) return "Finish";
  if (type.includes("pause")) return "Paused";
  return stepTitle(step);
}

function groupedNodeLabel(type: string, count: number): string {
  if (type === "search") return `Searches x${count}`;
  if (type === "command") return `Commands x${count}`;
  if (type === "tool") return `Tools x${count}`;
  if (type === "explore") return `Explored x${count}`;
  if (type === "edit") return `Edits x${count}`;
  return `${humanize(type)} x${count}`;
}

function parseRiskContributors(session: ActivitySessionV2, timeline: ReplayStepV2[]): RiskContributor[] {
  const raw = session.risk_contributors;
  const parsed: RiskContributor[] = [];
  if (Array.isArray(raw)) {
    raw.forEach((item, index) => {
      if (!isRecord(item)) return;
      const record: LooseRecord = item;
      const label = stringField(record, ["label", "name", "factor", "type"]) || `Contributor ${index + 1}`;
      const value = Number(record.points ?? record.weight ?? record.value ?? record.score ?? record.risk_score ?? 0);
      const detail = stringField(item, ["detail", "reason", "summary", "description"]) || "";
      parsed.push({ label, value: Number.isFinite(value) ? value : 0, detail });
    });
  } else if (isRecord(raw)) {
    Object.entries(raw).forEach(([label, value]) => {
      if (typeof value === "number") parsed.push({ label: humanize(label), value, detail: "Weighted risk signal." });
      else if (isRecord(value)) {
        const amount = Number(value.weight ?? value.value ?? value.score ?? 0);
        parsed.push({ label: humanize(label), value: Number.isFinite(amount) ? amount : 0, detail: stringField(value, ["detail", "reason", "summary"]) || "Weighted risk signal." });
      }
    });
  }
  if (parsed.length) return normalizeContributorPoints(parsed, session.risk_score);

  const highRiskSteps = timeline.filter((step) => step.risk_band === "high").length;
  const editedSteps = timeline.filter((step) => inferEvidenceKind(step) === "edited").length;
  const shellSteps = timeline.filter((step) => inferEvidenceKind(step) === "shell").length;
  return [
    { label: "Session risk score", value: session.risk_score, detail: "" },
    { label: "High risk steps", value: highRiskSteps * 20, detail: "" },
    { label: "File changes", value: editedSteps * 12, detail: "" },
    { label: "Command activity", value: shellSteps * 10, detail: "" },
  ].filter((item) => item.value > 0);
}

function normalizeContributorPoints(items: RiskContributor[], score: number): RiskContributor[] {
  const total = items.reduce((sum, item) => sum + Math.max(0, Math.round(item.value)), 0);
  if (!total || total === score) return items.map((item) => ({ ...item, value: Math.round(item.value) }));
  let running = 0;
  return items.map((item, index) => {
    const value = index === items.length - 1 ? Math.max(0, score - running) : Math.max(0, Math.round((item.value / total) * score));
    running += value;
    return { ...item, value };
  }).filter((item) => item.value > 0);
}

function skillCoverageFact(session: ActivitySessionV2): string {
  const coverage = session.skill_coverage;
  if (isRecord(coverage)) {
    const record: LooseRecord = coverage;
    const status = stringField(coverage, ["status", "summary", "verdict"]);
    const covered = Number(record.loaded_count ?? record.covered ?? record.loaded ?? record.matched);
    const total = Number(record.relevant_count ?? record.total ?? record.required);
    const missingValue = record.missing;
    const missing = Array.isArray(missingValue) ? missingValue.length : Number(record.missing_count ?? 0);
    if (status) return status;
    if (Number.isFinite(covered) && Number.isFinite(total) && total > 0) return `${covered} of ${total} expected skills were covered${missing ? `, with ${missing} gap${missing === 1 ? "" : "s"}` : ""}.`;
  }
  return session.skills_loaded.length ? `${session.skills_loaded.length} skills were loaded during the run.` : "No loaded skills were reported for this run.";
}

function accessPolicyFact(session: ActivitySessionV2): string {
  const access = session.full_access ? "Full-access" : humanize(session.access_scope || "default access");
  const approval = humanize(session.approval_policy || "approval unknown");
  const sandbox = humanize(session.sandbox_policy || "sandbox unknown");
  return `Access policy: ${access} - ${approval} approval - ${sandbox} sandbox.`;
}

function verdictFacts(session: ActivitySessionV2, timeline: ReplayStepV2[]): string[] {
  const denied = timeline.filter((step) => step.policy_decision?.toLowerCase() === "deny").length;
  const flagged = timeline.filter(isRiskFlagged).length;
  const policies = [...new Set(timeline.map((step) => humanize(step.policy_decision)).filter(Boolean))];
  return [
    denied ? `Compliance needs review because ${denied} step${denied === 1 ? "" : "s"} hit a deny decision.` : "Compliance stayed within the observed allow path.",
    skillCoverageFact(session),
    accessPolicyFact(session),
    policies.length ? `Access policy decisions observed: ${policies.join(", ")}.` : "No access policy decisions were attached to the replay.",
    flagged ? `${flagged} step${flagged === 1 ? "" : "s"} carried a risk flag or high-risk band.` : "No replay step carried an explicit risk flag.",
  ];
}

function recommendedAction(session: ActivitySessionV2, timeline: ReplayStepV2[]): string {
  if (session.risk_band === "high") return "Pause promotion, review the flagged evidence, and require an owner approval before reuse.";
  if (timeline.some((step) => step.policy_decision?.toLowerCase() === "deny")) return "Resolve the denied policy decision before considering this run complete.";
  if (session.risk_band === "medium") return "Review the highlighted contributors, then approve if the edited and command evidence matches the intended scope.";
  return "Safe to accept after a quick spot-check of the edited files and final outcome.";
}

function stepTime(step: ReplayStepV2): number {
  const value = step.timestamp ? new Date(step.timestamp).getTime() : NaN;
  return Number.isFinite(value) ? value : 0;
}

function durationLabel(session: ActivitySessionV2, timeline: ReplayStepV2[]): string {
  const start = session.started_at ? new Date(session.started_at).getTime() : Math.min(...timeline.map(stepTime).filter(Boolean));
  const end = session.ended_at ? new Date(session.ended_at).getTime() : Math.max(...timeline.map(stepTime).filter(Boolean));
  if (!session.ended_at && session.outcome === "in_progress") return "running";
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return session.ended_at ? "<1 min" : "running";
  const minutes = Math.max(1, Math.round((end - start) / 60000));
  return `${minutes} min`;
}

function nodeType(step: ReplayStepV2): string {
  const type = (step.type || step.action || step.action_class || "").toLowerCase();
  if (type.includes("session") || type.includes("finish") || type.includes("pause")) return "session";
  if (type.includes("search")) return "search";
  if (type.includes("explore") || type.includes("read")) return "explore";
  if (type.includes("edit") || type.includes("write")) return "edit";
  if (type.includes("command") || type.includes("exec") || commandForStep(step)) return "command";
  return "tool";
}

function nodeTone(type: string, destructive: boolean): { fill: string; stroke: string; text: string } {
  if (destructive) return { fill: "#7f1d1d", stroke: "#ef4444", text: "#fee2e2" };
  if (type === "search") return { fill: "#1e3a8a", stroke: "#60a5fa", text: "#dbeafe" };
  if (type === "explore") return { fill: "#134e4a", stroke: "#2dd4bf", text: "#ccfbf1" };
  if (type === "edit") return { fill: "#78350f", stroke: "#f59e0b", text: "#fef3c7" };
  if (type === "command") return { fill: "#4c1d95", stroke: "#a78bfa", text: "#ede9fe" };
  return { fill: "#27272a", stroke: "#71717a", text: "#e4e4e7" };
}

function buildFlowNodes(timeline: ReplayStepV2[], expanded: Set<string>, width = 980): { nodes: FlowNode[]; height: number; path: string } {
  const baseGroups: Array<{ id: string; steps: ReplayStepV2[]; firstIndex: number; type: string }> = [];
  timeline.forEach((step, index) => {
    const type = nodeType(step);
    const last = baseGroups[baseGroups.length - 1];
    const findings = findingsForStep(step, index);
    const canCollapse = last && last.type === type && findings.length === 0 && type !== "session" && !expanded.has(last.id);
    if (canCollapse) {
      last.steps.push(step);
    } else {
      baseGroups.push({ id: `node-${index}`, steps: [step], firstIndex: index, type });
    }
  });
  const groups = baseGroups.flatMap((group) => expanded.has(group.id) ? group.steps.map((step, offset) => ({ id: `${group.id}-${offset}`, steps: [step], firstIndex: group.firstIndex + offset, type: nodeType(step) })) : [group]);
  const nodeW = 116;
  const nodeH = 54;
  const colGap = 26;
  const rowGap = 50;
  const cols = Math.max(3, Math.floor((width - 32) / (nodeW + colGap)));
  const nodes = groups.map((group, index) => {
    const row = Math.floor(index / cols);
    const pos = index % cols;
    const col = row % 2 === 0 ? pos : cols - 1 - pos;
    const x = 16 + col * (nodeW + colGap);
    const y = 24 + row * (nodeH + rowGap);
    const riskScore = Math.max(...group.steps.map((step) => step.risk_score));
    const destructive = group.steps.some((step, stepOffset) => findingsForStep(step, group.firstIndex + stepOffset).some((finding) => finding.severity === "critical" || finding.severity === "high"));
    const riskBand = group.steps.find((step) => step.risk_score === riskScore)?.risk_band ?? "low";
    return {
      id: group.id,
      type: group.type,
      label: group.steps.length > 1 ? groupedNodeLabel(group.type, group.steps.length) : shortNodeLabel(group.steps[0]),
      target: group.steps.length > 1 ? `${group.steps.length} ${group.type} steps` : stepTarget(group.steps[0]),
      count: group.steps.length,
      steps: group.steps,
      firstIndex: group.firstIndex,
      riskScore,
      riskBand,
      destructive,
      x,
      y,
    };
  });
  const centers = nodes.map((node) => [node.x + nodeW / 2, node.y + nodeH / 2] as [number, number]);
  const path = d3.line<[number, number]>().x((d) => d[0]).y((d) => d[1])(centers) || "";
  const height = Math.max(160, (d3.max(nodes, (node) => node.y) || 0) + nodeH + 28);
  return { nodes, height, path };
}

function ReplayFlowchart({ activeIndex, expanded, onSelect, onToggleExpand, timeline }: { activeIndex: number; expanded: Set<string>; onSelect: (index: number) => void; onToggleExpand: (id: string) => void; timeline: ReplayStepV2[] }) {
  const { height, nodes } = useMemo(() => buildFlowNodes(timeline, expanded), [expanded, timeline]);
  const activeNode = nodes.find((node) => activeIndex >= node.firstIndex && activeIndex < node.firstIndex + node.steps.length);
  const nodeW = 116;
  const nodeH = 54;
  return (
    <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-medium text-[color:var(--text-primary)]">Replay flowchart</h3>
          <p className="mt-1 text-xs text-[color:var(--text-tertiary)]">Step {activeIndex + 1} of {timeline.length}</p>
        </div>
      </div>
      <svg className="mt-4 w-full overflow-visible" role="img" viewBox={`0 0 980 ${height}`}>
        <defs>
          <marker id="flow-arrow" markerHeight="8" markerWidth="8" orient="auto" refX="7" refY="4">
            <path d="M0,0 L8,4 L0,8 z" fill="#71717a" />
          </marker>
        </defs>
        {nodes.slice(0, -1).map((node, index) => {
          const next = nodes[index + 1];
          return <line key={`${node.id}-${next.id}`} markerEnd="url(#flow-arrow)" stroke="#3f3f46" strokeWidth="2" x1={node.x + nodeW / 2} x2={next.x + nodeW / 2} y1={node.y + nodeH / 2} y2={next.y + nodeH / 2} />;
        })}
        {nodes.map((node) => {
          const tone = nodeTone(node.type, node.destructive);
          const selected = activeNode?.id === node.id;
          return (
            <g className="cursor-pointer" key={node.id} onClick={() => onSelect(node.firstIndex)} transform={`translate(${node.x},${node.y})`}>
              {node.destructive ? <rect className="animate-pulse" fill="none" height="62" rx="10" stroke="#ef4444" strokeOpacity="0.45" strokeWidth="2" width="124" x="-4" y="-4" /> : null}
              <rect fill={tone.fill} height="54" rx="8" stroke={selected ? "var(--accent-primary)" : tone.stroke} strokeWidth={node.destructive ? 3 : selected ? 3 : 1.5} width="116" />
              {node.destructive ? <text fill="#fecaca" fontSize="13" fontWeight="500" x="8" y="18">!</text> : null}
              <text fill={tone.text} fontSize="12" fontWeight="500" textAnchor="middle" x="58" y="23">{node.label.slice(0, 18)}</text>
              <text fill="#c4c4cc" fontSize="10" textAnchor="middle" x="58" y="39">Step {node.firstIndex + 1}{node.count > 1 ? `-${node.firstIndex + node.count}` : ""}</text>
              {node.count > 1 ? <g onClick={(event) => { event.stopPropagation(); onToggleExpand(node.id); }}><circle cx="103" cy="12" fill="#0a0a0f" r="10" stroke={tone.stroke} /><text fill={tone.text} fontSize="10" fontWeight="500" textAnchor="middle" x="103" y="16">{node.count}</text></g> : null}
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function severityClass(severity: DangerFinding["severity"]): string {
  if (severity === "critical" || severity === "high") return "border-red-500/40 bg-red-500/10 text-red-200";
  return "border-amber-500/40 bg-amber-500/10 text-amber-200";
}

function groupedFindings(findings: DangerFinding[]): FindingGroup[] {
  const map = new Map<string, FindingGroup>();
  for (const finding of findings) {
    const key = `${finding.severity}:${finding.title}`;
    const current = map.get(key) ?? { key, severity: finding.severity, title: finding.title, reason: finding.reason, findings: [] };
    current.findings.push(finding);
    map.set(key, current);
  }
  const rank = { critical: 0, high: 1, medium: 2 };
  return [...map.values()].sort((a, b) => rank[a.severity] - rank[b.severity] || b.findings.length - a.findings.length);
}

function sensitiveFileMarker(path: string): string | null {
  const lower = path.toLowerCase();
  if (/(^|\/)\.env|\.pem$|id_rsa|auth\.py|config\.py|_seed\.db|\.sqlite/.test(lower)) return "sensitive";
  if (/skill\.md$|manifest\.md$/.test(lower)) return "skill doc";
  return null;
}

function EvidenceTriage({ onSelect, session, timeline }: { onSelect: (index: number) => void; session: ActivitySessionV2; timeline: ReplayStepV2[] }) {
  const [showAllCommands, setShowAllCommands] = useState(false);
  const [openDirs, setOpenDirs] = useState<Set<string>>(new Set(["apps", "skills", "."]));
  const [openFindingGroups, setOpenFindingGroups] = useState<Set<string>>(new Set());
  const details = session.activity_details ?? {};
  const allFindings = timeline.flatMap((step, index) => findingsForStep(step, index)).sort((a, b) => ({ critical: 0, high: 1, medium: 2 }[a.severity] - { critical: 0, high: 1, medium: 2 }[b.severity]));
  const findingGroups = groupedFindings(allFindings);
  const commandRows = timeline.map((step, index) => ({ command: commandForStep(step), step: index + 1, findings: findingsForStep(step, index) })).filter((row) => row.command);
  const searches = [...(details.searches ?? []), ...timeline.filter((step) => nodeType(step) === "search").map(stepTarget)];
  const networkCalls = (session.external_api_calls ?? []).filter((item) => item.domain || item.provider);
  const fileMap = new Map<string, { path: string; wrote: boolean; steps: number[] }>();
  const addFile = (path: string, wrote: boolean, step: number) => {
    if (!path || path === "Run context") return;
    const current = fileMap.get(path) ?? { path, wrote: false, steps: [] };
    current.wrote = current.wrote || wrote;
    if (!current.steps.includes(step)) current.steps.push(step);
    fileMap.set(path, current);
  };
  (details.edited_files ?? session.files_touched ?? []).forEach((path, index) => addFile(path, true, index + 1));
  (details.explored_files ?? []).forEach((path, index) => addFile(path, false, index + 1));
  timeline.forEach((step, index) => {
    if (nodeType(step) === "edit") addFile(stepTarget(step), true, index + 1);
    if (nodeType(step) === "explore") addFile(stepTarget(step), false, index + 1);
  });
  const dirs = [...fileMap.values()].reduce<Record<string, Array<{ path: string; wrote: boolean; steps: number[] }>>>((acc, item) => {
    const parts = item.path.split("/");
    const dir = parts.length > 1 ? parts.slice(0, -1).join("/") : ".";
    (acc[dir] ||= []).push(item);
    return acc;
  }, {});
  const coverage: LooseRecord = isRecord(session.skill_coverage) ? session.skill_coverage : {};
  const loaded = Number(coverage.loaded_count ?? session.skills_loaded.length ?? 0);
  const relevant = Number(coverage.relevant_count ?? loaded);
  const skillDocsRead = [...fileMap.keys()].some((path) => /skill\.md$|manifest\.md$/i.test(path));
  const visibleCommands = showAllCommands ? commandRows : commandRows.slice(0, 8);
  return (
    <section className="space-y-4">
      <div className="flex flex-wrap gap-2 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3 text-xs">
        <span className="rounded-md bg-black/20 px-2.5 py-1 text-[color:var(--text-secondary)]">files {fileMap.size}, {[...fileMap.values()].filter((item) => item.wrote).length} written</span>
        <span className="rounded-md bg-black/20 px-2.5 py-1 text-[color:var(--text-secondary)]">searches {new Set(searches).size}</span>
        <span className={`rounded-md px-2.5 py-1 ${allFindings.length ? "bg-red-500/10 text-red-200" : "bg-black/20 text-[color:var(--text-secondary)]"}`}>commands {commandRows.length}, {allFindings.length} flagged</span>
        <span className="rounded-md bg-black/20 px-2.5 py-1 text-[color:var(--text-secondary)]">network calls {networkCalls.reduce((sum, item) => sum + Number(item.count || 0), 0)}</span>
        <span className={`rounded-md px-2.5 py-1 ${relevant > 0 && loaded === 0 ? "bg-red-500/10 text-red-200" : "bg-black/20 text-[color:var(--text-secondary)]"}`}>skills loaded {loaded} of {relevant}</span>
      </div>

      <section className="rounded-lg border border-red-500/25 bg-red-500/5 p-4">
        <h3 className="text-sm font-medium text-[color:var(--text-primary)]">Flagged activity</h3>
        {findingGroups.length ? (
          <div className="mt-3 space-y-2">
            {findingGroups.map((group) => (
              <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3" key={group.key}>
                <button className="flex w-full flex-wrap items-start justify-between gap-3 text-left" onClick={() => setOpenFindingGroups((current) => { const next = new Set(current); next.has(group.key) ? next.delete(group.key) : next.add(group.key); return next; })} type="button">
                  <span className="min-w-0">
                    <span className={`mr-2 rounded-md border px-2 py-1 text-[11px] font-medium capitalize ${severityClass(group.severity)}`}>{group.severity}</span>
                    <span className="text-sm font-medium text-[color:var(--text-primary)]">{group.title} · {group.findings.length} step{group.findings.length === 1 ? "" : "s"}</span>
                  </span>
                  <ChevronDown className={`h-4 w-4 text-[color:var(--text-tertiary)] transition-transform ${openFindingGroups.has(group.key) ? "rotate-180" : ""}`} />
                </button>
                <div className="mt-2 space-y-1">
                  {group.findings.slice(0, 2).map((finding) => <code className="block overflow-x-auto whitespace-nowrap rounded bg-black/30 px-2 py-1 text-xs text-red-100" key={`${group.key}-${finding.step}`}>{finding.command}</code>)}
                </div>
                <p className="mt-2 text-xs text-[color:var(--text-secondary)]">{group.reason}</p>
                <div className="mt-2 flex flex-wrap gap-2 text-xs">
                  {group.findings.map((finding) => (
                    <button className="font-medium text-[color:var(--accent-primary)] hover:underline" key={`${group.key}-step-${finding.step}`} onClick={() => onSelect(finding.step - 1)} type="button">Step {finding.step}</button>
                  ))}
                </div>
                {openFindingGroups.has(group.key) ? (
                  <div className="mt-3 space-y-1 border-t border-[color:var(--bg-border)] pt-3">
                    {group.findings.map((finding) => <code className="block overflow-x-auto whitespace-nowrap rounded bg-black/30 px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={`${group.key}-all-${finding.step}`}>Step {finding.step}: {finding.command}</code>)}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        ) : <p className="mt-3 text-sm text-[color:var(--text-secondary)]">No command or policy event matched the danger classifier.</p>}
      </section>

      <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <h3 className="text-sm font-medium text-[color:var(--text-primary)]">Files touched</h3>
        {skillDocsRead && loaded === 0 ? <p className="mt-2 text-xs text-amber-200">The agent read skill docs as normal files, but did not load them as agent context, so skill coverage remains 0.</p> : null}
        <div className="mt-3 space-y-2">
          {Object.entries(dirs).map(([dir, files]) => {
            const open = openDirs.has(dir);
            return (
              <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)]" key={dir}>
                <button className="flex w-full items-center justify-between px-3 py-2 text-left text-sm font-medium text-[color:var(--text-primary)]" onClick={() => setOpenDirs((current) => { const next = new Set(current); next.has(dir) ? next.delete(dir) : next.add(dir); return next; })} type="button"><span>{dir}</span><ChevronDown className={`h-4 w-4 transition-transform ${open ? "rotate-180" : ""}`} /></button>
                {open ? <div className="divide-y divide-[color:var(--bg-border)]">{files.map((file) => {
                  const marker = sensitiveFileMarker(file.path);
                  return <div className="grid gap-2 px-3 py-2 text-xs md:grid-cols-[1fr_auto_auto]" key={file.path}><code className="truncate text-[color:var(--text-secondary)]">{file.path.split("/").pop()}</code><span className={file.wrote ? "text-amber-200" : "text-[color:var(--text-tertiary)]"}>{file.wrote ? "wrote" : "read"}</span><span className="text-[color:var(--text-tertiary)]">steps {file.steps.join(", ")}</span>{marker ? <span className={marker === "sensitive" ? "text-red-200" : "text-[color:var(--accent-primary)]"}>{marker}</span> : null}</div>;
                })}</div> : null}
              </div>
            );
          })}
        </div>
      </section>

      <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <h3 className="text-sm font-medium text-[color:var(--text-primary)]">Shell commands</h3>
        {commandRows.length ? <div className="mt-3 overflow-hidden rounded-md border border-[color:var(--bg-border)] font-mono text-xs">{visibleCommands.map((row) => <button className={`grid w-full grid-cols-[64px_1fr] gap-3 border-b border-[color:var(--bg-border)] px-3 py-2 text-left last:border-b-0 ${row.findings.length ? "bg-red-500/10 text-red-100" : "bg-[color:var(--bg-base)] text-[color:var(--text-secondary)]"}`} key={`${row.step}-${row.command}`} onClick={() => onSelect(row.step - 1)} type="button"><span className="inline-flex items-center gap-1">{row.findings.length ? <Flag className="h-3 w-3" /> : "#"} {row.step}</span><span className="break-all">{row.command}</span></button>)}</div> : <p className="mt-2 text-sm text-[color:var(--text-secondary)]">No shell commands captured.</p>}
        {commandRows.length > 8 ? <button className="mt-3 text-sm font-medium text-[color:var(--accent-primary)]" onClick={() => setShowAllCommands((value) => !value)} type="button">{showAllCommands ? "Show fewer" : `Show ${commandRows.length - 8} more`}</button> : null}
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4"><h3 className="text-sm font-medium text-[color:var(--text-primary)]">Searches</h3>{searches.length ? <ul className="mt-3 space-y-2 text-xs text-[color:var(--text-secondary)]">{[...new Set(searches)].map((item) => <li className="break-all font-mono" key={item}>{item}</li>)}</ul> : <p className="mt-2 text-sm text-[color:var(--text-secondary)]">0 searches captured.</p>}</div>
        <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4"><h3 className="text-sm font-medium text-[color:var(--text-primary)]">Network calls</h3>{networkCalls.length ? <ul className="mt-3 space-y-2 text-xs text-[color:var(--text-secondary)]">{networkCalls.map((item, index) => <li key={`${item.domain}-${index}`}>{[item.provider, item.domain, item.category].filter(Boolean).join(" / ")} · {item.count}</li>)}</ul> : <p className="mt-2 text-sm text-[color:var(--text-secondary)]">0 — no outbound network.</p>}</div>
      </section>
    </section>
  );
}

export function ReplayClient({ exportHtml, session, timeline }: { exportHtml: string; session: ActivitySession; timeline: ReplayStep[] }) {
  const [index, setIndex] = useState(0);
  const [copied, setCopied] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const typedSession = session as ActivitySessionV2;
  const typedTimeline = timeline as ReplayStepV2[];
  const activeIndex = Math.min(index, Math.max(0, typedTimeline.length - 1));
  const active = typedTimeline[activeIndex];
  const activeFindings = active ? findingsForStep(active, activeIndex) : [];
  const exportHref = useMemo(() => `data:text/html;charset=utf-8,${encodeURIComponent(exportHtml)}`, [exportHtml]);
  const contributors = useMemo(() => parseRiskContributors(typedSession, typedTimeline), [typedSession, typedTimeline]);
  const facts = useMemo(() => verdictFacts(typedSession, typedTimeline), [typedSession, typedTimeline]);

  if (!active) {
    return <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8 text-sm text-[color:var(--text-secondary)]">No replay timeline is available for this session.</div>;
  }

  const markerPosition = `clamp(3px, ${Math.min(100, Math.max(0, typedSession.risk_score))}%, calc(100% - 3px))`;

  return (
    <section className="space-y-5">
      <header className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="text-[11px] font-medium uppercase tracking-widest text-[color:var(--text-tertiary)]">{typedSession.agent_provider}</div>
            <h2 className="mt-1 text-xl font-medium text-[color:var(--text-primary)]">{typedSession.agent} - {typedSession.repo_name}</h2>
            <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-[color:var(--text-secondary)]">
              <button
                className="inline-flex max-w-full items-center gap-2 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-2 py-1 font-mono text-xs text-[color:var(--text-primary)]"
                onClick={async () => {
                  await navigator.clipboard?.writeText(typedSession.session_id);
                  setCopied(true);
                  window.setTimeout(() => setCopied(false), 1400);
                }}
                title={typedSession.session_id}
                type="button"
              >
                <Copy className="h-3.5 w-3.5 text-[color:var(--accent-primary)]" />
                <span className="truncate">{compactId(typedSession.session_id)}</span>
              </button>
              <span>{copied ? "Copied" : "Run id"}</span>
            </div>
            <p className="mt-3 text-sm text-[color:var(--text-secondary)]">
              {typedSession.model || "model unknown"} / {humanize(typedSession.intelligence_tier || typedSession.permission_profile || "tier unknown")} - {(typedSession.tokens_total ?? 0).toLocaleString()} tokens - ${(typedSession.cost_usd ?? 0).toFixed(2)} - {durationLabel(typedSession, typedTimeline)} - {humanize(typedSession.outcome)}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="inline-flex items-center rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-medium text-[color:var(--bg-base)]" type="button">Acknowledge run</button>
            <button className="inline-flex items-center rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm font-medium text-[color:var(--text-primary)]" type="button">Create policy rule</button>
            <a className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm font-medium text-[color:var(--text-primary)]" download={`skillayer-replay-${typedSession.session_id}.html`} href={exportHref}>
              <Download className="h-4 w-4" />
              Export
            </a>
          </div>
        </div>
      </header>

      <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 text-[11px] font-medium uppercase tracking-widest text-[color:var(--text-tertiary)]">
              <ShieldCheck className="h-4 w-4 text-[color:var(--accent-primary)]" />
              Risk verdict
            </div>
            <h3 className="mt-2 text-2xl font-medium text-[color:var(--text-primary)]">{bandText(typedSession.risk_band)} - {typedSession.risk_score}/100</h3>
          </div>
          <span className={`rounded-md border px-3 py-1.5 text-sm font-medium ${bandTone(typedSession.risk_band)}`}>{humanize(typedSession.risk_band)} band</span>
        </div>

        <div className="mt-5">
          <div className="relative h-3 rounded-full bg-[linear-gradient(90deg,var(--accent-green)_0%,var(--accent-green)_33%,#f59e0b_33%,#f59e0b_66%,#ef4444_66%,#ef4444_100%)]">
            <div className="absolute top-1/2 h-6 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white shadow-[0_0_0_3px_rgba(0,0,0,0.45)]" style={{ left: markerPosition }} />
          </div>
          <div className="mt-2 flex justify-between text-[11px] font-medium uppercase tracking-wide text-[color:var(--text-tertiary)]">
            <span>Low</span>
            <span>Medium</span>
            <span>High</span>
          </div>
        </div>

        <div className="mt-6 grid items-start gap-5 lg:grid-cols-[minmax(0,1.15fr)_minmax(280px,0.85fr)]">
          <div className="space-y-3">
            {contributors.map((item) => {
              const width = `${Math.min(100, Math.max(4, item.value))}%`;
              return (
                <div key={`${item.label}-${item.value}`}>
                  <div className="mb-1 flex justify-between gap-3 text-sm">
                    <span className="font-medium text-[color:var(--text-primary)]">{humanize(item.label)}</span>
                    <span className="text-[color:var(--text-tertiary)]">{Math.round(item.value)}</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/10"><div className="h-2 rounded-full bg-[color:var(--accent-primary)]" style={{ width }} /></div>
                </div>
              );
            })}
          </div>
          <div className="h-fit rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
            <h4 className="text-sm font-medium text-[color:var(--text-primary)]">Verdict facts</h4>
            <ul className="mt-3 space-y-2 text-sm leading-5 text-[color:var(--text-secondary)]">
              {facts.map((fact) => <li key={fact}>{fact}</li>)}
            </ul>
            <div className="mt-4 border-t border-[color:var(--bg-border)] pt-4">
              <div className="text-[11px] font-medium uppercase tracking-widest text-[color:var(--text-tertiary)]">Recommended action</div>
              <p className="mt-2 text-sm leading-5 text-[color:var(--text-primary)]">{recommendedAction(typedSession, typedTimeline)}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.55fr)_minmax(360px,0.85fr)]">
        <ReplayFlowchart
          activeIndex={activeIndex}
          expanded={expandedNodes}
          onSelect={setIndex}
          onToggleExpand={(id) => setExpandedNodes((current) => {
            const next = new Set(current);
            next.has(id) ? next.delete(id) : next.add(id);
            return next;
          })}
          timeline={typedTimeline}
        />
        <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="text-xs text-[color:var(--text-tertiary)]">{formatTime(active.timestamp)}</div>
              <h3 className="mt-1 text-xl font-medium text-[color:var(--text-primary)]">{stepTitle(active)}</h3>
              <p className="mt-2 truncate text-sm text-[color:var(--text-secondary)]">{detailTarget(active)}</p>
            </div>
            <div className="flex items-center gap-2">
              <button className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-[color:var(--bg-border)] text-[color:var(--text-primary)] disabled:opacity-40" disabled={activeIndex === 0} onClick={() => setIndex((value) => Math.max(0, value - 1))} type="button">
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-xs text-[color:var(--text-tertiary)]">Step {activeIndex + 1} of {typedTimeline.length}</span>
              <button className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-[color:var(--bg-border)] text-[color:var(--text-primary)] disabled:opacity-40" disabled={activeIndex === typedTimeline.length - 1} onClick={() => setIndex((value) => Math.min(typedTimeline.length - 1, value + 1))} type="button">
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-medium uppercase tracking-widest text-[color:var(--text-tertiary)]">Policy</div>
              <div className="mt-2 text-sm capitalize text-[color:var(--text-primary)]">{humanize(active.policy_decision)}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-medium uppercase tracking-widest text-[color:var(--text-tertiary)]">Action</div>
              <div className="mt-2 text-sm capitalize text-[color:var(--text-primary)]">{humanize(active.action_class || active.type)}</div>
            </div>
            <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <div className="text-[11px] font-medium uppercase tracking-widest text-[color:var(--text-tertiary)]">Result</div>
              <div className="mt-2 truncate text-sm text-[color:var(--text-primary)]">{readableValue(active.result) || humanize(typedSession.outcome)}</div>
            </div>
          </div>
          <div className="mt-3 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
            <div className="text-[11px] font-medium uppercase tracking-widest text-[color:var(--text-tertiary)]">Risk score</div>
            <div className={`mt-2 inline-flex rounded-md border px-2 py-1 text-sm font-medium ${bandTone(active.risk_band)}`}>{bandText(active.risk_band)} - {active.risk_score}</div>
          </div>
          {activeFindings.length ? (
            <div className="mt-4 rounded-md border border-red-500/40 bg-red-500/10 p-4">
              <div className="inline-flex items-center gap-2 text-sm font-medium text-red-100">
                <AlertTriangle className="h-4 w-4" />
                Flagged step
              </div>
              <div className="mt-3 space-y-2">
                {activeFindings.map((finding) => (
                  <p className="text-sm leading-5 text-red-100" key={`${finding.severity}-${finding.title}`}>
                    <span className="capitalize">{finding.severity}</span> · {finding.title}: {finding.reason}
                  </p>
                ))}
              </div>
            </div>
          ) : null}
          {active.reasoning ? <p className="mt-4 text-sm leading-6 text-[color:var(--text-secondary)]">{active.reasoning}</p> : null}
          {active.file_diff ? <pre className="mt-4 max-h-[360px] overflow-auto whitespace-pre-wrap rounded-md bg-black/30 p-4 text-xs leading-5 text-[color:var(--text-secondary)]">{active.file_diff}</pre> : null}
          {!active.file_diff ? <div className="mt-4 overflow-x-auto rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 font-mono text-xs text-[color:var(--text-secondary)]">{detailTarget(active)}</div> : null}
        </article>
      </section>

      <EvidenceTriage onSelect={setIndex} session={typedSession} timeline={typedTimeline} />
    </section>
  );
}
