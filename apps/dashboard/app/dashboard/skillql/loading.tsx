export default function Loading() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="space-y-3 text-center">
        <div className="mx-auto h-12 w-44 animate-pulse rounded-xl bg-white/5" />
        <div className="mx-auto h-4 w-[520px] max-w-full animate-pulse rounded bg-white/5" />
      </div>
      <section className="rounded-[28px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="h-24 animate-pulse rounded-2xl bg-white/5" />
        <div className="mt-4 flex items-center justify-between">
          <div className="h-4 w-16 animate-pulse rounded bg-white/5" />
          <div className="h-10 w-32 animate-pulse rounded-xl bg-white/5" />
        </div>
      </section>
      <div className="grid gap-3 md:grid-cols-2">
        {[...Array(4)].map((_, index) => (
          <div className="rounded-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={index}>
            <div className="h-4 w-36 animate-pulse rounded bg-white/5" />
            <div className="mt-4 space-y-2">
              {[...Array(3)].map((__, item) => <div className="h-9 animate-pulse rounded-full bg-white/5" key={item} />)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
