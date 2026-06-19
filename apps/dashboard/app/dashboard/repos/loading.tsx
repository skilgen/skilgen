export default function Loading() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div className="space-y-3">
          <div className="h-4 w-32 rounded bg-white/5" />
          <div className="h-8 w-48 rounded-lg bg-white/5" />
          <div className="h-4 w-36 rounded bg-white/5" />
        </div>
        <div className="h-10 w-36 rounded-md bg-white/5" />
      </div>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        <div className="border-b border-[color:var(--bg-border)] p-5">
          <div className="h-10 w-full max-w-sm rounded-md bg-white/5" />
        </div>
        <div className="divide-y divide-[color:var(--bg-border)]">
          {Array.from({ length: 6 }).map((_, index) => (
            <div className="grid gap-4 p-5 md:grid-cols-[minmax(0,1fr)_120px_140px_120px]" key={index}>
              <div className="space-y-2">
                <div className="h-4 w-48 rounded bg-white/5" />
                <div className="h-3 w-64 rounded bg-white/5" />
              </div>
              <div className="h-7 w-20 rounded-full bg-white/5" />
              <div className="h-4 w-24 rounded bg-white/5" />
              <div className="h-8 w-28 rounded-md bg-white/5" />
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
