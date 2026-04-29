import { BookOpen, CheckCircle2, Copy } from "lucide-react";

const template = `# Payments skill

## Summary
Use this when editing checkout, billing, invoices, or webhook code.

## Key patterns
- Use the existing BillingService wrapper instead of direct provider calls.
- Persist webhook event ids before side effects.

## Anti-patterns
- Do not trust client-supplied prices.
- Do not retry non-idempotent mutations without an idempotency key.

## Examples
\`\`\`python
await billing_service.create_checkout_session(user_id=user.id, plan_id=plan.id)
\`\`\`

## Last verified — April 2026`;

export default function SkillGuidePage() {
  const rules = [
    ["Add file references", "Groundedness +pts"],
    ["Include 2+ code examples", "Coverage +pts"],
    ["Anti-patterns section", "Coverage +10 pts"],
    ["Last verified date", "Freshness +pts"],
    ["Summary → Patterns → Anti-patterns → Examples", "Structure +pts"],
  ];

  return (
    <div className="space-y-10">
      <header className="relative overflow-hidden rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-8">
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5].map((dot) => <span className="h-2 w-8 rounded-full bg-[color:var(--accent-primary)]" key={dot} />)}
        </div>
        <div className="mt-8 max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-[color:var(--accent-primary)]/30 px-3 py-1 text-xs font-semibold text-[color:var(--accent-primary)]"><BookOpen className="h-3.5 w-3.5" /> Skill Writing Guide</div>
          <h1 className="mt-4 text-4xl font-semibold tracking-normal text-[color:var(--text-primary)]">Write skills that make agents code like your best engineer.</h1>
          <p className="mt-4 text-base leading-7 text-[color:var(--text-secondary)]">A skill is institutional memory packaged for AI agents: patterns, file references, examples, and the rules reviewers actually enforce.</p>
        </div>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-[color:var(--accent-red)]/30 bg-[color:var(--accent-red)]/10 p-5">
          <h2 className="font-semibold">Before: generic agent output</h2>
          <pre className="mt-4 overflow-x-auto rounded-md bg-black/30 p-4 text-sm text-red-100"><code>{`db.execute(f"SELECT * FROM users WHERE id={id}")`}</code></pre>
        </div>
        <div className="rounded-lg border border-[color:var(--accent-green)]/30 bg-[color:var(--accent-green)]/10 p-5">
          <h2 className="font-semibold">After: skill-loaded output</h2>
          <pre className="mt-4 overflow-x-auto rounded-md bg-black/30 p-4 text-sm text-green-100"><code>{`result = await db.execute(select(User).where(User.id == user_id))`}</code></pre>
        </div>
      </section>

      <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <h2 className="text-xl font-semibold">Anatomy of a great skill</h2>
        <div className="mt-5 grid gap-5 lg:grid-cols-[1.3fr_1fr]">
          <pre className="overflow-x-auto rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-base)] p-5 text-sm leading-6 text-[color:var(--text-secondary)]"><code>{template}</code></pre>
          <div className="space-y-3">
            {["Summary tells agents when to load it.", "Patterns encode the local way.", "Anti-patterns prevent review churn.", "Examples turn advice into executable taste."].map((item) => <div className="rounded-md border border-[color:var(--bg-border)] bg-black/20 p-3 text-sm" key={item}>{item}</div>)}
          </div>
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-5">
        {rules.map(([rule, boost]) => (
          <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={rule}>
            <CheckCircle2 className="h-5 w-5 text-[color:var(--accent-green)]" />
            <h3 className="mt-3 text-sm font-semibold">{rule}</h3>
            <p className="mt-2 text-xs text-[color:var(--accent-primary)]">{boost}</p>
          </article>
        ))}
      </section>

      <section className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-xl font-semibold">Starter template</h2>
          <button className="inline-flex items-center rounded-md border border-[color:var(--bg-border)] px-3 py-2 text-sm font-semibold"><Copy className="mr-2 h-4 w-4" /> Copy</button>
        </div>
        <pre className="mt-4 overflow-x-auto rounded-lg bg-[color:var(--bg-base)] p-5 text-sm text-[color:var(--text-secondary)]"><code>{template}</code></pre>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        {["Vague advice", "No examples", "No freshness signal"].map((mistake) => (
          <article className="rounded-lg border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-5" key={mistake}>
            <h3 className="font-semibold text-red-200">{mistake}</h3>
            <p className="mt-3 text-sm text-[color:var(--text-secondary)]">Bad: “Follow best practices.”</p>
            <p className="mt-3 rounded-md bg-[color:var(--accent-green)]/10 p-3 text-sm text-green-200">Better: name the exact file, helper, anti-pattern, and verified date.</p>
          </article>
        ))}
      </section>
    </div>
  );
}
