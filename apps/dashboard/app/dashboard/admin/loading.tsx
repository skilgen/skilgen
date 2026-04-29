export default function Loading() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-56 animate-pulse rounded-lg bg-white/5" />
      <div className="grid gap-4 md:grid-cols-4">{Array.from({ length: 8 }).map((_, i) => <div className="h-28 animate-pulse rounded-2xl bg-white/5" key={i} />)}</div>
      <div className="h-72 animate-pulse rounded-[24px] bg-white/5" />
      <div className="h-72 animate-pulse rounded-[24px] bg-white/5" />
    </div>
  );
}
