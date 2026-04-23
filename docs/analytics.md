# Skill Usage Analytics

Skill usage analytics records when agent runtimes load skills.

## Events

Events capture `skill_id`, `org_id`, `repo_id`, `agent_runtime`, `session_id`, and timestamp. The `load_count_30d` counter is updated atomically.

## CLI

```bash
skilgen analytics show --project-root .
```

The CLI prints usage mode, live events, top skills, least-used skills, and detected agents.

## Dashboard

`/dashboard/analytics` shows total loads, unique skills loaded, top 10 skills, never-loaded skills, daily activity, most active repo, and most loaded skill.

## API

`GET /orgs/{id}/analytics` returns:

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

Agents record loads with `POST /skills/{id}/usage`.

## Rollup

`POST /admin/rollup-usage` resets stale counters and should be run on a scheduled admin job.

## Interpreting Data

Never-loaded skills often need clearer names or consolidation. Stale but active skills are the highest urgency refresh candidates. Agent runtime breakdown shows which tools your team actually uses.
