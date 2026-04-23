# Quickstart

## 1. Install

```bash
pip install skilgen
```

## 2. Generate Skills

```bash
skilgen deliver --project-root .
```

Example output:

```json
{
  "runtime": "local",
  "generated_files": ["skills/backend/api/SKILL.md"],
  "non_code_sources": {
    "analysed": {"openapi": ["payments_api"]},
    "generated_files": ["skills/payments_api/SKILL.md"],
    "failures": {}
  }
}
```

## 3. View Score

```bash
skilgen score --project-root .
```

```json
{"total": 74, "groundedness": 18, "coverage": 19, "freshness": 21, "structure": 16}
```

## 4. Add Badge

```bash
skilgen score --badge
```

## 5. Enforce CI

```bash
skilgen score --ci --min-score 60
```

## 6. Install GitHub App

Install from `https://skillayer.dev/install`, select the organization, and grant repository access. Skillayer listens for push and pull request webhooks.

## 7. First Dashboard View

Open the Skillayer dashboard. The overview shows repo count, average score, generated skill count, score trend, repository table, and knowledge coverage.

## 8. First PR Comment

On a pull request, Skillayer posts a comment with the branch score, subscore deltas versus base, analyzed domains, and a link to the dashboard report.

## 9. Enterprise Policy

```bash
skilgen enterprise policy init --project-root .
skilgen enterprise policy check --project-root .
```

## Example `.skilgen.yml`

```yaml
include_paths:
  - .
exclude_paths:
  - .git
  - node_modules
sources:
  openapi: true
  terraform: true
  dbt: true
  runbooks: runbooks/
  sarif: true
```
