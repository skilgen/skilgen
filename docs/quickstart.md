# Quickstart

This walkthrough gets you from install to a repository that is generating,
scoring, and validating skills. It starts with the local CLI loop and ends with
the hosted Skillayer features that teams usually turn on next.

## 1. Install Skilgen

What it does: installs the CLI and the analysis runtime.

```bash
pip install skilgen
```

Example output:

```text
Collecting skilgen
  Downloading skilgen-0.8.0-py3-none-any.whl
Installing collected packages: skilgen
Successfully installed skilgen-0.8.0
```

Verify the install:

```bash
skilgen --help
```

## 2. Initialize the repository

What it does: writes `.skilgen.yml` and detects known source types.

```bash
skilgen init --project-root .
```

Example output:

```text
Initialized Skilgen config at .skilgen.yml
Detected sources:
  openapi: true
  runbooks: true
Generated .github/workflows/skilgen.yml
```

Example `.skilgen.yml`:

```yaml
version: 1
project_root: .
output_dir: skills
requirements_path: docs/Skilgen_PRD_v2.docx
include_paths: []
exclude_paths:
  - .git
  - .skilgen
  - node_modules
  - build
  - dist
sources:
  openapi: true
  graphql: false
  postman: false
  terraform: false
  kubernetes: false
  helm: false
  dbt: false
  sql_schema: false
  kafka: false
  sarif: false
  sbom: false
  security_policy: false
  runbooks: true
  confluence: false
  notion: false
  incidents: false
quality_gates:
  min_score: 60
  min_groundedness: 15
  min_coverage: 15
```

## 3. Generate skills

What it does: analyses the repository and writes `SKILL.md` files.

```bash
skilgen deliver --project-root .
```

Example output:

```text
Scanning repository...
Detected 12 domains
Writing skills/backend/api/SKILL.md
Writing skills/backend/testing/SKILL.md
Writing skills/frontend/SKILL.md
Writing skills/roadmap/SKILL.md

Analysed 12 domains, generated 12 SKILL.md files.
```

If you want Skilgen to include non-code inputs automatically:

```bash
skilgen deliver --project-root . --auto-detect
```

## 4. View the score

What it does: computes the overall knowledge quality score.

```bash
skilgen score --project-root .
```

Example output:

```text
Skilgen Score: 74/100

Groundedness   ████████████████░░░░  18/25
Coverage       ███████████████░░░░░  19/25
Freshness      █████████████████░░░  21/25
Structure      ████████████████░░░░  16/25

Grade: Good
```

## 5. Use the score as a CI gate

What it does: exits non-zero if the repo falls below your threshold.

```bash
skilgen score --ci --min-score 60
```

Example passing output:

```text
CI PASS: Skilgen Score 74/100 ✓
```

Example failing output:

```text
CI FAIL: Skilgen Score 45/100 is below minimum 60/100. Run skilgen deliver to fix.
```

## 6. Create a badge

What it does: prints Markdown for a README badge.

```bash
skilgen score --badge
```

Example output:

```text
![Skilgen Score](https://img.shields.io/badge/Skilgen%20Score-74-green)
```

## 7. Install the GitHub App

What it does: connects your repositories to the Skillayer automation layer.

Installation flow:

1. Open [skillayer.dev/install](https://skillayer.dev/install)
2. Choose the GitHub organization
3. Select the repos you want to monitor
4. Approve webhook, checks, and comment permissions
5. Return to the dashboard and wait for the first completed analysis

## 8. View the dashboard for the first time

What you see after the first completed analysis:

- an overview page with repo count, score, skills, and active agents
- a Knowledge Coverage section showing missing categories
- a repositories table with score badges and last analysed timestamps
- repo detail pages with skills, dependencies, and source coverage

## 9. Add non-code sources

What it does: widens the skill system beyond code.

```bash
skilgen analyze --source openapi --project-root .
```

Example output:

```text
Non-code sources analysed:
  openapi              → payments_api, auth_api

Generated 2 additional skill source(s) from non-code sources.
```

You can also run every detected source parser:

```bash
skilgen analyze --source all --project-root .
```

## 10. Start enterprise policy checks

```bash
skilgen enterprise policy init --project-root .
skilgen enterprise policy check --project-root .
```

This writes `.skilgen/policy.yml` and validates the repo against thresholds,
required domains, stale skill windows, and blocked licenses.

## Example CI Workflow

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
        run: skilgen score --ci --min-score 60
      - name: Check enterprise policy
        run: skilgen enterprise policy check --project-root .
```

## Where to Go Next

- Read [CLI Reference](cli-reference.md) for command-by-command detail
- Read [Non-Code Sources](non-code-sources.md) to widen coverage
- Read [Dashboard Guide](dashboard.md) after installing the GitHub App
- Read [Enterprise Governance](enterprise-governance.md) when you need policy
  gates, alerts, and compliance reporting
