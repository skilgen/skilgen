import { ForbiddenAdmin, requireAdmin } from "../admin-auth";
import { getAdminOrgs } from "../../../../lib/data";
import { AdminOrgsClient } from "./admin-orgs-client";

export default async function AdminOrgsPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const { isAdmin, adminSecret } = await requireAdmin();
  if (!isAdmin || !adminSecret) return <ForbiddenAdmin />;
  const params = new URLSearchParams();
  const raw = await searchParams;
  for (const key of ["search", "plan", "sort_by"]) if (raw[key]) params.set(key, raw[key] as string);
  const data = await getAdminOrgs(adminSecret, params);
  return <AdminOrgsClient orgs={data?.orgs ?? []} total={data?.total ?? 0} />;
}
