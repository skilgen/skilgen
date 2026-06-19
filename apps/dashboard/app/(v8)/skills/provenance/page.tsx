import { withAuth } from "@workos-inc/authkit-nextjs";
import { FileCheck2, GitCommitHorizontal, KeyRound, ShieldCheck } from "lucide-react";

import { API_URL, getBootstrapOrg, getMyOrg, type Org } from "../../../../lib/data";

type V8ProvenanceVersion = {
  skill_id: string;
  version_id: string;
  version_number: number;
  content_hash: string;
  signature_status: string;
  git_commit: string | null;
  generation_run_id: string;
  scoring_run_id: string;
  approver: string | null;
  created_at: string;
};

type V8ProvenanceResponse = {
  versions: V8ProvenanceVersion[];
  transparency_log: Array<Record<string, unknown>>;
  total: number;
};

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

async function getProvenance(accessToken: string, orgId: string): Promise<V8ProvenanceResponse | null> {
  try {
    const response = await fetch(`${API_URL}/v8/orgs/${orgId}/skills/provenance`, {
      cache: "no-store",
      headers: {
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) return null;
    return (await response.json()) as V8ProvenanceResponse;
  } catch {
    return null;
  }
}

function shortHash(value: string | null): string {
  if (!value) return "unlinked";
  return value.length > 12 ? `${value.slice(0, 12)}...` : value;
}

function fmtDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
}

function Metric({ label, value, detail, icon }: { label: string; value: string | number; detail: string; icon: React.ReactNode }) {
  return (
    <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="flex items-center justify-between gap-3">
        <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-tertiary)]">{label}</div>
        <div className="text-[color:var(--accent-primary)]">{icon}</div>
      </div>
      <div className="mt-3 text-[30px] font-semibold text-[color:var(--text-primary)]">{value}</div>
      <p className="mt-2 text-xs leading-5 text-[color:var(--text-secondary)]">{detail}</p>
    </article>
  );
}

