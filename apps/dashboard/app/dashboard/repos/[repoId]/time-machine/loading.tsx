export default function Loading() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="space-y-3">
        <div className="h-4 w-28 rounded bg-white/5" />
        <div className="h-8 w-48 rounded-lg bg-white/5" />
        <div className="h-4 w-96 max-w-full rounded bg-white/5" />
      </div>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4">
        <div className="h-4 w-40 rounded bg-white/5" />
        <div className="mt-3 grid gap-3 md:grid-cols-[260px_180px]">
          <div className="h-11 rounded-md bg-white/5" />
          <div className="h-11 rounded-md bg-white/5" />
        </div>
      </section>
      <section className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5">
        <div className="h-4 w-24 rounded bg-white/5" />
        <div className="mt-4 flex gap-3 overflow-hidden">
          {Array.from({ length: 4 }).map((_, index) => (
            <div className="h-[122px] min-w-[180px] rounded-lg bg-white/5" key={index} />
          ))}
        </div>
      </section>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
        <div className="h-[520px] rounded-xl bg-white/5" />
        <div className="h-[360px] rounded-xl bg-white/5" />
      </div>
    </div>
  );
}
