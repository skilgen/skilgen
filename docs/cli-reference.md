# CLI Reference

## `skilgen deliver`

Generates docs and skills.

Flags: `--project-root` default `.`, `--requirements`, `--target`, `--domain`, `--dry-run`, `--skip-index`, `--auto-detect/--no-auto-detect`.

```bash
skilgen deliver --auto-detect --project-root .
```

Exit code `0` on success.

## `skilgen score`

Computes the Skilgen Score.

Flags: `--project-root`, `--history`, `--history-limit`, `--ci`, `--min-score`, `--min-groundedness`, `--min-coverage`, `--badge`, `--badge-file`.

```bash
skilgen score --ci --min-score 60
```

Exit code `1` when CI thresholds fail.

## `skilgen diff`

Shows changed source files and stale skills.

Flags: `--project-root`, `--requirements`, `--json`.

## `skilgen validate`

Validates generated outputs.

Flags: `--project-root`.

## `skilgen analyze`

Prints analysis payloads or runs focused source parsers.

Flags: `--project-root`, `--requirements`, `--deps`, `--source`, `--all`, `--auto-detect/--no-auto-detect`.

Source values: `openapi`, `graphql`, `postman`, `terraform`, `kubernetes`, `helm`, `dbt`, `sql_schema`, `kafka`, `sarif`, `sbom`, `security_policy`, `runbook`, `runbooks`, `confluence`, `notion`, `incident`, `incidents`, `pagerduty`, `all`.

```bash
skilgen analyze --source openapi --project-root .
```

## `skilgen init`

Writes `skilgen.yml` and optionally CI files.

Flags: `--project-root`, `--ci`, `--provider`.

## `skilgen analytics`

Shows or records local usage events.

Flags: `--project-root`, `--limit`, `--record-skill`, `--event`, `--agent`, `--context`, `--session-id`, `--task`, `--json`.

## `skilgen skills publish`

Publishes a generated skill to Skillayer.

Flags: positional `skill_file`, `--skill-id`, `--name`, `--description`, `--tag`, `--private`, `--api-url`.

## `skilgen skills import`

Imports an external or registry skill.

Flags: positional `slug`, `--target-dir`, `--api-url`, plus external skill options.

## Enterprise Commands

`skilgen enterprise policy init`, `validate`, and `check` manage `.skilgen/policy.yml`.

`skilgen enterprise report --json` emits compliance JSON.

## Other Commands

`index`, `preview`, `watch`, `architecture`, `dashboard`, `decide`, `status`, `report`, `purge`, `doctor`, and `serve` support deeper workflows and local API serving.
