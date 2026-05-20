import Link from "next/link";
import { ArrowRight, Users2 } from "lucide-react";
import { revalidatePath } from "next/cache";

import { EmptyPanel, Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";
import { API_URL } from "../../../../lib/data";

type Team = {
  id?: string;
  team_name?: string;
  name?: string;
  repo_count?: number;
  skill_count?: number;
  score_now?: number;
  avg_score?: number;
  red_flag_count?: number;
};

export default async function TeamsSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const payload = await v8Fetch<{ teams: Team[]; total: number; auto_join_domain?: boolean }>(accessToken, org.id, "/teams");
  const teams = payload?.teams ?? [];
  const repoCount = teams.reduce((sum, team) => sum + Number(team.repo_count ?? 0), 0);
  const autoJoinDomain = payload?.auto_join_domain ?? true;

  async function setAutoJoinDomain(formData: FormData) {
    "use server";
    const enabled = formData.get("enabled") === "true";

    const ctx = await loadSettingsContext();
    const headers: HeadersInit = { "Content-Type": "application/json" };
    if (ctx.accessToken) headers.Authorization = `Bearer ${ctx.accessToken}`;

    await fetch(`${API_URL}/v8/orgs/${ctx.org.id}/settings/teams/auto-join-domain`, {
      method: "PUT",
      headers,
      body: JSON.stringify({ enabled }),
      cache: "no-store",
    });

    revalidatePath("/settings/teams");
  }

  return (
    <SettingsShell active="Teams">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Teams" value={teams.length} sub="Derived from repo ownership signals" />
        <Metric label="Repos" value={repoCount} sub="Grouped under Settings without behavior changes" />
        <Metric label="Role source" value="RBAC" sub="Fine-grained access lives in the next tab" />
      </div>

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <div className="text-sm font-semibold text-[color:var(--text-primary)]">Auto-join by domain</div>
            <p className="mt-1 text-xs leading-5 text-[color:var(--text-secondary)]">
              When enabled, new logins for your email domain join this org automatically. Disable to require explicit invitation.
            </p>
          </div>
          <form action={setAutoJoinDomain}>
            <input name="enabled" type="hidden" value={autoJoinDomain ? "false" : "true"} />
            <button
              className={
                autoJoinDomain
                  ? "inline-flex min-h-10 items-center rounded-[8px] bg-[color:var(--accent-primary)] px-4 text-sm font-semibold text-black transition hover:bg-[color:var(--accent-bright)]"
                  : "inline-flex min-h-10 items-center rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-elevated)] px-4 text-sm font-semibold text-[color:var(--text-primary)] transition hover:border-[color:var(--accent-primary)]"
              }
              type="submit"
            >
              {autoJoinDomain ? "Enabled" : "Disabled"}
            </button>
          </form>
        </div>
      </section>

      {teams.length ? (
        <section className="overflow-hidden rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="grid grid-cols-[1fr_120px_120px_120px] gap-4 bg-[color:var(--bg-base)] px-4 py-3 text-[11px] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-tertiary)]">
            <span>Team</span>
            <span>Repos</span>
            <span>Skills</span>
            <span>Risk flags</span>
          </div>
          {teams.map((team, index) => (
            <div className="grid grid-cols-[1fr_120px_120px_120px] gap-4 border-t border-[color:var(--bg-border)] px-4 py-4 text-sm" key={team.id ?? team.team_name ?? index}>
              <span className="font-semibold text-[color:var(--text-primary)]">{team.team_name ?? team.name ?? "Unassigned"}</span>
              <span className="text-[color:var(--text-secondary)]">{team.repo_count ?? 0}</span>
              <span className="text-[color:var(--text-secondary)]">{team.skill_count ?? 0}</span>
              <span className="text-[color:var(--text-secondary)]">{team.red_flag_count ?? 0}</span>
            </div>
          ))}
        </section>
      ) : (
        <EmptyPanel
          detail="Team management moved into Settings. The backing team rollup is unchanged and will populate when connected repos expose ownership signals."
          icon={<Users2 className="h-5 w-5" />}
          title="Teams appear once repos are connected."
        />
      )}

      <Link className="inline-flex items-center gap-2 text-sm font-semibold text-[color:var(--accent-primary)]" href="/settings/rbac">
        Configure scoped access
        <ArrowRight className="h-4 w-4" />
      </Link>
    </SettingsShell>
  );
}
