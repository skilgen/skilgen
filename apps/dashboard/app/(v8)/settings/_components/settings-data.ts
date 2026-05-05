import "server-only";

import { withAuth } from "@workos-inc/authkit-nextjs";

import { API_URL, getBootstrapOrg, getMyOrg, type BootstrapOrg } from "../../../../lib/data";
import { mockOrg } from "@/lib/mock-data";

export type SettingsContext = {
  accessToken: string;
  org: Pick<BootstrapOrg, "id" | "name" | "login" | "plan">;
};

export async function loadSettingsContext(): Promise<SettingsContext> {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    // Local preview can run without WorkOS.
  }

  const rawOrg = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg()) ?? mockOrg;
  const org = {
    id: rawOrg.id,
    name: rawOrg.name,
    login: "login" in rawOrg ? rawOrg.login : "skillayer",
    plan: rawOrg.plan,
  };
  return { accessToken, org };
}

export async function v8Fetch<T>(accessToken: string, orgId: string, path: string): Promise<T | null> {
  try {
    const headers: HeadersInit = { "Content-Type": "application/json" };
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
    const response = await fetch(`${API_URL}/v8/orgs/${orgId}/settings${path}`, {
      headers,
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}
