type MetricCardProps = {
  label: string;
  value: string | number | null;
  sub: string;
};

export function MetricCard({ label, value, sub }: MetricCardProps) {
  const hasValue = value !== null;
  const displayValue = hasValue ? value : "—";

  return (
    <article className="rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5 transition-colors hover:border-[color:var(--bg-hover)]">
      <div className="mb-3 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--text-tertiary)]">{label}</div>
      <div className={hasValue ? "text-[28px] font-bold leading-none text-white" : "text-[28px] font-bold leading-none text-[color:var(--text-tertiary)]"}>
        {displayValue}
      </div>
      <div className="mt-4 border-t border-[color:var(--bg-elevated)] pt-3 text-[12px] text-[color:var(--text-tertiary)]">{sub}</div>
    </article>
  );
}
