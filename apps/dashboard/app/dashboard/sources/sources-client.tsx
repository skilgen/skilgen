"use client";

import { CheckCircle2, Clipboard, Database, FileJson, GitBranch, Server, X } from "lucide-react";
import { useEffect, useState } from "react";
import Link from "next/link";

import type { SourceConnection } from "../../../lib/data";
import { CodebaseSkillMap } from "./codebase-skill-map";
import { SkillFinder } from "./skill-finder";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

const sourceCatalog = [
  ["openapi", "OpenAPI", "API endpoint patterns, request/response", "skilgen analyse --source openapi --file openapi.yaml", FileJson],
  ["database", "PostgreSQL", "Table schemas, query patterns, naming", "skilgen analyse --source sql-schema --file schema.sql", Database],
  ["terraform", "Terraform", "Infrastructure patterns, resource naming", "skilgen analyse --source terraform --dir infra/", Server],
  ["kubernetes", "Kubernetes", "Deployment patterns, resource limits", "skilgen analyse --source kubernetes --dir k8s/", Server],
  ["confluence", "Confluence", "Team docs, runbooks, decision records", "skilgen analyse --source confluence --space TEAM", Clipboard],
  ["dbt", "dbt", "Data model conventions, metric definitions", "skilgen analyse --source dbt --dir models/", Database],
  ["pagerduty", "PagerDuty", "Incident patterns, runbooks, escalation", "skilgen analyse --source pagerduty", Server],
  ["sarif", "SARIF", "Security scan results to security rules", "skilgen analyse --source sarif --file results.sarif", FileJson],
] as const;

function relative(value: string | null): string {
  if (!value) return "Never";
  const diff = Date.now() - new Date(value).getTime();
  if (!Number.isFinite(diff)) return "Unknown";
  const hours = Math.max(1, Math.round(diff / 3600000));
  if (hours < 24) return `${hours} hours ago`;
  return `${Math.round(hours / 24)} days ago`;
}

function isConnectable(id: string) {
  return ["database", "openapi", "confluence", "terraform"].includes(id);
}

function ConnectionModal({ accessToken, orgId, sourceType, onClose }: { accessToken: string; orgId: string; sourceType: string; onClose: () => void }) {
  const [params, setParams] = useState<Record<string, string>>({ port: sourceType === "database" ? "5432" : "", ssl_mode: "require", branch: "main", directory: "infra/" });
  const [result, setResult] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const fields = sourceType === "database"
    ? [["host", "Host"], ["port", "Port"], ["database", "Database name"], ["username", "Username"], ["password", "Password"], ["ssl_mode", "SSL mode"]]
    : sourceType === "openapi"
      ? [["spec_url", "Spec URL"]]
      : sourceType === "confluence"
        ? [["url", "Confluence URL"], ["space", "Space key"], ["email", "Email"], ["api_token", "API token"]]
        : [["git_url", "Git repo URL"], ["branch", "Branch"], ["directory", "Directory path"]];

  async function test() {
    setBusy(true);
    const response = await fetch(`${API_URL}/orgs/${orgId}/sources/test`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` }, body: JSON.stringify({ source_type: sourceType, connection_params: params }) }).then((res) => res.json()).catch((error) => ({ success: false, error: String(error) }));
    setResult(response.success ? `✓ Connected - ${response.metadata?.table_count ?? response.metadata?.endpoint_count ?? "preview"} found. Generate skill?` : `Failed: ${response.error ?? "Could not connect"}`);
    setBusy(false);
  }

  async function connect() {
    setBusy(true);
    const response = await fetch(`${API_URL}/orgs/${orgId}/sources/connect`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` }, body: JSON.stringify({ source_type: sourceType, connection_params: params, repo_id: params.repo_id || "", domain: sourceType === "database" ? "data_schema" : sourceType === "openapi" ? "internal_tools" : "operational_knowledge" }) }).then((res) => res.json()).catch((error) => ({ error: String(error) }));
    setResult(response.skill_id ? `✓ Skill generated: ${response.domain}` : `Failed: ${response.error ?? response.detail ?? "Could not generate skill"}`);
    setBusy(false);
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4">
      <div className="w-full max-w-2xl rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="flex items-center justify-between"><h2 className="text-lg font-semibold">Connect {sourceType}</h2><button onClick={onClose} type="button"><X className="h-4 w-4" /></button></div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {fields.map(([key, label]) => <label className="text-sm" key={key}>{label}<input className="mt-1 w-full rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-2" type={key.includes("password") || key.includes("token") ? "password" : "text"} value={params[key] ?? ""} onChange={(event) => setParams((current) => ({ ...current, [key]: event.target.value }))} /></label>)}
        </div>
        {result ? <div className={`mt-4 rounded-lg border p-3 text-sm ${result.startsWith("✓") ? "border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : "border-red-500/30 bg-red-500/10 text-red-200"}`}>{result}</div> : null}
        <div className="mt-5 flex justify-end gap-3"><button className="rounded-md border border-[color:var(--bg-border)] px-4 py-2 text-sm" disabled={busy} onClick={test} type="button">Test connection</button><button className="rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-black" disabled={busy} onClick={connect} type="button">Generate skill</button></div>
      </div>
    </div>
  );
}

