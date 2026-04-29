import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { CheckCircle2, Users2 } from "lucide-react";

import { getBootstrapOrg, getKnowledgeRisk, getMyOrg } from "../../../lib/data";

export const dynamic = "force-dynamic";

const levels = ["critical", "high", "medium"] as const;
const types = ["missing_skill", "zero_load", "stale_high_load"] as const;

export default async function KnowledgeRiskPage() {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: true });
    accessToken = session.accessToken || "";
  } catch {
    accessToken = "";
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const data = org ? await getKnowledgeRisk(accessToken, org.id) : null;
  const risks = data?.risks ?? [];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Knowledge Risk</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Find knowledge concentrated in people, stale high-load skills, and missing skill coverage.</p>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        {[["Critical", data?.critical_count ?? 0, "text-[color:var(--accent-red)]"], ["High", data?.high_count ?? 0, "text-amber-300"], ["Medium", data?.medium_count ?? 0, "text-[color:var(--accent-primary)]"]].map(([label, count, tone]) => (
          <div className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={label}>
            <div className="text-xs font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
            <div className={`mt-3 text-4xl font-semibold ${tone}`}>{count}</div>
          </div>
        ))}
      </section>

      <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <h2 className="text-base font-semibold">Risk matrix</h2>
        <div className="mt-4 grid grid-cols-3 gap-2">
          {levels.flatMap((level) =>
            types.map((type) => {
              const count = risks.filter((risk) => risk.risk_level === level && risk.risk_type === type).length;
              return (
                <a className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-sm hover:border-[color:var(--accent-primary)]" href={`#${level}-${type}`} key={`${level}-${type}`}>
                  <div className="font-semibold capitalize text-[color:var(--text-primary)]">{level.replace("_", " ")}</div>
                  <div className="mt-1 text-[12px] text-[color:var(--text-secondary)]">{type.replaceAll("_", " ")}</div>
                  <div className="mt-3 text-2xl font-semibold text-[color:var(--accent-primary)]">{count}</div>
                </a>
              );
            }),
          )}
        </div>
      </section>

      {risks.length === 0 ? (
        <section className="rounded-lg border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 p-8 text-center">
          <CheckCircle2 className="mx-auto h-10 w-10 text-[color:var(--accent-green)]" />
          <h2 className="mt-3 text-lg font-semibold">No concentration risks detected</h2>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Your critical knowledge is documented, fresh, and discoverable by agents.</p>
        </section>
      ) : (
        <section className="grid gap-4">
          {risks.map((risk) => (
            <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" id={`${risk.risk_level}-${risk.risk_type}`} key={`${risk.repo_id}-${risk.domain}-${risk.risk_type}`}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <Users2 className="h-4 w-4 text-[color:var(--accent-primary)]" />
                    <h3 className="font-semibold text-[color:var(--text-primary)]">{risk.domain} in {risk.repo_name}</h3>
                  </div>
                  <p className="mt-2 text-sm text-[color:var(--text-secondary)]">{risk.reason}</p>
                </div>
                <span className="rounded-full border border-[color:var(--bg-border)] px-3 py-1 text-xs font-semibold capitalize">{risk.risk_level}</span>
              </div>
              <p className="mt-4 rounded-md bg-[color:var(--bg-base)] p-3 text-sm text-[color:var(--text-primary)]">{risk.recommendation}</p>
              <div className="mt-4 flex flex-wrap gap-2 text-xs text-[color:var(--text-tertiary)]">{risk.affected_files.map((file) => <span className="rounded bg-black/20 px-2 py-1 font-mono" key={file}>{file}</span>)}</div>
              <Link className="mt-4 inline-flex text-sm font-semibold text-[color:var(--accent-primary)]" href={risk.skill_exists && risk.skill_id ? `/dashboard/repos/${risk.repo_id}/skills/${risk.skill_id}` : `/dashboard/repos/${risk.repo_id}`}>{risk.skill_exists ? "View skill" : "Create skill"} →</Link>
            </article>
          ))}
        </section>
      )}
    </div>
  );
}
