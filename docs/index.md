# Skilgen and Skillayer

Skilgen is the open-source CLI that turns code, API specs, infrastructure, data definitions, security evidence, runbooks, and incidents into agent-readable `SKILL.md` files. Skillayer is the SaaS platform around it: dashboards, GitHub App automation, PR comments, score history, registry, analytics, billing, and enterprise governance.

## Quick Start

```bash
pip install skilgen
cd your-repo
skilgen deliver --project-root .
skilgen score --project-root .
skilgen score --badge
```

Then install the GitHub App from `https://skillayer.dev/install` so Skillayer can analyze pushes, post PR score deltas, and keep dashboard data fresh.

## Feature Matrix

| Capability | Skilgen CLI | Skillayer Platform |
|---|---:|---:|
| Generate `SKILL.md` from code | Yes | Yes, automated |
| Generate skills from non-code sources | Yes | Yes, persisted by source type |
| Skilgen Score and CI gate | Yes | Yes, dashboard and checks |
| Diff, validate, and freshness | Yes | Yes |
| GitHub PR comment engine | No | Yes |
| Coverage map across 8 skill categories | Local output | Dashboard and API |
| Usage analytics | Local summary | Org analytics and rollups |
| Registry publish/import | CLI | Dashboard and API |
| Billing, teams, settings | No | Yes |

## Documentation

- [Quickstart](quickstart.md)
- [CLI Reference](cli-reference.md)
- [Skilgen Score](score.md)
- [Non-Code Sources](non-code-sources.md)
- [Coverage Map](coverage-map.md)
- [Dashboard Guide](dashboard.md)
- [GitHub App](github-app.md)
- [API Reference](api-reference.md)
- [Enterprise Governance](enterprise-governance.md)

## Why Skillayer

Most coding agents fail because they lack the local operating context that experienced engineers carry around: which domains exist, which files matter, how APIs behave, where data is defined, what incidents taught the team, and what security constraints are non-negotiable. Skilgen captures that context as portable skills. Skillayer keeps it fresh, scored, visible, and governed across teams.
