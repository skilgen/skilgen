import { getSignInUrl } from "@workos-inc/authkit-nextjs";
import { redirect } from "next/navigation";

function workOSRedirectUri(): string {
  return process.env.NEXT_PUBLIC_WORKOS_REDIRECT_URI || process.env.WORKOS_REDIRECT_URI || "";
}

function isWorkOSConfigured(): boolean {
  return Boolean(
    process.env.WORKOS_API_KEY &&
      process.env.WORKOS_CLIENT_ID &&
      process.env.WORKOS_COOKIE_PASSWORD &&
      process.env.WORKOS_COOKIE_PASSWORD.length >= 32 &&
      workOSRedirectUri(),
  );
}

export async function GET() {
  if (!isWorkOSConfigured()) {
    redirect("/activity");
  }

  const signInUrl = await getSignInUrl({
    redirectUri: workOSRedirectUri(),
    returnTo: "/dashboard/connect?auth=github",
    state: JSON.stringify({ source: "github_oauth", method: "github" }),
  });
  redirect(signInUrl);
}
