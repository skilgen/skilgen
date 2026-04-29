export default function Loading() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div className="space-y-3">
          <div className="h-8 w-56 animate-pulse rounded-lg bg-white/5" />
          <div className="h-4 w-96 animate-pulse rounded bg-white/5" />
        </div>
        <div className="h-10 w-28 animate-pulse rounded-lg bg-white/5" />
      </div>
      <div className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="grid gap-3 md:grid-cols-[1fr_1fr_180px]">
          <div className="h-10 animate-pulse rounded-xl bg-white/5" />
          <div className="h-10 animate-pulse rounded-xl bg-white/5" />
          <div className="h-10 animate-pulse rounded-xl bg-white/5" />
        </div>
      </div>
      <div className="space-y-3">
        {[...Array(6)].map((_, index) => (
          <div className="relative overflow-hidden rounded-[20px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={index}>
            <div className="absolute inset-y-0 left-0 w-1 animate-pulse bg-white/10" />
            <div className="grid gap-4 md:grid-cols-[1fr_170px_150px]">
              <div className="space-y-3">
                <div className="h-6 w-28 animate-pulse rounded-full bg-white/5" />
                <div className="h-5 w-2/3 animate-pulse rounded bg-white/5" />
                <div className="h-4 w-48 animate-pulse rounded bg-white/5" />
              </div>
              <div className="space-y-3">
                <div className="h-4 w-24 animate-pulse rounded bg-white/5" />
                <div className="h-8 w-full animate-pulse rounded-full bg-white/5" />
              </div>
              <div className="space-y-3">
                <div className="h-8 w-24 animate-pulse rounded-full bg-white/5" />
                <div className="h-8 w-full animate-pulse rounded-lg bg-white/5" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
