export default function AuditLoading() {
  return (
    <div className="space-y-6">
      <div>
        <div className="h-9 w-44 animate-pulse rounded-lg bg-white/10" />
        <div className="mt-3 h-5 w-80 max-w-full animate-pulse rounded bg-white/10" />
      </div>
      <div className="sticky top-0 z-20 border-y border-[color:var(--bg-border)] bg-[color:var(--bg-base)]/95 py-3 backdrop-blur">
        <div className="flex flex-wrap items-center gap-3">
          <div className="h-10 min-w-[240px] flex-1 animate-pulse rounded-lg bg-white/10" />
          <div className="h-10 w-40 animate-pulse rounded-lg bg-white/10" />
          <div className="h-10 w-36 animate-pulse rounded-lg bg-white/10" />
          <div className="h-10 w-32 animate-pulse rounded-lg bg-white/10" />
          <div className="h-10 w-32 animate-pulse rounded-lg bg-white/10" />
          <div className="h-10 w-28 animate-pulse rounded-lg bg-white/10" />
        </div>
      </div>
      <div className="space-y-4">
        {Array.from({ length: 8 }).map((_, index) => (
          <div className="relative border-l border-[color:var(--bg-border)] pl-5" key={index}>
            <span className="absolute -left-[5px] top-4 h-3 w-3 rounded-full bg-white/10 ring-4 ring-[color:var(--bg-base)]" />
            <div className="border-b border-[color:var(--bg-border)] pb-5">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 animate-pulse rounded-full bg-white/10" />
                <div className="h-4 w-28 animate-pulse rounded bg-white/10" />
                <div className="h-6 w-40 animate-pulse rounded-md bg-white/10" />
              </div>
              <div className="mt-4 h-4 w-4/5 animate-pulse rounded bg-white/10" />
              <div className="mt-2 h-4 w-2/5 animate-pulse rounded bg-white/10" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
