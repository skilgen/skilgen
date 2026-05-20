import { WorkOS } from "@workos-inc/node";
import { NextResponse, type NextRequest } from "next/server";

const PERSONAL_EMAIL_DOMAINS = new Set([
  "aol.com",
  "gmail.com",
  "hotmail.com",
  "icloud.com",
  "live.com",
  "me.com",
  "msn.com",
  "outlook.com",
  "proton.me",
  "protonmail.com",
  "yahoo.com",
]);

function workOSRedirectUri(request: NextRequest): string {
  return process.env.NEXT_PUBLIC_WORKOS_REDIRECT_URI || process.env.WORKOS_REDIRECT_URI || new URL("/callback", request.url).toString();
}

function workOSReady(): boolean {
  return Boolean(process.env.WORKOS_API_KEY && process.env.WORKOS_CLIENT_ID && process.env.WORKOS_COOKIE_PASSWORD && process.env.WORKOS_COOKIE_PASSWORD.length >= 32);
}

function signInRedirect(request: NextRequest, params: Record<string, string>): NextResponse {
  const url = new URL("/sign-in", request.url);
  for (const [key, value] of Object.entries(params)) url.searchParams.set(key, value);
  return NextResponse.redirect(url);
}

function normalizeEmail(value: FormDataEntryValue | null): string {
  return typeof value === "string" ? value.trim().toLowerCase() : "";
}

function corporateEmail(email: string): boolean {
  const [, domain = ""] = email.split("@");
  return Boolean(email.includes("@") && domain && !PERSONAL_EMAIL_DOMAINS.has(domain));
}

function returnState(): string {
  return Buffer.from(JSON.stringify({ returnPathname: "/dashboard/connect?auth=magic-link" })).toString("base64");
}

export async function GET(request: NextRequest) {
  return signInRedirect(request, {});
}

export async function POST(request: NextRequest) {
  const form = await request.formData();
  const email = normalizeEmail(form.get("email"));

  if (!email.includes("@")) {
    return signInRedirect(request, { error: "email-required" });
  }

  if (!corporateEmail(email)) {
    return signInRedirect(request, { error: "personal-email", email });
  }

  if (!workOSReady()) {
    const previewUrl = new URL("/dashboard/connect", request.url);
    previewUrl.searchParams.set("auth", "magic-link-preview");
    previewUrl.searchParams.set("email", email);
    return NextResponse.redirect(previewUrl);
  }

  try {
    const workos = new WorkOS(process.env.WORKOS_API_KEY);
    const session = await workos.passwordless.createSession({
      type: "MagicLink",
      email,
      redirectURI: workOSRedirectUri(request),
      state: returnState(),
      expiresIn: 15 * 60,
    });
    await workos.passwordless.sendSession(session.id);
    return signInRedirect(request, { sent: "magic-link", email });
  } catch (error) {
    console.error("Skillayer magic-link send failed", error);
    return signInRedirect(request, { error: "auth-configuration", email });
  }
}
