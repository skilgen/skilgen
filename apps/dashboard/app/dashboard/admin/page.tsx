import { AdminOverviewClient } from "./admin-overview-client";
import { ForbiddenAdmin, requireAdmin } from "./admin-auth";
import { getAdminOrgs, getAdminOverview, getAdminUsers } from "../../../lib/data";

export default async function AdminPage() {
  const { isAdmin, adminSecret } = await requireAdmin();
  if (!isAdmin || !adminSecret) return <ForbiddenAdmin />;
  const [overview, orgs, users] = await Promise.all([
    getAdminOverview(adminSecret),
    getAdminOrgs(adminSecret, new URLSearchParams({ sort_by: "last_active", limit: "10" })),
    getAdminUsers(adminSecret, new URLSearchParams({ limit: "10" })),
  ]);
  if (!overview) return <div className="rounded-[24px] border border-red-500/30 bg-red-500/10 p-6 text-red-200">Could not load admin overview.</div>;
  return <AdminOverviewClient overview={overview} orgs={orgs?.orgs ?? []} users={users?.users ?? []} />;
}
