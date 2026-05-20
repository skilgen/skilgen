import { handleAuth } from "@workos-inc/authkit-nextjs";

import { API_URL } from "../lib/data";

type ProvisionPayload = {
  source: "workos" | "magic_link" | "github_oauth";
  authentication_method?: string | null;
  email?: string | null;
  name?: string | null;
};

function normalizeProvisionSource(authenticationMethod?: string, state?: string): ProvisionPayload["source"] {
  if (state) {
    try {
      const parsed = JSON.parse(state) as { source?: string };
      if (parsed?.source === "github_oauth") return "github_oauth";
      if (parsed?.source === "magic_link") return "magic_link";
      if (parsed?.source === "workos") return "workos";
    } catch {
      // ignore invalid custom state
    }
  }

  const normalized = String(authenticationMethod ?? "").toLowerCase();
  if (normalized.includes("github")) return "github_oauth";
  if (normalized.includes("magic")) return "magic_link";
  return "workos";
}

export const GET = handleAuth({
  returnPathname: "/dashboard/connect",
  onSuccess: async ({ accessToken, authenticationMethod, state, user }) => {
    const source = normalizeProvisionSource(authenticationMethod, state);
    const nameParts = [user.firstName, user.lastName].filter(Boolean);
    const payload: ProvisionPayload = {
      source,
      authentication_method: authenticationMethod ?? null,
      email: user.email ?? null,
      name: nameParts.length ? nameParts.join(" ") : null,
    };

    try {
      await fetch(`${API_URL}/me/provision`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(payload),
        cache: "no-store",
      });
    } catch (error) {
      console.error("Skillayer JIT provisioning warmup failed", error);
    }
  },
});
