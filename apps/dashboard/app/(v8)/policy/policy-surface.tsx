import Link from "next/link";
import { revalidatePath } from "next/cache";
import { CheckCircle2, Clock3, FileText, FileWarning, LockKeyhole, ShieldCheck, ThumbsDown, ThumbsUp } from "lucide-react";
import { withAuth } from "@workos-inc/authkit-nextjs";

import {
  API_URL,
  getBootstrapOrg,
  getMyOrg,
  getV8AgentCompliancePolicy,
  getV8PolicyApprovals,
  getV8PolicyQuarantine,
  getV8PolicyRules,
  getV8PolicyStarterPacks,
  getV8PolicyViolations,
  type Org,
  type V8AgentCompliancePolicyEvent,
  type V8PolicyRule,
  type V8PolicyStarterPack,
  type V8PolicyViolation,
  type V8QuarantineItem,
} from "../../../lib/data";
import { mockOrg } from "@/lib/mock-data";

type PolicyTab = "rules" | "violations" | "approvals" | "agent-events" | "quarantine";

const tabs: Array<{ id: PolicyTab; label: string; href: string }> = [
  { id: "rules", label: "Rules", href: "/policy/rules" },
  { id: "violations", label: "Violations", href: "/policy/violations" },
  { id: "approvals", label: "Approvals", href: "/policy/approvals" },
  { id: "agent-events", label: "Agent events", href: "/policy/agent-events" },
  { id: "quarantine", label: "Quarantine", href: "/policy/quarantine" },
];

