export default function Loading() {
  return (
    <div className="space-y-6">
      <div className="animate-pulse space-y-3">
        <div className="h-7 w-56 rounded-lg bg-white/5" />
        <div className="h-4 w-96 max-w-full rounded bg-white/5" />
      </div>
      <div className="grid animate-pulse gap-4 md:grid-cols-4">
        {[...Array(4)].map((_, index) => (
          <div className="h-24 rounded-2xl bg-white/5" key={index} />
        ))}
      </div>
      <div className="grid animate-pulse gap-3 md:grid-cols-[180px_1fr_160px]">
        <div className="h-11 rounded-xl bg-white/5" />
        <div className="h-11 rounded-xl bg-white/5" />
        <div className="h-11 rounded-xl bg-white/5" />
      </div>
      <div className="space-y-3">
        {[...Array(4)].map((_, index) => (
          <div className="h-32 rounded-[22px] border border-[color:var(--bg-border)] bg-white/5" key={index} />
        ))}
      </div>
    </div>
  );
}
