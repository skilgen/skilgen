import type { ReactElement } from "react";

type SectionFallbackProps = {
  section: string;
};

/** Render a consistent visible fallback for dashboard sections that fail to load. */
export function SectionFallback({ section }: SectionFallbackProps): ReactElement {
  return (
    <section className="rounded-xl border border-red-900/40 bg-red-950/20 p-5 text-[13px] text-red-200/80">
      <h2 className="text-[15px] font-semibold text-red-200">Unable to load {section}.</h2>
      <p className="mt-1">Refresh the page or contact support.</p>
    </section>
  );
}