function VersionCard({ version }: { version: V8ProvenanceVersion }) {
  const verified = version.signature_status === "verified";
  return (
    <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-md bg-[color:var(--accent-primary)]/15 px-2 py-1 text-xs font-semibold text-[color:var(--accent-primary)]">v{version.version_number}</span>
            <h2 className="font-semibold text-[color:var(--text-primary)]">{version.skill_id}</h2>
            <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${verified ? "border-[color:var(--accent-green)]/40 text-[color:var(--accent-green)]" : "border-amber-400/40 text-amber-200"}`}>
              {version.signature_status}
            </span>
          </div>
          <p className="mt-2 text-sm text-[color:var(--text-secondary)]">Created {fmtDate(version.created_at)}</p>
        </div>
        <div className="rounded-md border border-[color:var(--bg-border)] bg-black/20 px-3 py-2 font-mono text-xs text-[color:var(--text-secondary)]">{version.version_id}</div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Content hash</div>
          <div className="mt-2 break-all font-mono text-sm text-[color:var(--text-primary)]">{shortHash(version.content_hash)}</div>
        </div>
        <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Git commit</div>
          <div className="mt-2 break-all font-mono text-sm text-[color:var(--text-primary)]">{shortHash(version.git_commit)}</div>
        </div>
        <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Generation run</div>
          <div className="mt-2 break-all font-mono text-sm text-[color:var(--text-primary)]">{version.generation_run_id || "unknown"}</div>
        </div>
        <div className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3">
          <div className="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">Scoring run</div>
          <div className="mt-2 break-all font-mono text-sm text-[color:var(--text-primary)]">{version.scoring_run_id || "unknown"}</div>
        </div>
      </div>

      <div className="mt-4 rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-3 text-sm text-[color:var(--text-secondary)]">
        Approver: <span className="font-semibold text-[color:var(--text-primary)]">{version.approver ?? "No manual approver recorded"}</span>
      </div>
    </article>
  );
}

export default async function SkillsProvenancePage() {
  const { accessToken, org } = await loadContext();
  const provenance = org?.id ? await getProvenance(accessToken, org.id) : null;
  const versions = provenance?.versions ?? [];
  const verified = versions.filter((version) => version.signature_status === "verified").length;
  const linkedCommits = versions.filter((version) => version.git_commit).length;
  const generationRuns = new Set(versions.map((version) => version.generation_run_id).filter(Boolean)).size;
  const scoringRuns = new Set(versions.map((version) => version.scoring_run_id).filter(Boolean)).size;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-[32px] font-semibold text-[color:var(--text-primary)]">Provenance</h1>
          <p className="mt-2 max-w-3xl text-[15px] leading-6 text-[color:var(--text-secondary)]">Track skill versions from generation to scoring and signature verification without leaving the migrated Skillayer Skills surface.</p>
        </div>
        <div className="inline-flex w-fit items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-xs font-semibold text-[color:var(--text-secondary)]">
          <ShieldCheck className="h-4 w-4 text-[color:var(--accent-primary)]" />
          v8 provenance API
        </div>
      </div>

      <section className="grid gap-4 md:grid-cols-4">
        <Metric detail="Skill versions returned by the v8 provenance endpoint." icon={<FileCheck2 className="h-4 w-4" />} label="Versions" value={provenance?.total ?? 0} />
        <Metric detail="Versions with content-hash backed signature evidence." icon={<KeyRound className="h-4 w-4" />} label="Verified" value={verified} />
        <Metric detail="Versions linked to source commits when available." icon={<GitCommitHorizontal className="h-4 w-4" />} label="Git commits" value={linkedCommits} />
        <Metric detail={`${scoringRuns} scoring runs across ${generationRuns} generation runs.`} icon={<ShieldCheck className="h-4 w-4" />} label="Run links" value={generationRuns + scoringRuns} />
      </section>

      <section className="rounded-[8px] border border-[color:var(--accent-primary)]/35 bg-[color:var(--accent-primary)]/10 p-4">
        <p className="text-sm leading-6 text-[color:var(--text-secondary)]">
          Provenance evidence includes skill id, version id, version number, content hash, signature status, git commit, generation run, scoring run, approver, creation time, and transparency-log readiness from `/v8/orgs/:orgId/skills/provenance`.
        </p>
      </section>

      {provenance === null ? (
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-sm text-[color:var(--text-secondary)]">
          <FileCheck2 className="mx-auto h-6 w-6 text-[color:var(--text-tertiary)]" />
          <p className="mt-4 text-[15px] font-semibold text-[color:var(--text-primary)]">Provenance could not reach the API.</p>
          <p className="mx-auto mt-2 max-w-xl leading-6">Refresh after sign-in. Skill version evidence will appear here once the authenticated v8 Skills API call succeeds.</p>
        </div>
      ) : versions.length === 0 ? (
        <div className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-sm text-[color:var(--text-secondary)]">
          <FileCheck2 className="mx-auto h-6 w-6 text-[color:var(--text-tertiary)]" />
          <p className="mt-4 text-[15px] font-semibold text-[color:var(--text-primary)]">No skill version evidence yet.</p>
          <p className="mx-auto mt-2 max-w-xl leading-6">Analyze a repository to generate signed skill versions and begin building a provenance chain.</p>
        </div>
      ) : (
        <section className="space-y-4">
          {versions.map((version) => <VersionCard key={version.version_id} version={version} />)}
        </section>
      )}

      <section className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex items-start gap-3">
          <KeyRound className="mt-0.5 h-4 w-4 shrink-0 text-[color:var(--accent-primary)]" />
          <p className="text-sm leading-6 text-[color:var(--text-secondary)]">
            Transparency log entries: <span className="font-semibold text-[color:var(--text-primary)]">{provenance?.transparency_log.length ?? 0}</span>. The surface stays honest when the log is not populated yet and still exposes hash-backed version evidence.
          </p>
        </div>
      </section>
    </div>
  );
}
