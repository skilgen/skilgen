import { withAuth } from "@workos-inc/authkit-nextjs";
import { API_URL, getBootstrapOrg, getMyOrg, getOrgApiKey } from "../../../lib/data";
import { DigestShell, type Digest, type DigestConfig } from "./digest-shell";

async function fetchJson<T>(url: string, token: string): Promise<T | null> {
  try {
    const res = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {}, cache: "no-store" });
    return res.ok ? ((await res.json()) as T) : null;
  } catch {
    return null;
  }
}

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
  const token = apiKey || accessToken;
  const [digest, config] = org
    ? await Promise.all([
        fetchJson<Digest>(`${API_URL}/orgs/${org.id}/digest/preview`, token),
        fetchJson<Partial<DigestConfig>>(`${API_URL}/orgs/${org.id}/digest/config`, token),
      ])
    : [null, null];
  return <DigestShell accessToken={accessToken} apiKey={apiKey} email={email} initialConfig={config} initialDigest={digest} orgId={org?.id ?? ""} />;
}
