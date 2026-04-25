import { withAuth } from "@workos-inc/authkit-nextjs";
import { API_URL, getBootstrapOrg, getMyOrg, getOrgApiKey } from "../../../lib/data";
import { DigestShell } from "./digest-shell";

export const dynamic = "force-dynamic";

export default async function DigestPage() {
  let accessToken = "";
  let email = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
    email = session?.user?.email || "";
  } catch {
    accessToken = "";
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const apiKey = org ? (await getOrgApiKey(accessToken, org.id))?.api_key ?? "" : "";
  const res = org ? await fetch(`${API_URL}/orgs/${org.id}/digest/preview`, { headers: { Authorization: `Bearer ${apiKey || accessToken}` }, cache: "no-store" }) : null;
  const digest = res?.ok ? await res.json() : null;
  return <DigestShell apiKey={apiKey} email={email} initialDigest={digest} orgId={org?.id ?? ""} />;
}
