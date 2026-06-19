# CLI Reference

This page covers the primary Skilgen commands used in local development, CI,
and Skillayer integrations. The syntax below reflects the current interface
expected by the repo and docs.

## skilgen deliver

Generate or refresh repository skills.

### Usage

```bash
skilgen deliver [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root to analyse |
| `--force` | bool | `false` | Overwrite generated content aggressively |
| `--dry-run` | bool | `false` | Preview writes without changing files |
| `--domains` | string | none | Restrict generation to named domains |
| `--output-dir` | path | `skills` | Output directory for skills |
| `--config` | path | auto | Explicit config file path |
| `--auto-detect` | bool | `true` | Include auto-detected non-code sources |

### Examples

```bash
skilgen deliver --project-root .
skilgen deliver --project-root . --auto-detect
skilgen deliver --project-root . --domains backend,frontend
```

### Output

Deliver prints scan status, detected domains, each written `SKILL.md`, and any
non-code source summary when source detection is enabled.

### Exit codes

- `0` generation succeeded
- `1` generation failed

## skilgen score

Compute the Skilgen Score.

### Usage

```bash
skilgen score [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root |
| `--history` | bool | `false` | Print recent score history |
| `--ci` | bool | `false` | Enable CI pass/fail behavior |
| `--min-score` | int | `60` | Minimum total score |
| `--min-groundedness` | int | `15` | Minimum groundedness |
| `--min-coverage` | int | `15` | Minimum coverage |
| `--badge` | bool | `false` | Print Markdown badge |
| `--json` | bool | `false` | Print JSON |

### Examples

```bash
skilgen score --project-root .
skilgen score --project-root . --json
skilgen score --ci --min-score 70
skilgen score --badge
```

### Output

Default output prints the total score, four subscores, grade, and quality gate
messages. JSON output includes totals and gate pass/fail state.

### Exit codes

- `0` score computed and all CI gates passed
- `1` CI gate failed

## skilgen diff

Show fresh, stale, and missing skills.

### Usage

```bash
skilgen diff [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root |
| `--base` | string | none | Optional base ref |
| `--head` | string | none | Optional head ref |
| `--json` | bool | `false` | Output machine-readable JSON |

### Examples

```bash
skilgen diff --project-root .
skilgen diff --project-root . --json
```

### Output

Text mode prints Fresh, Stale, and Missing sections. JSON mode returns arrays of
skills and changed source files.

### Exit codes

- `0` diff completed
- `1` diff failed

## skilgen validate

Validate generated skills for existence, structure, and references.

### Usage

```bash
skilgen validate [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root |
| `--strict` | bool | `false` | Treat warnings as failures |

### Examples

```bash
skilgen validate --project-root .
skilgen validate --project-root . --strict
```

### Output

Validation prints one line per skill, then a passed / warning / error summary.

### Exit codes

- `0` all checks passed
- `1` warnings only
- `2` errors found

## skilgen analyze

Run targeted analysis, including non-code source parsing.

### Usage

```bash
skilgen analyze [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root |
| `--requirements` | path | none | Optional requirements input |
| `--source` | list | none | Source parsers to run |
| `--auto-detect` / `--no-auto-detect` | bool | `true` | Enable or disable source detection |
| `--deps` | bool | `false` | Run dependency risk analysis |
| `--json` | bool | `false` | Print structured output |

### `--source` values

| Value | Meaning |
|---|---|
| `openapi` | OpenAPI 3.x and Swagger 2.0 |
| `graphql` | GraphQL schema and introspection JSON |
| `postman` | Postman Collection v2.1 |
| `terraform` | Terraform HCL |
| `kubernetes` | Kubernetes YAML manifests |
| `helm` | Helm charts |
| `dbt` | dbt projects |
| `sql_schema` | SQL DDL and JSON schema exports |
| `kafka` | Kafka topics and schemas |
| `sarif` | SARIF findings |
| `sbom` | SPDX and CycloneDX BOMs |
| `security_policy` | `SECURITY.md` and policy inputs |
| `runbooks` | Markdown runbooks |
| `confluence` | Confluence exports |
| `notion` | Notion exports or API content |
| `incidents` | Incidents, postmortems, PagerDuty exports |
| `all` | Run every detected source parser |

### Examples

```bash
skilgen analyze --project-root . --source openapi
skilgen analyze --project-root . --source terraform kubernetes
skilgen analyze --project-root . --source all
```

### Output

When source parsers run, Skilgen prints:

```text
Non-code sources analysed:
  openapi              → payments_api, auth_api
  runbook              → deploy_runbook

Generated 3 additional skill source(s) from non-code sources.
```

### Exit codes

- `0` analysis completed
- `1` command failed

## skilgen init

Write `.skilgen.yml` and optionally CI scaffolding.

### Usage

```bash
skilgen init [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root |
| `--ci` | bool | `false` | Write GitHub Actions workflow |
| `--force` | bool | `false` | Overwrite existing config |

### Examples

```bash
skilgen init --project-root .
skilgen init --project-root . --ci
```

### Exit codes

- `0` init succeeded
- `1` init failed

## skilgen analytics show

Print analytics in human-readable or JSON form.

### Usage

```bash
skilgen analytics show [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root |
| `--json` | bool | `false` | Raw JSON output |
| `--days` | int | `30` | Lookback window |

### Example

```bash
skilgen analytics show --project-root . --days 30
```

### Exit codes

- `0` analytics fetched
- `1` analytics failed

## skilgen skills publish

Publish a local skill to the Skillayer registry.

### Usage

```bash
skilgen skills publish [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--skill-id` | string | required | Skill ID to publish |
| `--name` | string | required | Registry display name |
| `--description` | string | required | Registry description |
| `--tag` | repeatable | none | Tags to attach |
| `--private` | bool | `false` | Publish privately |

### Example

```bash
skilgen skills publish --skill-id abc123 --name "Payments API" --description "Auth and rate limits" --tag api --tag payments
```

### Exit codes

- `0` publish succeeded
- `1` publish failed

## skilgen skills import

Import a skill from the registry into a local directory.

### Usage

```bash
skilgen skills import [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--registry-id` | string | required | Registry entry ID |
| `--target-dir` | path | required | Output directory |

### Example

```bash
skilgen skills import --registry-id reg_123 --target-dir ./skills
```

### Exit codes

- `0` import succeeded
- `1` import failed

## skilgen enterprise policy init

Create `.skilgen/policy.yml`.

### Usage

```bash
skilgen enterprise policy init [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root |
| `--force` | bool | `false` | Overwrite existing policy |

## skilgen enterprise policy check

Validate the repo against the active policy.

### Usage

```bash
skilgen enterprise policy check [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root |
| `--json` | bool | `false` | JSON report |

## skilgen enterprise policy validate

Validate the syntax of `.skilgen/policy.yml`.

### Usage

```bash
skilgen enterprise policy validate [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root |

## skilgen enterprise report

Generate a full compliance report.

### Usage

```bash
skilgen enterprise report [flags]
```

### Flags

| Flag | Type | Default | Description |
|---|---|---:|---|
| `--project-root` | path | `.` | Repository root |
| `--json` | bool | `false` | Emit JSON |
| `--output` | path | none | Write to file |

### Exit codes for enterprise commands

- `0` command succeeded
- `1` violations found or generation failed
