export default function Loading() {
  return (
    <div className="animate-pulse space-y-6 p-8">
      <div className="h-8 w-48 rounded-lg bg-white/5" />
      <div className="h-4 w-96 rounded bg-white/5" />
      <div className="grid grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div className="h-28 rounded-xl bg-white/5" key={i} />
        ))}
      </div>
      <div className="h-64 rounded-xl bg-white/5" />
    </div>
  );
}
