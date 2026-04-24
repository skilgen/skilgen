# Skill Usage Analytics

Skill usage analytics tells you whether generated knowledge is being used by
agents in practice. That makes it the bridge between “we generated a skill”
and “this skill is actually shaping real work.”

## What Skill Load Events Are

A load event is recorded when an agent runtime fetches or uses a skill.

Tracked data includes:

- `skill_id`
- `org_id`
- `repo_id`
- `agent_runtime`
- `session_id`
- timestamp

The system also maintains:

- `load_count_30d`
- `last_loaded_at`

## CLI Analytics

Show local analytics with:

```bash
skilgen analytics show --project-root .
```

The CLI can print:

- total loads
- most used skills
- least used skills
- runtime breakdown

Use `--json` for machine-readable output.

## Dashboard Analytics

Dashboard path:

```text
/dashboard/analytics
```

The page includes:

- total loads in the last 30 days
- most active repo
- most loaded skill
- top 10 skills chart
- never-loaded skills
- 30-day sparkline
- agent runtime breakdown

## API Analytics

Org analytics:

```text
GET /orgs/{id}/analytics
```

Example response:

```json
{
  "total_loads_30d": 42,
  "unique_skills_loaded": 8,
  "total_skills": 20,
  "top_skills": [],
  "never_loaded": [],
  "agent_breakdown": {"codex": 12},
  "daily_loads": []
}
```

Skill usage ingestion:

```text
POST /skills/{id}/usage
```

Request body:

```json
{"agent_runtime":"codex","session_id":"sess_123"}
```

## Admin Rollup

Admin route:

```text
POST /admin/rollup-usage
```

Purpose:

- reset `load_count_30d` for skills not used in 30+ days

Recommended schedule:

- monthly cron
- or explicit admin maintenance run

## Interpreting the Data

- **Never loaded** skills often need better naming or consolidation
- **Stale but active** skills are the highest urgency refresh targets
- **Runtime breakdown** shows which agent platforms matter most to your team

Useful heuristic:

- `load_count_30d = 0` for 90+ days is a strong cleanup signal

## Example CLI Output

```text
$ skilgen analytics show --project-root .

Total loads (30d): 42
Most active repo: payments-service
Most loaded skill: payments_api
Never loaded skills: ui_copy, legacy_batch_jobs
Runtime breakdown:
  codex   22
  cursor  11
  claude   9
```

This output is meant for quick human review. Use `--json` when you want to
forward the data into another system.

## How Teams Use Analytics

Analytics is most useful when paired with score and freshness:

- high load + low freshness means regenerate soon
- low load + high maintenance cost means consolidate or delete
- strong runtime concentration on one agent platform can guide integration work

If one repo has strong usage but weak coverage, that is a strong signal to add
non-code sources before increasing agent autonomy.
