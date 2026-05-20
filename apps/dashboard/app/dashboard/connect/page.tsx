import { withAuth } from "@workos-inc/authkit-nextjs";
import { CheckCircle2, CircleDashed, GitBranch, KeyRound, PlugZap, TerminalSquare } from "lucide-react";

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
  agent_runtimes?: Record<string, { connected?: boolean; load_count_30d?: number }>;
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
  const runtimeConnected = Object.values(status?.agent_runtimes ?? {}).some((runtime) => Boolean(runtime.connected) || Number(runtime.load_count_30d ?? 0) > 0);
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
      detail: agentConnected ? "Agents have loaded Skillayer context" : "Connect Claude, Codex, Cursor, or CI",
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

export default async function ConnectPage() {
  const data = await resolveConnectData();
  return (
    <div className="space-y-6">
      <ConnectionStatusPanel apiKey={data.apiKey} repos={data.repos} setupStatus={data.setupStatus} status={data.connectStatus} />
      <ConnectShell accessToken={data.accessToken} apiKey={data.apiKey} orgId={data.orgId} repos={data.repos} setupStatus={data.setupStatus} />
    </div>
  );
}
