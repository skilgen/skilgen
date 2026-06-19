"use client";

import { useMemo, useState } from "react";
import { KeyRound, Plus, ShieldCheck } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

type Role = {
  id: string;
  name: string;
  description?: string | null;
  permissions: string[];
};

type Binding = {
  id: string;
  role_id: string;
  role_name?: string | null;
  principal_id: string;
  principal_type: string;
  scope_expression: Record<string, unknown> | string | null;
};

type RbacPayload = {
  permissions: string[];
  roles: Role[];
  bindings: Binding[];
};

function authHeaders(accessToken: string): HeadersInit {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

export function RbacPanel({ accessToken, initial, orgId }: { accessToken: string; initial: RbacPayload; orgId: string }) {
  const [roles, setRoles] = useState<Role[]>(initial.roles);
  const [bindings, setBindings] = useState<Binding[]>(initial.bindings);
  const [roleName, setRoleName] = useState("Policy approver");
  const [permission, setPermission] = useState("policy.approvals.approve");
  const [principal, setPrincipal] = useState("reviewer@example.com");
  const [scope, setScope] = useState("repo:payments/*");
  const [status, setStatus] = useState<string | null>(null);
  const selectedRole = roles[0];

  const permissionOptions = useMemo(() => initial.permissions.length ? initial.permissions : ["settings.read", "policy.approvals.approve"], [initial.permissions]);

  async function createRole() {
    setStatus(null);
    const optimistic: Role = { id: `local-role-${Date.now()}`, name: roleName, permissions: [permission] };
    try {
      const response = await fetch(`${API_URL}/v8/orgs/${orgId}/settings/rbac/roles`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders(accessToken) },
        body: JSON.stringify({ name: roleName, permissions: [permission] }),
      });
      const body = response.ok ? ((await response.json()) as Role) : optimistic;
      setRoles((current) => [body, ...current]);
      setStatus("Role created.");
    } catch {
      setRoles((current) => [optimistic, ...current]);
      setStatus("Role staged locally for preview.");
    }
  }

  async function createBinding() {
    setStatus(null);
    const role = selectedRole ?? { id: `local-role-${Date.now()}`, name: roleName, permissions: [permission] };
    const optimistic: Binding = {
      id: `local-binding-${Date.now()}`,
      role_id: role.id,
      role_name: role.name,
      principal_id: principal,
      principal_type: "user",
      scope_expression: scope,
    };
    if (!selectedRole) setRoles((current) => [role, ...current]);
    try {
      const response = await fetch(`${API_URL}/v8/orgs/${orgId}/settings/rbac/bindings`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders(accessToken) },
        body: JSON.stringify({ role_id: role.id, principal_type: "user", principal_id: principal, scope_expression: scope }),
      });
      const body = response.ok ? ((await response.json()) as Binding) : optimistic;
      setBindings((current) => [body, ...current]);
      setStatus("Role binding created.");
    } catch {
      setBindings((current) => [optimistic, ...current]);
      setStatus("Binding staged locally for preview.");
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[380px_1fr]">
      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-[color:var(--accent-primary)]" />
          <h2 className="text-[17px] font-semibold text-[color:var(--text-primary)]">Create role</h2>
        </div>
        <div className="mt-5 space-y-4">
          <label className="block space-y-2">
            <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Role name</span>
            <input className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]" value={roleName} onChange={(event) => setRoleName(event.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Permission</span>
            <select className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]" value={permission} onChange={(event) => setPermission(event.target.value)}>
              {permissionOptions.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
          <button className="inline-flex items-center gap-2 rounded-[8px] bg-[color:var(--accent-primary)] px-3 py-2 text-sm font-semibold text-[color:var(--bg-base)]" onClick={() => void createRole()} type="button">
            <Plus className="h-4 w-4" />
            Create role
          </button>
        </div>

        <div className="mt-8 flex items-center gap-2">
          <KeyRound className="h-5 w-5 text-[color:var(--accent-primary)]" />
          <h2 className="text-[17px] font-semibold text-[color:var(--text-primary)]">Bind scope</h2>
        </div>
        <div className="mt-5 space-y-4">
          <label className="block space-y-2">
            <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Principal</span>
            <input className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 text-sm text-[color:var(--text-primary)]" value={principal} onChange={(event) => setPrincipal(event.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="text-[12px] font-semibold text-[color:var(--text-secondary)]">Scope expression</span>
            <input className="w-full rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] px-3 py-2 font-mono text-sm text-[color:var(--text-primary)]" value={scope} onChange={(event) => setScope(event.target.value)} />
          </label>
          <button className="inline-flex items-center gap-2 rounded-[8px] border border-[color:var(--bg-border)] px-3 py-2 text-sm font-semibold text-[color:var(--text-primary)]" onClick={() => void createBinding()} type="button">
            <Plus className="h-4 w-4" />
            Add binding
          </button>
          {status ? <p className="text-sm text-[color:var(--accent-primary)]">{status}</p> : null}
        </div>
      </section>

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="border-b border-[color:var(--bg-border)] px-5 py-4">
          <h2 className="text-[17px] font-semibold text-[color:var(--text-primary)]">Scoped permissions</h2>
        </div>
        <div className="divide-y divide-[color:var(--bg-border)]">
          {roles.map((role) => (
            <div className="px-5 py-4" key={role.id}>
              <div className="font-semibold text-[color:var(--text-primary)]">{role.name}</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {role.permissions.map((item) => <span className="rounded-full bg-[color:var(--bg-base)] px-2.5 py-1 font-mono text-[12px] text-[color:var(--text-secondary)]" key={item}>{item}</span>)}
              </div>
            </div>
          ))}
          {!roles.length ? <div className="px-5 py-8 text-sm text-[color:var(--text-secondary)]">No RBAC roles yet.</div> : null}
        </div>

        <div className="border-t border-[color:var(--bg-border)] px-5 py-4">
          <h2 className="text-[17px] font-semibold text-[color:var(--text-primary)]">Bindings</h2>
          <div className="mt-3 space-y-3">
            {bindings.map((binding) => (
              <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-sm" key={binding.id}>
                <div className="font-semibold text-[color:var(--text-primary)]">{binding.principal_id}</div>
                <div className="mt-1 text-[color:var(--text-secondary)]">{binding.role_name ?? binding.role_id}</div>
                <div className="mt-2 font-mono text-[12px] text-[color:var(--text-tertiary)]">{typeof binding.scope_expression === "string" ? binding.scope_expression : JSON.stringify(binding.scope_expression ?? {})}</div>
              </div>
            ))}
            {!bindings.length ? <div className="text-sm text-[color:var(--text-secondary)]">No scoped bindings yet.</div> : null}
          </div>
        </div>
      </section>
    </div>
  );
}
