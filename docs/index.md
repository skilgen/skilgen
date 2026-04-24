# Skillayer — Enterprise Knowledge OS

Skillayer is the knowledge operating system for software teams using coding
agents. The open-source piece is **Skilgen**, a CLI that analyses a repository,
detects domains, builds `SKILL.md` files, scores quality, and tracks freshness.
The hosted piece is **Skillayer**, which adds the GitHub App, PR comments,
dashboard, registry, billing, analytics, and enterprise controls. The best
analogy is Terraform plus HCP: the local tool is useful on its own, while the
platform makes the workflow repeatable for teams.

## What Skilgen Does

Skilgen turns implementation detail into agent-readable knowledge:

- scans source files and evidence graphs
- groups code into reusable engineering domains
- generates `SKILL.md` content from code and non-code sources
- scores the result on groundedness, coverage, freshness, and structure
- validates references and surfaces stale or missing skills

Pillar 4 extends that model beyond code, so agents can also learn from:

- API contracts: OpenAPI, GraphQL, Postman
- Infrastructure: Terraform, Kubernetes, Helm
- Data systems: dbt, SQL schema, Kafka
- Security inputs: SARIF, SBOM, security policy
- Operations: runbooks, Confluence, Notion, incidents

## What Skillayer Adds

Skillayer takes the same skill graph and adds the hosted operating layer:

- a GitHub App that runs analyses on pushes and pull requests
- PR comments with score deltas and knowledge coverage context
- a dashboard for repos, skills, analytics, settings, and billing
- a skill registry for publishing and importing institutional knowledge
- org-level policy thresholds, stale alerts, audit data, and score gates

## Quick Start

1. Install the CLI:

   ```bash
   pip install skilgen
   ```

2. Initialize your repository:

   ```bash
   skilgen init --project-root .
   ```

3. Generate skills:

   ```bash
   skilgen deliver --project-root .
   ```

4. Gate quality in CI:

   ```bash
   skilgen score --ci --min-score 60
   ```

5. Install the GitHub App:

   Open [skillayer.dev/install](https://skillayer.dev/install) and connect the
   repositories you want Skillayer to watch.

## Feature Matrix

| Capability | Skilgen CLI (free / OSS) | Skillayer Platform (paid) |
|---|---|---|
| Generate `SKILL.md` from code | Yes | Yes |
| Generate skills from non-code sources | Yes | Yes |
| Local score computation and CI gates | Yes | Yes |
| Freshness diff and validation | Yes | Yes |
| GitHub PR comment engine | No | Yes |
| GitHub Check Run integration | No | Yes |
| Repo and org coverage views | Local only | Dashboard + API |
| Usage analytics and top skills | Local summary | Org rollups |
| Registry publish/import | CLI + API | Dashboard + API |
| Billing, seat management, settings | No | Yes |

## Why Skillayer

- **Grounded analysis:** skills are generated from code, schemas, specs,
  manifests, and docs instead of generic prose.
- **Measurable quality:** the Skilgen Score makes knowledge quality visible,
  comparable, and enforceable in CI.
- **Freshness as an engineering signal:** stale-but-active skills can be caught
  before they mislead agents in the middle of real work.

## Typical Local Workflow

```bash
skilgen init --project-root .
skilgen deliver --project-root . --auto-detect
skilgen validate --project-root .
skilgen diff --project-root .
skilgen score --project-root .
```

If your repository includes non-code sources, you can widen coverage with:

```bash
skilgen analyze --source openapi --project-root .
skilgen analyze --source terraform --project-root .
skilgen analyze --source runbooks --project-root .
```

Or run all detected sources at once:

```bash
skilgen analyze --source all --project-root .
```

## Documentation Map

### Getting Started

- [Quickstart](quickstart.md)
- [CLI Reference](cli-reference.md)

### Core Features

- [Skilgen Score](score.md)
- [Non-Code Sources](non-code-sources.md)
- [Coverage Map](coverage-map.md)
- [Diff & Auto-Refresh](diff-and-autoupdate.md)
- [Architecture Mode](architecture-mode.md)
- [Evidence Graph](evidence-graph.md)

### Skillayer Platform

- [Dashboard Guide](dashboard.md)
- [GitHub App](github-app.md)
- [Skill Registry](skill-registry.md)
- [Analytics](analytics.md)
- [API Reference](api-reference.md)

### Enterprise

- [Enterprise Governance](enterprise-governance.md)

## Suggested Rollout Path

Start by generating skills locally in one repository and using the score in CI.
Once the local output is genuinely helpful, install the GitHub App so pull
requests begin receiving score feedback automatically. Then add non-code source
parsers to improve coverage, and turn on enterprise policy checks when the
skill system becomes part of your engineering standard.
