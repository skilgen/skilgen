# Coverage Map

The Coverage Map shows whether a repository has usable skills across eight
knowledge categories. It is designed to answer a simple operational question:
what kinds of context will an agent have if it starts working in this repo
right now?

## The 8 Skill Categories

| Category | Icon | What agents get | How generated |
|---|---|---|---|
| Codebase Architecture | 🏗️ | service layout, domain ownership, important files, architectural boundaries | code analysis, Terraform, Kubernetes, Helm |
| Code Style | 🎨 | naming conventions, formatting expectations, UI or code idioms | code analysis |
| Testing Conventions | 🧪 | test locations, commands, fixtures, failure-path expectations | code analysis |
| Internal Tools | 🔧 | API contracts, auth flows, rate limits, collections, internal integration rules | OpenAPI, GraphQL, Postman |
| Security Compliance | 🔒 | findings, license posture, disclosure process, policy constraints | SARIF, SBOM, security policy |
| Design System | 🎯 | UI patterns, shared components, visual rules, frontend constraints | code analysis |
| Data Schema | 🗄️ | model lineage, table shape, indexes, topic schemas, retention rules | dbt, SQL schema, Kafka |
| Operational Knowledge | 📋 | runbooks, validation steps, incident lessons, recovery actions | runbooks, Confluence, Notion, incidents |

## Coverage Score

Coverage Score uses a simple formula:

```text
(covered categories / 8) × 100
```

A category counts as **covered** if the repository has at least one generated
skill in that category.

Examples:

- `2/8` categories covered → `25%`
- `4/8` categories covered → `50%`
- `8/8` categories covered → `100%`

## Why Uncovered Categories Matter

Missing categories create predictable agent failure modes:

- **Missing Codebase Architecture:** the agent does not know where to start and
  may change the wrong module first.
- **Missing Code Style:** the agent writes code that technically works but feels
  foreign to the repo.
- **Missing Testing Conventions:** the agent can implement changes without
  knowing how this repo verifies happy and failure paths.
- **Missing Internal Tools:** the agent will guess API behavior instead of using
  the real contract.
- **Missing Security Compliance:** the agent may ignore license risk, flagged
  patterns, or disclosure rules.
- **Missing Design System:** UI work drifts from established component and style
  expectations.
- **Missing Data Schema:** the agent invents table shape, lineage, or topic
  semantics and makes poor migration assumptions.
- **Missing Operational Knowledge:** the agent hallucinates runbook steps,
  verification flows, and incident handling procedures.

## How to Improve Coverage

| Category | CLI command | Best first source |
|---|---|---|
| Codebase Architecture | `skilgen deliver --project-root .` | code graph |
| Code Style | `skilgen deliver --project-root .` | existing code patterns |
| Testing Conventions | `skilgen deliver --project-root .` | repo tests |
| Internal Tools | `skilgen analyze --source openapi` | API specs |
| Security Compliance | `skilgen analyze --source sarif` | SARIF or SBOM |
| Design System | `skilgen deliver --project-root .` | frontend code |
| Data Schema | `skilgen analyze --source dbt` | dbt or SQL schema |
| Operational Knowledge | `skilgen analyze --source runbooks` | runbooks or incidents |

## Viewing Coverage

You can inspect coverage in three places:

- dashboard org view: `/dashboard/sources`
- dashboard repo detail: repository Coverage section
- API: `GET /repos/{id}/skill-sources`

Repo detail shows the per-repo category cards. The org-wide Sources page shows
how many repos cover each category and which repos are still missing them.

## Practical Use

Teams typically use coverage for two decisions:

1. deciding which new parser to turn on next
2. deciding which repos are ready for more autonomous agent workflows

If you see high score but low coverage, the repo may have strong skills in only
one slice of the system. If you see broad coverage but low groundedness, the
repo has the right categories but the generated content still needs stronger
evidence.

## Example Improvement Plan

Here is a practical progression for a repo starting from code-only knowledge:

1. run `skilgen deliver --project-root .`
2. add API context with `skilgen analyze --source openapi`
3. add schema knowledge with `skilgen analyze --source dbt`
4. add runbook context with `skilgen analyze --source runbooks`
5. add security posture with `skilgen analyze --source sarif`

That sequence usually moves a service from narrow code understanding to a
well-rounded operational profile with much better agent reliability.

## Org-Level Use

At the org level, coverage answers a portfolio question: where are we still
asking agents to improvise?

The `/dashboard/sources` page helps platform teams:

- find the most-missing category across repos
- identify rollout candidates for a new parser
- justify operational work such as adding runbooks or dbt metadata
- track how coverage improves after enabling auto-detection
