import { ForbiddenAdmin, requireAdmin } from "../../admin-auth";
import { getAdminOrg, getAdminOrgUsage } from "../../../../../lib/data";
import { AdminOrgDetailClient } from "./admin-org-detail-client";

export default async function AdminOrgDetailPage({ params }: { params: Promise<{ orgId: string }> }) {
  const { isAdmin, adminSecret } = await requireAdmin();
  if (!isAdmin || !adminSecret) return <ForbiddenAdmin />;
  const { orgId } = await params;
  const [org, usage] = await Promise.all([getAdminOrg(orgId, adminSecret), getAdminOrgUsage(orgId, adminSecret, 30)]);
  if (!org) return <div className="rounded-[24px] border border-red-500/30 bg-red-500/10 p-6 text-red-200">Could not load org.</div>;
  return <AdminOrgDetailClient org={org} usage={usage} />;
}
