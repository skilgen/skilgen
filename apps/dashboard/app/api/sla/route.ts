import { withAuth } from "@workos-inc/authkit-nextjs";
import { NextRequest, NextResponse } from "next/server";

import { API_URL, getBootstrapOrg, getMyOrg, getOrgApiKey } from "../../../lib/data";

export async function POST(req: NextRequest) {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  if (!org?.id) return NextResponse.json({ error: "No org" }, { status: 404 });

  const keyData = await getOrgApiKey(accessToken, org.id);
  const apiKey = keyData?.api_key ?? "";
  const auth = apiKey ? `Bearer ${apiKey}` : `Bearer ${accessToken}`;

  const body = await req.formData();
  const payload = {
    name: body.get("name") as string,
    repo_id: (body.get("repo_id") as string) || null,
    coverage_target_pct: Number(body.get("coverage_target_pct") ?? 80),
    alert_email: (body.get("alert_email") as string) || null,
  };

  const res = await fetch(`${API_URL}/orgs/${org.id}/sla`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: auth },
    body: JSON.stringify(payload),
  });

  if (!res.ok) return NextResponse.json({ error: "Failed to create SLA" }, { status: res.status });
  return NextResponse.redirect(new URL("/dashboard/sla", req.url));
}
