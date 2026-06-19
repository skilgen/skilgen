import { ActivityHome } from "./ActivityHome";

export const dynamic = "force-dynamic";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

export default async function ActivityPage({ searchParams }: { searchParams?: PageSearchParams }) {
  return <ActivityHome searchParams={searchParams ? await searchParams : undefined} />;
}
