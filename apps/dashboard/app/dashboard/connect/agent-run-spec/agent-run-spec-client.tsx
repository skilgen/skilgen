"use client";

import { useState } from "react";
import { CheckCircle2, Clipboard, Eye, EyeOff } from "lucide-react";

function maskKey(key: string): string {
  if (!key) return "No API key available";
  return `${key.slice(0, 6)}••••••••${key.slice(-4)}`;
}

export function AgentRunSpecClient({ apiKey, webhookUrl, example }: { apiKey: string; webhookUrl: string; example: string }) {
  const [revealed, setRevealed] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  async function copy(label: string, value: string) {
    await navigator.clipboard.writeText(value);
    setCopied(label);
    setTimeout(() => setCopied(null), 1500);
  }

  return (
    <div className="space-y-4">
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="grid gap-4 lg:grid-cols-[1fr_340px]">
          <div>
            <label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Webhook URL</label>
            <div className="mt-2 flex min-w-0 items-center gap-2 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <code className="min-w-0 flex-1 break-all font-mono text-[12px] text-[color:var(--text-primary)]">{webhookUrl}</code>
              <button className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-[12px] font-semibold text-[color:var(--text-primary)] hover:bg-white/5" onClick={() => copy("url", webhookUrl)} type="button">
                {copied === "url" ? <CheckCircle2 className="h-4 w-4 text-[color:var(--accent-green)]" /> : <Clipboard className="h-4 w-4" />}
                {copied === "url" ? "Copied" : "Copy"}
              </button>
            </div>
          </div>
          <div>
            <label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">Authorization</label>
            <div className="mt-2 flex items-center gap-2 rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
              <code className="min-w-0 flex-1 truncate font-mono text-[12px] text-[color:var(--text-primary)]">Bearer {revealed ? apiKey || "sk-..." : maskKey(apiKey)}</code>
              <button className="rounded-md border border-[color:var(--bg-border)] p-2 text-[color:var(--text-secondary)] hover:bg-white/5" onClick={() => setRevealed((value) => !value)} type="button" aria-label={revealed ? "Hide API key" : "Reveal API key"}>
                {revealed ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
              <button className="rounded-md border border-[color:var(--bg-border)] p-2 text-[color:var(--text-secondary)] hover:bg-white/5" onClick={() => copy("key", apiKey)} type="button" aria-label="Copy API key" disabled={!apiKey}>
                {copied === "key" ? <CheckCircle2 className="h-4 w-4 text-[color:var(--accent-green)]" /> : <Clipboard className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="mb-3 flex items-center justify-between gap-3">
          <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">Example request</h2>
          <button className="inline-flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-[12px] font-semibold text-[color:var(--text-primary)] hover:bg-white/5" onClick={() => copy("example", example)} type="button">
            {copied === "example" ? <CheckCircle2 className="h-4 w-4 text-[color:var(--accent-green)]" /> : <Clipboard className="h-4 w-4" />}
            {copied === "example" ? "Copied" : "Copy example"}
          </button>
        </div>
        <pre className="max-h-[520px] overflow-auto rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4 font-mono text-[12px] leading-6 text-[color:var(--text-primary)]">
          <code>{example}</code>
        </pre>
      </section>
    </div>
  );
}
