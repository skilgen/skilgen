import { Archive, CheckCircle2, Clock3, ShieldCheck } from "lucide-react";

import { getV8AuditWormTargets } from "../../../../lib/data";
import { loadAuditOrg } from "../common";

export default async function AuditWormRootsPage() {
  const { accessToken, orgId } = await loadAuditOrg();
  const targets = orgId ? await getV8AuditWormTargets(accessToken, orgId) : null;
  const configured = (targets ?? []).filter((target) => target.configured).length;

  return (
    <div className="space-y-5">
      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Root targets</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{targets?.length ?? 0}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">S3 Object Lock, GCS Bucket Lock, and Azure Immutable Blob.</p>
        </article>
        <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Configured</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">{configured}</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">Targets with bucket or container environment configured.</p>
        </article>
        <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Retention</div>
          <div className="mt-3 text-[28px] font-semibold text-[color:var(--text-primary)]">Proof</div>
          <p className="mt-2 text-xs text-[color:var(--text-secondary)]">Root hash and Merkle proof only. Event payloads are rejected.</p>
        </article>
      </section>

      <section className="rounded-[8px] border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-[color:var(--accent-primary)]" />
          <p className="text-[13px] leading-6 text-[color:var(--text-secondary)]">
            WORM roots publish tamper-evident audit-chain roots and Merkle proofs only. Skillayer never sends raw audit event payloads to root publication targets from this flow.
          </p>
        </div>
      </section>

      {targets ? (
        <section className="grid gap-4 lg:grid-cols-3">
          {targets.map((target) => {
            const Icon = target.configured ? CheckCircle2 : Clock3;
            return (
              <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={target.provider}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="font-semibold text-[color:var(--text-primary)]">{target.label}</h2>
                    <p className="mt-1 text-xs text-[color:var(--text-secondary)]">{target.provider.replaceAll("_", " ")}</p>
                  </div>
                  <span className={`inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold ${target.configured ? "bg-[color:var(--accent-green)]/10 text-[color:var(--accent-green)]" : "bg-amber-500/10 text-amber-200"}`}>
                    <Icon className="h-3.5 w-3.5" />
                    {target.status}
                  </span>
                </div>
                <dl className="mt-5 space-y-3 text-sm">
                  <div>
                    <dt className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Bucket or container env</dt>
                    <dd className="mt-1 break-all font-mono text-xs text-[color:var(--text-secondary)]">{target.bucket_env}</dd>
                  </div>
                  <div>
                    <dt className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Prefix</dt>
                    <dd className="mt-1 break-all font-mono text-xs text-[color:var(--text-secondary)]">{target.prefix || "root"}</dd>
                  </div>
                  <div>
                    <dt className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Content</dt>
                    <dd className="mt-1 inline-flex items-center gap-2 text-[color:var(--text-secondary)]">
                      <Archive className="h-3.5 w-3.5 text-[color:var(--accent-primary)]" />
                      {target.content_retention}
                    </dd>
                  </div>
                </dl>
              </article>
            );
          })}
        </section>
      ) : (
        <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
          <Archive className="mx-auto h-8 w-8 text-[color:var(--text-tertiary)]" />
          <h2 className="mt-3 font-semibold text-[color:var(--text-primary)]">WORM target status unavailable</h2>
          <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-[color:var(--text-secondary)]">Refresh after sign-in. Audit root targets will appear here when the authenticated API call succeeds.</p>
        </section>
      )}
    </div>
  );
}
