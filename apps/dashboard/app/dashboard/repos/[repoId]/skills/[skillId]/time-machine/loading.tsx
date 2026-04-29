export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="mb-6 space-y-3">
        <div className="h-4 w-28 rounded bg-white/5" />
        <div className="h-8 w-80 max-w-full rounded bg-white/5" />
        <div className="h-4 w-[460px] max-w-full rounded bg-white/5" />
      </div>
      <div className="grid min-h-[680px] gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="space-y-3 border-r border-[color:var(--bg-border)] pr-4">
          <div className="h-36 rounded-md bg-white/5" />
          {Array.from({ length: 5 }).map((_, index) => (
            <div className="h-24 rounded-md bg-white/5" key={index} />
          ))}
        </aside>
        <main className="rounded-md border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
          <div className="h-24 border-b border-[color:var(--bg-border)] bg-white/5" />
          <div className="m-4 h-[520px] rounded-md bg-white/5" />
        </main>
      </div>
    </div>
  );
}
