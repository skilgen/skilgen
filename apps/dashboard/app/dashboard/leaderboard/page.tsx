import { withAuth } from "@workos-inc/authkit-nextjs";
import { Trophy } from "lucide-react";

import { getBootstrapOrg, getMyOrg } from "../../../lib/data";
import { LeaderboardClient } from "./leaderboard-client";

type PageProps = {
  searchParams?: Promise<{ days?: string | string[]; sort_by?: string | string[] }>;
};

const ALLOWED_DAYS = new Set([7, 30, 90]);
const ALLOWED_SORTS = new Set(["compliance", "prs", "sessions", "violations", "lines"]);

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function parseDays(value: string | string[] | undefined): number {
  const parsed = Number.parseInt(first(value) ?? "30", 10);
  return ALLOWED_DAYS.has(parsed) ? parsed : 30;
}

function parseSort(value: string | string[] | undefined): string {
  const raw = first(value) ?? "compliance";
  return ALLOWED_SORTS.has(raw) ? raw : "compliance";
}

export default async function LeaderboardPage({ searchParams }: PageProps) {
  let accessToken = "";
  let org = null;

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
    org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  } catch {
    org = await getBootstrapOrg();
  }

  const params = (await searchParams) ?? {};
  const days = parseDays(params.days);
  const sortBy = parseSort(params.sort_by);

  if (!org?.id) {
    return (
      <div className="rounded-[28px] border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-6 py-16 text-center">
        <Trophy className="mx-auto h-12 w-12 text-[color:var(--text-tertiary)]" />
        <h1 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">No workspace available</h1>
        <p className="mx-auto mt-2 max-w-lg text-sm text-[color:var(--text-secondary)]">Connect an organization before ranking developer activity.</p>
      </div>
    );
  }

  return <LeaderboardClient accessToken={accessToken} initialDays={days} initialSortBy={sortBy} orgId={org.id} />;
}
