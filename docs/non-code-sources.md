# Non-Code Sources

Non-code sources are what make Skilgen useful outside pure code-generation
tasks. Most real repositories have critical knowledge in contracts, schemas,
runbooks, dashboards, and incident docs. Pillar 4 brings that material into the
same skill system as the codebase so agents can operate with real context.

## Overview

Why this matters:

- API teams need agent context from specs, not just route files
- platform teams need infra constraints from Terraform and manifests
- data teams need lineage and schema context from dbt and DDL
- security teams need findings and policy inputs included in the skill tree
- operations teams need runbooks and postmortems captured for agents

The source groups map to skill categories like this:

- API specs → `internal_tools`
- Infrastructure → `codebase_architecture`
- Data systems → `data_schema`
- Security inputs → `security_compliance`
- Runbooks and docs → `operational_knowledge`
- Incidents → `operational_knowledge`

## API Specifications

**Supported formats**

- OpenAPI 3.x: `openapi.yaml`, `openapi.json`
- Swagger 2.0: `swagger.yaml`, `swagger.json`
- GraphQL schema: `.graphql`, `.gql`, introspection JSON
- Postman Collection v2.1: `.postman_collection.json`

**Auto-detected files**

- `openapi.yaml`
- `openapi.json`
- `swagger.yaml`
- `swagger.json`
- `api/openapi.yaml`
- `docs/openapi.yaml`
- `schema.graphql`
- `src/**/*.graphql`
- `*.postman_collection.json`

**Enable manually**

```bash
skilgen analyze --source openapi --project-root .
skilgen analyze --source graphql --project-root .
skilgen analyze --source postman --project-root .
```

**In `.skilgen.yml`**

```yaml
sources:
  openapi: true
  graphql: true
  postman: true
```

**What gets generated**

- endpoint lists grouped by domain
- auth schemes and security requirements
- rate-limit headers and common error responses
- deprecated and unauthenticated endpoint warnings
- evidence such as operation IDs, schema names, and examples

**Example skill snippet**

```markdown
## Detected patterns
- Auth: bearerAuth (http)
- Endpoint: POST /payments/authorize — Authorize a card payment
- Endpoint: POST /payments/refund — Refund a captured payment
```

**Skill category:** Internal Tools & APIs

## Infrastructure as Code

**Supported formats**

- Terraform HCL
- Kubernetes YAML manifests
- Helm charts

**Auto-detected paths**

- `**/*.tf`
- `k8s/`
- `kubernetes/`
- `manifests/`
- `deploy/`
- `Chart.yaml`

**Enable manually**

```bash
skilgen analyze --source terraform --project-root .
skilgen analyze --source kubernetes --project-root .
skilgen analyze --source helm --project-root .
```

**What gets generated**

- providers, versions, variables, outputs, and backends from Terraform
- deployments, services, probes, limits, ingress, secrets, and RBAC from k8s
- chart metadata, values, kinds, helpers, and deprecated APIs from Helm

**Example skill snippet**

```markdown
## Detected patterns
- Provider: aws = ~> 5.0
- Resource: aws_instance (2 instances)
- Backend: s3
```

**Skill category:** Codebase Architecture

## Data Pipelines

**Supported formats**

- dbt projects
- SQL DDL files
- JSON schema exports
- Kafka topic YAML
- Avro schemas
- Kafka JSON Schema definitions

**Enable manually**

```bash
skilgen analyze --source dbt --project-root .
skilgen analyze --source sql_schema --project-root .
skilgen analyze --source kafka --project-root .
```

**What gets generated**

- dbt model lineage and test coverage
- SQL tables, indexes, primary keys, and foreign keys
- Kafka retention policies, partitions, cleanup policies, and schema fields

**Example skill snippet**

```markdown
## Detected patterns
- Model: fct_orders — Fact table for orders
- Source: app.orders
- Test coverage: 67% of models have tests
```

**Skill category:** Data & Schema

## Security & Compliance

**Supported formats**

- SARIF 2.1 from tools like Semgrep, CodeQL, Trivy, and Checkov
- SPDX SBOM
- CycloneDX SBOM
- `SECURITY.md`
- structured YAML or JSON security policy files

**Enable manually**

```bash
skilgen analyze --source sarif --project-root .
skilgen analyze --source sbom --project-root .
skilgen analyze --source security_policy --project-root .
```

**What gets generated**

- finding categories and severities
- license distributions and copyleft risks
- vulnerability reporting and disclosure processes
- approved and blocked policy settings

**Skill category:** Security & Compliance

## Operational Runbooks

**Supported formats**

- Markdown in `runbooks/`, `playbooks/`, `operations/`, or similar folders
- Confluence HTML/XML exports
- Notion Markdown exports
- Notion API content when `NOTION_API_KEY` is set

**Enable manually**

```bash
skilgen analyze --source runbooks --project-root .
skilgen analyze --source confluence --project-root .
skilgen analyze --source notion --project-root .
```

**Markdown mapping rules**

- `Steps`, `Procedure`, `Checklist` → patterns
- `Do NOT`, `Avoid`, `Warnings` → anti-patterns
- `Verification`, `Health check`, `Confirm` → check paths
- fenced code blocks → evidence

**Skill category:** Operational Knowledge

## Incident Post-Mortems

**Supported formats**

- Markdown postmortems and PIRs
- PagerDuty export JSON
- GitHub issues labeled `incident` or `post-mortem`

**Enable manually**

```bash
skilgen analyze --source incidents --project-root .
```

**What gets generated**

- root causes and contributing factors as known failure modes
- lessons learned as anti-patterns
- action items as check paths
- timelines and impact summaries as evidence

**Skill category:** Operational Knowledge

## Run Everything at Once

```bash
skilgen analyze --source all --project-root .
```

Example output:

```text
Non-code sources analysed:
  openapi              → payments_api, auth_api
  terraform            → aws_infrastructure
  runbook              → deploy_runbook

Generated 4 additional skill source(s) from non-code sources.
```

## Full `sources:` Block Example

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

Once these sources are enabled, Skillayer can show category coverage in the
dashboard and per-repo API responses. See [Coverage Map](coverage-map.md) for
the eight-category model and how to improve missing areas.
