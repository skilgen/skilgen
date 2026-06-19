# Skilgen Score

The Skilgen Score is a 0-100 measure of how usable your repository knowledge is
for AI coding agents. It is not a code-quality score and it is not a generic
documentation score. It is a measure of how well the generated skill system
captures the operating context an agent needs to work safely and productively.

The score has four 25-point subscores:

- Groundedness
- Coverage
- Freshness
- Structure

## Overview

The score answers a practical question: if an agent had to work in this repo
today, how much trustworthy context would it have? A repo can have good source
code and still score poorly if the skills are generic, stale, or incomplete.

The score is used in three places:

- local CLI feedback
- CI gates with `skilgen score --ci`
- Skillayer dashboard, PR comments, and check runs

## The Four Subscores

### Groundedness (0–25)

Groundedness measures how much of the skill tree is backed by concrete evidence.
Evidence includes source paths, symbol names, imports, tests, schema fields,
operations, manifests, findings, runbook commands, and incident timelines.

Scoring rubric:

- `0–8`: fewer than 3 evidence items or mostly generic prose
- `9–15`: some evidence exists, but many patterns are still broad or vague
- `16–20`: most patterns reference real repo artifacts
- `21–25`: patterns, anti-patterns, and check paths are all tied to specifics

Example of a strong grounded skill:

- names the exact API handlers involved
- references actual tests that validate the behavior
- lists the files the agent should inspect first
- includes imports, routes, or commands as evidence

What earns points:

- AST-derived names and symbols
- actual file paths and command names
- real endpoint names, schema names, resource names, or model names
- check paths that can be run or verified

What loses points:

- advice like “follow best practices” with no evidence
- empty evidence sections
- placeholder text instead of repo-specific facts

Important cap:

If the skill tree has effectively no evidence, Groundedness is capped at `8/25`
even if the Markdown looks polished.

### Coverage (0–25)

Coverage measures how much of the repository has been mapped into meaningful
skills. For code, that means materialized domains from the code graph. For
non-code sources, that means generated skills for APIs, infrastructure, data,
security, and operational knowledge.

Coverage rewards:

- detected domains that were actually materialized into `SKILL.md`
- skills tied to files, schemas, manifests, or documents
- additional source categories beyond code-only analysis

Coverage loses points when:

- domains are inferred but never written out
- important categories are missing entirely
- only a small slice of the repo has generated skills

Example coverage output in the CLI:

```text
Coverage       ███████████████░░░░░  19/25
```

Example interpretation:

- codebase architecture is covered
- testing conventions are covered
- internal tools are covered because OpenAPI or GraphQL inputs were parsed
- operational knowledge is still missing because no runbooks or incidents exist

### Freshness (0–25)

Freshness measures how current the skill tree is relative to the underlying
repo. It compares skill generation time to repository changes and analysis
history.

Freshness uses:

- git recency when available
- change velocity on the affected repo
- timestamps on generated skills and score history

The important fallback behavior is:

- when git is unavailable, Skilgen defaults Freshness to `15/25`
- this avoids unfairly dropping the score to zero for zip-based environments

Freshness decays when the repo changes but `skilgen deliver` has not been run
recently enough to refresh the skill tree.

Operational implication:

- `freshness < 20`
- and `load_count_30d > 5`

This combination is treated as a stale-but-active signal and can trigger Slack
alerts in Skillayer.

### Structure (0–25)

Structure measures whether the generated skills are shaped in a consistent,
agent-usable format.

A high-structure skill usually has:

- a valid H1 title
- non-empty content
- a domain summary
- concrete sections such as key files or patterns
- check paths where applicable
- valid file references

A poor-structure skill often looks like:

- one short paragraph with no headings
- missing or empty sections
- broken references
- no check paths or actionable guidance

Example of a healthy structure:

```markdown
# payments_api

## Domain summary
Handles payment authorization, capture, refund, and webhook intake.

## Key files
- api/payments/routes.py
- api/payments/service.py

## Detected patterns
- Bearer auth
- Idempotency keys

## Agent guidance
- Run `pytest tests/payments -q`
```

## Quality Gates and Score Caps

The total score is not just a sum. Weak subscores can cap the final result so
one strong dimension cannot hide a severe blind spot.

Examples:

- no evidence means Groundedness is capped at `8`
- poor coverage means the repo cannot score as Excellent
- very low freshness means the total may look healthy but still fail CI gates

Default grade bands:

| Score | Grade |
|---:|---|
| 85–100 | Excellent |
| 70–84 | Good |
| 50–69 | Needs work |
| 0–49 | Poor |

## CI Integration

Use the score as a quality gate in GitHub Actions:

```yaml
name: skilgen

on:
  pull_request:
  push:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install Skilgen
        run: pip install skilgen
      - name: Generate skills
        run: skilgen deliver --project-root . --auto-detect
      - name: Check score
        run: skilgen score --ci --min-score 60 --min-groundedness 15 --min-coverage 15
      - name: Check enterprise policy
        run: skilgen enterprise policy check --project-root .
```

Relevant flags:

- `--min-score` default `60`
- `--min-groundedness` default `15`
- `--min-coverage` default `15`

Exit codes:

- `0` CI pass
- `1` CI fail

Example fail message:

```text
CI FAIL: Skilgen Score 45/100 is below minimum 60/100. Run skilgen deliver to fix.
```

## Badge

Generate a README badge with:

```bash
skilgen score --badge
```

Badge colors:

- `85+` brightgreen
- `70–84` green
- `50–69` yellow
- `<50` red

Example README usage:

```markdown
![Skilgen Score](https://img.shields.io/badge/Skilgen%20Score-74-green)
```

## Score History

Local score history is stored in:

```text
.skilgen/state/score-history.jsonl
```

Each line is a JSON object:

```json
{"timestamp":"2026-04-23T12:00:00Z","total":74,"groundedness":18,"coverage":19,"freshness":21,"structure":16}
```

Use the CLI to inspect recent history:

```bash
skilgen score --history --project-root .
```

Skillayer uses the same dimensions for dashboard charts, repo history graphs,
PR comments, and trend comparisons over time.
