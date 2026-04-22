import { withAuth } from "@workos-inc/authkit-nextjs";

import { OverviewLiveData } from "@/components/overview-live-data";
import { API_URL } from "../../lib/data";

export const dynamic = "force-dynamic";

export default async function OverviewPage() {
  let accessToken = "";
  let userId = "";

  try {
    const session = await withAuth({ ensureSignedIn: true });
    accessToken = session?.accessToken || "";
    userId = session?.user?.id || "";
    console.log("Auth session:", {
      hasToken: !!accessToken,
      userId,
    });
  } catch (error) {
    console.error("Auth error:", error);
  }

  console.log("API URL:", API_URL);
  console.log("Has access token:", !!accessToken);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Overview</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Your org AI readiness at a glance</p>
      </div>

      <OverviewLiveData apiUrl={API_URL} />
    </div>
  );
}
