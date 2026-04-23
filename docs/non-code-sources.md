# Non-Code Sources

Non-code sources turn the knowledge around the codebase into skills agents can use: API behavior, infrastructure constraints, data lineage, security policy, operational runbooks, and incident lessons.

## API Specifications

Supported formats: OpenAPI 3.x, Swagger 2.0, GraphQL SDL/introspection JSON, and Postman Collection v2.1.

Enable with auto-detection or:

```bash
skilgen analyze --source openapi --project-root .
```

Generated skills include endpoints, auth schemes, rate limits, error responses, examples, deprecated endpoints, unauthenticated endpoints, and raw PII warnings. Category: Internal Tools.

## Infrastructure as Code

Supported formats: Terraform HCL, Kubernetes YAML, and Helm charts.

```bash
skilgen analyze --source terraform --project-root .
```

Generated skills include resource types, provider versions, variables, outputs, backends, Kubernetes images, probes, limits, RBAC objects, chart values, and deprecated API versions. Category: Codebase Architecture.

## Data Pipelines

Supported formats: dbt projects, SQL DDL, JSON schema exports, Kafka topic YAML, Avro schemas, and JSON schemas.

```bash
skilgen analyze --source dbt --project-root .
```

Generated skills include model lineage, `ref()` and `source()` calls, column tests, SQL tables, indexes, constraints, Kafka retention policies, and schema evolution signals. Category: Data Schema.

## Security and Compliance

Supported formats: SARIF 2.1, SPDX SBOM, CycloneDX SBOM, `SECURITY.md`, and structured security policy YAML/JSON.

```bash
skilgen analyze --source sarif --project-root .
```

Generated skills include tool names, severities, CWE categories, affected paths, license distribution, copyleft risks, blocked licenses, required headers, and vulnerability disclosure process. Category: Security Compliance.

## Operational Runbooks

Supported formats: Markdown runbooks, playbooks, Confluence HTML/XML exports, and Notion Markdown/API JSON.

```bash
skilgen analyze --source runbooks --project-root .
```

Section mapping: Steps and Procedure become patterns; Do NOT, Never, Avoid, and Warnings become anti-patterns; Verification and Health Checks become check paths; code blocks become evidence. Category: Operational Knowledge.

## Incident Post-Mortems

Supported formats: structured Markdown postmortems, PagerDuty export JSON, and GitHub issues when `GITHUB_TOKEN` is configured.

```bash
skilgen analyze --source incidents --project-root .
```

Root Cause, Contributing Factors, and Lessons Learned become known failure modes. Action Items become check paths. Timelines and impact summaries become evidence. Category: Operational Knowledge.

## Full Sources Block

```yaml
sources:
  openapi: true
  graphql: true
  postman: true
  terraform: true
  kubernetes: true
  helm: true
  dbt: true
  sql_schema: true
  kafka: true
  sarif: true
  sbom: true
  security_policy: true
  runbooks: runbooks/
  confluence: false
  notion: false
  incidents: true
```

## Coverage Map

The dashboard shows which of the eight skill categories are covered for each repo and which source parser can fill the gaps.
