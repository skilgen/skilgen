export default function Loading() {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-3">
          <div className="h-6 w-40 animate-pulse rounded-full bg-white/5" />
          <div className="h-9 w-72 animate-pulse rounded-lg bg-white/5" />
          <div className="h-4 w-[420px] max-w-full animate-pulse rounded bg-white/5" />
        </div>
        <div className="h-10 w-28 animate-pulse rounded-lg bg-white/5" />
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {[...Array(4)].map((_, index) => (
          <div className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={index}>
            <div className="h-4 w-28 animate-pulse rounded bg-white/5" />
            <div className="mt-3 h-8 w-20 animate-pulse rounded bg-white/5" />
          </div>
        ))}
      </div>

      <section className="rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="flex gap-2">
          {[...Array(3)].map((_, index) => (
            <div className="h-10 w-20 animate-pulse rounded-xl bg-white/5" key={index} />
          ))}
        </div>
      </section>

      <div className="overflow-hidden rounded-[24px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
        {[...Array(6)].map((_, index) => (
          <div className="grid gap-4 border-b border-[color:var(--bg-border)] p-5 md:grid-cols-[1.1fr_.6fr_.6fr_.8fr_.8fr_.8fr_1.1fr_1.2fr]" key={index}>
            {[...Array(8)].map((__, cell) => (
              <div className="h-5 animate-pulse rounded bg-white/5" key={cell} />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
