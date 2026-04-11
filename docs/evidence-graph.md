# Evidence Graph

Skilgen’s evidence graph is the bridge between deterministic extraction and Deep Agents synthesis.

## Signals included

- language inventory
- import graph
- symbol graph
- call graph
- config/runtime graph
- test mapping
- requirements evidence
- representative code evidence

## Why it matters

This makes Skilgen more than a path heuristic system. The architecture planner and skill generator can reason over real implementation evidence instead of only folder names.

## Output shape

The evidence graph is returned from:

```bash
skilgen architecture --project-root . --json
```

and is also embedded into the native analysis payload for downstream tooling.
