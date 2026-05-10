import { withAuth } from "@workos-inc/authkit-nextjs";
import { MessageSquareText } from "lucide-react";

import { API_URL, getBootstrapOrg, getMyOrg, type Org, type SkillQLSuggestions } from "../../../../lib/data";
import { SkillQLWorkbench } from "./skillql-workbench";

async function loadContext(): Promise<{ accessToken: string; org: Org | null }> {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch {
    accessToken = "";
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  return { accessToken, org };
}

async function getSuggestions(accessToken: string, orgId: string): Promise<SkillQLSuggestions> {
  try {
    const response = await fetch(`${API_URL}/v8/orgs/${orgId}/skills/skillql/suggestions`, {
      cache: "no-store",
      headers: {
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) return {};
    return (await response.json()) as SkillQLSuggestions;
  } catch {
    return {};
  }
}

export default async function V8SkillQLPage() {
  const { accessToken, org } = await loadContext();

  if (!org?.id) {
    return (
      <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-sm text-[color:var(--text-secondary)]">
        <MessageSquareText className="mx-auto h-6 w-6 text-[color:var(--text-tertiary)]" />
        <p className="mt-4 text-[15px] font-semibold text-[color:var(--text-primary)]">No workspace available.</p>
        <p className="mx-auto mt-2 max-w-xl leading-6">Connect an organization before asking SkillQL about governed skills, agent activity, policy risk, or developer evidence.</p>
      </div>
    );
  }

  const suggestions = await getSuggestions(accessToken, org.id);

  return <SkillQLWorkbench accessToken={accessToken} orgId={org.id} suggestions={suggestions} />;
}
