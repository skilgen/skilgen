import { ActivityHome } from "./ActivityHome";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

export default function ActivityPage({ searchParams }: { searchParams?: PageSearchParams }) {
  return <ActivityHome searchParams={searchParams} />;
}
