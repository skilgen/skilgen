export default function Loading() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="h-8 w-44 rounded-lg bg-white/5" />
          <div className="mt-3 h-4 w-80 rounded bg-white/5" />
        </div>
        <div className="h-10 w-32 rounded-md bg-white/5" />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {[...Array(4)].map((_, index) => (
          <div className="h-56 rounded-xl border border-[color:var(--bg-border)] bg-white/5" key={index} />
        ))}
      </div>
    </div>
  );
}
