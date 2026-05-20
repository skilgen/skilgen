import "server-only";

import { cache } from "react";
import { withAuth } from "@workos-inc/authkit-nextjs";

import { API_URL } from "./data";

type FlagResponse = {
  IA_V8?: boolean;
};

export function readBooleanEnv(value: string | undefined): boolean | undefined {
  if (value === undefined || value.trim() === "") return undefined;
  const normalized = value.trim().toLowerCase();
  if (["1", "true", "yes", "on"].includes(normalized)) return true;
  if (["0", "false", "no", "off"].includes(normalized)) return false;
  return undefined;
}

export function iaV8EnvDefault(): boolean {
  return readBooleanEnv(process.env.IA_V8_DEFAULT) ?? false;
}

export function selfServeAuthEnvDefault(): boolean {
  return readBooleanEnv(process.env.FF_SELF_SERVE_AUTH) ?? false;
}

async function accessTokenFromSession(): Promise<string> {
  try {
    const session = await withAuth({ ensureSignedIn: false });
    return session?.accessToken || "";
  } catch {
    return "";
  }
}

export const isV8ForOrg = cache(async (orgId: string): Promise<boolean> => {
  const envDefault = iaV8EnvDefault();
  if (!orgId) return envDefault;

  const accessToken = await accessTokenFromSession();
  if (!accessToken) return envDefault;

  try {
    const response = await fetch(`${API_URL}/v8/orgs/${orgId}/flags/ia-v8`, {
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) return envDefault;
    const payload = (await response.json()) as FlagResponse;
    return typeof payload.IA_V8 === "boolean" ? payload.IA_V8 : envDefault;
  } catch {
    return envDefault;
  }
});

export async function isDashboardV8Enabled(orgId: string): Promise<boolean> {
  return isV8ForOrg(orgId);
}
