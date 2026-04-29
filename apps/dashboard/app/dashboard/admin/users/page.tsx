import { ForbiddenAdmin, requireAdmin } from "../admin-auth";
import { getAdminUsers } from "../../../../lib/data";
import { AdminUsersClient } from "./admin-users-client";

export default async function AdminUsersPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const { isAdmin, adminSecret } = await requireAdmin();
  if (!isAdmin || !adminSecret) return <ForbiddenAdmin />;
  const raw = await searchParams;
  const params = new URLSearchParams();
  if (raw.search) params.set("search", raw.search);
  const data = await getAdminUsers(adminSecret, params);
  return <AdminUsersClient users={data?.users ?? []} total={data?.total ?? 0} />;
}
