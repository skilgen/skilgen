"use client";

import { useState } from "react";

import type { LLMConfig, PolicyCheckResult, PolicyRule } from "../../../lib/data";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

export function LlmSettingsPanel({ accessToken, orgId, initialConfig }: { accessToken: string; orgId: string; initialConfig: LLMConfig | null }) {
  const [provider, setProvider] = useState(initialConfig?.provider ?? "skillayer");
  const [model, setModel] = useState(initialConfig?.model ?? "");
  const [endpointUrl, setEndpointUrl] = useState(initialConfig?.base_url ?? "");
  const [apiKey, setApiKey] = useState("");
  const [status, setStatus] = useState("");
  const providers = ["anthropic", "openai", "gemini", "custom"];

  async function save() {
    setStatus("Saving...");
    const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/llm-config`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify({ provider, model: model || "gpt-4o-mini", base_url: endpointUrl || null, api_key: apiKey || "" }),
    });
    setStatus(response.ok ? "Saved ✓" : "Could not save LLM config");
  }

  async function test() {
    setStatus("Testing...");
    const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/llm-config/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify({ provider, model: model || "gpt-4o-mini", base_url: endpointUrl || null, api_key: apiKey || "" }),
    });
    const body = (await response.json()) as { success?: boolean; response?: string | null; error?: string | null };
    setStatus(body.success ? `✓ Connected — ${body.response ?? "OK"}` : body.error || "Connection failed");
  }

  return (
    <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">LLM Configuration</h2>
      <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Control which LLM powers Skilgen analysis runs for your org.</p>
      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {providers.map((item) => (
          <button
            className={`rounded-xl border p-4 text-left transition-colors ${provider === item ? "border-[color:var(--accent-primary)] bg-[rgb(var(--accent-primary-rgb)/0.08)]" : "border-[color:var(--bg-border)] bg-[color:var(--bg-base)]"}`}
            key={item}
            onClick={() => setProvider(item)}
            type="button"
          >
            <div className="text-[15px] font-semibold text-[color:var(--text-primary)]">{item === "skillayer" ? "Skillayer Hosted" : item.replaceAll("_", " ")}</div>
            <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">{item === "skillayer" ? "Default hosted provider." : "Bring your own provider configuration."}</div>
          </button>
        ))}
      </div>
      {provider ? (
        <div className="mt-5 space-y-3">
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 p-3 text-[12px] text-amber-300">Source code is analysed using this provider. Ensure your data processing agreement covers AI-assisted code analysis.</div>
          <Input label="API Key" onChange={setApiKey} placeholder={initialConfig?.api_key_hint ? `Current key: ${initialConfig.api_key_hint}` : "sk-..."} type="password" value={apiKey} />
          <Input label="Model" onChange={setModel} placeholder="claude-3-5-sonnet-20241022" value={model} />
          <Input label="Endpoint URL" onChange={setEndpointUrl} placeholder="https://..." value={endpointUrl} />
        </div>
      ) : null}
      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button className="rounded-full bg-[color:var(--accent-primary)] px-5 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)]" onClick={save} type="button">Save LLM config</button>
        <button className="rounded-full border border-[color:var(--bg-border)] px-4 py-2 text-[13px] font-semibold text-[color:var(--text-primary)]" onClick={test} type="button">Test connection</button>
        {status ? <span className={`text-[12px] ${status.includes("✓") || status.includes("Saved") ? "text-green-400" : status.includes("Could") || status.includes("failed") ? "text-red-300" : "text-[color:var(--text-tertiary)]"}`}>{status}</span> : null}
      </div>
    </section>
  );
}

export function PolicySettingsPanel({ accessToken, orgId, initialPolicies, templates, initialCheck }: { accessToken: string; orgId: string; initialPolicies: PolicyRule[]; templates: PolicyRule[]; initialCheck: PolicyCheckResult | null }) {
  const [policies, setPolicies] = useState(initialPolicies);
  const [check, setCheck] = useState(initialCheck);
  const [status, setStatus] = useState("");

  async function runCheck() {
    setStatus("Checking...");
    const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/policy-check`, { headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` } });
    const body = (await response.json()) as PolicyCheckResult;
    setCheck(body);
    setStatus(body.passed ? "All policies passed" : "Policy violations found");
  }

  async function addTemplate(template: PolicyRule) {
    const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/policies`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify(template),
    });
    if (response.ok) setPolicies([(await response.json()) as PolicyRule, ...policies]);
  }

  async function toggle(policy: PolicyRule) {
    const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/policies/${policy.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify({ enabled: !policy.enabled }),
    });
    if (response.ok) {
      const updated = (await response.json()) as PolicyRule;
      setPolicies(policies.map((item) => (item.id === policy.id ? updated : item)));
    }
  }

  return (
    <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Policy Enforcement</h2>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Org-wide rules enforced across all repos.</p>
        </div>
        <button className="rounded-full border border-[color:var(--bg-border)] px-4 py-2 text-[13px] font-semibold" onClick={runCheck} type="button">Run check now</button>
      </div>
      {check ? <div className={`mt-4 rounded-xl border p-3 text-[13px] ${check.passed ? "border-green-500/20 bg-green-500/10 text-green-300" : "border-red-500/20 bg-red-500/10 text-red-300"}`}>{check.passed ? "✓ All policies passed" : `✗ ${check.error_count} violations · ${check.warning_count} warnings`}</div> : null}
      {status ? <div className="mt-3 text-[12px] text-[color:var(--text-tertiary)]">{status}</div> : null}
      <details className="mt-4 rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
        <summary className="cursor-pointer text-[13px] font-semibold text-[color:var(--text-primary)]">CI integration (GitHub Actions)</summary>
        <pre className="mt-3 overflow-auto rounded-lg bg-black/40 px-4 py-3 font-mono text-[12px] text-[color:var(--text-secondary)]">{`- name: Skillayer Policy Check\n  run: |\n    curl -f https://api.skillayer.com/orgs/$ORG_ID/policy-check/ci \\\n      || (echo "Skillayer policy violations found" && exit 1)`}</pre>
      </details>
      <div className="mt-5 divide-y divide-[color:var(--bg-elevated)]">
        {policies.length === 0 ? <div className="py-4 text-[13px] text-[color:var(--text-secondary)]">No policies configured. Add from templates below.</div> : null}
        {policies.map((policy) => (
          <div className="flex items-center justify-between gap-4 py-3" key={policy.id}>
            <div>
              <div className="text-[14px] font-semibold text-[color:var(--text-primary)]">{policy.name}</div>
              <div className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{policy.rule_type}</div>
            </div>
            <div className="flex items-center gap-3">
              <span className={policy.violation_count > 0 ? "text-[12px] text-red-300" : "text-[12px] text-[color:var(--text-tertiary)]"}>{policy.violation_count} violations</span>
              <button className="rounded-full border border-[color:var(--bg-border)] px-3 py-1.5 text-[12px]" onClick={() => void toggle(policy)} type="button">{policy.enabled ? "Enabled" : "Disabled"}</button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-5 flex gap-3 overflow-x-auto pb-2">
        {templates.map((template) => (
          <div className="min-w-[240px] rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-4 py-3" key={`${template.rule_type}-${template.name}`}>
            <div className="text-[13px] font-semibold text-[color:var(--text-primary)]">{template.name}</div>
            <p className="mt-1 text-[12px] text-[color:var(--text-secondary)]">{template.description}</p>
            <button className="mt-3 text-[12px] font-semibold text-[color:var(--accent-primary)]" onClick={() => void addTemplate(template)} type="button">Add →</button>
          </div>
        ))}
      </div>
    </section>
  );
}

export function SiemSettingsPanel({ accessToken, orgId }: { accessToken: string; orgId: string }) {
  const [url, setUrl] = useState("");
  const [secret, setSecret] = useState("");
  const [enabled, setEnabled] = useState(false);
  const [status, setStatus] = useState("");
  async function save() {
    setStatus("Saving...");
    const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/audit-log/webhook`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify({ webhook_url: url, secret: secret || null, enabled, event_filter: "warnings" }),
    });
    setStatus(response.ok ? "Saved ✓" : "Could not save SIEM webhook");
  }
  return (
    <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">SIEM Export</h2>
      <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">Forward critical and warning audit events to Splunk, Datadog, Panther, or any webhook endpoint.</p>
      <div className="mt-5 space-y-3">
        <Input label="Webhook URL" onChange={setUrl} placeholder="https://..." value={url} />
        <Input label="Webhook Secret" onChange={setSecret} placeholder="optional" type="password" value={secret} />
        <label className="flex items-center gap-2 text-[13px] text-[color:var(--text-secondary)]"><input checked={enabled} onChange={(event) => setEnabled(event.target.checked)} type="checkbox" /> Forward events to SIEM webhook</label>
      </div>
      <button className="mt-5 rounded-full bg-[color:var(--accent-primary)] px-5 py-2.5 text-[13px] font-semibold text-[color:var(--bg-base)]" onClick={save} type="button">Save SIEM webhook</button>
      {status ? <span className="ml-3 text-[12px] text-[color:var(--text-tertiary)]">{status}</span> : null}
    </section>
  );
}

function Input({ label, value, onChange, placeholder, type = "text" }: { label: string; value: string; onChange: (value: string) => void; placeholder?: string; type?: string }) {
  return (
    <label className="block text-[12px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">
      {label}
      <input className="mt-2 h-11 w-full rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 text-[13px] text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]" onChange={(event) => onChange(event.target.value)} placeholder={placeholder} type={type} value={value} />
    </label>
  );
}
