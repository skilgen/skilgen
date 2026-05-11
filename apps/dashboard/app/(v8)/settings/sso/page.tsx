import { AlertTriangle, CheckCircle2, KeyRound, ShieldCheck, UsersRound } from "lucide-react";

import { Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";

type SsoPayload = {
  workos_org_id: string | null;
  saml_enabled: boolean;
  oidc_enabled: boolean;
  scim_enabled: boolean;
  managed_by: string;
  ready: boolean;
  connection_state: string;
  protocols_enabled: string[];
  provisioning_state: string;
  next_actions: string[];
};

function label(value: string): string {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function compactId(value: string | null): string {
  if (!value) return "Unavailable";
  return value.length > 16 ? `${value.slice(0, 8)}...${value.slice(-4)}` : value;
}

export default async function SsoSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const sso = await v8Fetch<SsoPayload>(accessToken, org.id, "/sso");
  const ssoAvailable = sso !== null;
  const current: SsoPayload = sso ?? {
    workos_org_id: null,
    saml_enabled: false,
    oidc_enabled: false,
    scim_enabled: false,
    managed_by: "Unavailable",
    ready: false,
    connection_state: "unavailable",
    protocols_enabled: [],
    provisioning_state: "unavailable",
    next_actions: ["sso_api_unavailable"],
  };
  const statusLabel = ssoAvailable ? (current.ready ? "Ready" : "Setup needed") : "Unavailable";
  const protocols = ssoAvailable ? current.protocols_enabled.join(", ") || "None configured" : "Unknown";

  return (
    <SettingsShell active="SSO">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Identity" value={label(current.connection_state)} sub={ssoAvailable ? "WorkOS organization state" : "Live SSO unavailable"} />
        <Metric label="Protocols" value={protocols} sub="SAML and OIDC readiness" />
        <Metric label="Provisioning" value={label(current.provisioning_state)} sub="SCIM lifecycle state" />
      </div>

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="border-b border-[color:var(--bg-border)] p-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-start gap-3">
              <ShieldCheck className="mt-0.5 h-5 w-5 text-[color:var(--accent-primary)]" />
              <div>
                <h2 className="text-[18px] font-semibold text-[color:var(--text-primary)]">Enterprise identity readiness</h2>
                <p className="mt-1 text-sm text-[color:var(--text-secondary)]">SSO state is surfaced from existing WorkOS and org settings without changing sign-in behavior.</p>
              </div>
            </div>
            <span className={`inline-flex w-fit items-center gap-2 rounded-full px-3 py-1 text-[12px] font-semibold ${current.ready ? "bg-[color:var(--accent-green)]/15 text-[color:var(--accent-green)]" : "bg-amber-500/15 text-amber-100"}`}>
              {current.ready ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
              {statusLabel}
            </span>
          </div>
        </div>

        <div className="grid gap-4 p-5 lg:grid-cols-[minmax(0,1fr)_320px]">
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-[color:var(--text-primary)]">
                <KeyRound className="h-4 w-4 text-[color:var(--accent-primary)]" />
                Identity provider
              </div>
              <div className="mt-4 space-y-3 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-[color:var(--text-secondary)]">Managed by</span>
                  <span className="font-semibold text-[color:var(--text-primary)]">{current.managed_by}</span>
                </div>
                <div>
                  <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">WorkOS organization</div>
                  <div className="mt-1 truncate font-mono text-[color:var(--text-primary)]">{ssoAvailable ? compactId(current.workos_org_id) : "Unavailable"}</div>
                </div>
              </div>
            </div>

            <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-[color:var(--text-primary)]">
                <UsersRound className="h-4 w-4 text-[color:var(--accent-primary)]" />
                Protocol coverage
              </div>
              <div className="mt-4 grid gap-2">
                {(["SAML", "OIDC", "SCIM"] as const).map((item) => {
                  const enabled = item === "SAML" ? current.saml_enabled : item === "OIDC" ? current.oidc_enabled : current.scim_enabled;
                  const unknown = !ssoAvailable;
                  return (
                    <div className="flex items-center justify-between rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-2 text-sm" key={item}>
                      <span className="font-semibold text-[color:var(--text-primary)]">{item}</span>
                      <span className={enabled ? "text-[color:var(--accent-green)]" : unknown ? "text-[color:var(--text-tertiary)]" : "text-amber-100"}>
                        {unknown ? "Unknown" : enabled ? "Enabled" : "Not configured"}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <aside className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-4">
            <div className="text-[12px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">Next actions</div>
            <div className="mt-3 space-y-2">
              {current.next_actions.map((action) => (
                <div className="flex items-center gap-2 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-3 py-2 text-sm text-[color:var(--text-primary)]" key={action}>
                  {action === "monitor_identity_sync" ? <CheckCircle2 className="h-4 w-4 text-[color:var(--accent-green)]" /> : <AlertTriangle className="h-4 w-4 text-amber-100" />}
                  <span>{label(action)}</span>
                </div>
              ))}
            </div>
          </aside>
        </div>
      </section>
    </SettingsShell>
  );
}
