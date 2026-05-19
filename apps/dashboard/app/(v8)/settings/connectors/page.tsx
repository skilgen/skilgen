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
  credential_state: "missing" | "encrypted" | "legacy-migrated";
  credential_kind?: string | null;
  credential_hint?: Record<string, string | number | boolean | null>;
  credential_source_type?: string | null;
  last_tested_at?: string | null;
  last_connected_at?: string | null;
  last_error?: string | null;
  source_types: string[];
  scopes: string[];
  last_cursor?: string | null;
  last_sync_status?: string | null;
  last_sync_requested_at?: string | null;
  last_sync_mode?: string | null;
  last_sync_plan?: AgentComplianceSyncPlan | null;
  last_provider_sync_job?: {
    job_id: string;
    status: string;
    cursor?: string | null;
    next_cursor?: string | null;
    ingested_count?: number | null;
    skipped_count?: number | null;
    content_retention: "metadata-only";
    queued_at?: string | null;
    completed_at?: string | null;
    failed_at?: string | null;
    blocked_reason?: string | null;
    error?: string | null;
    next_sync_at?: string | null;
  } | null;
  next_sync_at?: string | null;
  last_success_at?: string | null;
  last_failure_at?: string | null;
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
  enterprise_setup?: {
    setup_complete: boolean;
    github_connected: boolean;
    required_provider_ids: string[];
    steps: Array<{
      id: string;
      label: string;
      status: "complete" | "pending" | "blocked" | string;
      detail: string;
      next_action: string;
    }>;
    coverage_gaps: Array<{
      id: string;
      label: string;
      severity: "low" | "medium" | "high" | string;
      next_action: string;
    }>;
  };
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
    description: "GitHub repository, pull-request, webhook, commit-signature, and AI attribution evidence for governed engineering work.",
    capabilities: ["repositories", "pull requests", "webhooks", "commit signatures", "AI attribution headers", "post-receive events"],
  },
  {
    id: "gitlab",
    label: "GitLab",
    category: "source-control",
    status: "planned",
    connected: false,
    description: "GitLab project, merge-request, webhook, post-receive, signed-commit, and Duo attribution evidence for governed source control.",
    capabilities: ["projects", "merge requests", "webhooks", "post-receive events", "commit signatures", "AI attribution headers"],
  },
  {
    id: "bitbucket",
    label: "Bitbucket",
    category: "source-control",
    status: "planned",
    connected: false,
    description: "Bitbucket repository, pull-request, webhook, commit-signature, and AI attribution evidence for regulated engineering workflows.",
    capabilities: ["repositories", "pull requests", "webhooks", "post-receive events", "commit signatures", "AI attribution headers"],
  },
  {
    id: "github-actions",
    label: "GitHub Actions",
    category: "ci-cd",
    status: "planned",
    connected: false,
    description: "Workflow runs, jobs, steps, artifacts, actor attribution, repository scope, and agent-driven CI outcomes from GitHub Actions.",
    capabilities: ["workflow runs", "jobs", "steps", "artifacts", "test outcomes", "actor attribution"],
  },
  {
    id: "gitlab-ci",
    label: "GitLab CI",
    category: "ci-cd",
    status: "planned",
    connected: false,
    description: "Pipelines, jobs, merge-request context, artifacts, runner metadata, and agent-driven CI outcomes from GitLab CI.",
    capabilities: ["pipelines", "jobs", "artifacts", "merge requests", "test outcomes", "runner metadata"],
  },
  {
    id: "circleci",
    label: "CircleCI",
    category: "ci-cd",
    status: "planned",
    connected: false,
    description: "Pipeline, workflow, job, artifact, test, actor, and repository metadata from CircleCI for agent-driven build governance.",
    capabilities: ["pipelines", "workflows", "jobs", "artifacts", "test outcomes", "actor attribution"],
  },
  {
    id: "jira",
    label: "Jira",
    category: "work-management",
    status: "planned",
    connected: false,
    description: "Jira issue, project, approval, change-ticket, and incident trigger context linked to coding-agent activity.",
    capabilities: ["issues", "projects", "change tickets", "approvals", "incident triggers", "external ticket links"],
  },
  {
    id: "linear",
    label: "Linear",
    category: "work-management",
    status: "planned",
    connected: false,
    description: "Linear issue, project, cycle, team, and incident trigger context linked to coding-agent sessions and policy reviews.",
    capabilities: ["issues", "projects", "cycles", "teams", "incident triggers", "external ticket links"],
  },
  {
    id: "slack",
    label: "Slack",
    category: "notifications",
    status: "available",
    connected: false,
    description: "Slack workspace notifications, slash-command callbacks, stale skill alerts, policy decisions, and digest delivery for engineering governance.",
    capabilities: ["chat routing", "slash commands", "stale skill alerts", "policy notifications", "digest delivery"],
  },
  {
    id: "email-digest",
    label: "Email Digest",
    category: "notifications",
    status: "available",
    connected: false,
    description: "Scheduled governance digests, compliance summaries, policy-review reminders, and delivery metadata from Skillayer notification settings.",
    capabilities: ["digest delivery", "scheduled summaries", "policy reminders", "delivery metadata", "compliance summaries"],
  },
  {
    id: "notification-webhook",
    label: "Notification Webhooks",
    category: "notifications",
    status: "planned",
    connected: false,
    description: "Outbound webhook delivery for agent activity, policy alerts, compliance milestones, and custom notification automation.",
    capabilities: ["webhook delivery", "agent activity alerts", "policy alerts", "compliance milestones", "delivery retries"],
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
    id: "splunk",
    label: "Splunk",
    category: "siem",
    status: "planned",
    connected: false,
    description: "Splunk HEC export target for normalized audit events, policy decisions, agent activity, and evidence package export records.",
    capabilities: ["HEC exports", "audit events", "policy decisions", "agent activity", "evidence export logs", "security analytics"],
  },
  {
    id: "datadog",
    label: "Datadog Cloud SIEM",
    category: "siem",
    status: "planned",
    connected: false,
    description: "Datadog Cloud SIEM export target for governed agent events, policy violations, audit trails, and risk analytics.",
    capabilities: ["cloud SIEM exports", "audit events", "policy violations", "agent activity", "risk analytics", "security signals"],
  },
  {
    id: "sentinel",
    label: "Microsoft Sentinel",
    category: "siem",
    status: "planned",
    connected: false,
    description: "Microsoft Sentinel export target for normalized audit events, agent actions, policy decisions, and compliance evidence.",
    capabilities: ["sentinel exports", "audit events", "policy decisions", "agent actions", "compliance evidence", "security analytics"],
  },
  {
    id: "s3-worm",
    label: "S3 Object Lock",
    category: "worm-store",
    status: "planned",
    connected: false,
    description: "Customer-owned S3 Object Lock target for tamper-evident audit-chain roots, Merkle proofs, and long-term evidence retention.",
    capabilities: ["immutable roots", "Merkle proofs", "audit chain roots", "retention policy", "evidence packages", "customer-owned storage"],
  },
  {
    id: "gcs-worm",
    label: "GCS Bucket Lock",
    category: "worm-store",
    status: "planned",
    connected: false,
    description: "Customer-owned GCS Bucket Lock target for tamper-evident audit-chain roots, Merkle proofs, and compliance evidence retention.",
    capabilities: ["immutable roots", "Merkle proofs", "audit chain roots", "retention policy", "evidence packages", "customer-owned storage"],
  },
  {
    id: "azure-worm",
    label: "Azure Immutable Blob",
    category: "worm-store",
    status: "planned",
    connected: false,
    description: "Customer-owned Azure Immutable Blob target for tamper-evident audit-chain roots, Merkle proofs, and regulated evidence retention.",
    capabilities: ["immutable roots", "Merkle proofs", "audit chain roots", "retention policy", "evidence packages", "customer-owned storage"],
  },
  {
    id: "sigstore",
    label: "Sigstore",
    category: "provenance",
    status: "planned",
    connected: false,
    description: "Sigstore signing, Rekor transparency-log, and Fulcio certificate evidence for release and skill provenance review.",
    capabilities: ["signatures", "transparency log", "certificate identity", "release evidence", "policy review"],
  },
  {
    id: "slsa-attestations",
    label: "SLSA Attestations",
    category: "provenance",
    status: "planned",
    connected: false,
    description: "SLSA provenance attestations for build builder identity, source revision, artifact digest, dependency materials, and supply-chain policy evidence.",
    capabilities: ["build provenance", "builder identity", "artifact digest", "dependency materials", "supply-chain policy"],
  },
  {
    id: "github-artifact-attestations",
    label: "GitHub Artifact Attestations",
    category: "provenance",
    status: "planned",
    connected: false,
    description: "GitHub artifact attestation evidence for workflow-signed build outputs, repository source, commit SHA, and deployment release review.",
    capabilities: ["artifact attestations", "workflow identity", "commit SHA", "repository source", "release evidence"],
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
  "ci-cd": {
    title: "CI/CD",
    detail: "Agent-driven build jobs, artifacts, and test outcomes.",
    icon: Workflow,
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
  "ci-cd",
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

function setupStepClass(status: string) {
  if (status === "complete") return "border-[color:var(--accent-green)]/40 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]";
  if (status === "pending") return "border-[color:var(--accent-primary)]/40 bg-[color:var(--accent-primary)]/10 text-[color:var(--accent-primary)]";
  return "border-amber-500/40 bg-amber-500/10 text-amber-100";
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

async function queueAgentComplianceProviderSync(formData: FormData) {
  "use server";

  const connectorId = String(formData.get("connector_id") ?? "");
  if (!connectorId) return;
  const { accessToken, org } = await loadSettingsContext();
  if (!accessToken) return;

  const response = await fetch(`${API_URL}/v8/orgs/${org.id}/settings/connectors/${encodeURIComponent(connectorId)}/sync-jobs`, {
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

async function testAgentComplianceCredentials(formData: FormData) {
  "use server";

  const connectorId = String(formData.get("connector_id") ?? "");
  if (!connectorId) return;
  const { accessToken, org } = await loadSettingsContext();
  if (!accessToken) return;

  const response = await fetch(`${API_URL}/v8/orgs/${org.id}/settings/connectors/${encodeURIComponent(connectorId)}/credentials/test`, {
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
  const agentConnectors = agentCompliance?.connectors ?? fallbackConnectors.filter((connector) => connector.category === "compliance-telemetry" || connector.category === "coding-agent" || connector.category === "ci-cd" || connector.id === "internal-mcp").map((connector) => ({
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
    last_provider_sync_job: null,
    next_sync_at: null,
    last_success_at: null,
    last_failure_at: null,
    credential_state: "missing" as const,
    credential_kind: null,
    credential_hint: {},
    credential_source_type: `agent_compliance:${connector.id}`,
    last_tested_at: null,
    last_connected_at: null,
    last_error: null,
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
  const enterpriseSetup = agentCompliance?.enterprise_setup;
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
        <Metric label="Catalog connected" value={connected} sub="Source catalog state only" />
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
        {enterpriseSetup ? (
          <div className="border-b border-[color:var(--bg-border)] p-4">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <h3 className="text-[14px] font-semibold text-[color:var(--text-primary)]">Enterprise setup path</h3>
                <p className="mt-1 max-w-4xl text-[12px] leading-6 text-[color:var(--text-secondary)]">
                  Connect GitHub and provider compliance APIs, test credentials, start cursor sync, then review coverage gaps before trusting automatic developer rollups.
                </p>
              </div>
              <span className={`inline-flex h-8 w-fit items-center rounded-md px-3 text-[12px] font-semibold ${enterpriseSetup.setup_complete ? "bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]" : "bg-amber-500/15 text-amber-100"}`}>
                {enterpriseSetup.setup_complete ? "Setup complete" : `${enterpriseSetup.coverage_gaps.length} coverage gaps`}
              </span>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {enterpriseSetup.steps.map((step) => (
                <article className={`rounded-md border p-3 ${setupStepClass(step.status)}`} key={step.id}>
                  <div className="flex items-center justify-between gap-2">
                    <h4 className="text-[13px] font-semibold">{step.label}</h4>
                    <span className="rounded-full bg-black/20 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide">{step.status}</span>
                  </div>
                  <p className="mt-2 text-[12px] leading-5 text-[color:var(--text-secondary)]">{step.detail}</p>
                  <p className="mt-2 text-[11px] font-semibold text-[color:var(--text-primary)]">Next: {step.next_action}</p>
                </article>
              ))}
            </div>
            {enterpriseSetup.coverage_gaps.length ? (
              <div className="mt-4 rounded-md border border-amber-500/35 bg-amber-500/10 p-3">
                <div className="text-[11px] font-semibold uppercase tracking-widest text-amber-100">Coverage gaps</div>
                <div className="mt-2 grid gap-2">
                  {enterpriseSetup.coverage_gaps.map((gap) => (
                    <div className="flex flex-col gap-1 rounded-md border border-amber-500/20 bg-black/10 p-2 text-[12px] sm:flex-row sm:items-center sm:justify-between" key={gap.id}>
                      <span className="font-semibold text-[color:var(--text-primary)]">{gap.label}</span>
                      <span className="text-[color:var(--text-secondary)]">{gap.next_action}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        ) : null}
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
              {(connector.last_success_at || connector.last_failure_at || connector.next_sync_at) ? (
                <div className="mt-2 grid gap-1 text-[11px] leading-5 text-[color:var(--text-tertiary)]">
                  {connector.last_success_at ? <span>Last success: {new Date(connector.last_success_at).toLocaleString()}</span> : null}
                  {connector.last_failure_at ? <span className="text-[color:var(--accent-red)]">Last failure: {new Date(connector.last_failure_at).toLocaleString()}</span> : null}
                  {connector.next_sync_at ? <span>Next sync window: {new Date(connector.next_sync_at).toLocaleString()}</span> : null}
                </div>
              ) : null}
              <div className="mt-3 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Credential vault</span>
                  <span className={`rounded-full px-2 py-1 text-[11px] font-semibold ${connector.credential_state === "encrypted" || connector.credential_state === "legacy-migrated" ? "bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]" : "bg-amber-500/15 text-amber-100"}`}>
                    {connector.credential_state === "missing" ? "Missing" : "Encrypted"}
                  </span>
                </div>
                <div className="mt-2 grid gap-1 text-[11px] leading-5 text-[color:var(--text-secondary)]">
                  <span>Kind: {connector.credential_kind ?? "not set"}</span>
                  <span>Stored as: {connector.credential_source_type ?? `agent_compliance:${connector.id}`}</span>
                  <span>Last test: {connector.last_tested_at ? new Date(connector.last_tested_at).toLocaleString() : "not tested"}</span>
                  {connector.credential_hint && Object.keys(connector.credential_hint).length ? (
                    <span className="truncate">Hint: {Object.entries(connector.credential_hint).filter(([key]) => key.endsWith("_hint")).map(([, value]) => String(value)).join(", ") || "metadata only"}</span>
                  ) : null}
                  {connector.last_error ? <span className="text-[color:var(--accent-red)]">{connector.last_error}</span> : null}
                </div>
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
              {connector.last_provider_sync_job ? (
                <div className="mt-3 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Provider sync job</span>
                    <span className="rounded-full bg-[color:var(--accent-primary)]/15 px-2 py-1 text-[11px] font-semibold text-[color:var(--accent-primary)]">{connector.last_provider_sync_job.status}</span>
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-[color:var(--text-secondary)]">
                    <span>Retention: {connector.last_provider_sync_job.content_retention}</span>
                    <span>Cursor: {connector.last_provider_sync_job.cursor ? "resume" : "first page"}</span>
                    <span>Events: {connector.last_provider_sync_job.ingested_count ?? 0}</span>
                    <span>Next: {connector.last_provider_sync_job.next_sync_at ? "scheduled" : "pending"}</span>
                  </div>
                  {connector.last_provider_sync_job.blocked_reason || connector.last_provider_sync_job.error ? (
                    <p className="mt-2 text-[11px] leading-5 text-[color:var(--accent-red)]">{connector.last_provider_sync_job.blocked_reason ?? connector.last_provider_sync_job.error}</p>
                  ) : null}
                  <p className="mt-2 truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{connector.last_provider_sync_job.job_id}</p>
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
                <form action={queueAgentComplianceProviderSync}>
                  <input name="connector_id" type="hidden" value={connector.id} />
                  <button
                    className="inline-flex h-9 w-full items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-3 text-[12px] font-semibold text-[color:var(--bg-base)] disabled:cursor-not-allowed disabled:bg-[color:var(--bg-surface)] disabled:text-[color:var(--text-tertiary)]"
                    disabled={!accessToken || !connector.enabled || connector.credential_state === "missing" || !["openai-compliance", "anthropic-compliance"].includes(connector.id)}
                    type="submit"
                  >
                    {connector.credential_state === "missing" ? "Credentials gated" : ["openai-compliance", "anthropic-compliance"].includes(connector.id) ? "Start provider sync" : "Adapter pending"}
                  </button>
                </form>
                <form action={testAgentComplianceCredentials}>
                  <input name="connector_id" type="hidden" value={connector.id} />
                  <button
                    className="inline-flex h-9 w-full items-center justify-center rounded-md border border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-primary)] disabled:cursor-not-allowed disabled:text-[color:var(--text-tertiary)]"
                    disabled={!accessToken || connector.credential_state === "missing"}
                    type="submit"
                  >
                    {connector.credential_state === "missing" ? "Add credentials" : "Test credentials"}
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
