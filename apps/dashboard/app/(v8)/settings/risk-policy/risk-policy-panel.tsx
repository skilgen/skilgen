"use client";

import { useMemo, useState } from "react";
import { Save } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type AgentRiskPolicy = {
  critical_threshold: number;
  high_threshold: number;
  medium_threshold: number;
  critical_requires_danger_signal: boolean;
  full_access_score_floor: number;
  dangerous_command_score_floor: number;
  sensitive_path_score_floor: number;
  unknown_external_score_floor: number;
  unapproved_mcp_score_floor: number;
  dangerous_command_patterns: string[];
  sensitive_path_patterns: string[];
  approved_external_domains: string[];
  approved_mcp_tools: string[];
  updated_at?: string | null;
};

function authHeaders(accessToken: string): HeadersInit {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

function lines(values: string[]): string {
  return values.join("\n");
}

function splitLines(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function clampScore(value: number): number {
  return Number.isFinite(value) ? Math.max(0, Math.min(100, Math.round(value))) : 0;
}

export function RiskPolicyPanel({ accessToken, initial, orgId }: { accessToken: string; initial: AgentRiskPolicy; orgId: string }) {
  const [policy, setPolicy] = useState<AgentRiskPolicy>(initial);
  const [dangerousCommands, setDangerousCommands] = useState(lines(initial.dangerous_command_patterns));
  const [sensitivePaths, setSensitivePaths] = useState(lines(initial.sensitive_path_patterns));
  const [approvedDomains, setApprovedDomains] = useState(lines(initial.approved_external_domains));
  const [approvedTools, setApprovedTools] = useState(lines(initial.approved_mcp_tools));
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const requestPolicy = useMemo<AgentRiskPolicy>(() => ({
    ...policy,
    dangerous_command_patterns: splitLines(dangerousCommands),
    sensitive_path_patterns: splitLines(sensitivePaths),
    approved_external_domains: splitLines(approvedDomains),
    approved_mcp_tools: splitLines(approvedTools),
  }), [approvedDomains, approvedTools, dangerousCommands, policy, sensitivePaths]);

  function updateNumber(key: keyof AgentRiskPolicy, value: string) {
    const next = clampScore(Number(value));
    setPolicy((current) => ({ ...current, [key]: next }));
  }

  async function savePolicy() {
    setSaving(true);
    setStatus(null);
    try {
      const response = await fetch(`${API_URL}/v8/orgs/${orgId}/settings/risk-policy`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...authHeaders(accessToken) },
        body: JSON.stringify(requestPolicy),
      });
      if (!response.ok) {
        setStatus("Could not save policy.");
        return;
      }
      const saved = (await response.json()) as AgentRiskPolicy;
      setPolicy(saved);
      setDangerousCommands(lines(saved.dangerous_command_patterns));
      setSensitivePaths(lines(saved.sensitive_path_patterns));
      setApprovedDomains(lines(saved.approved_external_domains));
      setApprovedTools(lines(saved.approved_mcp_tools));
      setStatus("Policy saved.");
    } catch {
      setStatus("Could not save policy.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="space-y-4 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
      <div className="grid gap-3 md:grid-cols-3">
        <NumberInput label="Critical threshold" name="critical_threshold" onChange={updateNumber} value={policy.critical_threshold} />
        <NumberInput label="High threshold" name="high_threshold" onChange={updateNumber} value={policy.high_threshold} />
        <NumberInput label="Medium threshold" name="medium_threshold" onChange={updateNumber} value={policy.medium_threshold} />
        <NumberInput label="Full-access floor" name="full_access_score_floor" onChange={updateNumber} value={policy.full_access_score_floor} />
        <NumberInput label="Dangerous command floor" name="dangerous_command_score_floor" onChange={updateNumber} value={policy.dangerous_command_score_floor} />
        <NumberInput label="Sensitive path floor" name="sensitive_path_score_floor" onChange={updateNumber} value={policy.sensitive_path_score_floor} />
        <NumberInput label="Unknown API floor" name="unknown_external_score_floor" onChange={updateNumber} value={policy.unknown_external_score_floor} />
        <NumberInput label="Unapproved MCP floor" name="unapproved_mcp_score_floor" onChange={updateNumber} value={policy.unapproved_mcp_score_floor} />
        <label className="flex min-h-[72px] items-center gap-3 rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-sm font-semibold text-[color:var(--text-primary)]">
          <input
            checked={policy.critical_requires_danger_signal}
            className="h-4 w-4 accent-[color:var(--accent-primary)]"
            onChange={(event) => setPolicy((current) => ({ ...current, critical_requires_danger_signal: event.target.checked }))}
            type="checkbox"
          />
          Critical requires danger signal
        </label>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <TextArea label="Dangerous command patterns" onChange={setDangerousCommands} value={dangerousCommands} />
        <TextArea label="Sensitive path patterns" onChange={setSensitivePaths} value={sensitivePaths} />
        <TextArea label="Approved external domains" onChange={setApprovedDomains} value={approvedDomains} />
        <TextArea label="Approved MCP/tools" onChange={setApprovedTools} value={approvedTools} />
      </div>

      <div className="flex flex-wrap items-center justify-end gap-3">
        {status ? <p className="text-sm font-medium text-[color:var(--text-secondary)]" role="status">{status}</p> : null}
        <button
          className="inline-flex min-h-10 items-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-4 text-sm font-semibold text-black transition hover:bg-[color:var(--accent-bright)] disabled:cursor-not-allowed disabled:opacity-60"
          disabled={saving}
          onClick={() => void savePolicy()}
          type="button"
        >
          <Save className="h-4 w-4" />
          {saving ? "Saving" : "Save policy"}
        </button>
      </div>
    </section>
  );
}

function NumberInput({ label, name, onChange, value }: { label: string; name: keyof AgentRiskPolicy; onChange: (key: keyof AgentRiskPolicy, value: string) => void; value: number }) {
  return (
    <label className="block rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
      <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">{label}</span>
      <input
        className="mt-2 w-full rounded-md border border-[color:var(--bg-border)] bg-black/20 px-3 py-2 text-sm text-[color:var(--text-primary)]"
        max={100}
        min={0}
        onChange={(event) => onChange(name, event.target.value)}
        type="number"
        value={value}
      />
    </label>
  );
}

function TextArea({ label, onChange, value }: { label: string; onChange: (value: string) => void; value: string }) {
  return (
    <label className="block">
      <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">{label}</span>
      <textarea
        className="mt-2 min-h-36 w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 font-mono text-[12px] leading-5 text-[color:var(--text-primary)]"
        onChange={(event) => onChange(event.target.value)}
        value={value}
      />
    </label>
  );
}
