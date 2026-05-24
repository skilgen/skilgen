import { withAuth } from "@workos-inc/authkit-nextjs";
import { CheckCircle2, CircleDashed, CloudCog, GitBranch, KeyRound, PlugZap, ShieldCheck, TerminalSquare } from "lucide-react";

import { API_URL, getBootstrapOrg, getMyOrg, getOrgApiKey, getOrgRepos, getOrgSetupStatus, type Repo, type SetupStatus } from "../../../lib/data";
import { ConnectShell } from "./connect-shell";

export const dynamic = "force-dynamic";

type ConnectStatusItem = {
  id?: string;
  label?: string;
  name?: string;
  connected?: boolean;
  status?: string;
  detail?: string;
  description?: string;
  updated_at?: string | null;
};

type ConnectStatus = {
  github_connected?: boolean;
  github_app_installed?: boolean;
  github_enrichment_active?: boolean;
  github_repo_count?: number;
  github_pr_count?: number;
  github_commit_count?: number;
  github_last_pr_at?: string | null;
  github_last_commit_at?: string | null;
  github_join_missing_30d?: number;
  api_key_configured?: boolean;
  agent_connected?: boolean;
  repos_connected?: number;
  skills_generated?: number;
  connections?: ConnectStatusItem[];
  provider_sync?: ProviderSyncStatus[];
  agent_runtimes?: Record<
    string,
    {
      connected?: boolean;
      last_seen_at?: string | null;
      load_count_30d?: number;
      uploads_30d?: number;
      tokens_total_30d?: number;
      cost_usd_30d?: number;
      commands_30d?: number;
      files_touched_30d?: number;
    }
  >;
};

type ProviderSyncStatus = {
  id: string;
  label: string;
  enabled?: boolean;
  connected?: boolean;
  credential_state?: string;
  last_sync_status?: string | null;
  last_sync_mode?: string | null;
  last_success_at?: string | null;
  last_failure_at?: string | null;
  next_sync_at?: string | null;
  last_ingested_count?: number;
  total_ingested_count?: number;
  last_cursor?: string | null;
  last_error?: string | null;
  active_job_status?: string | null;
  blocked_reason?: string | null;
};

async function resolveConnectData(): Promise<{
  accessToken: string;
  orgId: string;
  apiKey: string;
  repos: Repo[];
  setupStatus: SetupStatus | null;
  connectStatus: ConnectStatus | null;
}> {
  let accessToken = "";

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    // Auth can be unavailable in local preview; continue with bootstrap data.
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const orgId = org?.id ?? "";
  const apiToken = accessToken || "bootstrap";
  const [apiKey, repos, setupStatus, connectStatus] = orgId
    ? await Promise.all([getOrgApiKey(apiToken, orgId), getOrgRepos(apiToken, orgId), getOrgSetupStatus(apiToken, orgId), getConnectStatus(apiToken, orgId)])
    : [null, [], null, null];

  return {
    accessToken,
    orgId,
    apiKey: apiKey?.api_key ?? "",
    repos: repos ?? [],
    setupStatus,
    connectStatus,
  };
}

