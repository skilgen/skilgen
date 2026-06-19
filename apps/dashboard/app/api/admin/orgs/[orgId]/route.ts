import { proxyAdminRequest } from "../../_admin-proxy";

export async function DELETE(_request: Request, { params }: { params: Promise<{ orgId: string }> }) {
  const { orgId } = await params;
  return proxyAdminRequest(`/admin/orgs/${orgId}`, { method: "DELETE" });
}
