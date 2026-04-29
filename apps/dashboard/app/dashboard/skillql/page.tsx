import { withAuth } from "@workos-inc/authkit-nextjs";
import { Sparkles } from "lucide-react";

import { getBootstrapOrg, getMyOrg, getSkillQLSuggestions } from "../../../lib/data";
import { SkillQLClient } from "./skillql-client";

export default async function SkillQLPage() {
  let accessToken = "";
  let org = null;

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
    org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  } catch {
    org = await getBootstrapOrg();
  }

  if (!org?.id) {
    return (
      <div className="mx-auto max-w-4xl rounded-[28px] border border-dashed border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-6 py-16 text-center">
        <Sparkles className="mx-auto h-12 w-12 text-[color:var(--text-tertiary)]" />
        <h1 className="mt-5 text-xl font-semibold text-[color:var(--text-primary)]">No workspace available</h1>
        <p className="mx-auto mt-2 max-w-lg text-sm text-[color:var(--text-secondary)]">Connect an organization before asking SkillQL about your agent data.</p>
      </div>
    );
  }

  const suggestions = (await getSkillQLSuggestions(accessToken, org.id)) ?? {};

  return <SkillQLClient accessToken={accessToken} orgId={org.id} suggestions={suggestions} />;
}
