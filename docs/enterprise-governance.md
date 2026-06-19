# Enterprise Governance

Enterprise governance turns repository knowledge into an enforceable standard.
That includes policy files, CI gates, Slack alerts, GitHub checks, and
machine-readable compliance output.

## Policy Engine

Create the default policy:

```bash
skilgen enterprise policy init --project-root .
```

Default policy file:

```yaml
min_score: 60
required_domains: []
max_stale_days: 30
blocked_licenses:
  - AGPL-3.0
  - GPL-3.0
```

Rules:

- `min_score` must be `0-100`
- `required_domains` must be a list of strings
- `max_stale_days` must be positive
- `blocked_licenses` must be a list of license identifiers

Validate the file:

```bash
skilgen enterprise policy validate --project-root .
```

Run the policy:

```bash
skilgen enterprise policy check --project-root .
```

Example output:

```text
✓ Score threshold met (74 >= 60)
✓ Required domains present
✓ Skill freshness within 30 days
✗ Blocked licenses found: GPL-3.0
```

Exit codes:

- `0` all checks passed
- `1` at least one violation occurred

## CI Integration

Most teams run policy and score together:

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
      - run: pip install skilgen
      - run: skilgen deliver --project-root . --auto-detect
      - run: skilgen score --ci --min-score 60
      - run: skilgen enterprise policy check --project-root .
```

## Compliance Report

Generate JSON with:

```bash
skilgen enterprise report --json --project-root .
```

Example response:

```json
{
  "timestamp": "2026-04-23T12:00:00Z",
  "score": {"total": 74},
  "policy_violations": [],
  "stale_skills": [],
  "missing_domains": [],
  "dependency_risks": [],
  "overall_status": "pass"
}
```

This output is designed for Slack, SIEM pipelines, or archival compliance jobs.

## Score Threshold Enforcement

Skillayer stores `org.score_threshold`, default `60`.

That threshold drives:

- PR comment expectations
- GitHub Check Run pass / fail state
- branch protection policy when the check is required

## Slack Notifications

Configure Slack in Dashboard → Settings → Notifications.

Common triggers:

- PR score drops below threshold
- stale-but-active skill detected

The stale-but-active rule is:

- freshness below `20`
- load count above `5` in the last 30 days

## Audit Trail

Skillayer records:

- analysis runs
- score changes
- webhook deliveries
- registry imports and publishes
- settings changes

These records help explain why a repo score changed or why a check failed.

## BYOK LLM

The governance layer is designed to support future bring-your-own-model options
such as Anthropic, Azure OpenAI, OpenAI-compatible gateways, and local runtimes
like Ollama without changing the policy model.

## Policy Field Reference

### `min_score`

- Type: integer
- Default: `60`
- Allowed range: `0` through `100`
- Meaning: minimum total Skilgen Score allowed for pass status

### `required_domains`

- Type: array of strings
- Default: `[]`
- Meaning: skill domains that must exist after generation
- Typical use: enforce that every service exposes at least `auth`, `api`, or
  `testing` coverage before merge

### `max_stale_days`

- Type: integer
- Default: `30`
- Minimum: `1`
- Meaning: maximum allowed age between skill refresh and relevant code changes

### `blocked_licenses`

- Type: array of SPDX identifiers
- Default: `["AGPL-3.0", "GPL-3.0"]`
- Meaning: dependency licenses that fail enterprise policy checks

## Example Violation Output

```text
$ skilgen enterprise policy check --project-root .

✓ Score threshold met (67 >= 60)
✗ Required domains missing: operational_knowledge
✓ Skill freshness within 30 days
✗ Blocked licenses found: GPL-3.0

Policy check failed with 2 violation(s).
```

This exits with code `1`, which makes it appropriate for GitHub Actions, other
CI systems, or deployment gating.

## Full Compliance Report Example

```json
{
  "timestamp": "2026-04-23T12:00:00Z",
  "repo": "payments-service",
  "score": {
    "total": 74,
    "groundedness": 19,
    "coverage": 21,
    "freshness": 18,
    "structure": 16
  },
  "policy_violations": [
    {
      "code": "STALE_SKILL",
      "message": "payments_api is older than max_stale_days"
    }
  ],
  "stale_skills": ["payments_api"],
  "missing_domains": [],
  "dependency_risks": [
    {
      "package": "legacy-lib",
      "license": "GPL-3.0",
      "severity": "high"
    }
  ],
  "overall_status": "fail"
}
```

This schema is straightforward to ship into SIEM pipelines, a Slack formatter,
or a compliance archive job that snapshots policy state per release.

## Governance In Branch Protection

The usual enterprise setup is:

1. require the Skilgen Check Run in GitHub branch protection
2. set org-level threshold in the dashboard
3. keep repo-level exceptions in `.skilgen.yml`
4. enforce blocked licenses and stale windows through enterprise policy

That gives teams a clean split between org-wide defaults and repo-specific
needs without hand-maintaining dozens of ad hoc GitHub checks.

## Slack Notification Payloads

Teams usually enable Slack for three categories of alert:

- score dropped below threshold on a PR
- stale-but-active skill detected
- enterprise policy failure on default branch analysis

A good Slack message contains:

- repo name
- branch or PR number
- total score
- failing rule or stale skill name
- direct dashboard link

This keeps notifications actionable instead of noisy.

## Recommended Rollout Pattern

For a new org, start simple:

1. enable score checks first
2. add blocked licenses next
3. add stale windows after the team trusts regeneration cadence
4. add required domains once non-code source coverage is in place

This staged rollout keeps governance useful without producing false urgency in
the first week of adoption.
