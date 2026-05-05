import { CheckCircle2, ShieldCheck } from "lucide-react";

import { EmptyPanel, Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";

type SsoPayload = {
  workos_org_id: string | null;
  saml_enabled: boolean;
  oidc_enabled: boolean;
  scim_enabled: boolean;
  managed_by: string;
};

export default async function SsoSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const sso = await v8Fetch<SsoPayload>(accessToken, org.id, "/sso");

  return (
    <SettingsShell active="SSO">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="SAML" value={sso?.saml_enabled ? "Enabled" : "Not configured"} sub="Existing WorkOS flow" />
        <Metric label="OIDC" value={sso?.oidc_enabled ? "Enabled" : "Not configured"} sub="Self-hosted identity support" />
        <Metric label="SCIM" value={sso?.scim_enabled ? "Enabled" : "Not configured"} sub="Enterprise provisioning" />
      </div>

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-0.5 h-5 w-5 text-[color:var(--accent-primary)]" />
          <div>
            <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Enterprise identity</h2>
            <p className="mt-1 text-sm text-[color:var(--text-secondary)]">SSO is surfaced here without changing the WorkOS or auth flow.</p>
          </div>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
            <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Managed by</div>
            <div className="mt-2 text-sm text-[color:var(--text-primary)]">{sso?.managed_by ?? "WorkOS"}</div>
          </div>
          <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
            <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">WorkOS organization</div>
            <div className="mt-2 truncate font-mono text-sm text-[color:var(--text-primary)]">{sso?.workos_org_id ?? "Not linked"}</div>
          </div>
        </div>
      </section>

      {!sso?.workos_org_id ? (
        <EmptyPanel detail="Connect or configure SSO through the existing auth administration path. This v8 route intentionally does not alter sign-in behavior." icon={<CheckCircle2 className="h-5 w-5" />} title="No SSO connection is linked yet." />
      ) : null}
    </SettingsShell>
  );
}
