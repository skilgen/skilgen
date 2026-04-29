"use client";

import { CheckCircle2, Eye, EyeOff, KeyRound, Loader2, PlugZap, RefreshCw, Server, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";

import type { LLMConfig } from "../../../lib/data";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

const PROVIDERS = [
  { id: "anthropic", name: "Anthropic", note: "Claude models", models: ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-3-5"], placeholder: "sk-ant-...", hint: "claude-opus-4-5, claude-sonnet-4-5, claude-haiku-3-5" },
  { id: "openai", name: "OpenAI", note: "GPT-4o, o-series", models: ["gpt-4o", "gpt-4o-mini", "o3-mini", "o1-mini", "gpt-4-turbo"], placeholder: "sk-...", hint: "gpt-4o, gpt-4o-mini, o3-mini, o1-mini, gpt-4-turbo" },
  { id: "gemini", name: "Gemini", note: "Google AI", models: ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"], placeholder: "AIza...", hint: "gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash" },
  { id: "custom", name: "Custom", note: "OpenAI-compatible", models: ["llama-3.1-70b"], placeholder: "Your API key", hint: "your-model-id (depends on your endpoint)" },
] as const;

type ProviderId = (typeof PROVIDERS)[number]["id"];

function headers(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

function providerName(provider: string): string {
  return PROVIDERS.find((item) => item.id === provider)?.name ?? provider;
}

function emptyConfig(): LLMConfig {
  return {
    provider: "anthropic",
    model: "claude-sonnet-4-5",
    base_url: null,
    api_key_hint: null,
    is_configured: false,
  };
}

function commonFix(error: string, model: string): string | null {
  const lower = error.toLowerCase();
  if (lower.includes("max_tokens") || lower.includes("max_completion_tokens")) {
    return "ℹ This model requires max_completion_tokens. Skillayer has applied this fix automatically. Try Test connection again.";
  }
  if (lower.includes("system") && lower.includes("role")) {
    return "ℹ This model does not support system prompts. Skillayer has applied the o-series fix. Try again.";
  }
  if (lower.includes("invalid api key") || lower.includes("401")) {
    return "ℹ Check that your API key is correct and has not expired.";
  }
  if (lower.includes("model not found") || lower.includes("404")) {
    return `ℹ Model name '${model}' was not found. Check the exact model ID.`;
  }
  return null;
}

export function LLMConfigPanel({ accessToken, initialConfig, orgId }: { accessToken: string; initialConfig: LLMConfig | null; orgId: string }) {
  const initial = initialConfig ?? emptyConfig();
  const [provider, setProvider] = useState<ProviderId>((PROVIDERS.some((item) => item.id === initial.provider) ? initial.provider : "custom") as ProviderId);
  const [model, setModel] = useState(initial.model ?? "claude-sonnet-4-5");
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [rotating, setRotating] = useState(!initial.is_configured);
  const [baseUrl, setBaseUrl] = useState(initial.base_url ?? "");
  const [configured, setConfigured] = useState(initial.is_configured);
  const [keyHint, setKeyHint] = useState(initial.api_key_hint);
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [removing, setRemoving] = useState(false);
  const [status, setStatus] = useState<{ tone: "ok" | "warn" | "error"; text: string }>({
    tone: initial.is_configured ? "ok" : "warn",
    text: initial.is_configured ? `Using ${providerName(initial.provider ?? "")} · ${initial.model ?? "model"} · key ending in ${initial.api_key_hint ?? "saved"}` : "Choose a provider and save an API key to enable Improve with AI.",
  });
  const [fixHint, setFixHint] = useState<string | null>(null);

  const selectedProvider = useMemo(() => PROVIDERS.find((item) => item.id === provider) ?? PROVIDERS[0], [provider]);
  const needsBaseUrl = provider === "custom";

  async function saveConfig() {
    if (!apiKey.trim()) {
      setStatus({ tone: "error", text: "Paste an API key before saving this provider." });
      return;
    }
    setSaving(true);
    setFixHint(null);
    setStatus({ tone: "warn", text: "Saving model configuration..." });
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/llm-config`, {
        method: "POST",
        headers: headers(accessToken),
        body: JSON.stringify({
          provider,
          model: model.trim(),
          api_key: apiKey.trim(),
          base_url: baseUrl.trim() || null,
        }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Could not save AI model configuration.");
      setConfigured(true);
      setRotating(false);
      setApiKey("");
      setKeyHint(body.api_key_hint ?? keyHint ?? "saved");
      setStatus({ tone: "ok", text: `${providerName(provider)} configuration saved.` });
    } catch (error) {
      setStatus({ tone: "error", text: error instanceof Error ? error.message : "Could not save AI model configuration." });
    } finally {
      setSaving(false);
    }
  }

  async function testConnection() {
    setTesting(true);
    setFixHint(null);
    setStatus({ tone: "warn", text: "Testing provider connection..." });
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/llm-config/test`, {
        method: "POST",
        headers: headers(accessToken),
        body: JSON.stringify({ provider, model: model.trim(), api_key: apiKey.trim(), base_url: baseUrl.trim() || null }),
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok || body.success === false) throw new Error(body.error || body.detail || "Connection test failed.");
      setStatus({ tone: "ok", text: `Connected! Response: ${body.response ?? "OK"}` });
    } catch (error) {
      const text = error instanceof Error ? error.message : "Connection test failed.";
      setStatus({ tone: "error", text });
      setFixHint(commonFix(text, model.trim()));
    } finally {
      setTesting(false);
    }
  }

  async function removeConfig() {
    setRemoving(true);
    setStatus({ tone: "warn", text: "Removing saved model configuration..." });
    try {
      const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/llm-config`, {
        method: "DELETE",
        headers: headers(accessToken),
      });
      if (!response.ok && response.status !== 404) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || "Could not remove model configuration.");
      }
      setConfigured(false);
      setRotating(true);
      setKeyHint(null);
      setApiKey("");
      setStatus({ tone: "warn", text: "Configuration removed. AI actions will ask users to configure a provider." });
    } catch (error) {
      setStatus({ tone: "error", text: error instanceof Error ? error.message : "Could not remove model configuration." });
    } finally {
      setRemoving(false);
    }
  }

  return (
    <section id="ai-model" className="mb-8 scroll-mt-6 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
      <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <PlugZap className="h-5 w-5 text-[color:var(--accent-primary)]" />
            <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">AI Model</h2>
          </div>
          <p className="mt-2 text-[13px] leading-6 text-[color:var(--text-secondary)]">Configure the model used by Improve with AI and skill authoring workflows.</p>
        </div>
        <span className={configured ? "rounded-full bg-[rgb(var(--accent-green-rgb)/0.14)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-green)]" : "rounded-full bg-amber-500/15 px-3 py-1 text-[12px] font-semibold text-amber-300"}>
          {configured ? "Configured" : "Action required"}
        </span>
      </div>

      <div className={`mb-5 rounded-md border px-4 py-3 text-[13px] ${status.tone === "ok" ? "border-green-500/30 bg-green-500/10 text-green-200" : status.tone === "error" ? "border-red-500/30 bg-red-500/10 text-red-200" : "border-amber-500/30 bg-amber-500/10 text-amber-200"}`}>
        {status.text}
        {fixHint ? <div className="mt-2 border-t border-current/20 pt-2 text-[12px] leading-5">{fixHint}</div> : null}
      </div>

      <div className="grid gap-3 lg:grid-cols-4">
        {PROVIDERS.map((item) => {
          const active = item.id === provider;
          return (
            <button
              className={active ? "rounded-lg border border-[color:var(--accent-primary)] bg-[rgb(var(--accent-primary-rgb)/0.12)] p-4 text-left" : "rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 text-left transition-colors hover:border-[rgb(var(--accent-primary-rgb)/0.4)]"}
              key={item.id}
              onClick={() => {
                setProvider(item.id);
                setModel(item.models[0]);
              }}
              type="button"
            >
              <div className="flex items-center justify-between gap-3">
                <div className="text-[14px] font-semibold text-[color:var(--text-primary)]">{item.name}</div>
                {active ? <CheckCircle2 className="h-4 w-4 text-[color:var(--accent-primary)]" /> : null}
              </div>
              <div className="mt-2 text-[12px] text-[color:var(--text-secondary)]">{item.note}</div>
            </button>
          );
        })}
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <label className="block">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Model</span>
          <input className="mt-2 h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-black/20 px-3 font-mono text-[13px] text-[color:var(--text-primary)] outline-none focus:border-[color:var(--accent-primary)]" list="llm-models" onChange={(event) => setModel(event.target.value)} value={model} />
          <datalist id="llm-models">
            {selectedProvider.models.map((option) => <option key={option} value={option} />)}
          </datalist>
          <span className="mt-1.5 block text-[11px] text-[color:var(--text-tertiary)]">Suggested IDs: {selectedProvider.hint}</span>
        </label>

        <label className="block">
          <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">API key</span>
          <div className="mt-2 flex">
            <input
              className="h-11 min-w-0 flex-1 rounded-l-md border border-[color:var(--bg-border)] bg-black/20 px-3 font-mono text-[13px] text-[color:var(--text-primary)] outline-none placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]"
              onChange={(event) => setApiKey(event.target.value)}
              placeholder={configured && !rotating ? `••••••...${keyHint ?? ""}` : selectedProvider.placeholder}
              type={showKey ? "text" : "password"}
              value={apiKey}
            />
            <button aria-label={showKey ? "Hide API key" : "Show API key"} className="inline-flex h-11 w-11 items-center justify-center border-y border-r border-[color:var(--bg-border)] text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]" onClick={() => setShowKey((value) => !value)} type="button">
              {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
            <button className="inline-flex h-11 items-center justify-center rounded-r-md border-y border-r border-[color:var(--bg-border)] px-3 text-[12px] font-semibold text-[color:var(--text-secondary)] hover:text-[color:var(--text-primary)]" onClick={() => setRotating(true)} type="button">
              <RefreshCw className="mr-2 h-4 w-4" />
              Rotate
            </button>
          </div>
        </label>

        {needsBaseUrl ? (
          <label className="block">
            <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Custom base URL</span>
            <div className="relative mt-2">
              <Server className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--text-tertiary)]" />
              <input className="h-11 w-full rounded-md border border-[color:var(--bg-border)] bg-black/20 pl-9 pr-3 text-[13px] text-[color:var(--text-primary)] outline-none placeholder:text-[color:var(--text-tertiary)] focus:border-[color:var(--accent-primary)]" onChange={(event) => setBaseUrl(event.target.value)} placeholder="https://my-ollama.example.com/v1" value={baseUrl} />
            </div>
          </label>
        ) : null}
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button className="inline-flex h-10 items-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)] disabled:cursor-wait disabled:opacity-60" disabled={saving} onClick={saveConfig} type="button">
          {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <KeyRound className="mr-2 h-4 w-4" />}
          Save config
        </button>
        <button className="inline-flex h-10 items-center rounded-md border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-primary)] hover:border-[color:var(--accent-primary)] disabled:cursor-wait disabled:opacity-60" disabled={testing || !apiKey.trim()} onClick={testConnection} type="button">
          {testing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <PlugZap className="mr-2 h-4 w-4" />}
          Test connection
        </button>
        <button className="inline-flex h-10 items-center rounded-md border border-red-500/30 px-4 text-[13px] font-semibold text-red-200 hover:bg-red-500/10 disabled:cursor-wait disabled:opacity-60" disabled={removing || !configured} onClick={removeConfig} type="button">
          {removing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Trash2 className="mr-2 h-4 w-4" />}
          Remove config
        </button>
      </div>
    </section>
  );
}
