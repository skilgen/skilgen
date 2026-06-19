# GitHub App

The Skillayer GitHub App connects repository events to the skill system. It is
the piece that makes Skilgen continuous instead of purely manual.

## Installation

1. Open [skillayer.dev/install](https://skillayer.dev/install)
2. Choose the GitHub organization to install into
3. Pick the repositories to connect
4. Review the permissions screen
5. Finish installation and return to the dashboard

Permissions are requested for a reason:

- **Contents / metadata** so Skillayer knows which repo triggered an analysis
- **Pull requests** so it can read PR context
- **Checks** so it can create a GitHub Check Run
- **Issues / comments** so it can post or update the PR comment
- **Webhooks** so pushes and PR events can trigger work automatically

## What Happens on Each Pull Request

When a PR is opened, synchronized, or reopened, Skillayer does the following:

1. receives the `pull_request` webhook
2. looks up the repository and base score on the default branch
3. queues a Skilgen analysis for the PR head SHA
4. computes the current branch score
5. posts or updates the PR comment
6. creates a GitHub Check Run for pass / fail status

This keeps the feedback loop inside the place where engineers are already
reviewing changes.

## PR Comment Anatomy

A typical PR comment includes:

- total score and grade label
- delta versus the base branch
- four subscores
- a domains analysed line
- stale skill warnings when freshness is low
- a link back to the Skillayer dashboard

Example structure:

```text
Skilgen Score: 78/100 (+4 vs base)

Groundedness  19/25
Coverage      20/25
Freshness     21/25
Structure     18/25

9 domains analysed: auth, billing, api, frontend, backend, roadmap, +3 more
```

## GitHub Check Run

The GitHub Check Run uses the org score threshold:

- default threshold: `60`
- configurable in Dashboard → Settings → General

Check behavior:

- score greater than or equal to the threshold → success
- score below the threshold → failure

To require it in branch protection:

1. Open GitHub repository settings
2. Go to **Branches**
3. Edit branch protection for your main branch
4. Enable **Require status checks to pass before merging**
5. Search for the Skillayer or Skilgen check name
6. Save the rule

## Configuring via `.skilgen.yml`

Repo-local quality settings still matter. Example:

```yaml
quality_gates:
  min_score: 60
  min_groundedness: 15
  min_coverage: 15
sources:
  openapi: true
  runbooks: true
```

The GitHub App respects the generated skills and score output from that repo.

## Webhook Behavior

Skillayer listens for:

- `push`
- `pull_request`
- `installation`
- `installation_repositories`

Key pull request actions:

- handled: `opened`, `synchronize`, `reopened`
- ignored: `closed`, `labeled`, `unlabeled`, `assigned`, `review_requested`

## Troubleshooting

### App not posting comments

- check GitHub App webhook deliveries
- confirm the app still has comment permission
- confirm the repo is installed under the app

### Check run not appearing

- verify the app has **Checks** permission
- verify the PR event was one of the handled actions
- confirm the analysis run completed successfully

### Score not updating

- run **Analyse now** from the dashboard
- make sure the repo has a recent complete analysis on the default branch
- verify the webhook reached `https://api.skillayer.com/webhook/github`

### Wrong pass / fail threshold

- open Dashboard → Settings → General
- confirm `score_threshold` is the value your team expects
- re-run analysis if you changed the threshold after the PR was opened

## Example PR Feedback Flow

An end-to-end PR cycle usually looks like this:

1. a developer opens a PR against `main`
2. GitHub sends the webhook to Skillayer
3. Skillayer resolves installation, repo, and org context
4. a focused analysis runs for the PR head SHA
5. score deltas are computed against the base branch
6. the PR comment is created or updated in place
7. the GitHub Check Run is marked success or failure

The important product behavior is that Skillayer updates the same PR comment
instead of spamming the thread with a new bot message every time.

## Example Check Run Summary

Typical summary text:

```text
Skilgen Score 78/100
Threshold 60/100
Coverage 5 of 8 categories
Status: pass
```

If a PR fails, the check summary should tell reviewers whether the problem is:

- low groundedness
- missing coverage
- stale knowledge
- enterprise policy failure

That makes the next step obvious instead of forcing the team to guess.

## Recommended Installation Practices

- start with a small set of repos first
- verify branch protection on one repo before org-wide rollout
- make sure the dashboard org mapping matches the GitHub org installation
- confirm the app has access to the repos where you expect PR feedback

This gives teams a controlled rollout path and keeps webhook troubleshooting
manageable.
