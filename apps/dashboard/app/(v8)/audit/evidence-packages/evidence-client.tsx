"use client";

import { PackagePlus } from "lucide-react";
import { useState } from "react";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type V8EvidencePackage = {
  job_id: string;
  status: string;
  result?: Record<string, unknown>;
  created_at?: string;
};

export function EvidencePackagesClient({ accessToken, orgId }: { accessToken: string; orgId: string }) {
  const [control, setControl] = useState("SOC2 CC8.1");
  const [result, setResult] = useState<V8EvidencePackage | null>(null);
  const [busy, setBusy] = useState(false);

  async function createPackage() {
    setBusy(true);
    const now = new Date();
    const start = new Date(now);
    start.setDate(now.getDate() - 90);
    const response = await fetch(`${CLIENT_API_URL}/v8/orgs/${orgId}/audit/evidence-packages`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: JSON.stringify({ control, period_start: start.toISOString(), period_end: now.toISOString() }),
    });
    setResult(response.ok ? ((await response.json()) as V8EvidencePackage) : null);
    setBusy(false);
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <input className="h-10 min-w-[260px] rounded-md border border-[color:var(--bg-border)] bg-black/15 px-3 text-sm" onChange={(event) => setControl(event.target.value)} value={control} />
        <button className="inline-flex h-10 items-center gap-2 rounded-md bg-[color:var(--accent-primary)] px-3 text-sm font-semibold text-[color:var(--bg-base)]" disabled={busy || !orgId} onClick={createPackage} type="button">
          <PackagePlus className="h-4 w-4" />
          {busy ? "Queueing" : "Create package"}
        </button>
      </div>
      {result ? <pre className="border-y border-[color:var(--bg-border)] py-4 font-mono text-xs text-[color:var(--text-secondary)]">{JSON.stringify(result, null, 2)}</pre> : null}
    </div>
  );
}
