import { getV8AuditLog } from "../../../../lib/data";
import { loadAuditOrg } from "../common";

function metadataText(metadata: Record<string, unknown>, key: string): string | null {
  const value = metadata[key];
  return typeof value === "string" && value ? value : null;
}

function metadataNumber(metadata: Record<string, unknown>, key: string): number | null {
  const value = metadata[key];
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() && Number.isFinite(Number(value))) return Number(value);
  return null;
}

function metadataList(metadata: Record<string, unknown>, key: string): string[] {
  const value = metadata[key];
  if (Array.isArray(value)) return value.map((item) => String(item)).filter(Boolean);
  return [];
}

export default async function AuditEventLogPage() {
  const { accessToken, orgId } = await loadAuditOrg();
  const audit = orgId ? await getV8AuditLog(accessToken, orgId, new URLSearchParams({ limit: "50" })) : null;
  const events = audit?.events ?? [];
  if (audit === null) {
    return (
      <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-sm text-[color:var(--text-secondary)]">
        <p className="text-[15px] font-semibold text-[color:var(--text-primary)]">Audit could not reach the API.</p>
        <p className="mx-auto mt-2 max-w-xl leading-6">Refresh after sign-in. Existing audit events will appear here once the authenticated API call succeeds.</p>
      </div>
    );
  }
  return (
    <div className="overflow-x-auto border-y border-[color:var(--bg-border)]">
      <table className="w-full min-w-[980px] border-collapse text-left text-[13px]">
        <thead className="text-[11px] uppercase tracking-wide text-[color:var(--text-tertiary)]">
          <tr>
            {["Time", "Event", "Actor", "Repo", "Severity", "Chain", "Summary"].map((heading) => (
              <th className="border-b border-[color:var(--bg-border)] px-3 py-3 font-semibold" key={heading}>{heading}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr className="border-b border-[color:var(--bg-elevated)]" key={event.id}>
              <td className="whitespace-nowrap px-3 py-3 font-mono text-[12px] text-[color:var(--text-secondary)]">{new Date(event.created_at).toLocaleString()}</td>
              <td className="px-3 py-3 font-mono text-[12px]">{event.event_type}</td>
              <td className="px-3 py-3">{event.actor_login ?? "system"}</td>
              <td className="px-3 py-3">{event.repo_name ?? event.repo_id ?? "-"}</td>
              <td className="px-3 py-3 capitalize">{event.severity}</td>
              <td className="px-3 py-3 font-mono text-[11px] text-[color:var(--text-secondary)]">{event.chain ? `#${event.chain.sequence} ${event.chain.root_hash.slice(0, 12)}` : "not chained yet"}</td>
              <td className="max-w-[520px] px-3 py-3">
                <div className="font-medium text-[color:var(--text-primary)]">{event.summary}</div>
                <div className="mt-1 flex flex-wrap gap-1.5 text-[11px] text-[color:var(--text-secondary)]">
                  {metadataText(event.metadata, "model") ? <span className="rounded-sm border border-[color:var(--bg-border)] px-1.5 py-0.5">{metadataText(event.metadata, "model")}</span> : null}
                  {metadataText(event.metadata, "reasoning_tier") ? <span className="rounded-sm border border-[color:var(--bg-border)] px-1.5 py-0.5">reasoning {metadataText(event.metadata, "reasoning_tier")}</span> : null}
                  {metadataText(event.metadata, "access_scope") ? <span className="rounded-sm border border-[color:var(--bg-border)] px-1.5 py-0.5">{metadataText(event.metadata, "access_scope")}</span> : null}
                  {metadataNumber(event.metadata, "tokens_total") ? <span className="rounded-sm border border-[color:var(--bg-border)] px-1.5 py-0.5">{metadataNumber(event.metadata, "tokens_total")?.toLocaleString()} tokens</span> : null}
                  {metadataNumber(event.metadata, "cost_usd") ? <span className="rounded-sm border border-[color:var(--bg-border)] px-1.5 py-0.5">est. ${metadataNumber(event.metadata, "cost_usd")?.toFixed(2)}</span> : null}
                  {metadataList(event.metadata, "tool_permissions").slice(0, 4).map((tool) => (
                    <span className="rounded-sm border border-[color:var(--bg-border)] px-1.5 py-0.5" key={`${event.id}-${tool}`}>{tool}</span>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {events.length === 0 ? <div className="py-12 text-center text-sm text-[color:var(--text-secondary)]">No audit events recorded yet.</div> : null}
    </div>
  );
}
