import { getSignInUrl } from "@workos-inc/authkit-nextjs";
import { NextRequest } from "next/server";
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

function safeReturnTo(value: string | null): string {
  if (!value || !value.startsWith("/") || value.startsWith("//")) return "/dashboard/connect?auth=sso";
  return value;
}

export async function GET(request: NextRequest) {
  if (!isWorkOSConfigured()) {
    redirect("/activity");
  }

  const returnTo = safeReturnTo(request.nextUrl.searchParams.get("returnTo"));
  const signInUrl = await getSignInUrl({
    redirectUri: workOSRedirectUri(),
    returnTo,
    state: JSON.stringify({ source: "workos", method: "sso" }),
  });
  redirect(signInUrl);
}