const fallbackStarterPacks: V8PolicyStarterPack[] = [
  {
    pack_id: "agent-compliance",
    id: "agent-compliance-full-access",
    title: "Very-high intelligence agents with full access require review",
    decision: "require_approval",
    compliance_tags: ["agent-compliance", "internal:AI-governance", "SOC2:CC6.6"],
    match_fields: ["access_scope", "intelligence_tier", "provider", "repo_sensitivity", "tool_permissions"],
    predicate_count: 5,
    yaml: `id: agent-compliance-full-access
title: "Very-high intelligence agents with full access require review"
scope:
  provider: ["Codex CLI", "Claude Code", "Cursor", "GitHub Copilot"]
match:
  intelligence_tier: "very-high"
  access_scope: "full-access"
  tool_permissions: ["shell", "apply_patch", "filesystem.write", "settings.write"]
  repo_sensitivity: ["confidential", "restricted", "regulated"]
decision: require_approval
notify: ["#sec-aiops"]
compliance_tags: ["agent-compliance", "internal:AI-governance", "SOC2:CC6.6"]`,
  },
  {
    pack_id: "soc2",
    id: "soc2-change-management",
    title: "SOC2 CC8.1 requires approval for production change commands",
    decision: "require_approval",
    compliance_tags: ["SOC2:CC8.1", "SOC2:CC7.2", "SOC2:CC6.1"],
    match_fields: ["action_class", "command_regex", "file_glob"],
    predicate_count: 3,
    yaml: `id: soc2-change-management
title: "SOC2 CC8.1 requires approval for production change commands"
scope:
  action_class: shell_exec
match:
  command_regex: "\\\\b(terraform apply|kubectl apply|gh pr merge)\\\\b"
  file_glob: ["infra/prod/*", "k8s/prod/*", ".github/workflows/*"]
decision: require_approval
notify: ["#sec-aiops"]
compliance_tags: ["SOC2:CC8.1", "SOC2:CC7.2", "SOC2:CC6.1"]`,
  },
  {
    pack_id: "hipaa",
    id: "hipaa-phi-redaction",
    title: "HIPAA baseline redacts PHI before model exposure",
    decision: "redact",
    compliance_tags: ["HIPAA:164.312", "HIPAA:minimum-necessary"],
    match_fields: ["action_class", "data_class", "file_glob"],
    predicate_count: 3,
    yaml: `id: hipaa-phi-redaction
title: "HIPAA baseline redacts PHI before model exposure"
scope:
  action_class: file_read
match:
  file_glob: ["**/patients/**", "**/claims/**", "**/*phi*"]
  data_class: "phi"
decision: redact
notify: ["#privacy"]
compliance_tags: ["HIPAA:164.312", "HIPAA:minimum-necessary"]`,
  },
  {
    pack_id: "production-safety",
    id: "production-safety-infra",
    title: "Production infrastructure changes require approval",
    decision: "require_approval",
    compliance_tags: ["internal:production-safety"],
    match_fields: ["action_class", "command_regex", "file_glob"],
    predicate_count: 3,
    yaml: `id: production-safety-infra
title: "Production infrastructure changes require approval"
scope:
  action_class: shell_exec
match:
  command_regex: "\\\\b(apply|deploy|restart|delete)\\\\b"
  file_glob: ["**/prod/**", "**/production/**"]
decision: require_approval
notify: ["#platform-ops"]
compliance_tags: ["internal:production-safety"]`,
  },
  {
    pack_id: "fedramp-mod",
    id: "fedramp-mod-privileged-action",
    title: "FedRAMP Moderate routes privileged actions through DLP",
    decision: "route_to_dlp",
    compliance_tags: ["NIST:AC-2", "NIST:AC-3", "NIST:AU-2", "NIST:CM-3"],
    match_fields: ["action_class", "command_regex", "data_class"],
    predicate_count: 3,
    yaml: `id: fedramp-mod-privileged-action
title: "FedRAMP Moderate routes privileged actions through DLP"
scope:
  action_class: shell_exec
match:
  command_regex: "\\\\b(iam|security-group|firewall|kms|secretsmanager)\\\\b"
  data_class: "privileged-resource"
decision: route_to_dlp
notify: ["#govcloud-review"]
compliance_tags: ["NIST:AC-2", "NIST:AC-3", "NIST:AU-2", "NIST:CM-3"]`,
  },
  {
    pack_id: "internal-ip",
    id: "internal-ip-protected-files",
    title: "Internal IP files cannot be read by coding agents",
    decision: "deny",
    compliance_tags: ["internal:IP-policy"],
    match_fields: ["action_class", "file_glob"],
    predicate_count: 2,
    yaml: `id: internal-ip-protected-files
title: "Internal IP files cannot be read by coding agents"
scope:
  action_class: file_read
match:
  file_glob: ["**/strategy/**", "**/roadmap/**", "**/*trade-secret*"]
decision: deny
notify: ["#legal-security"]
compliance_tags: ["internal:IP-policy"]`,
  },
  {
    pack_id: "license-hygiene",
    id: "license-hygiene-gpl",
    title: "GPL and AGPL dependency additions are blocked",
    decision: "deny",
    compliance_tags: ["internal:license-hygiene"],
    match_fields: ["action_class", "command_regex", "file_glob"],
    predicate_count: 3,
    yaml: `id: license-hygiene-gpl
title: "GPL and AGPL dependency additions are blocked"
scope:
  action_class: file_write
match:
  file_glob: ["**/package.json", "**/pyproject.toml", "**/go.mod", "**/Cargo.toml"]
  command_regex: "(GPL|AGPL|gpl|agpl)"
decision: deny
notify: ["#opensource-review"]
compliance_tags: ["internal:license-hygiene"]`,
  },
];

async function loadContext(): Promise<{ org: Pick<Org, "id" | "name" | "plan">; accessToken: string | null }> {
  let accessToken: string | null = null;
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || null;
  } catch {
    accessToken = null;
  }

  if (accessToken) {
    const org = await getMyOrg(accessToken);
    if (org) return { org, accessToken };
  }

  const org = await getBootstrapOrg();
  return { org: org ?? mockOrg, accessToken };
}

async function applyStarterPack(formData: FormData) {
  "use server";

  const yaml = String(formData.get("yaml") ?? "");
  const policyPack = String(formData.get("policy_pack") ?? "");
  if (!yaml) return;

  const { org, accessToken } = await loadContext();
  if (!accessToken) return;

  const response = await fetch(`${API_URL}/v8/orgs/${org.id}/policy/rules`, {
    body: JSON.stringify({ yaml, policy_pack: policyPack || null }),
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    method: "POST",
  });

  if (response.ok) {
    revalidatePath("/policy");
    revalidatePath("/policy/rules");
  }
}