async function getConnectStatus(accessToken: string | null, orgId: string): Promise<ConnectStatus | null> {
  try {
    const headers: HeadersInit = { "Content-Type": "application/json" };
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
    const response = await fetch(`${API_URL}/orgs/${orgId}/connect/status`, {
      headers,
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as ConnectStatus;
  } catch (error) {
    console.error("Failed to load connect status:", error);
    return null;
  }
}

function isConnected(item: ConnectStatusItem): boolean {
  const status = String(item.status ?? "").toLowerCase();
  return item.connected === true || ["connected", "ready", "ok", "healthy", "complete"].includes(status);
}

function statusCards(status: ConnectStatus | null, repos: Repo[], setupStatus: SetupStatus | null, apiKey: string): ConnectStatusItem[] {
  if (status?.connections?.length) return status.connections;
  const repoCount = status?.repos_connected ?? repos.length;
  const githubInstalled = Boolean(status?.github_app_installed ?? status?.github_connected);
  const githubEnrichmentActive = Boolean(status?.github_enrichment_active);
  const githubConnected = githubInstalled && githubEnrichmentActive;
  const githubPrCount = Number(status?.github_pr_count ?? 0);
  const githubCommitCount = Number(status?.github_commit_count ?? 0);
  const githubJoinMissing = Number(status?.github_join_missing_30d ?? 0);
  const githubDetail = !githubInstalled
    ? "Install the GitHub App to unlock repo/PR/commit evidence"
    : !githubEnrichmentActive
      ? "GitHub App installed · waiting for PR/commit enrichment"
      : `Enrichment active · ${githubPrCount} PRs · ${githubCommitCount} commits${githubJoinMissing ? ` · ${githubJoinMissing} join gaps` : ""}`;
  const runtimeConnected = Object.values(status?.agent_runtimes ?? {}).some((runtime) => Boolean(runtime.connected) || Number(runtime.load_count_30d ?? 0) > 0 || Number(runtime.uploads_30d ?? 0) > 0);
  const agentConnected = status?.agent_connected ?? (Boolean(setupStatus?.has_agent_loads) || runtimeConnected);
  return [
    {
      id: "github",
      label: "GitHub repositories",
      connected: githubConnected,
      detail: githubDetail || (repoCount ? `${repoCount} repo${repoCount === 1 ? "" : "s"} connected` : "No repositories connected yet"),
    },
    {
      id: "api-key",
      label: "Agent API key",
      connected: status?.api_key_configured ?? Boolean(apiKey),
      detail: apiKey ? "API key is ready for agents" : "Generate a key before wiring agents",
    },
    {
      id: "skills",
      label: "Skills generated",
      connected: (status?.skills_generated ?? 0) > 0 || Boolean(setupStatus?.has_skills),
      detail: status?.skills_generated ? `${status.skills_generated} skills generated` : "Run analysis to create skills",
    },
    {
      id: "agent",
      label: "Agent loads",
      connected: agentConnected,
      detail: agentConnected ? "Local helper or agents have sent metadata" : "Install Skillayer locally or send a test load",
    },
  ];
}

function iconFor(id: string | undefined) {
  if (id === "github") return GitBranch;
  if (id === "api-key") return KeyRound;
  if (id === "agent") return TerminalSquare;
  return PlugZap;
}

function ConnectionCard({ item }: { item: ConnectStatusItem }) {
  const connected = isConnected(item);
  const Icon = iconFor(item.id);
  return (
    <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-[8px] border ${connected ? "border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : "border-[color:var(--bg-border)] bg-black/20 text-[color:var(--text-tertiary)]"}`}>
            <Icon className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <h2 className="truncate text-[15px] font-semibold text-[color:var(--text-primary)]">{item.label ?? item.name ?? "Connection"}</h2>
            <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{item.detail ?? item.description ?? (connected ? "Connected" : "Needs setup")}</p>
          </div>
        </div>
        <span className={`inline-flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] ${connected ? "bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : "bg-[color:var(--bg-base)] text-[color:var(--text-tertiary)]"}`}>
          {connected ? <CheckCircle2 className="h-3.5 w-3.5" /> : <CircleDashed className="h-3.5 w-3.5" />}
          {connected ? "Connected" : "Pending"}
        </span>
      </div>
    </article>
  );
}

function ConnectionStatusPanel({ apiKey, repos, setupStatus, status }: { apiKey: string; repos: Repo[]; setupStatus: SetupStatus | null; status: ConnectStatus | null }) {
  const cards = statusCards(status, repos, setupStatus, apiKey);
  const connectedCount = cards.filter(isConnected).length;
  return (
    <section className="space-y-4">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--accent-primary)]">Connection status</p>
          <h1 className="mt-2 text-2xl font-semibold text-[color:var(--text-primary)]">Agent context pipeline</h1>
          <p className="mt-1 max-w-2xl text-sm text-[color:var(--text-secondary)]">See which parts of Skillayer are wired up, then use the setup instructions below to finish any missing steps.</p>
        </div>
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-4 py-3 text-sm text-[color:var(--text-secondary)]">
          <span className="font-semibold text-[color:var(--text-primary)]">{connectedCount}/{cards.length}</span> connected
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((item, index) => (
          <ConnectionCard key={item.id ?? item.label ?? item.name ?? index} item={item} />
        ))}
      </div>
    </section>
  );
}

const RUNTIME_LABELS: Record<string, string> = {
  codex_desktop: "Codex Desktop",
  codex_cli: "Codex CLI",
  claude_code: "Claude Code",
  cursor: "Cursor",
  windsurf: "Windsurf",
  copilot: "GitHub Copilot",
  gemini_cli: "Gemini CLI",
  unidentified_agent: "Unidentified",
};

