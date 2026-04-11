# Skilgen Score

Skilgen Score is the quality standard for a repo’s skill system.

## Repo score

The top-level repo score is `0-100` and is made of four `0-25` subscores:

- groundedness
- coverage
- freshness
- structure

## Drill-downs

Skilgen also returns:

- materialized domain scores
- per-skill scores
- inferred-only domains as a planning signal

## Opinionated quality gates

The score is intentionally not just arithmetic. Weak grounding, low coverage, stale skills, and structural gaps can cap the final score even if the raw score is higher.

## Commands

```bash
skilgen score --project-root .
skilgen score --project-root . --history
```

## History and trend

Skilgen stores score snapshots in `.skilgen/state/score-history.jsonl` and can surface:

- score delta from the previous snapshot
- domain regressions
- recent history for dashboards or CI checks
