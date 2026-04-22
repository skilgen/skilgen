import { ReposTable } from "@/components/repos-table";
import { API_URL, type Org, type Repo } from "../../../lib/data";

export const dynamic = "force-dynamic";

export default async function ReposPage() {
  let repos: Repo[] = [];

  try {
    const bootstrapRes = await fetch(`${API_URL}/orgs/bootstrap`, {
      next: { revalidate: 60 },
    });
    if (bootstrapRes.ok) {
      const org = (await bootstrapRes.json()) as Org;
      const reposRes = await fetch(`${API_URL}/orgs/${org.id}/repos`, {
        next: { revalidate: 60 },
      });
      if (reposRes.ok) {
        repos = ((await reposRes.json()) as Repo[]) ?? [];
      }
    }
  } catch (error) {
    console.error("Failed to fetch repos:", error);
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Repos</h1>
        <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Connected repositories and their Skilgen readiness.</p>
      </div>
      {repos.length > 0 ? (
        <ReposTable repos={repos} />
      ) : (
        <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center text-[color:var(--text-secondary)]">
          No repositories found.
        </section>
      )}
    </div>
  );
}
