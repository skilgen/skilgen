# Onboarding Timing

Measured on April 27, 2026 against `https://api.skillayer.com` using the bootstrap org and an already-connected repo. This measures the product path from dashboard access to the first `/skills/load` event being visible to Skillayer.

## Target

New user reaches a visible skill load in under 5 minutes with no external help.

## Before Fix

| Step | Expected Time | Issue |
| --- | ---: | --- |
| Open dashboard after sign-up | 20s | Works when WorkOS/bootstrap resolves an org. |
| Connect GitHub repo | 60-120s | Clear CTA exists. |
| Generate first skills | 60-120s | Setup status still told users to run `skilgen deliver --project-root .`, which sent them back to the terminal instead of the dashboard. |
| Connect agent | 60-120s | Connect page provided snippets, but the only validation was "Check connection"; users had to leave the dashboard and run an agent before seeing whether the live feed worked. |
| First `/skills/load` visible | Unknown | No dashboard-controlled test load, so a user could not confirm the pipeline immediately. |

Estimated first-load time before fixes: 5-8 minutes depending on whether the user already knew which agent file to edit.

## Fixes Applied

1. Setup status now points skill generation to `/dashboard/repos` and the dashboard "Analyse now" flow instead of the CLI.
2. Connect Agent now explains the goal as "paste instructions, then send a test load".
3. Connect Agent includes a **Send test load** button that calls `/repos/{repo_id}/skills/load` with the org API key and selected runtime hint.
4. Connect Agent links to the new AgentRun spec for vendors/internal agents that can post sessions directly.

## After Fix Measurement

Live API smoke test:

| Step | Result |
| --- | --- |
| Resolve bootstrap org | OK |
| Fetch org API key | OK |
| Fetch connected repos | OK |
| Send `/repos/{repo_id}/skills/load` | OK, 12 skills returned |
| Fetch setup status | OK, `has_agent_loads=true`, `completion_percent=100` |
| Total measured API time | 9 seconds |

Expected guided user time after fixes:

| Step | Target Time |
| --- | ---: |
| Open dashboard and connect repo | 1-2 min |
| Run first repo analysis from dashboard | 1-2 min |
| Open Connect Agent and paste one agent block | 1 min |
| Send test load and see status update | < 15s |

Expected total: 3-5 minutes.

## Remaining Manual Verification

For a truly fresh org, verify the GitHub App installation redirect and first repo sync time. The dashboard path no longer requires discovering CLI commands to create the first visible load.
