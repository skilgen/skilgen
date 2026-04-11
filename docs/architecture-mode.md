# Architecture Mode

`skilgen architecture` turns repo evidence into an architecture blueprint that coding agents can load before they start editing code.

## What it uses

- requirements intent
- file and path signals
- import relationships
- symbol graph
- call graph
- config and runtime graph
- test-to-code mapping
- representative source snippets

## Commands

```bash
skilgen architecture --project-root . --requirements docs/requirements.pdf
skilgen architecture --project-root . --json
skilgen architecture --project-root . --graph-format mermaid --graph-file architecture.mmd
skilgen architecture --project-root . --graph-format json --graph-file architecture.json
```

## What you get

- `ARCHITECTURE.md`
- `evidence_graph`
- architecture domains with responsibilities and evidence paths
- graph exports for dashboards or follow-on tooling

Use this mode when you want Skilgen to answer not just “what files exist?” but “what are the real architectural boundaries and what should become first-class skills?”
