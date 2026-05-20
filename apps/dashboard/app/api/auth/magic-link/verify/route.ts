import { NextResponse, type NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const callbackUrl = new URL("/callback", request.url);
  for (const [key, value] of request.nextUrl.searchParams.entries()) {
    callbackUrl.searchParams.set(key, value);
  }
  return NextResponse.redirect(callbackUrl);
}