export function SourcesClient({ accessToken, initialTab, orgId, sources }: { accessToken: string; initialTab: "connected" | "finder"; orgId: string; sources: SourceConnection[] }) {
  const [tab, setTab] = useState<"connected" | "finder">(initialTab);
  const [showExplainer, setShowExplainer] = useState(false);
  const [expandedSource, setExpandedSource] = useState<string | null>(null);
  const [connectSource, setConnectSource] = useState<string | null>(null);
  const [enterpriseModal, setEnterpriseModal] = useState(false);
  const [enterpriseForm, setEnterpriseForm] = useState({ name: "", domain: "security_compliance", content: "" });
  const [enterpriseStatus, setEnterpriseStatus] = useState("");
  useEffect(() => setShowExplainer(localStorage.getItem("skillayer_sources_explainer") !== "dismissed"), []);
  const connected = sources.filter((source) => source.connected);
  const byType = new Map(sources.map((source) => [source.source_type, source]));

  function dismiss() {
    localStorage.setItem("skillayer_sources_explainer", "dismissed");
    setShowExplainer(false);
  }

  async function copy(command: string) {
    await navigator.clipboard.writeText(command);
  }

  async function createEnterpriseSkill() {
    const response = await fetch(`${API_URL}/orgs/${orgId}/enterprise-skills`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` }, body: JSON.stringify({ name: enterpriseForm.name, domain: enterpriseForm.domain, content: enterpriseForm.content, applies_to: "all" }) }).then((res) => res.json()).catch((error) => ({ detail: String(error) }));
    setEnterpriseStatus(Array.isArray(response) ? `✓ Created across ${response.length} repos` : `Failed: ${response.detail ?? "Could not create enterprise skill"}`);
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap gap-2 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-1">
        <button className={tab === "connected" ? "rounded-lg bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-black" : "rounded-lg px-4 py-2 text-sm font-semibold text-[color:var(--text-secondary)]"} onClick={() => setTab("connected")} type="button">Connected Sources</button>
        <button className={tab === "finder" ? "rounded-lg bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-black" : "rounded-lg px-4 py-2 text-sm font-semibold text-[color:var(--text-secondary)]"} onClick={() => setTab("finder")} type="button">What skill do I need? ←</button>
      </div>
      {tab === "finder" ? <SkillFinder /> : (
        <>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold">Enterprise Skills</h2>
            <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Skills that apply to every repo in your organisation - loaded by all agents automatically.</p>
          </div>
          <button className="rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-black" onClick={() => setEnterpriseModal(true)} type="button">+ Add enterprise skill</button>
        </div>
        <div className="mt-4 rounded-lg border border-dashed border-[color:var(--bg-border)] p-5 text-sm text-[color:var(--text-secondary)]">No enterprise skills yet. Add a security policy, compliance requirement, brand voice, or privacy rule that applies to every codebase.</div>
      </section>

      {showExplainer ? (
        <section className="rounded-xl border border-[color:var(--accent-primary)]/30 bg-[color:var(--accent-primary)]/10 p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">Sources → Skills → Better Code</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-[color:var(--text-secondary)]">Connect a data source and Skillayer generates a SKILL.md from it. Your agents load that skill and write code that matches your actual schema, APIs, and conventions.</p>
            </div>
            <button className="inline-flex items-center gap-1 rounded-md border border-[color:var(--bg-border)] px-3 py-1.5 text-xs font-semibold text-[color:var(--text-secondary)]" onClick={dismiss} type="button">Got it <X className="h-3.5 w-3.5" /></button>
          </div>
        </section>
      ) : null}

      <section>
        <h2 className="mb-4 text-lg font-semibold">Connected sources</h2>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {(connected.length ? connected : sources.slice(0, 3)).map((source) => (
            <article className={`rounded-xl border p-5 ${source.connected ? "border-[color:var(--accent-green)]/35 bg-[rgb(var(--accent-green-rgb)/0.08)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]"}`} key={source.id}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <GitBranch className="h-5 w-5 text-[color:var(--accent-primary)]" />
                  <h3 className="font-semibold text-[color:var(--text-primary)]">{source.display_name.split(" · ")[0]}</h3>
                </div>
                <span className={source.connected ? "inline-flex items-center gap-1 rounded-full bg-[color:var(--accent-green)]/15 px-2 py-1 text-xs font-semibold text-[color:var(--accent-green)]" : "rounded-full bg-white/5 px-2 py-1 text-xs font-semibold text-[color:var(--text-tertiary)]"}>
                  {source.connected ? <CheckCircle2 className="h-3.5 w-3.5" /> : null}
                  {source.connected ? "Connected" : "Not connected"}
                </span>
              </div>
              <p className="mt-3 text-sm text-[color:var(--text-secondary)]">{source.display_name.split(" · ").slice(1).join(" · ") || "Ready to connect"}</p>
              <p className="mt-3 text-sm text-[color:var(--text-secondary)]">{source.skill_count} skills generated · Last: {relative(source.last_skill_generated_at)}</p>
              <div className="mt-3 flex flex-wrap gap-2">{source.coverage_domains.slice(0, 5).map((domain) => <span className="rounded-full bg-black/20 px-2 py-1 text-xs text-[color:var(--text-secondary)]" key={domain}>{domain}</span>)}</div>
              <button className="mt-5 text-sm font-semibold text-[color:var(--accent-primary)]" onClick={() => source.source_type === "code" || source.source_type === "github" ? setExpandedSource(expandedSource === source.id ? null : source.id) : undefined} type="button">{source.source_type === "code" || source.source_type === "github" ? "Explore skills →" : source.connected ? "Regenerate skills →" : "Connect →"}</button>
              {expandedSource === source.id && source.repo_id ? <div className="mt-5"><CodebaseSkillMap repoId={source.repo_id} repoName={source.display_name.split(" · ").slice(1).join(" · ") || "Codebase"} /></div> : null}
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold">Add a source</h2>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {sourceCatalog.map(([id, name, description, command, Icon]) => {
            const existing = byType.get(id);
            return (
              <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={id}>
                <Icon className="h-5 w-5 text-[color:var(--accent-primary)]" />
                <h3 className="mt-3 font-semibold">{name}</h3>
                <p className="mt-2 min-h-10 text-sm text-[color:var(--text-secondary)]">{description}</p>
                {isConnectable(id) ? <button className="mt-4 rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-xs font-semibold text-black" onClick={() => setConnectSource(id)} type="button">Connect</button> : <>
                  <Link className="mt-4 block text-xs font-semibold text-[color:var(--accent-primary)]" href="/dashboard/repos">Or connect via GitHub integration →</Link>
                  <code className="mt-3 block rounded-md bg-[color:var(--bg-base)] p-3 text-xs leading-5 text-[color:var(--text-tertiary)]">{existing?.generate_command ?? command}</code>
                  <button className="mt-3 inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs font-semibold" onClick={() => void copy(existing?.generate_command ?? command)} type="button">
                    <Clipboard className="h-3.5 w-3.5" />
                    Copy command
                  </button>
                </>}
              </article>
            );
          })}
        </div>
      </section>
        </>
      )}
      {connectSource ? <ConnectionModal accessToken={accessToken} orgId={orgId} sourceType={connectSource} onClose={() => setConnectSource(null)} /> : null}
      {enterpriseModal ? <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"><div className="w-full max-w-2xl rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5"><div className="flex items-center justify-between"><h2 className="text-lg font-semibold">Add enterprise skill</h2><button onClick={() => setEnterpriseModal(false)} type="button"><X className="h-4 w-4" /></button></div><div className="mt-4 grid gap-3"><input className="rounded-md bg-[color:var(--bg-base)] p-2" placeholder="Name, e.g. Security Policy" value={enterpriseForm.name} onChange={(event) => setEnterpriseForm((current) => ({ ...current, name: event.target.value }))} /><select className="rounded-md bg-[color:var(--bg-base)] p-2" value={enterpriseForm.domain} onChange={(event) => setEnterpriseForm((current) => ({ ...current, domain: event.target.value }))}><option>security_compliance</option><option>data_schema</option><option>operational_knowledge</option><option>code_style</option><option>custom</option></select><textarea className="min-h-48 rounded-md bg-[color:var(--bg-base)] p-3 font-mono text-sm" placeholder="# Skill content in Markdown" value={enterpriseForm.content} onChange={(event) => setEnterpriseForm((current) => ({ ...current, content: event.target.value }))} /><div className="rounded-md bg-black/20 p-3 text-sm text-[color:var(--text-secondary)]">Apply to: All repos</div></div>{enterpriseStatus ? <div className="mt-3 rounded-md border border-[color:var(--bg-border)] p-3 text-sm">{enterpriseStatus}</div> : null}<div className="mt-5 flex justify-end"><button className="rounded-md bg-[color:var(--accent-primary)] px-4 py-2 text-sm font-semibold text-black" onClick={() => void createEnterpriseSkill()} type="button">Create enterprise skill</button></div></div></div> : null}
    </div>
  );
}