async function decideApproval(formData: FormData) {
  "use server";

  const approvalId = String(formData.get("approval_id") ?? "");
  const decision = String(formData.get("decision") ?? "");
  if (!approvalId || !["approve", "deny", "request_info"].includes(decision)) return;

  const { org, accessToken } = await loadContext();
  if (!accessToken) return;

  const response = await fetch(`${API_URL}/v8/orgs/${org.id}/policy/approvals/${encodeURIComponent(approvalId)}/decision`, {
    body: JSON.stringify({ decision }),
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    method: "POST",
  });

  if (response.ok) {
    revalidatePath("/policy");
    revalidatePath("/policy/approvals");
    revalidatePath("/policy/violations");
  }
}

async function decideQuarantine(formData: FormData) {
  "use server";

  const skillId = String(formData.get("skill_id") ?? "");
  const action = String(formData.get("action") ?? "");
  if (!skillId || !["promote", "retire"].includes(action)) return;

  const { org, accessToken } = await loadContext();
  if (!accessToken) return;

  const response = await fetch(`${API_URL}/v8/orgs/${org.id}/policy/quarantine/${encodeURIComponent(skillId)}/decision`, {
    body: JSON.stringify({ action }),
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    method: "POST",
  });

  if (response.ok) {
    revalidatePath("/policy");
    revalidatePath("/policy/quarantine");
  }
}

