import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { ArrowLeft, BookOpen, ShieldCheck, Webhook } from "lucide-react";

import { API_URL, getBootstrapOrg, getMyOrg, getOrgApiKey } from "../../../../lib/data";
import { AgentRunSpecClient } from "./agent-run-spec-client";

export const dynamic = "force-dynamic";

async function loadSpecContext() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    // Auth can be unavailable in local preview; continue with bootstrap data.
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const apiKey = org ? (await getOrgApiKey(accessToken || "bootstrap", org.id))?.api_key ?? "" : "";
  return { orgId: org?.id ?? "", apiKey };
}

export default async function AgentRunSpecPage() {
  const { orgId, apiKey } = await loadSpecContext();
  const webhookUrl = `${API_URL}/orgs/${orgId || "{org_id}"}/agent-runs`;
  const example = `curl -X POST "${webhookUrl}" \\
  -H "Authorization: Bearer sk-..." \\
  -H "Content-Type: application/json" \\
  -d '{
    "spec_version": "0",
    "session_id": "codex-run-8842",
    "agent": {"vendor": "OpenAI", "product": "Codex CLI", "runtime": "codex_cli"},
    "repo": {"full_name": "acme/api"},
    "skills_loaded": ["agents", "cli", "core"],
    "code_artifacts": [{
      "file_path": "apps/api/routes/review.py",
      "tool": "Write",
      "diff": "--- a/apps/api/routes/review.py\\n+++ b/apps/api/routes/review.py\\n..."
    }],
    "outcome": "success"
  }'`;

  return (
    <div className="space-y-6">
      <div>
        <Link className="inline-flex items-center gap-2 text-sm font-semibold text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]" href="/dashboard/connect">
          <ArrowLeft className="h-4 w-4" />
          Back to Connect Agent
        </Link>
        <div className="mt-5 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-[rgb(var(--accent-primary-rgb)/0.24)] bg-[rgb(var(--accent-primary-rgb)/0.08)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)]">
              <Webhook className="h-4 w-4" />
              AgentRun v0
            </div>
            <h1 className="mt-4 text-[32px] font-semibold text-[color:var(--text-primary)]">Vendor-neutral agent session webhook</h1>
            <p className="mt-2 max-w-3xl text-[15px] leading-7 text-[color:var(--text-secondary)]">
              Let any agent vendor send Skillayer the same shape of session data: loaded skills, code artifacts, outcome, and runtime identity.
            </p>
          </div>
          <Link className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)]" href="https://github.com/RaviChanduUmmadisetti/skilgen/blob/main/docs/specs/AgentRun_v0.md">
            <BookOpen className="h-4 w-4" />
            Spec on GitHub
          </Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {[
          ["One endpoint", "POST sessions from Claude, Codex, Cursor, Copilot, Devin, or internal agents."],
          ["Governance-ready", "Every event populates AgentSession for attribution, replay, and audit evidence."],
          ["Same auth", "Use the existing org API key with a Bearer token. No separate vendor secret needed."],
        ].map(([title, body]) => (
          <article key={title} className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
            <ShieldCheck className="h-5 w-5 text-[color:var(--accent-primary)]" />
            <h2 className="mt-3 text-[15px] font-semibold text-[color:var(--text-primary)]">{title}</h2>
            <p className="mt-2 text-[13px] leading-6 text-[color:var(--text-secondary)]">{body}</p>
          </article>
        ))}
      </div>

      <AgentRunSpecClient apiKey={apiKey} webhookUrl={webhookUrl} example={example} />

      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">Required payload fields</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {[
            ["spec_version", "Use \"0\" for this version."],
            ["session_id", "Stable vendor session ID. Repeated calls update the same AgentSession."],
            ["agent", "Vendor, product, version, and optional normalized runtime."],
            ["repo_id or repo.full_name", "Identifies the connected repository."],
            ["skills_loaded", "Skill paths, IDs, or domains loaded by the agent."],
            ["code_artifacts", "Changed files, diffs, hashes, and timestamps."],
          ].map(([field, detail]) => (
            <div key={field} className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
              <code className="font-mono text-[13px] font-semibold text-[color:var(--text-primary)]">{field}</code>
              <p className="mt-2 text-[13px] leading-6 text-[color:var(--text-secondary)]">{detail}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
