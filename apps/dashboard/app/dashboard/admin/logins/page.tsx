import { ForbiddenAdmin, requireAdmin } from "../admin-auth";
import { getAdminLogins } from "../../../../lib/data";
import { AdminLoginsClient } from "./admin-logins-client";

export default async function AdminLoginsPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const { isAdmin, adminSecret } = await requireAdmin();
  if (!isAdmin || !adminSecret) return <ForbiddenAdmin />;
  const raw = await searchParams;
  const params = new URLSearchParams();
  for (const key of ["user_login", "date_from", "date_to"]) if (raw[key]) params.set(key, raw[key] as string);
  const data = await getAdminLogins(adminSecret, params);
  return <AdminLoginsClient logins={data?.logins ?? []} total={data?.total ?? 0} />;
}
