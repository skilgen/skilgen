import Link from "next/link";
import { ArrowRight, Users2 } from "lucide-react";

import { EmptyPanel, Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";

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
  const payload = await v8Fetch<{ teams: Team[]; total: number }>(accessToken, org.id, "/teams");
  const teams = payload?.teams ?? [];
  const repoCount = teams.reduce((sum, team) => sum + Number(team.repo_count ?? 0), 0);

  return (
    <SettingsShell active="Teams">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Teams" value={teams.length} sub="Derived from repo ownership signals" />
        <Metric label="Repos" value={repoCount} sub="Grouped under Settings without behavior changes" />
        <Metric label="Role source" value="RBAC" sub="Fine-grained access lives in the next tab" />
      </div>

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
