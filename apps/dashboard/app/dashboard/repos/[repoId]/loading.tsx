export default function Loading() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="space-y-3">
        <div className="h-4 w-28 rounded bg-white/5" />
        <div className="h-8 w-56 rounded-lg bg-white/5" />
        <div className="h-4 w-80 rounded bg-white/5" />
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div className="h-28 rounded-xl bg-white/5" key={index} />
        ))}
      </div>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="h-96 rounded-xl bg-white/5" />
        <div className="h-96 rounded-xl bg-white/5" />
      </div>
    </div>
  );
}
