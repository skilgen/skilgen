export default function Loading() {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-3">
          <div className="h-6 w-44 animate-pulse rounded-full bg-white/5" />
          <div className="h-9 w-80 animate-pulse rounded-lg bg-white/5" />
          <div className="h-4 w-[520px] max-w-full animate-pulse rounded bg-white/5" />
        </div>
        <div className="h-10 w-28 animate-pulse rounded-lg bg-white/5" />
      </div>

      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex flex-wrap justify-between gap-3">
          <div className="flex gap-2">
            {[...Array(3)].map((_, index) => <div className="h-10 w-20 animate-pulse rounded-xl bg-white/5" key={index} />)}
          </div>
          <div className="h-10 w-44 animate-pulse rounded-xl bg-white/5" />
        </div>
      </section>

      <div className="grid gap-4 lg:grid-cols-3">
        {[...Array(3)].map((_, index) => (
          <div className="min-h-[150px] rounded-[22px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={index}>
            <div className="h-8 w-12 animate-pulse rounded bg-white/5" />
            <div className="mt-5 h-5 w-32 animate-pulse rounded bg-white/5" />
            <div className="mt-3 h-9 w-24 animate-pulse rounded bg-white/5" />
            <div className="mt-4 h-4 w-36 animate-pulse rounded bg-white/5" />
          </div>
        ))}
      </div>

      <div className="overflow-hidden rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        {[...Array(8)].map((_, row) => (
          <div className="grid min-w-[1680px] grid-cols-[60px_160px_repeat(13,100px)] gap-4 border-b border-[color:var(--bg-border)] p-4" key={row}>
            {[...Array(15)].map((__, cell) => <div className="h-5 animate-pulse rounded bg-white/5" key={cell} />)}
          </div>
        ))}
      </div>
    </div>
  );
}
