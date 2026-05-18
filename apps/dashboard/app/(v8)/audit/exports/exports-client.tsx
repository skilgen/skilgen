"use client";

import { Download } from "lucide-react";
import { useState } from "react";

function clientApiUrl() {
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
  if (typeof window !== "undefined" && ["127.0.0.1", "localhost"].includes(window.location.hostname)) {
    return "http://127.0.0.1:8000";
  }
  return "https://api.skillayer.com";
}

const formats = ["csv", "json", "splunk_hec", "datadog_cloud_siem", "sumo_logic", "microsoft_sentinel", "raw_ndjson_s3"];

type V8AuditExportResponse = {
  format: string;
  event_count: number;
  content_type: string;
  body: string | Record<string, unknown> | Array<Record<string, unknown>> | null;
  destination: string | null;
  audit_event_logged: boolean;
};

export function AuditExportsClient({ accessToken, orgId }: { accessToken: string; orgId: string }) {
  const [format, setFormat] = useState("csv");
  const [result, setResult] = useState<V8AuditExportResponse | null>(null);
  const [busy, setBusy] = useState(false);

  async function runExport() {
    setBusy(true);
    const response = await fetch(`${clientApiUrl()}/v8/orgs/${orgId}/audit/exports`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: JSON.stringify({ format }),
    });
    setResult(response.ok ? ((await response.json()) as V8AuditExportResponse) : null);
    setBusy(false);
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <select className="h-10 rounded-md border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm" onChange={(event) => setFormat(event.target.value)} value={format}>
          {formats.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
        <button className="inline-flex h-10 items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 text-sm font-semibold text-[color:var(--bg-base)]" disabled={busy || !orgId} onClick={runExport} type="button">
          <Download className="h-4 w-4" />
          {busy ? "Exporting" : "Export"}
        </button>
      </div>
      {result ? (
        <pre className="max-h-[520px] overflow-auto border-y border-[color:var(--bg-border)] py-4 font-mono text-xs leading-5 text-[color:var(--text-secondary)]">{JSON.stringify(result, null, 2)}</pre>
      ) : null}
    </div>
  );
}
