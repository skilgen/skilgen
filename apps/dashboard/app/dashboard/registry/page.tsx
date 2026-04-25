import { withAuth } from "@workos-inc/authkit-nextjs";

import { getBootstrapOrg, getCompatibilityMatrix, getMarketplaceEntries, getMyOrg, getOrgRegistryEntries } from "../../../lib/data";
import { RegistryShell } from "./registry-shell";

export const dynamic = "force-dynamic";

type RegistryPageProps = {
  searchParams?: Promise<{ tab?: string }>;
};

export default async function RegistryPage({ searchParams }: RegistryPageProps) {
  let accessToken = "";
  try {
    const session = await withAuth({ ensureSignedIn: false });
    accessToken = session?.accessToken || "";
  } catch (error) {
    console.error("Registry auth unavailable:", error);
  }
  const org = (accessToken ? await getMyOrg(accessToken) : null) ?? (await getBootstrapOrg());
  const orgId = org?.id ?? "";
  const resolved = searchParams ? await searchParams : {};
  const activeTab = resolved.tab === "marketplace" || resolved.tab === "import" || resolved.tab === "compatibility" ? resolved.tab : "org";
  const [orgEntries, marketplace, compatibility] = orgId
    ? await Promise.all([getOrgRegistryEntries(accessToken, orgId), getMarketplaceEntries(), getCompatibilityMatrix(accessToken, orgId)])
    : [null, null, null];

  return (
    <RegistryShell
      accessToken={accessToken}
      activeTab={activeTab}
      compatibility={compatibility}
      marketplaceEntries={marketplace?.entries ?? []}
      orgEntries={orgEntries?.entries ?? []}
      orgId={orgId}
    />
  );
}
