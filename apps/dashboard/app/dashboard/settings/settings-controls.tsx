"use client";

import { Bell, CheckCircle2, Loader2, Save } from "lucide-react";
import type { ReactElement } from "react";
import { useMemo, useState } from "react";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type OrgSettings = {
  id: string;
  login: string;
  name: string;
  plan: string;
  score_threshold: number;
  slack_webhook_url: string | null;
  notify_on_pr: boolean;
  notify_on_stale: boolean;
  github_app_installed: boolean;
  github_installation_id: number | null;
  webhook_url: string;
  recent_deliveries: {
    id: string;
    status: string;
    trigger: string;
    created_at: string | null;
  }[];
};

type GovernancePolicy = {
  id: string;
  name: string;
  type: "min_score" | "max_staleness_days" | "required_categories" | "min_groundedness";
  threshold: number | string[] | null;
  scope: string;
  action: "warn" | "block_pr" | "notify_slack";
  enabled: boolean;
  created_at?: string | null;
};

type SettingsControlsProps = {
  accessToken: string;
  initialPolicies?: GovernancePolicy[];
  initialSettings: OrgSettings;
  orgId: string;
  tab: "general" | "notifications";
};

type StatusState = {
  message: string;
  tone: "success" | "error";
} | null;

function buildHeaders(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

export function SettingsControls({ accessToken, initialPolicies = [], initialSettings, orgId, tab }: SettingsControlsProps): ReactElement {
  const [settings, setSettings] = useState(initialSettings);
  const [policies, setPolicies] = useState<GovernancePolicy[]>(initialPolicies);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [policySavingId, setPolicySavingId] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusState>(null);
  const slackValue = settings.slack_webhook_url ?? "";

  const updateBody = useMemo(
    () => ({
      name: settings.name,
      score_threshold: settings.score_threshold,
      slack_webhook_url: slackValue || null,
      notify_on_pr: settings.notify_on_pr,
      notify_on_stale: settings.notify_on_stale,
    }),
    [settings.name, settings.notify_on_pr, settings.notify_on_stale, settings.score_threshold, slackValue],
  );

  async function saveSettings(): Promise<void> {
    setSaving(true);
    setStatus(null);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/settings`, {
        method: "PATCH",
        headers: buildHeaders(accessToken),
        body: JSON.stringify(updateBody),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Could not update settings");
      setSettings(body as OrgSettings);
      setStatus({ message: "Settings saved", tone: "success" });
    } catch (error) {
      setStatus({ message: error instanceof Error ? error.message : "Could not update settings", tone: "error" });
    } finally {
      setSaving(false);
    }
  }

  async function sendTestNotification(): Promise<void> {
    setTesting(true);
    setStatus(null);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/test-notification`, {
        method: "POST",
        headers: buildHeaders(accessToken),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Could not send test notification");
      setStatus({ message: "Test notification sent", tone: "success" });
    } catch (error) {
      setStatus({ message: error instanceof Error ? error.message : "Could not send test notification", tone: "error" });
    } finally {
      setTesting(false);
    }
  }

  async function persistPolicies(nextPolicies: GovernancePolicy[], successMessage: string): Promise<void> {
    setStatus(null);
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/policies`, {
        method: "POST",
        headers: buildHeaders(accessToken),
        body: JSON.stringify({ policies: nextPolicies }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Could not update policies");
      setPolicies((body.policies as GovernancePolicy[]) ?? nextPolicies);
      setStatus({ message: successMessage, tone: "success" });
    } catch (error) {
      setStatus({ message: error instanceof Error ? error.message : "Could not update policies", tone: "error" });
    }
  }

  async function updatePolicy(policyId: string, updater: (policy: GovernancePolicy) => GovernancePolicy): Promise<void> {
    const nextPolicies = policies.map((policy) => (policy.id === policyId ? updater(policy) : policy));
    setPolicies(nextPolicies);
    setPolicySavingId(policyId);
    await persistPolicies(nextPolicies, "Governance policies updated");
    setPolicySavingId(null);
  }

  const settingsPanel =
    tab === "general" ? (
      <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">General</h2>
            <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Workspace identity and quality gate.</p>
          </div>
          <button className="inline-flex h-9 items-center rounded-md bg-[#C9973A] px-4 text-[13px] font-semibold text-black transition-colors hover:bg-[#d7aa55] disabled:cursor-wait disabled:opacity-60" disabled={saving} onClick={saveSettings} type="button">
            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
            Save
          </button>
        </div>
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_260px]">
          <label className="block">
            <span className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Org name</span>
            <input className="mt-2 h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[#08080d] px-3 text-[14px] text-white outline-none transition-colors focus:border-[#C9973A]" onChange={(event) => setSettings((current) => ({ ...current, name: event.target.value }))} value={settings.name} />
          </label>
          <div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Score threshold</span>
              <span className="rounded-md bg-[#C9973A]/15 px-2 py-1 text-[13px] font-semibold text-[#C9973A]">{settings.score_threshold}</span>
            </div>
            <input aria-label="Score threshold" className="mt-4 w-full accent-[#C9973A]" max={100} min={0} onChange={(event) => setSettings((current) => ({ ...current, score_threshold: Number(event.target.value) }))} type="range" value={settings.score_threshold} />
          </div>
        </div>
      </section>
    ) : (
      <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Notifications</h2>
            <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Slack alerts for pull requests and stale high-usage skills.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="inline-flex h-9 items-center rounded-md border border-[#C9973A]/60 px-4 text-[13px] font-semibold text-[#C9973A] transition-colors hover:bg-[#C9973A]/10 disabled:cursor-wait disabled:opacity-60" disabled={testing || !slackValue} onClick={sendTestNotification} type="button">
              {testing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Bell className="mr-2 h-4 w-4" />}
              Test
            </button>
            <button className="inline-flex h-9 items-center rounded-md bg-[#C9973A] px-4 text-[13px] font-semibold text-black transition-colors hover:bg-[#d7aa55] disabled:cursor-wait disabled:opacity-60" disabled={saving} onClick={saveSettings} type="button">
              {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
              Save
            </button>
          </div>
        </div>
        <label className="block">
          <span className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Slack webhook URL</span>
          <input className="mt-2 h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-[#08080d] px-3 font-mono text-[13px] text-white outline-none transition-colors focus:border-[#C9973A]" onChange={(event) => setSettings((current) => ({ ...current, slack_webhook_url: event.target.value }))} placeholder="https://hooks.slack.com/services/..." value={slackValue} />
        </label>
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          <Toggle checked={settings.notify_on_pr} label="Pull request alerts" onChange={(value) => setSettings((current) => ({ ...current, notify_on_pr: value }))} />
          <Toggle checked={settings.notify_on_stale} label="Stale skill alerts" onChange={(value) => setSettings((current) => ({ ...current, notify_on_stale: value }))} />
        </div>
      </section>
    );

  return (
    <div className="space-y-8">
      {settingsPanel}

      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-6">
        <div className="mb-6">
          <h2 className="text-[20px] font-semibold text-[color:var(--text-primary)]">Governance policies</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Define the score and freshness rules that guard how Skillayer evaluates your repositories.</p>
        </div>
        <div className="space-y-4">
          {policies.map((policy) => (
            <article className="rounded-[22px] border border-[color:var(--bg-border)] bg-black/15 p-5" key={policy.id}>
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <div className="text-[17px] font-semibold text-[color:var(--text-primary)]">{policy.name}</div>
                  <div className="mt-1 text-[13px] text-[color:var(--text-secondary)]">
                    {policy.type === "min_score" ? "Block PRs when Skilgen Score drops below threshold." : null}
                    {policy.type === "max_staleness_days" ? "Alert when skills haven't been refreshed recently." : null}
                    {policy.type === "min_groundedness" ? "Set a minimum groundedness requirement before a repo is considered healthy." : null}
                    {policy.type === "required_categories" ? "Require key skill categories to be covered before a repo is considered complete." : null}
                  </div>
                </div>
                <button className={`relative h-7 w-12 rounded-full ${policy.enabled ? "bg-[#C9973A]" : "bg-[color:var(--bg-border)]"}`} disabled={policySavingId === policy.id} onClick={() => void updatePolicy(policy.id, (current) => ({ ...current, enabled: !current.enabled }))} type="button">
                  <span className={`absolute top-1 h-5 w-5 rounded-full ${policy.enabled ? "right-1 bg-black" : "left-1 bg-[color:var(--text-tertiary)]"}`} />
                </button>
              </div>
              <div className="mt-5 grid gap-4 md:grid-cols-3">
                <label className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">
                  Threshold
                  <input className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[#08080d] px-3 text-[14px] text-[color:var(--text-primary)]" disabled={Array.isArray(policy.threshold)} onChange={(event) => void updatePolicy(policy.id, (current) => ({ ...current, threshold: Number(event.target.value) || 0 }))} type="number" value={Array.isArray(policy.threshold) ? 0 : Number(policy.threshold ?? 0)} />
                </label>
                <label className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">
                  Action
                  <select className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[#08080d] px-3 text-[14px] text-[color:var(--text-primary)]" onChange={(event) => void updatePolicy(policy.id, (current) => ({ ...current, action: event.target.value as GovernancePolicy["action"] }))} value={policy.action}>
                    <option value="warn">warn</option>
                    <option value="block_pr">block_pr</option>
                    <option value="notify_slack">notify_slack</option>
                  </select>
                </label>
                <div className="rounded-xl border border-[color:var(--bg-border)] bg-[#08080d] px-4 py-3">
                  <div className="text-[12px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Scope</div>
                  <div className="mt-2 text-[14px] text-[color:var(--text-primary)]">{policy.scope}</div>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      {status ? <StatusNotice status={status} /> : null}
    </div>
  );
}

function Toggle({ checked, label, onChange }: { checked: boolean; label: string; onChange: (checked: boolean) => void }): ReactElement {
  return (
    <button aria-pressed={checked} className="flex min-h-[56px] items-center justify-between rounded-lg border border-[color:var(--bg-border)] bg-[#08080d] px-4 text-left transition-colors hover:border-[#C9973A]/50" onClick={() => onChange(!checked)} type="button">
      <span className="text-[14px] font-medium text-[color:var(--text-primary)]">{label}</span>
      <span className={checked ? "relative h-6 w-11 rounded-full bg-[#C9973A]" : "relative h-6 w-11 rounded-full bg-[color:var(--bg-border)]"}>
        <span className={checked ? "absolute right-1 top-1 h-4 w-4 rounded-full bg-black" : "absolute left-1 top-1 h-4 w-4 rounded-full bg-[color:var(--text-tertiary)]"} />
      </span>
    </button>
  );
}

function StatusNotice({ status }: { status: NonNullable<StatusState> }): ReactElement {
  return (
    <div className={status.tone === "success" ? "flex items-center gap-2 rounded-md border border-[#3dd68c]/30 bg-[#3dd68c]/10 px-3 py-2 text-[13px] font-medium text-[#91efbd]" : "rounded-md border border-[color:var(--accent-red)]/30 bg-[color:var(--accent-red)]/10 px-3 py-2 text-[13px] font-medium text-[color:var(--accent-red)]"}>
      {status.tone === "success" ? <CheckCircle2 className="h-4 w-4" /> : null}
      {status.message}
    </div>
  );
}
