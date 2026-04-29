import { withAuth } from "@workos-inc/authkit-nextjs";
import { UserRound } from "lucide-react";

import { getBootstrapOrg, getMyCodeToday, getMyOrg } from "../../../lib/data";
import { MyCodeTodayClient } from "./my-code-today-client";

type PageProps = {
  searchParams: Promise<{ date?: string | string[]; login?: string | string[] }>;
};

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function todayUtc(): string {
  return new Date().toISOString().slice(0, 10);
}

function loginFromEmail(email: string | null | undefined): string {
  return email?.split("@")[0]?.replace(/[^a-zA-Z0-9-]/g, "-") || "developer";
}

export default async function MyCodeTodayPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const selectedDate = first(params.date) || todayUtc();
  let accessToken = "";
  let currentLogin = first(params.login) || "";
  let org = null;

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
    currentLogin ||= loginFromEmail(session?.user?.email);
    org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  } catch {
    currentLogin ||= "developer";
    org = await getBootstrapOrg();
  }

  if (!org?.id) {
    return (
      <div className="rounded-[28px] border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-6 py-16 text-center">
        <UserRound className="mx-auto h-12 w-12 text-[color:var(--text-tertiary)]" />
        <h1 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">No workspace available</h1>
        <p className="mx-auto mt-2 max-w-lg text-sm text-[color:var(--text-secondary)]">Connect an organization before reviewing your daily agent activity.</p>
      </div>
    );
  }

  const initialData = await getMyCodeToday(accessToken, org.id, currentLogin, selectedDate);

  return <MyCodeTodayClient accessToken={accessToken} initialData={initialData} initialDate={selectedDate} initialLogin={currentLogin} orgId={org.id} />;
}
