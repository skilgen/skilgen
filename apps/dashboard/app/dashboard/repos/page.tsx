import Link from "next/link";
import { withAuth } from "@workos-inc/authkit-nextjs";
import { Plus } from "lucide-react";

import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { SectionFallback } from "@/components/section-fallback";
import { API_URL, type Org, type Repo } from "../../../lib/data";
import { AddReposButton } from "./add-repos-button";
import { ReposBrowser, type RepoListItem } from "./repos-browser";

export default async function ReposPage() {
  let accessToken = "";
  let orgId = "";
  let repos: RepoListItem[] = [];
  let reposError = false;

  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Repos auth unavailable:", error);
  }

  try {
    if (accessToken) {
      const orgRes = await fetch(`${API_URL}/me/org`, {
        cache: "no-store",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (orgRes.ok) {
        const org = (await orgRes.json()) as Org;
        orgId = org.id;
      }
    }

    if (!orgId) {
      const bootstrapRes = await fetch(`${API_URL}/orgs/bootstrap`, {
        cache: "no-store",
      });
      if (bootstrapRes.ok) {
        const org = (await bootstrapRes.json()) as Org;
        orgId = org.id;
      } else {
        reposError = true;
      }
    }

    if (orgId) {
      const reposRes = await fetch(`${API_URL}/orgs/${orgId}/repos`, {
        cache: "no-store",
        headers: accessToken
          ? {
              Authorization: `Bearer ${accessToken}`,
            }
          : undefined,
      });
      if (reposRes.ok) {
        repos = (((await reposRes.json()) as Repo[]) ?? []) as RepoListItem[];
      } else {
        reposError = true;
      }
    }
  } catch (error) {
    reposError = true;
    console.error("Failed to fetch repos:", error);
  }

  const connectLabel = repos.length === 0 ? "Connect repo" : "Add more repos";
  const hasInstallation = repos.some((repo) => repo.installation_id != null) || repos.length > 0;

  return (
    <div>
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="mb-3 flex items-center gap-2 text-[12px] text-[color:var(--text-tertiary)]">
            <Link className="hover:text-[color:var(--accent-primary)]" href="/dashboard">
              Overview
            </Link>
            <span>/</span>
            <span className="text-[color:var(--text-secondary)]">Repos</span>
          </div>
          <h1 className="text-2xl font-semibold text-[color:var(--text-primary)]">Repositories</h1>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{repos.length} repos connected</p>
        </div>

        <AddReposButton accessToken={accessToken} hasInstallation={hasInstallation} label={connectLabel} orgId={orgId} />
      </div>

      <SectionErrorBoundary section="repositories">
        {reposError ? (
          <SectionFallback section="repositories" />
        ) : repos.length > 0 ? (
          <ReposBrowser accessToken={accessToken} orgId={orgId} repos={repos} />
        ) : (
          <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-10 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[color:var(--accent-primary)]">
              <Plus className="h-5 w-5" />
            </div>
            <h2 className="text-[17px] font-semibold text-[color:var(--text-primary)]">Connect your first repository</h2>
            <p className="mx-auto mt-2 max-w-md text-[14px] text-[color:var(--text-secondary)]">
              Install the Skillayer GitHub App to analyse repositories, generate skills, and track score history.
            </p>
            <div className="mt-6 flex justify-center">
              <AddReposButton accessToken={accessToken} hasInstallation={hasInstallation} label="Connect repo" orgId={orgId} />
            </div>
          </section>
        )}
      </SectionErrorBoundary>
    </div>
  );
}
