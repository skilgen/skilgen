import { withAuth } from "@workos-inc/authkit-nextjs";

import { getABTests, getBootstrapOrg, getMyOrg, getOrgRepos, getRepoSkills, getSkillVersions, type Skill } from "../../../../lib/data";
import { ABShell, type SkillOption } from "./ab-shell";

export const dynamic = "force-dynamic";

async function load(): Promise<{ accessToken: string; orgId: string }> {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: true });
    accessToken = session.accessToken || "";
    const org = accessToken ? await getMyOrg(accessToken) : null;
    if (org) return { accessToken, orgId: org.id };
  } catch {
    // Local preview can run without WorkOS.
  }
  const org = await getBootstrapOrg();
  return { accessToken, orgId: org?.id ?? "current" };
}

export default async function ABTestsPage(): Promise<React.ReactElement> {
  const { accessToken, orgId } = await load();
  const tests = (await getABTests(accessToken, orgId)) ?? [];
  const repos = (await getOrgRepos(accessToken, orgId)) ?? [];
  const skillLists = await Promise.all(repos.map((repo) => getRepoSkills(accessToken, repo.id)));
  const skills = skillLists.flatMap((items) => items ?? []);
  const versionLists = await Promise.all(skills.map((skill: Skill) => getSkillVersions(accessToken, skill.id)));
  const options: SkillOption[] = skills.map((skill, index) => ({
    id: skill.id,
    label: `${skill.repo_name} / ${skill.domain}`,
    versions: (versionLists[index] ?? []).map((version) => ({ id: version.id, version_number: version.version_number, is_latest: version.is_latest })),
  }));
  return <ABShell accessToken={accessToken} orgId={orgId} skills={options} tests={tests} />;
}