export async function PolicySurface({ tab }: { tab: PolicyTab }) {
  const { org, accessToken } = await loadContext();
  const [rules, starterPacks, violations, approvals, agentPolicy, quarantine] = await Promise.all([
    getV8PolicyRules(accessToken, org.id),
    getV8PolicyStarterPacks(accessToken, org.id),
    getV8PolicyViolations(accessToken, org.id),
    getV8PolicyApprovals(accessToken, org.id),
    getV8AgentCompliancePolicy(accessToken, org.id),
    getV8PolicyQuarantine(accessToken, org.id),
  ]);

  const violationItems = violations?.items ?? [];
  const approvalItems = approvals?.items ?? [];
  const agentPolicyItems = agentPolicy?.items ?? [];

  return (
    <section className="mx-auto max-w-7xl">
      <div className="flex flex-col gap-4 border-b border-[color:var(--bg-border)] pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="text-[12px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Policy</div>
          <h1 className="mt-2 text-3xl font-semibold text-[color:var(--text-primary)]">Agent Governance Rules</h1>
        </div>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          <Metric label="Rules" value={rules.length} />
          <Metric label="Violations" value={violationItems.length} />
          <Metric label="Approvals" value={approvalItems.length} />
          <Metric label="Agent flags" value={agentPolicy?.flagged_count ?? 0} />
        </div>
      </div>

      <nav aria-label="Policy tabs" className="mt-5 flex gap-2 overflow-x-auto border-b border-[color:var(--bg-border)] pb-2">
        {tabs.map((item) => (
          <Link
            className={`inline-flex h-9 shrink-0 items-center rounded-md px-3 text-[13px] font-semibold ${
              tab === item.id
                ? "bg-[color:var(--accent-primary)] text-[color:var(--bg-base)]"
                : "text-[color:var(--text-secondary)] hover:bg-[color:var(--bg-surface)] hover:text-[color:var(--text-primary)]"
            }`}
            href={item.href}
            key={item.id}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="mt-6">
        {tab === "rules" ? <RulesTab canApply={Boolean(accessToken)} rules={rules} starterPacks={starterPacks.length ? starterPacks : fallbackStarterPacks} /> : null}
        {tab === "violations" ? <ViolationsTab items={violationItems} /> : null}
        {tab === "approvals" ? <ApprovalsTab canReview={Boolean(accessToken && approvals?.rbac.available)} items={approvalItems} rbacAvailable={Boolean(approvals?.rbac.available)} /> : null}
        {tab === "agent-events" ? <AgentEventsTab contentRetention={agentPolicy?.content_retention ?? "metadata-only"} items={agentPolicyItems} /> : null}
        {tab === "quarantine" ? <QuarantineTab canReview={Boolean(accessToken)} items={quarantine} /> : null}
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="min-w-[120px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-2">
      <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">{label}</div>
      <div className="mt-1 text-xl font-semibold text-[color:var(--text-primary)]">{value}</div>
    </div>
  );
}

function DecisionBadge({ decision }: { decision: V8PolicyRule["decision"] }) {
  const color =
    decision === "deny"
      ? "text-[color:var(--accent-red)]"
      : decision === "require_approval"
        ? "text-[#f59e0b]"
        : decision === "allow"
          ? "text-[color:var(--accent-green)]"
          : "text-[color:var(--accent-primary)]";
  return <span className={`text-[12px] font-semibold ${color}`}>{decision.replaceAll("_", " ")}</span>;
}

const decisionDescriptions: Record<V8PolicyRule["decision"], string> = {
  allow: "Proceed and log normally.",
  deny: "Block the action and alert reviewers.",
  require_approval: "Hold the agent until a reviewer decides.",
  log_only: "Let the action proceed but flag it for review.",
  redact: "Scrub sensitive data before it reaches the model.",
  route_to_dlp: "Send the action through DLP inspection first.",
};

function RulesTab({
  rules,
  starterPacks,
  canApply,
}: {
  canApply: boolean;
  rules: V8PolicyRule[];
  starterPacks: V8PolicyStarterPack[];
}) {
  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
      <div className="border border-[color:var(--bg-border)]">
        {rules.length ? (
          <>
            <div className="hidden overflow-x-auto md:block">
              <div className="grid min-w-[720px] grid-cols-[minmax(180px,1.5fr)_150px_110px_100px] border-b border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-4 py-2 text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">
                <div>Name</div>
                <div>Decision</div>
                <div>Status</div>
                <div>Flags</div>
              </div>
              {rules.map((rule) => (
                <div className="grid min-w-[720px] grid-cols-[minmax(180px,1.5fr)_150px_110px_100px] items-center border-b border-[color:var(--bg-border)] px-4 py-3 last:border-b-0" key={rule.id}>
                  <div className="min-w-0">
                    <div className="text-[14px] font-semibold leading-5 text-[color:var(--text-primary)]">{rule.name}</div>
                    <div className="mt-1 truncate text-[12px] text-[color:var(--text-tertiary)]">{rule.id}</div>
                  </div>
                  <DecisionBadge decision={rule.decision} />
                  <div className="text-[12px] font-medium text-[color:var(--text-secondary)]">{rule.enabled ? "Enabled" : "Paused"}</div>
                  <div className="text-[12px] font-semibold text-[color:var(--text-primary)]">{rule.violation_count}</div>
                </div>
              ))}
            </div>
            <div className="divide-y divide-[color:var(--bg-border)] md:hidden">
              {rules.map((rule) => (
                <div className="px-4 py-3" key={`mobile-${rule.id}`}>
                  <div className="text-[14px] font-semibold text-[color:var(--text-primary)]">{rule.name}</div>
                  <div className="mt-1 break-all text-[12px] text-[color:var(--text-tertiary)]">{rule.id}</div>
                  <div className="mt-3 flex items-center justify-between gap-3 text-[12px]">
                    <DecisionBadge decision={rule.decision} />
                    <span className="text-[color:var(--text-secondary)]">{rule.enabled ? "Enabled" : "Paused"}</span>
                    <span className="font-semibold text-[color:var(--text-primary)]">{rule.violation_count} flags</span>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="flex min-h-[136px] items-center gap-3 bg-[color:var(--bg-base)] px-4 py-8 text-[13px] text-[color:var(--text-secondary)]">
            <ShieldCheck className="h-5 w-5 shrink-0" />
            <span>No active v8 rules</span>
          </div>
        )}
      </div>

      <div className="border border-[color:var(--bg-border)]">
        <div className="border-b border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-4 py-3">
          <div className="flex items-center gap-2 text-[13px] font-semibold text-[color:var(--text-primary)]">
            <FileText className="h-4 w-4 text-[color:var(--accent-primary)]" />
            Starter Packs
          </div>
          <p className="mt-1 text-[12px] leading-5 text-[color:var(--text-secondary)]">Adopt a PRD baseline, inspect the YAML, then tune it as a versioned rule.</p>
        </div>
        <div className="divide-y divide-[color:var(--bg-border)]">
          {starterPacks.map((pack) => (
            <div className="px-4 py-3" key={pack.pack_id}>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0 text-[13px] font-semibold leading-5 text-[color:var(--text-primary)]">{pack.title}</div>
                <div className="shrink-0">
                  <DecisionBadge decision={pack.decision} />
                </div>
              </div>
              <p className="mt-2 text-[12px] leading-5 text-[color:var(--text-secondary)]">{decisionDescriptions[pack.decision]}</p>
              <div className="mt-2 flex items-center justify-between gap-3 text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">
                <span>{pack.pack_id.replaceAll("-", " ")}</span>
                {pack.predicate_count ? <span>{pack.predicate_count} predicates</span> : null}
              </div>
              {pack.match_fields?.length ? (
                <div className="mt-2 flex flex-wrap gap-1.5" aria-label={`${pack.title} target predicates`}>
                  {pack.match_fields.slice(0, 5).map((field) => (
                    <span className="rounded-sm border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-2 py-0.5 font-mono text-[11px] text-[color:var(--text-secondary)]" key={`${pack.pack_id}-${field}`}>
                      {field}
                    </span>
                  ))}
                </div>
              ) : null}
              <div className="mt-2 flex flex-wrap gap-1.5">
                {pack.compliance_tags.map((tag) => (
                  <span className="border border-[color:var(--bg-border)] px-2 py-0.5 text-[11px] text-[color:var(--text-secondary)]" key={tag}>{tag}</span>
                ))}
              </div>
              <details className="mt-3">
                <summary className="cursor-pointer text-[12px] font-semibold text-[color:var(--accent-primary)]">Preview YAML</summary>
                <pre className="mt-2 max-h-[220px] overflow-auto rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-[11px] leading-5 text-[color:var(--text-secondary)]">{pack.yaml}</pre>
              </details>
              {canApply ? (
                <form action={applyStarterPack} className="mt-3">
                  <input name="yaml" type="hidden" value={pack.yaml} />
                  <input name="policy_pack" type="hidden" value={pack.pack_id} />
                  <button className="inline-flex w-full items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-3 py-2 text-[12px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]" type="submit">
                    Apply pack
                  </button>
                </form>
              ) : (
                <button className="mt-3 inline-flex w-full cursor-not-allowed items-center justify-center rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-[12px] font-semibold text-[color:var(--text-secondary)]" disabled type="button">
                  Sign in to apply
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ViolationsTab({ items }: { items: V8PolicyViolation[] }) {
  return items.length ? (
    <div className="divide-y divide-[color:var(--bg-border)] border border-[color:var(--bg-border)]">
      {items.map((item) => <ViolationRow item={item} key={item.id} />)}
    </div>
  ) : (
    <EmptyPanel icon={<CheckCircle2 className="h-8 w-8 text-[color:var(--accent-green)]" />} title="No flagged policy decisions" />
  );
}

function ApprovalsTab({ items, rbacAvailable, canReview }: { items: V8PolicyViolation[]; rbacAvailable: boolean; canReview: boolean }) {
  return (
    <div className="space-y-4">
      {items.length && !rbacAvailable ? (
        <div className="border border-[#f59e0b]/40 bg-[#f59e0b]/10 px-4 py-3 text-[13px] font-medium text-[#f59e0b]">Settings RBAC middleware unavailable; approval actions are disabled.</div>
      ) : null}
      {items.length ? (
        <div className="divide-y divide-[color:var(--bg-border)] border border-[color:var(--bg-border)]">
          {items.map((item) => <ApprovalRow canReview={canReview} item={item} key={item.id} />)}
        </div>
      ) : (
        <EmptyPanel icon={<Clock3 className="h-8 w-8 text-[color:var(--accent-primary)]" />} title="No approvals waiting" />
      )}
    </div>
  );
}

function AgentEventsTab({ items, contentRetention }: { items: V8AgentCompliancePolicyEvent[]; contentRetention: "metadata-only" }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-3">
        <Metric label="Evaluated" value={items.length} />
        <Metric label="Flagged" value={items.filter((item) => item.decision !== "allow").length} />
        <div className="border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-2">
          <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Retention</div>
          <div className="mt-1 text-sm font-semibold text-[color:var(--accent-primary)]">{contentRetention}</div>
        </div>
      </div>
      {items.length ? (
        <div className="divide-y divide-[color:var(--bg-border)] border border-[color:var(--bg-border)]">
          {items.map((item) => (
            <div className="grid gap-3 px-4 py-3 lg:grid-cols-[minmax(0,1fr)_150px_180px] lg:items-center" key={item.event_id}>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <FileWarning className="h-4 w-4 shrink-0 text-[#f59e0b]" />
                  <div className="font-semibold text-[color:var(--text-primary)]">{item.provider ?? "Agent telemetry"}</div>
                  <span className="rounded-sm border border-[color:var(--bg-border)] px-2 py-0.5 text-[11px] text-[color:var(--text-tertiary)]">{item.source_record_type ?? "operational-telemetry"}</span>
                </div>
                <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">
                  {item.actor_login ?? "Unknown actor"} · {item.repo_name ?? "Org scope"} · {item.model ?? "model unknown"}
                </div>
                <div className="mt-1 truncate font-mono text-[11px] text-[color:var(--text-tertiary)]">{item.provider_event_id ?? item.event_id}</div>
                {item.reasons.length ? <div className="mt-2 text-[12px] text-[color:var(--text-secondary)]">{item.reasons.join(", ")}</div> : null}
              </div>
              <DecisionBadge decision={item.decision} />
              <div className="flex flex-wrap gap-1.5">
                {[item.intelligence_tier, item.access_scope, ...item.compliance_tags].filter(Boolean).slice(0, 4).map((tag) => (
                  <span className="rounded-sm border border-[color:var(--bg-border)] px-2 py-0.5 text-[11px] text-[color:var(--text-secondary)]" key={`${item.event_id}-${tag}`}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyPanel icon={<CheckCircle2 className="h-8 w-8 text-[color:var(--accent-green)]" />} title="No agent compliance events to evaluate" />
      )}
    </div>
  );
}

function QuarantineTab({ items, canReview }: { items: V8QuarantineItem[]; canReview: boolean }) {
  return items.length ? (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {items.map((item) => (
        <div className="border border-[color:var(--bg-border)] p-4" key={item.id}>
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="truncate text-[14px] font-semibold text-[color:var(--text-primary)]">{item.name}</div>
              <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{item.domain} · v{item.version}</div>
            </div>
            <LockKeyhole className="h-4 w-4 shrink-0 text-[#f59e0b]" />
          </div>
          <div className="mt-4 flex items-center justify-between text-[12px]">
            <span className="font-semibold text-[color:var(--text-secondary)]">{item.disposition}</span>
            <span className="text-[color:var(--text-tertiary)]">Score {Math.round(item.score_total)}</span>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            <ReviewButton
              action={decideQuarantine}
              disabled={!canReview || item.disposition === "retired"}
              fields={{ skill_id: item.id, action: "promote" }}
              icon={<ThumbsUp className="h-3.5 w-3.5" />}
              label={item.disposition === "retired" ? "Retired" : "Promote"}
              tone="approve"
            />
            <ReviewButton
              action={decideQuarantine}
              disabled={!canReview || item.disposition === "retired"}
              fields={{ skill_id: item.id, action: "retire" }}
              icon={<ThumbsDown className="h-3.5 w-3.5" />}
              label="Retire"
              tone="deny"
            />
          </div>
        </div>
      ))}
    </div>
  ) : (
    <EmptyPanel icon={<CheckCircle2 className="h-8 w-8 text-[color:var(--accent-green)]" />} title="No quarantined skills" />
  );
}

function ApprovalRow({ item, canReview }: { item: V8PolicyViolation; canReview: boolean }) {
  return (
    <div className="grid gap-4 px-4 py-4 lg:grid-cols-[minmax(0,1fr)_minmax(260px,320px)] lg:items-center">
      <div>
        <ViolationSummary item={item} />
        {item.review_decision === "request_info" ? (
          <div className="mt-3 inline-flex rounded-md border border-[#f59e0b]/40 bg-[#f59e0b]/10 px-2 py-1 text-[11px] font-semibold text-[#f59e0b]">
            More info requested
          </div>
        ) : null}
      </div>
      <div className="grid gap-2 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
        <ReviewButton
          action={decideApproval}
          disabled={!canReview}
          fields={{ approval_id: item.id, decision: "approve" }}
          icon={<ThumbsUp className="h-3.5 w-3.5" />}
          label="Approve"
          tone="approve"
        />
        <ReviewButton
          action={decideApproval}
          disabled={!canReview}
          fields={{ approval_id: item.id, decision: "request_info" }}
          label="Need info"
          tone="neutral"
        />
        <ReviewButton
          action={decideApproval}
          disabled={!canReview}
          fields={{ approval_id: item.id, decision: "deny" }}
          icon={<ThumbsDown className="h-3.5 w-3.5" />}
          label="Deny"
          tone="deny"
        />
      </div>
    </div>
  );
}

function ViolationRow({ item }: { item: V8PolicyViolation }) {
  return (
    <div className="px-4 py-3">
      <ViolationSummary item={item} />
    </div>
  );
}

function ViolationSummary({ item }: { item: V8PolicyViolation }) {
  return (
    <div className="grid gap-3 md:grid-cols-[1fr_160px_130px] md:items-center">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <FileWarning className="h-4 w-4 shrink-0 text-[#f59e0b]" />
          <div className="truncate text-[14px] font-semibold text-[color:var(--text-primary)]">{item.policy_name}</div>
        </div>
        <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">{item.description}</div>
        <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{item.repo_name ?? "Org scope"}</div>
      </div>
      <DecisionBadge decision={item.decision} />
      <div className="text-[12px] font-medium text-[color:var(--text-secondary)]">{item.sla_minutes_remaining}m SLA</div>
    </div>
  );
}

function ReviewButton({
  action,
  disabled,
  fields,
  icon,
  label,
  tone,
}: {
  action: (formData: FormData) => Promise<void>;
  disabled: boolean;
  fields: Record<string, string>;
  icon?: React.ReactNode;
  label: string;
  tone: "approve" | "deny" | "neutral";
}) {
  const toneClass =
    tone === "approve"
      ? "border-[color:var(--accent-green)]/50 text-[color:var(--accent-green)] hover:bg-[color:var(--accent-green)]/10"
      : tone === "deny"
        ? "border-[color:var(--accent-red)]/50 text-[color:var(--accent-red)] hover:bg-[color:var(--accent-red)]/10"
        : "border-[color:var(--bg-border)] text-[color:var(--text-secondary)] hover:bg-[color:var(--bg-surface)] hover:text-[color:var(--text-primary)]";

  return (
    <form action={action}>
      {Object.entries(fields).map(([name, value]) => (
        <input key={name} name={name} type="hidden" value={value} />
      ))}
      <button
        className={`inline-flex h-9 w-full items-center justify-center gap-1.5 rounded-md border px-3 text-[12px] font-semibold disabled:cursor-not-allowed disabled:border-[color:var(--bg-border)] disabled:text-[color:var(--text-tertiary)] disabled:hover:bg-transparent ${toneClass}`}
        disabled={disabled}
        type="submit"
      >
        {icon}
        {label}
      </button>
    </form>
  );
}

function EmptyPanel({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <div className="flex min-h-[280px] flex-col items-center justify-center border border-[color:var(--bg-border)] text-center">
      {icon}
      <div className="mt-3 text-[15px] font-semibold text-[color:var(--text-primary)]">{title}</div>
    </div>
  );
}
