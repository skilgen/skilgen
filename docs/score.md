# Skilgen Score

The Skilgen Score is a 0-100 quality metric for how ready a repository is for AI coding agents. It combines four 25-point subscores: Groundedness, Coverage, Freshness, and Structure.

## Groundedness

Groundedness measures whether generated skills are backed by real evidence: source paths, AST signals, imports, dependency edges, API operations, schema fields, infrastructure resources, security findings, runbook steps, and incident timelines.

Strong evidence earns points for file references, concrete patterns, specific anti-patterns, and verifiable check paths. Generic prose loses points. A skill tree with no evidence is capped at 8/25 even if the markdown is well formatted.

## Coverage

Coverage measures how much of the repository is mapped to useful skill domains. Code domains come from static signals, domain graph planning, and generated `SKILL.md` materialization. Non-code sources improve coverage by adding API, data, infrastructure, security, and operational knowledge.

Coverage rewards materialized domains with assigned files or source artifacts. Inferred but unwritten domains do not count.

## Freshness

Freshness compares skill generation time with repository changes. Git history is used when available to estimate recency and change velocity. When git is unavailable, such as a zip download, freshness defaults to 15/25 rather than 0/25 so CI does not fail solely because history is missing.

Freshness decays as source files change without a matching `skilgen deliver` run.

## Structure

Structure validates `SKILL.md` format: frontmatter when generated, a valid H1, non-empty domain summary, useful sections, check paths, and references that point at existing files.

## Quality Gates

Caps prevent one strong dimension from hiding a serious weakness. For example, a skill tree with broad coverage but no grounded evidence cannot score as Excellent.

Default grades:

| Score | Grade |
|---:|---|
| 85-100 | Excellent |
| 70-84 | Good |
| 50-69 | Needs work |
| 0-49 | Poor |

## CI Integration

```yaml
name: Skilgen
on:
  pull_request:
jobs:
  skilgen:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -e .
      - run: skilgen deliver --auto-detect --project-root .
      - run: skilgen score --ci --min-score 60 --project-root .
      - run: skilgen enterprise policy check --project-root .
```

On failure:

```text
CI FAIL: Skilgen Score 45/100 is below minimum 60/100. Run skilgen deliver to fix.
```

## Badge Integration

```bash
skilgen score --badge
```

Example:

```markdown
![Skilgen Score](https://img.shields.io/badge/Skilgen%20Score-74%2F100-green)
```

## Score History

Score history is written to `.skilgen/state/score-history.jsonl` as one JSON object per run:

```json
{"timestamp":"2026-04-23T12:00:00Z","total":74,"groundedness":18,"coverage":19,"freshness":21,"structure":16}
```

Dashboard charts use the same dimensions and store server-side trends in Skillayer.
