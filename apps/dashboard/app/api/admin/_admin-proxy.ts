import { withAuth } from "@workos-inc/authkit-nextjs";
import { NextResponse } from "next/server";

import { API_URL } from "../../../lib/data";

export async function requireAdminProxy() {
  let email = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    email = session?.user?.email || "";
  } catch {
    email = "";
  }
  const adminEmails = (process.env.NEXT_PUBLIC_ADMIN_EMAILS || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
  const adminSecret = process.env.ADMIN_SECRET || "";
  if (!email || !adminEmails.includes(email) || !adminSecret) {
    return { ok: false as const, response: NextResponse.json({ detail: "Admin access required" }, { status: 403 }) };
  }
  return { ok: true as const, adminSecret };
}

export async function proxyAdminRequest(path: string, init: RequestInit) {
  const auth = await requireAdminProxy();
  if (!auth.ok) return auth.response;
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Secret": auth.adminSecret,
      ...(init.headers || {}),
    },
    cache: "no-store",
  });
  const text = await response.text();
  return new NextResponse(text, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("content-type") || "application/json",
    },
  });
}
