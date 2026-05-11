import { Bot, DatabaseZap, GitBranch, PlugZap, ShieldCheck, Siren, Workflow } from "lucide-react";
import { revalidatePath } from "next/cache";

import { EmptyPanel, Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";
import { API_URL } from "../../../../lib/data";

type Connector = {
  id: string;
  label: string;
  category: string;
  status: string;
  connected: boolean;
  description?: string | null;
  capabilities?: string[];
  connection_status?: string | null;
};

type AgentComplianceSyncPlan = {
  connector_id: string;
  status: "pending";
  mode: "dry-run";
  cursor?: string | null;
  next_cursor_required: boolean;
  provider_adapter_required: boolean;
  pagination_strategy: string;
  retention_window_days: number;
  retention_deadline_at: string;
  content_retention: "metadata-only";
  source_record_type: "formal-compliance" | "operational-telemetry";
  ready_for_provider_pull: boolean;
  blocked_reason: string;
  next_actions: string[];
};

type AgentComplianceConnector = Connector & {
  configured: boolean;
  enabled: boolean;
  source_types: string[];
  scopes: string[];
  last_cursor?: string | null;
  last_sync_status?: string | null;
  last_sync_requested_at?: string | null;
  last_sync_mode?: string | null;
  last_sync_plan?: AgentComplianceSyncPlan | null;
  last_ingest_job?: {
    job_id: string;
    status: string;
    event_count: number;
    cursor?: string | null;
    next_cursor?: string | null;
    content_retention: "metadata-only";
    queued_at?: string | null;
  } | null;
  last_ingested_at?: string | null;
  last_ingested_count: number;
  total_ingested_count: number;
  last_provider_event_id?: string | null;
  content_retention: "metadata-only" | "tenant-enabled-content";
  updated_at?: string | null;
};

type AgentCompliancePayload = {
  content_retention_default: "metadata-only";
  configured_count: number;
  enabled_count: number;
  connectors: AgentComplianceConnector[];
};

const fallbackConnectors: Connector[] = [
  {
    id: "openai-compliance",
    label: "OpenAI Compliance Platform",
    category: "compliance-telemetry",
    status: "planned",
    connected: false,
    description: "ChatGPT Enterprise/Edu compliance logs and metadata for audit, DLP, SIEM, and eDiscovery workflows.",
    capabilities: ["audit logs", "chat metadata", "user activity", "model usage"],
  },
  {
    id: "anthropic-compliance",
    label: "Anthropic Compliance API",
    category: "compliance-telemetry",
    status: "planned",
    connected: false,
    description: "Claude Enterprise compliance activity, chat data, file content, and audit log records where the tenant has API access.",
    capabilities: ["audit logs", "chat data", "file content", "user activity"],
  },
  {
    id: "claude-cowork-otel",
    label: "Claude Cowork OpenTelemetry",
    category: "compliance-telemetry",
    status: "planned",
    connected: false,
    description: "Real-time Cowork telemetry for prompts, tool/MCP calls, file access, approvals, model usage, and errors.",
    capabilities: ["prompts", "tool calls", "file access", "approval decisions"],
  },
  {
    id: "claude-code",
    label: "Claude Code",
    category: "coding-agent",
    status: "planned",
    connected: false,
    description: "Coding-agent activity, tool use, file access, skills, and permission decisions from Claude Code hooks or supported telemetry.",
    capabilities: ["agent sessions", "tool calls", "file access", "permission decisions"],
  },
  {
    id: "codex-cli",
    label: "Codex CLI",
    category: "coding-agent",
    status: "planned",
    connected: false,
    description: "Codex CLI sessions, model/intelligence tier, command/tool access, file access, and approval decisions from local hooks.",
    capabilities: ["agent sessions", "model tier", "tool access", "file access"],
  },
  {
    id: "cursor",
    label: "Cursor",
    category: "coding-agent",
    status: "planned",
    connected: false,
    description: "Cursor agent usage, full-access grants, model tier, tool calls, and workspace/repo activity where enterprise telemetry is available.",
    capabilities: ["agent sessions", "model tier", "full-access grants", "repo activity"],
  },
  {
    id: "windsurf",
    label: "Windsurf",
    category: "coding-agent",
    status: "planned",
    connected: false,
    description: "Windsurf/Cascade coding-agent sessions, model tier, workspace actions, terminal/tool use, and file-target metadata where enterprise telemetry is available.",
    capabilities: ["agent sessions", "model tier", "tool calls", "file access", "repo activity"],
  },
  {
    id: "aider",
    label: "Aider",
    category: "coding-agent",
    status: "planned",
    connected: false,
    description: "Aider coding sessions, repository targets, model usage, git changes, and shell/tool activity from local or enterprise telemetry hooks.",
    capabilities: ["agent sessions", "model usage", "git changes", "shell access", "file access"],
  },
  {
    id: "github-copilot",
    label: "GitHub Copilot",
    category: "coding-agent",
    status: "planned",
    connected: false,
    description: "GitHub Copilot Business/Enterprise coding-agent and chat activity with organization, repo, model, policy, seat, and usage metadata.",
    capabilities: ["agent sessions", "chat activity", "repo activity", "policy metadata", "model usage"],
  },
  {
    id: "gitlab-duo",
    label: "GitLab Duo",
    category: "coding-agent",
    status: "planned",
    connected: false,
    description: "GitLab Duo assistant activity, project targets, model usage, merge-request context, and policy metadata from GitLab telemetry or audit exports.",
    capabilities: ["agent sessions", "project activity", "merge requests", "policy metadata", "model usage"],
  },
  {
    id: "internal-mcp",
    label: "Internal MCP servers",
    category: "runtime",
    status: "planned",
    connected: false,
    description: "Internal MCP server calls, tool names, resource scopes, approval decisions, latency, and error metadata for agent runtime governance.",
    capabilities: ["mcp calls", "tool access", "resource scopes", "approval decisions", "latency"],
  },
  {
    id: "github",
    label: "GitHub",
    category: "source-control",
    status: "available",
    connected: false,
    description: "Source-control activity, pull requests, repository metadata, and delivery evidence for governed engineering work.",
    capabilities: ["repositories", "pull requests", "source evidence"],
  },
  {
    id: "pagerduty",
    label: "PagerDuty",
    category: "incident",
    status: "available",
    connected: false,
    description: "Incident response evidence for operational timelines, on-call ownership, and escalation review.",
    capabilities: ["incidents", "escalations", "response audit"],
  },
  {
    id: "s3-worm",
    label: "S3 Object Lock",
    category: "worm-store",
    status: "planned",
    connected: false,
    description: "Immutable evidence retention target for long-term audit records and export packages.",
    capabilities: ["immutable storage", "retention", "audit export"],
  },
  {
    id: "sigstore",
    label: "Sigstore",
    category: "provenance",
    status: "planned",
    connected: false,
    description: "Provenance and signing evidence for build attestations, releases, and policy review.",
    capabilities: ["attestations", "signatures", "release evidence"],
  },
];

const categoryMeta = {
  "compliance-telemetry": {
    title: "Compliance Telemetry",
    detail: "Provider compliance logs, agent telemetry, and model-use evidence.",
    icon: ShieldCheck,
  },
  "coding-agent": {
    title: "Coding Agents",
    detail: "Agent sessions, tool access, file access, and approval decisions.",
    icon: Bot,
  },
  "source-control": {
    title: "Source Control",
    detail: "Repository activity and delivery evidence.",
    icon: GitBranch,
  },
  runtime: {
    title: "Runtime",
    detail: "Internal MCP and runtime integration surfaces.",
    icon: Workflow,
  },
  "work-management": {
    title: "Work Management",
    detail: "Issue, ticket, and planning context.",
    icon: Workflow,
  },
  notifications: {
    title: "Notifications",
    detail: "Chat and notification routing.",
    icon: PlugZap,
  },
  incident: {
    title: "Incident",
    detail: "On-call and response evidence.",
    icon: Siren,
  },
  siem: {
    title: "SIEM",
    detail: "Security analytics exports and event forwarding.",
    icon: DatabaseZap,
  },
  "worm-store": {
    title: "WORM Storage",
    detail: "Immutable evidence retention targets.",
    icon: DatabaseZap,
  },
  provenance: {
    title: "Provenance",
    detail: "Signing and attestation evidence.",
    icon: ShieldCheck,
  },
} as const;

const categoryOrder = [
  "compliance-telemetry",
  "coding-agent",
  "source-control",
  "runtime",
  "work-management",
  "notifications",
  "incident",
  "siem",
  "worm-store",
  "provenance",
];

function statusLabel(connector: Connector, isFallback: boolean) {
  if (connector.connected) {
    return connector.connection_status ?? "Connected";
  }
  if (isFallback) {
    return connector.status === "available" ? "Available" : "Planned";
  }
  return connector.status;
}

function statusClass(connector: Connector) {
  if (connector.connected) {
    return "bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]";
  }
  if (connector.status === "available") {
    return "bg-[color:var(--accent-primary)]/15 text-[color:var(--accent-primary)]";
  }
  return "bg-[color:var(--bg-base)] text-[color:var(--text-tertiary)]";
}

async function configureAgentComplianceConnector(formData: FormData) {
  "use server";

  const connectorId = String(formData.get("connector_id") ?? "");
  if (!connectorId) return;
  const { accessToken, org } = await loadSettingsContext();
  if (!accessToken) return;

  const response = await fetch(`${API_URL}/v8/orgs/${org.id}/settings/connectors/agent-compliance`, {
    body: JSON.stringify({
      connector_id: connectorId,
      enabled: true,
      source_types: String(formData.get("source_types") ?? "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      scopes: String(formData.get("scopes") ?? "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      content_retention: "metadata-only",
      last_sync_status: "pending",
    }),
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    method: "POST",
  });

  if (response.ok) {
    revalidatePath("/settings/connectors");
  }
}

async function requestAgentComplianceSync(formData: FormData) {
  "use server";

  const connectorId = String(formData.get("connector_id") ?? "");
  if (!connectorId) return;
  const { accessToken, org } = await loadSettingsContext();
  if (!accessToken) return;

  const response = await fetch(`${API_URL}/v8/orgs/${org.id}/settings/connectors/${encodeURIComponent(connectorId)}/sync`, {
    body: JSON.stringify({
      cursor: String(formData.get("cursor") ?? "") || null,
      dry_run: true,
    }),
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    method: "POST",
  });

  if (response.ok) {
    revalidatePath("/settings/connectors");
  }
}

async function queueAgentComplianceIngestJob(formData: FormData) {
  "use server";

  const connectorId = String(formData.get("connector_id") ?? "");
  if (!connectorId) return;
  const { accessToken, org } = await loadSettingsContext();
  if (!accessToken) return;

  const response = await fetch(`${API_URL}/v8/orgs/${org.id}/settings/connectors/${encodeURIComponent(connectorId)}/ingest-jobs`, {
    body: JSON.stringify({
      cursor: String(formData.get("cursor") ?? "") || null,
      next_cursor: String(formData.get("next_cursor") ?? "") || null,
      events: [],
    }),
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    method: "POST",
  });

  if (response.ok) {
    revalidatePath("/settings/connectors");
  }
}

export default async function ConnectorsSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const [payload, agentCompliance] = await Promise.all([
    v8Fetch<{ connectors: Connector[] }>(accessToken, org.id, "/connectors"),
    v8Fetch<AgentCompliancePayload>(accessToken, org.id, "/connectors/agent-compliance"),
  ]);
  const showingFallback = payload === null || !payload.connectors.length;
  const connectors = showingFallback ? fallbackConnectors : payload.connectors;
  const agentConnectors = agentCompliance?.connectors ?? fallbackConnectors.filter((connector) => connector.category === "compliance-telemetry" || connector.category === "coding-agent" || connector.id === "internal-mcp").map((connector) => ({
    ...connector,
    configured: false,
    enabled: false,
    source_types: [],
    scopes: [],
    last_cursor: null,
    last_sync_status: null,
    last_sync_requested_at: null,
    last_sync_mode: null,
    last_sync_plan: null,
    last_ingest_job: null,
    last_ingested_at: null,
    last_ingested_count: 0,
    total_ingested_count: 0,
    last_provider_event_id: null,
    content_retention: "metadata-only" as const,
  }));
  const connected = connectors.filter((connector) => connector.connected).length;
  const categories = new Set(connectors.map((connector) => connector.category));
  const available = connectors.filter((connector) => connector.status === "available").length;
  const sections = categoryOrder
    .map((category) => ({
      category,
      connectors: connectors.filter((connector) => connector.category === category),
      meta: categoryMeta[category as keyof typeof categoryMeta],
    }))
    .filter((section) => section.connectors.length);

  return (
    <SettingsShell active="Connectors">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Registry entries" value={connectors.length} sub="Data-driven connector catalog" />
        <Metric label="Connected" value={connected} sub="Backed by existing source connections" />
        <Metric label="Available now" value={available} sub={`${categories.size} categories in the Skillayer catalog`} />
      </div>

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="border-b border-[color:var(--bg-border)] p-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">Agent compliance setup</h2>
              <p className="mt-1 max-w-4xl text-[13px] leading-6 text-[color:var(--text-secondary)]">
                Configure provider compliance-log and coding-agent sources for normalized Audit, Activity, Insights, and Policy metadata. Raw prompts, chat, files, and tool parameters stay metadata-only unless a tenant explicitly enables retention later.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2 text-right">
              <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2">
                <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Configured</div>
                <div className="mt-1 text-lg font-semibold text-[color:var(--text-primary)]">{agentCompliance?.configured_count ?? 0}</div>
              </div>
              <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2">
                <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Retention</div>
                <div className="mt-1 text-sm font-semibold text-[color:var(--accent-primary)]">{agentCompliance?.content_retention_default ?? "metadata-only"}</div>
              </div>
            </div>
          </div>
        </div>
        <div className="grid gap-3 p-4 lg:grid-cols-3">
          {agentConnectors.map((connector) => (
            <article className="flex min-h-[190px] flex-col rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3" key={`agent-${connector.id}`}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-[13px] font-semibold text-[color:var(--text-primary)]">{connector.label}</h3>
                  <p className="mt-1 text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">{connector.category}</p>
                </div>
                <span className={`rounded-full px-2 py-1 text-[11px] font-semibold ${connector.enabled ? "bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]" : "bg-[color:var(--bg-surface)] text-[color:var(--text-tertiary)]"}`}>
                  {connector.enabled ? "Configured" : "Metadata setup"}
                </span>
              </div>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {(connector.source_types.length ? connector.source_types : connector.capabilities?.slice(0, 3) ?? []).map((item) => (
                  <span className="rounded-sm border border-[color:var(--bg-border)] px-2 py-0.5 text-[11px] text-[color:var(--text-secondary)]" key={`${connector.id}-${item}`}>
                    {item}
                  </span>
                ))}
              </div>
              <div className="mt-3 text-[12px] text-[color:var(--text-secondary)]">
                Sync: {connector.last_sync_status ?? "not started"}{connector.last_sync_mode ? ` · ${connector.last_sync_mode}` : ""} · Retention: {connector.content_retention}
              </div>
              {connector.last_sync_plan ? (
                <div className="mt-3 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Sync readiness</span>
                    <span className={`rounded-full px-2 py-1 text-[11px] font-semibold ${connector.last_sync_plan.ready_for_provider_pull ? "bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]" : "bg-amber-500/15 text-amber-100"}`}>
                      {connector.last_sync_plan.ready_for_provider_pull ? "Ready for adapter" : "Setup gap"}
                    </span>
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-[color:var(--text-secondary)]">
                    <span>Pagination: {connector.last_sync_plan.pagination_strategy}</span>
                    <span>Window: {connector.last_sync_plan.retention_window_days}d</span>
                    <span>Record: {connector.last_sync_plan.source_record_type}</span>
                    <span>Cursor: {connector.last_sync_plan.cursor ? "resume" : "first page"}</span>
                  </div>
                  <p className="mt-2 max-h-10 overflow-hidden text-[11px] leading-5 text-[color:var(--text-tertiary)]">{connector.last_sync_plan.blocked_reason}</p>
                </div>
              ) : null}
              <div className="mt-3 grid grid-cols-2 gap-2">
                <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-2 py-2">
                  <div className="text-[10px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Last ingest</div>
                  <div className="mt-1 text-[15px] font-semibold text-[color:var(--text-primary)]">{connector.last_ingested_count}</div>
                </div>
                <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-2 py-2">
                  <div className="text-[10px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Total events</div>
                  <div className="mt-1 text-[15px] font-semibold text-[color:var(--accent-primary)]">{connector.total_ingested_count}</div>
                </div>
              </div>
              {connector.last_provider_event_id ? (
                <p className="mt-2 truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">Last event {connector.last_provider_event_id}</p>
              ) : null}
              {connector.last_ingest_job ? (
                <div className="mt-3 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Ingest job</span>
                    <span className="rounded-full bg-[color:var(--accent-primary)]/15 px-2 py-1 text-[11px] font-semibold text-[color:var(--accent-primary)]">{connector.last_ingest_job.status}</span>
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-[color:var(--text-secondary)]">
                    <span>Events: {connector.last_ingest_job.event_count}</span>
                    <span>Retention: {connector.last_ingest_job.content_retention}</span>
                    <span>Cursor: {connector.last_ingest_job.cursor ? "resume" : "first page"}</span>
                    <span>Next: {connector.last_ingest_job.next_cursor ? "stored" : "pending"}</span>
                  </div>
                  <p className="mt-2 truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{connector.last_ingest_job.job_id}</p>
                </div>
              ) : null}
              <div className="mt-auto grid gap-2 pt-3 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
                <form action={configureAgentComplianceConnector}>
                  <input name="connector_id" type="hidden" value={connector.id} />
                  <input name="source_types" type="hidden" value={(connector.capabilities ?? []).join(",")} />
                  <input name="scopes" type="hidden" value="audit.read,activity.read,insights.read,policy.evaluate" />
                  <button
                    className="inline-flex h-9 w-full items-center justify-center rounded-md border border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-primary)] disabled:cursor-not-allowed disabled:text-[color:var(--text-tertiary)]"
                    disabled={!accessToken}
                    type="submit"
                  >
                    {connector.enabled ? "Update setup" : accessToken ? "Enable setup" : "Sign in"}
                  </button>
                </form>
                <form action={requestAgentComplianceSync}>
                  <input name="connector_id" type="hidden" value={connector.id} />
                  <input name="cursor" type="hidden" value={connector.last_cursor ?? ""} />
                  <button
                    className="inline-flex h-9 w-full items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-3 text-[12px] font-semibold text-[color:var(--bg-base)] disabled:cursor-not-allowed disabled:bg-[color:var(--bg-surface)] disabled:text-[color:var(--text-tertiary)]"
                    disabled={!accessToken || !connector.enabled}
                    type="submit"
                  >
                    {connector.enabled ? "Request sync" : "Sync gated"}
                  </button>
                </form>
                <form action={queueAgentComplianceIngestJob}>
                  <input name="connector_id" type="hidden" value={connector.id} />
                  <input name="cursor" type="hidden" value={connector.last_cursor ?? ""} />
                  <input name="next_cursor" type="hidden" value="" />
                  <button
                    className="inline-flex h-9 w-full items-center justify-center rounded-md border border-[color:var(--accent-primary)]/45 px-3 text-[12px] font-semibold text-[color:var(--accent-primary)] disabled:cursor-not-allowed disabled:border-[color:var(--bg-border)] disabled:text-[color:var(--text-tertiary)]"
                    disabled={!accessToken || !connector.enabled}
                    type="submit"
                  >
                    {connector.enabled ? "Queue ingest" : "Job gated"}
                  </button>
                </form>
              </div>
            </article>
          ))}
        </div>
      </section>

      {showingFallback ? (
        <section className="rounded-[8px] border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-sm font-semibold text-[color:var(--text-primary)]">Catalog preview</h2>
              <p className="mt-1 max-w-4xl text-[13px] leading-6 text-[color:var(--text-secondary)]">
                Live connection state is unavailable in this session, so Skillayer is showing the PRD-backed connector catalog without marking any source connected.
              </p>
            </div>
            <span className="inline-flex h-8 w-fit items-center gap-2 rounded-md border border-[color:var(--accent-primary)]/40 px-3 text-[12px] font-semibold text-[color:var(--accent-primary)]">
              <PlugZap className="h-4 w-4" />
              Setup actions remain gated
            </span>
          </div>
        </section>
      ) : null}

      {sections.length ? (
        <div className="space-y-6">
          {sections.map((section) => {
            const Icon = section.meta.icon;
            return (
              <section className="space-y-3" key={section.category}>
                <div className="flex flex-col gap-2 border-b border-[color:var(--bg-border)] pb-3 sm:flex-row sm:items-end sm:justify-between">
                  <div className="flex items-start gap-3">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-[color:var(--bg-surface)] text-[color:var(--accent-primary)]">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <h2 className="text-[15px] font-semibold text-[color:var(--text-primary)]">{section.meta.title}</h2>
                      <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{section.meta.detail}</p>
                    </div>
                  </div>
                  <span className="text-[12px] font-semibold text-[color:var(--text-tertiary)]">{section.connectors.length} connectors</span>
                </div>
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                  {section.connectors.map((connector) => (
                    <article className="flex min-h-[220px] flex-col rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={connector.id}>
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h3 className="font-semibold text-[color:var(--text-primary)]">{connector.label}</h3>
                          <p className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{connector.category}</p>
                        </div>
                        <span className={`rounded-full px-2 py-1 text-[12px] font-semibold ${statusClass(connector)}`}>
                          {statusLabel(connector, showingFallback)}
                        </span>
                      </div>
                      {connector.description ? (
                        <p className="mt-3 flex-1 text-[13px] leading-6 text-[color:var(--text-secondary)]">{connector.description}</p>
                      ) : (
                        <p className="mt-3 flex-1 text-[13px] leading-6 text-[color:var(--text-secondary)]">Connector catalog entry reserved for this integration family.</p>
                      )}
                      {connector.capabilities?.length ? (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {connector.capabilities.map((capability) => (
                            <span className="rounded-full border border-[color:var(--bg-border)] px-2 py-1 text-[11px] font-semibold text-[color:var(--text-tertiary)]" key={capability}>
                              {capability}
                            </span>
                          ))}
                        </div>
                      ) : null}
                    </article>
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      ) : (
        <EmptyPanel detail="No connectors are configured yet. Connect GitHub or another source to populate live connection status." icon={<PlugZap className="h-5 w-5" />} title="No connectors connected yet." />
      )}
    </SettingsShell>
  );
}