function formatNumber(value: number | undefined): string {
  return new Intl.NumberFormat("en-US").format(Number(value ?? 0));
}

function formatDateTime(value: string | null | undefined): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}

function RuntimeHealthPanel({ status }: { status: ConnectStatus | null }) {
  const runtimeStatus =
    status?.agent_runtimes ?? {
      codex_desktop: {},
      codex_cli: {},
      claude_code: {},
      cursor: {},
      windsurf: {},
      copilot: {},
    };
  const runtimes = Object.entries(runtimeStatus)
    .map(([id, runtime]) => ({ id, ...runtime }))
    .filter((runtime) => ["codex_desktop", "codex_cli", "claude_code", "cursor", "windsurf", "copilot"].includes(runtime.id))
    .sort((a, b) => Number(Boolean(b.connected)) - Number(Boolean(a.connected)) || (RUNTIME_LABELS[a.id] ?? a.id).localeCompare(RUNTIME_LABELS[b.id] ?? b.id));
  const totals = runtimes.reduce(
    (acc, runtime) => ({
      uploads: acc.uploads + Number(runtime.uploads_30d ?? 0),
      commands: acc.commands + Number(runtime.commands_30d ?? 0),
      files: acc.files + Number(runtime.files_touched_30d ?? 0),
      tokens: acc.tokens + Number(runtime.tokens_total_30d ?? 0),
      cost: acc.cost + Number(runtime.cost_usd_30d ?? 0),
    }),
    { uploads: 0, commands: 0, files: 0, tokens: 0, cost: 0 },
  );
  if (!runtimes.length) return null;
  return (
    <section className="space-y-4">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--accent-primary)]">Runtime health</p>
          <h2 className="mt-2 text-xl font-semibold text-[color:var(--text-primary)]">Local coding-agent coverage</h2>
          <p className="mt-1 max-w-2xl text-sm text-[color:var(--text-secondary)]">Start with the fleet picture, then drill into which runtimes are uploading commands, files, tokens, and cost.</p>
        </div>
        <div className="grid grid-cols-2 gap-2 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3 text-[12px] text-[color:var(--text-secondary)] md:grid-cols-5">
          <span><strong className="block text-[color:var(--text-primary)]">{formatNumber(totals.uploads)}</strong>uploads</span>
          <span><strong className="block text-[color:var(--text-primary)]">{formatNumber(totals.commands)}</strong>commands</span>
          <span><strong className="block text-[color:var(--text-primary)]">{formatNumber(totals.files)}</strong>files</span>
          <span><strong className="block text-[color:var(--text-primary)]">{formatNumber(totals.tokens)}</strong>tokens</span>
          <span><strong className="block text-[color:var(--text-primary)]">${totals.cost.toFixed(2)}</strong>cost</span>
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {runtimes.map((runtime) => {
          const connected = Boolean(runtime.connected) || Number(runtime.uploads_30d ?? 0) > 0 || Number(runtime.load_count_30d ?? 0) > 0;
          const lastSeenLabel = runtime.last_seen_at
            ? `Last upload ${new Date(runtime.last_seen_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}`
            : null;
          const uploadLabel = `${formatNumber(runtime.uploads_30d)} uploads in 30d`;
          const subtitle = connected ? [lastSeenLabel, uploadLabel].filter(Boolean).join(" · ") : "No local metadata yet";
          return (
            <article key={runtime.id} className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-[14px] font-semibold text-[color:var(--text-primary)]">{RUNTIME_LABELS[runtime.id] ?? runtime.id}</h3>
                  <p className="mt-1 text-[12px] text-[color:var(--text-secondary)]">{subtitle}</p>
                </div>
                <span className={`rounded-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] ${connected ? "bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : "bg-[color:var(--bg-base)] text-[color:var(--text-tertiary)]"}`}>
                  {connected ? "Active" : "Pending"}
                </span>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2 text-[12px] text-[color:var(--text-secondary)]">
                <span><strong className="block text-[color:var(--text-primary)]">{formatNumber(runtime.commands_30d)}</strong>commands</span>
                <span><strong className="block text-[color:var(--text-primary)]">{formatNumber(runtime.files_touched_30d)}</strong>files</span>
                <span><strong className="block text-[color:var(--text-primary)]">{formatNumber(runtime.tokens_total_30d)}</strong>tokens</span>
                <span><strong className="block text-[color:var(--text-primary)]">${Number(runtime.cost_usd_30d ?? 0).toFixed(2)}</strong>cost</span>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function ProviderSyncHealthPanel({ status }: { status: ConnectStatus | null }) {
  const providers = status?.provider_sync ?? [];
  if (!providers.length) return null;
  const connectedCount = providers.filter((provider) => provider.connected).length;
  const activeCount = providers.filter((provider) => ["success", "queued", "running"].includes(String(provider.last_sync_status ?? provider.active_job_status ?? "").toLowerCase())).length;
  const totalIngested = providers.reduce((sum, provider) => sum + Number(provider.total_ingested_count ?? 0), 0);
  return (
    <section className="space-y-4">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--accent-primary)]">Provider sync health</p>
          <h2 className="mt-2 text-xl font-semibold text-[color:var(--text-primary)]">Compliance API coverage</h2>
          <p className="mt-1 max-w-2xl text-sm text-[color:var(--text-secondary)]">Provider pulls show whether org-wide OpenAI and Anthropic evidence is fresh before you drill into Settings.</p>
        </div>
        <div className="grid grid-cols-3 gap-2 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-3 text-[12px] text-[color:var(--text-secondary)]">
          <span><strong className="block text-[color:var(--text-primary)]">{connectedCount}/{providers.length}</strong>credentialed</span>
          <span><strong className="block text-[color:var(--text-primary)]">{activeCount}</strong>active</span>
          <span><strong className="block text-[color:var(--text-primary)]">{formatNumber(totalIngested)}</strong>events</span>
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {providers.map((provider) => {
          const statusText = String(provider.active_job_status ?? provider.last_sync_status ?? (provider.connected ? "ready" : "missing")).toLowerCase();
          const healthy = Boolean(provider.connected) && ["success", "completed", "queued", "running", "ready"].includes(statusText);
          const lastSuccess = formatDateTime(provider.last_success_at);
          const nextSync = formatDateTime(provider.next_sync_at);
          const issue = provider.blocked_reason ?? provider.last_error;
          return (
            <article key={provider.id} className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex min-w-0 gap-3">
                  <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-[8px] border ${healthy ? "border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : "border-amber-500/25 bg-amber-500/10 text-amber-200"}`}>
                    {healthy ? <ShieldCheck className="h-5 w-5" /> : <CloudCog className="h-5 w-5" />}
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-[14px] font-semibold text-[color:var(--text-primary)]">{provider.label}</h3>
                    <p className="mt-1 text-[12px] text-[color:var(--text-secondary)]">
                      {lastSuccess ? `Last success ${lastSuccess}` : provider.connected ? "Credential ready; waiting for first sync" : "Credentials missing"}
                    </p>
                  </div>
                </div>
                <span className={`shrink-0 rounded-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] ${healthy ? "bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : "bg-amber-500/10 text-amber-200"}`}>
                  {statusText}
                </span>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2 text-[12px] text-[color:var(--text-secondary)] md:grid-cols-4">
                <span><strong className="block text-[color:var(--text-primary)]">{formatNumber(provider.last_ingested_count)}</strong>last pull</span>
                <span><strong className="block text-[color:var(--text-primary)]">{formatNumber(provider.total_ingested_count)}</strong>total</span>
                <span><strong className="block text-[color:var(--text-primary)]">{nextSync ?? "pending"}</strong>next sync</span>
                <span><strong className="block text-[color:var(--text-primary)]">{provider.credential_state ?? "missing"}</strong>credential</span>
              </div>
              {issue ? <p className="mt-3 rounded-[8px] border border-amber-500/20 bg-amber-500/10 px-3 py-2 text-[12px] text-amber-100">{issue}</p> : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}

export default async function ConnectPage() {
  const data = await resolveConnectData();
  return (
    <div className="space-y-6">
      <ConnectionStatusPanel apiKey={data.apiKey} repos={data.repos} setupStatus={data.setupStatus} status={data.connectStatus} />
      <RuntimeHealthPanel status={data.connectStatus} />
      <ProviderSyncHealthPanel status={data.connectStatus} />
      <ConnectShell accessToken={data.accessToken} apiKey={data.apiKey} orgId={data.orgId} repos={data.repos} setupStatus={data.setupStatus} />
    </div>
  );
}
