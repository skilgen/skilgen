import Link from "next/link";
import { CheckCircle2, Clock3, FileWarning, LockKeyhole, ShieldCheck } from "lucide-react";
import { withAuth } from "@workos-inc/authkit-nextjs";

import {
  getBootstrapOrg,
  getMyOrg,
  getV8PolicyApprovals,
  getV8PolicyQuarantine,
  getV8PolicyRules,
  getV8PolicyStarterPacks,
  getV8PolicyViolations,
  type Org,
  type V8PolicyRule,
  type V8PolicyViolation,
  type V8QuarantineItem,
} from "../../../lib/data";
import { mockOrg } from "@/lib/mock-data";

type PolicyTab = "rules" | "violations" | "approvals" | "quarantine";

const tabs: Array<{ id: PolicyTab; label: string; href: string }> = [
  { id: "rules", label: "Rules", href: "/policy/rules" },
  { id: "violations", label: "Violations", href: "/policy/violations" },
  { id: "approvals", label: "Approvals", href: "/policy/approvals" },
  { id: "quarantine", label: "Quarantine", href: "/policy/quarantine" },
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

export async function PolicySurface({ tab }: { tab: PolicyTab }) {
  const { org, accessToken } = await loadContext();
  const [rules, starterPacks, violations, approvals, quarantine] = await Promise.all([
    getV8PolicyRules(accessToken, org.id),
    getV8PolicyStarterPacks(accessToken, org.id),
    getV8PolicyViolations(accessToken, org.id),
    getV8PolicyApprovals(accessToken, org.id),
    getV8PolicyQuarantine(accessToken, org.id),
  ]);

  const violationItems = violations?.items ?? [];
  const approvalItems = approvals?.items ?? [];

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
          <Metric label="Quarantined" value={quarantine.length} />
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
        {tab === "rules" ? <RulesTab rules={rules} starterPacks={starterPacks} /> : null}
        {tab === "violations" ? <ViolationsTab items={violationItems} /> : null}
        {tab === "approvals" ? <ApprovalsTab items={approvalItems} rbacAvailable={Boolean(approvals?.rbac.available)} /> : null}
        {tab === "quarantine" ? <QuarantineTab items={quarantine} /> : null}
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
  return <span className={`text-[12px] font-semibold ${color}`}>{decision}</span>;
}

function RulesTab({
  rules,
  starterPacks,
}: {
  rules: V8PolicyRule[];
  starterPacks: Array<{ pack_id: string; title: string; decision: V8PolicyRule["decision"]; compliance_tags: string[] }>;
}) {
  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
      <div className="overflow-hidden border border-[color:var(--bg-border)]">
        <div className="grid grid-cols-[minmax(180px,1.5fr)_150px_110px_100px] border-b border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-4 py-2 text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">
          <div>Name</div>
          <div>Decision</div>
          <div>Status</div>
          <div>Flags</div>
        </div>
        {rules.length ? (
          rules.map((rule) => (
            <div className="grid grid-cols-[minmax(180px,1.5fr)_150px_110px_100px] items-center border-b border-[color:var(--bg-border)] px-4 py-3 last:border-b-0" key={rule.id}>
              <div className="min-w-0">
                <div className="truncate text-[14px] font-semibold text-[color:var(--text-primary)]">{rule.name}</div>
                <div className="mt-1 truncate text-[12px] text-[color:var(--text-tertiary)]">{rule.id}</div>
              </div>
              <DecisionBadge decision={rule.decision} />
              <div className="text-[12px] font-medium text-[color:var(--text-secondary)]">{rule.enabled ? "Enabled" : "Paused"}</div>
              <div className="text-[12px] font-semibold text-[color:var(--text-primary)]">{rule.violation_count}</div>
            </div>
          ))
        ) : (
          <EmptyRow icon={<ShieldCheck className="h-5 w-5" />} title="No active v8 rules" />
        )}
      </div>

      <div className="border border-[color:var(--bg-border)]">
        <div className="border-b border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-4 py-3 text-[13px] font-semibold text-[color:var(--text-primary)]">Starter Packs</div>
        <div className="divide-y divide-[color:var(--bg-border)]">
          {starterPacks.map((pack) => (
            <div className="px-4 py-3" key={pack.pack_id}>
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0 truncate text-[13px] font-semibold text-[color:var(--text-primary)]">{pack.title}</div>
                <DecisionBadge decision={pack.decision} />
              </div>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {pack.compliance_tags.slice(0, 3).map((tag) => (
                  <span className="border border-[color:var(--bg-border)] px-2 py-0.5 text-[11px] text-[color:var(--text-secondary)]" key={tag}>{tag}</span>
                ))}
              </div>
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

function ApprovalsTab({ items, rbacAvailable }: { items: V8PolicyViolation[]; rbacAvailable: boolean }) {
  return (
    <div className="space-y-4">
      {!rbacAvailable ? (
        <div className="border border-[#f59e0b]/40 bg-[#f59e0b]/10 px-4 py-3 text-[13px] font-medium text-[#f59e0b]">Settings RBAC middleware unavailable; approval actions are disabled.</div>
      ) : null}
      {items.length ? (
        <div className="divide-y divide-[color:var(--bg-border)] border border-[color:var(--bg-border)]">
          {items.map((item) => <ViolationRow item={item} key={item.id} />)}
        </div>
      ) : (
        <EmptyPanel icon={<Clock3 className="h-8 w-8 text-[color:var(--accent-primary)]" />} title="No approvals waiting" />
      )}
    </div>
  );
}

function QuarantineTab({ items }: { items: V8QuarantineItem[] }) {
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
        </div>
      ))}
    </div>
  ) : (
    <EmptyPanel icon={<CheckCircle2 className="h-8 w-8 text-[color:var(--accent-green)]" />} title="No quarantined skills" />
  );
}

function ViolationRow({ item }: { item: V8PolicyViolation }) {
  return (
    <div className="grid gap-3 px-4 py-3 md:grid-cols-[1fr_160px_130px] md:items-center">
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

function EmptyRow({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <div className="flex items-center gap-3 px-4 py-10 text-[13px] text-[color:var(--text-secondary)]">
      {icon}
      <span>{title}</span>
    </div>
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
