import { authkitMiddleware } from "@workos-inc/authkit-nextjs";
import { NextResponse, type NextFetchEvent, type NextRequest } from "next/server";

const workOSRedirectUri = process.env.NEXT_PUBLIC_WORKOS_REDIRECT_URI || process.env.WORKOS_REDIRECT_URI || "";

const isWorkOSConfigured = Boolean(
  process.env.WORKOS_API_KEY &&
    process.env.WORKOS_CLIENT_ID &&
    process.env.WORKOS_COOKIE_PASSWORD &&
    process.env.WORKOS_COOKIE_PASSWORD.length >= 32 &&
    workOSRedirectUri,
);

const workOSMiddleware = isWorkOSConfigured
  ? authkitMiddleware({
      redirectUri: workOSRedirectUri,
      middlewareAuth: {
        enabled: true,
        unauthenticatedPaths: ["/", "/sign-in", "/callback"],
      },
    })
  : null;

export default async function middleware(request: NextRequest, event: NextFetchEvent) {
  if (!workOSMiddleware) {
    const response = NextResponse.next();
    response.headers.set("x-skillayer-auth-mode", "preview");
    return response;
  }

  try {
    return await workOSMiddleware(request, event);
  } catch (error) {
    console.error("Skillayer dashboard auth middleware failed", error);
    return NextResponse.redirect(new URL("/sign-in?error=auth-configuration", request.url));
  }
}

export const config = {
  matcher: ["/dashboard", "/dashboard/:path*"],
};
