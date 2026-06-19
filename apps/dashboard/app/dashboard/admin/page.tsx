import { AdminOverviewClient } from "./admin-overview-client";
import { ForbiddenAdmin, requireAdmin } from "./admin-auth";
import { getAdminOrgs, getAdminOverview, getAdminUsers } from "../../../lib/data";

export default async function AdminPage() {
  const { isAdmin, adminSecret } = await requireAdmin();
  if (!isAdmin) return <ForbiddenAdmin />;
  if (!adminSecret) {
    return (
      <div className="rounded-[24px] border border-amber-500/30 bg-amber-500/10 p-6 text-amber-100">
        Admin is enabled for your email, but the dashboard deployment is missing the server-side ADMIN_SECRET env var. Set ADMIN_SECRET on the dashboard project to the same value as the API project, then redeploy.
      </div>
    );
  }
  const [overview, orgs, users] = await Promise.all([
    getAdminOverview(adminSecret),
    getAdminOrgs(adminSecret, new URLSearchParams({ sort_by: "last_active", limit: "10" })),
    getAdminUsers(adminSecret, new URLSearchParams({ limit: "10" })),
  ]);
  if (!overview) return <div className="rounded-[24px] border border-red-500/30 bg-red-500/10 p-6 text-red-200">Could not load admin overview. The API rejected the admin secret or the admin route failed; check the API ADMIN_SECRET and recent function logs.</div>;
  return <AdminOverviewClient overview={overview} orgs={orgs?.orgs ?? []} users={users?.users ?? []} />;
}
