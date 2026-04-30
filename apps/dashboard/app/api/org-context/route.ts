import { withAuth } from "@workos-inc/authkit-nextjs";
import { NextResponse } from "next/server";

import { getBootstrapOrg, getMyOrg, getOrgApiKey } from "../../../lib/data";

export async function GET() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }

  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  if (!org?.id) {
    return NextResponse.json({ error: "No org" }, { status: 404 });
  }

  const keyData = await getOrgApiKey(accessToken, org.id);
  return NextResponse.json({ orgId: org.id, orgName: org.name, apiKey: keyData?.api_key ?? "" });
}
