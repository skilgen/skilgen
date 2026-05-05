import { ActivityHome } from "../ActivityHome";

type PageSearchParams = Promise<Record<string, string | string[] | undefined>>;

export default function ActivityLiveFeedPage({ searchParams }: { searchParams?: PageSearchParams }) {
  return <ActivityHome searchParams={searchParams} />;
}
