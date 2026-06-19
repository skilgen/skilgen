import { proxyAdminRequest } from "../../../_admin-proxy";

export async function POST(request: Request, { params }: { params: Promise<{ orgId: string }> }) {
  const { orgId } = await params;
  const body = await request.text();
  return proxyAdminRequest(`/admin/orgs/${orgId}/suspend`, { method: "POST", body });
}
