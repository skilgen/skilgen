import { getSignInUrl } from "@workos-inc/authkit-nextjs";
import { redirect } from "next/navigation";

export async function GET() {
  const redirectUri = process.env.NEXT_PUBLIC_WORKOS_REDIRECT_URI || process.env.WORKOS_REDIRECT_URI || "";
  const isWorkOSConfigured = Boolean(
    process.env.WORKOS_API_KEY &&
      process.env.WORKOS_CLIENT_ID &&
      process.env.WORKOS_COOKIE_PASSWORD &&
      process.env.WORKOS_COOKIE_PASSWORD.length >= 32 &&
      redirectUri,
  );

  if (!isWorkOSConfigured) {
    redirect("/dashboard");
  }

  const signInUrl = await getSignInUrl({ redirectUri });

  redirect(signInUrl);
}
