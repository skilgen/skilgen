# Dashboard Guide

This guide explains how the Skillayer dashboard is organized and how teams
typically use it once repository analyses are running continuously.

## `/dashboard` — Org Overview

The overview page is the first stop for most users.

It shows:

- stats cards for repos, average score, skills, and active agents
- a score trend sparkline
- a Knowledge Coverage section with org-wide category coverage
- a repository table with score badges and freshness context

This page answers:

- how healthy the org is overall
- which repo is falling behind
- whether coverage is broad or still too code-only

## `/dashboard/repos` — Repository List

This page is the inventory view for connected repositories.

Key interactions:

- search by name
- sort by score, name, or last analysed
- scan red / amber / green score badges
- open individual repo detail pages

Typical uses:

- triage which repos need another analysis run
- find repos with no meaningful coverage yet
- compare score movement across the portfolio

## `/dashboard/repos/[id]` — Repository Detail

This is the most operational page in the product.

It includes:

- repository metadata like full name, language, and default branch
- a total score ring plus the four subscores
- score history for recent runs
- dependency risk information
- a Knowledge Coverage section across eight categories
- a source filter above the skills list

Why it matters:

- the score explains current quality
- the coverage cards explain what knowledge is still missing
- the skills list shows the actual domains agents will use

## `/dashboard/repos/[id]/skills/[id]` — Skill Detail

The skill detail page shows the raw knowledge that is handed to agents.

Important elements:

- domain title and source type badge
- stale or fresh state
- four subscore values
- raw `SKILL.md` content
- version metadata and usage information

Teams use this page to answer:

- is this skill actually specific enough
- did a parser create useful content
- is this stale skill still heavily used

## `/dashboard/analytics` — Usage Analytics

This page shows whether the generated knowledge is being used.

Metrics include:

- total loads in the last 30 days
- most active repo
- most loaded skill
- top 10 skills chart
- never-loaded skills
- daily activity sparkline
- agent runtime breakdown

It is the best page for deciding which skills deserve the highest freshness SLA.

## `/dashboard/registry` — Skill Registry

The registry page is for browsing and reusing institutional knowledge.

It supports:

- search by name or description
- filtering by tag
- sorting by imports, score, or recency
- browsing published skills from the current org
- importing reusable knowledge into another repo

## `/dashboard/sources` — Coverage Map

The Sources page is the org-wide Pillar 4 control panel.

It shows:

- org coverage score as a percentage
- all eight knowledge categories
- how many repos cover each category
- which repos are missing each category
- the recommended CLI command to fill a missing area

This page is ideal for planning rollout of new parsers such as OpenAPI, dbt, or
runbook ingestion.

## `/dashboard/upgrade` — Pricing

The upgrade page explains plan tiers and starts the checkout flow for paid plans.

Expected plan structure:

- Free
- Team
- Business
- Enterprise

The Team and Business cards link into Stripe checkout.

## `/dashboard/settings` — Org Settings

Settings is where the org-level operating policy is defined.

Important areas:

- General: org name and score threshold
- Notifications: Slack webhook and alert toggles
- GitHub App: installation status and recent deliveries
- Billing: current plan and Stripe customer portal

## Typical Workflow Across Pages

1. Start on `/dashboard` for the high-level health view
2. Open `/dashboard/repos` to find a repo needing attention
3. Use the repo detail page to inspect coverage and dependencies
4. Open a skill detail page to review the actual generated knowledge
5. Use `/dashboard/sources` to decide which parser to enable next
6. Use `/dashboard/analytics` to prioritize skill upkeep

## What Data Powers The Dashboard

Most screens are server-rendered and fetch directly from the API layer using
the current WorkOS access token.

Primary backing endpoints:

- `/orgs/{id}/stats` for overview cards
- `/orgs/{id}/analytics` for usage trends
- `/orgs/{id}/coverage-summary` for the Knowledge Coverage sections
- `/repos/{id}` for repo details and scores
- `/repos/{id}/dependencies` for dependency risk
- `/repos/{id}/skill-sources` for source coverage and category status
- `/skills/{id}` for the full skill detail view
- `/registry` for browse and import experiences

This split keeps the UI simple: the dashboard mostly composes API responses
instead of recalculating score or coverage logic in the browser.

## Reading The Main Signals

### Score badges

The dashboard intentionally makes score state easy to scan:

- green means the repo is above the expected quality threshold
- amber means the repo is usable but needs attention
- red means either score or coverage is too weak for dependable autonomous work

Teams usually watch the change in score more closely than the absolute number on
day one, because sudden drops often signal freshness drift or broken generation.

### Knowledge Coverage

Coverage is a separate signal from score.

A repo can have:

- high score and low coverage, meaning the generated knowledge is strong but too
  narrow
- low score and broad coverage, meaning the right categories exist but the
  individual skills are weak or stale

That distinction is why coverage is shown in both the org view and repo view.

### Usage analytics

Usage answers whether the skill system is creating value after generation.

Watch for:

- heavily loaded skills with low freshness
- never-loaded skills that may need better naming or consolidation
- repos with strong scores but no real usage, which often means the knowledge is
  hard to discover or not aligned with actual workflows

## Recommended Team Rituals

Teams tend to get the most value from the dashboard when they treat it as an
operating loop instead of a static report.

Suggested routine:

1. Review `/dashboard` weekly for overall score and coverage drift.
2. Review `/dashboard/sources` after onboarding a new repo.
3. Check `/dashboard/analytics` every sprint to spot stale-but-active skills.
4. Use repo detail pages during incidents or upgrade work because they combine
   score, dependency risk, and operational knowledge in one place.
5. Revisit the registry monthly to publish skills that are clearly reusable
   across teams.

## Troubleshooting UI States

### Coverage data unavailable

If the repo or org coverage panel shows an unavailable state:

- confirm the API is reachable
- confirm the current session belongs to the expected org
- verify the repo has at least one completed analysis run
- check whether source taxonomy columns exist in the `skills` table

### Empty analytics charts

If analytics is blank:

- make sure agent runtimes are actually calling `POST /skills/{id}/usage`
- verify `last_loaded_at` and `load_count_30d` are being updated
- confirm the selected repo or org has recent activity

### Missing source badges on skills

Source badges appear when `source_type` is present. If they are missing for
non-code skills, verify the parser output is being persisted into the skill row
and that the response schema includes the taxonomy fields.
