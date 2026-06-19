import { Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";
import { RbacPanel } from "./rbac-panel";

const fallback = {
  permissions: ["settings.read", "settings.rbac.manage", "policy.approvals.approve"],
  roles: [],
  bindings: [],
};

export default async function RbacSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const payload = await v8Fetch<typeof fallback>(accessToken, org.id, "/rbac") ?? fallback;

  return (
    <SettingsShell active="RBAC">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Roles" value={payload.roles.length} sub="Reusable permission bundles" />
        <Metric label="Bindings" value={payload.bindings.length} sub="Scoped to users or teams" />
        <Metric label="Scope grammar" value="Glob" sub="repo:payments/* and JSON all/any/not" />
      </div>
      <RbacPanel accessToken={accessToken} initial={payload} orgId={org.id} />
    </SettingsShell>
  );
}
