# Enterprise Governance

Enterprise governance turns skill generation into an enforceable operating model: policies, CI gates, score thresholds, Slack alerts, and audit trails.

## Policy Engine

Create a policy:

```bash
skilgen enterprise policy init --project-root .
```

Default `.skilgen/policy.yml`:

```yaml
min_score: 60
required_domains: []
max_stale_days: 30
blocked_licenses:
  - AGPL-3.0
  - GPL-3.0
```

Check it:

```bash
skilgen enterprise policy check --project-root .
```

Example output:

```text
PASS score threshold
PASS required domains
PASS freshness
FAIL blocked licenses: GPL-3.0 detected in dependency evidence
```

Exit code is `0` when all checks pass and `1` on any violation.

## Compliance Report

```bash
skilgen enterprise report --json --project-root .
```

Response:

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

The JSON can be sent to SIEM, Slack, or internal policy systems.

## Score Threshold Enforcement

Skillayer stores `org.score_threshold`, default `60`. PR check runs use this threshold. If the branch score is below the threshold, the GitHub Check Run fails and can be required by branch protection.

## Slack Notifications

Configure the Slack webhook in Dashboard Settings. Skillayer sends stale-skill alerts when a skill has freshness below 20 and more than 5 loads in the last 30 days. Slack failures are logged but never crash analysis.

## Audit Trail

Skillayer records recent analysis runs, GitHub webhook deliveries, registry imports, registry publishes, and settings changes. The dashboard exposes these in Settings under the GitHub App and general organization views.

## BYOK LLM Roadmap

Enterprise BYOK will support Anthropic, Azure OpenAI, OpenAI-compatible gateways, and local Ollama endpoints through configuration rather than source code changes.
