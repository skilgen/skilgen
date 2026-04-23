# GitHub App

Install the GitHub App from `https://skillayer.dev/install`, choose the organization, and select repositories.

## What It Does

- Receives push webhooks on default branches.
- Receives pull request webhooks for opened, synchronized, and reopened PRs.
- Queues Skilgen analysis runs.
- Posts PR comments with score deltas.
- Creates GitHub Check Runs using the organization score threshold.
- Updates dashboard score history and skill freshness.

## PR Comment Anatomy

The PR comment includes total score, grade label, subscores, delta from base branch, analyzed domain badges, stale skill warnings, and dashboard links.

## Check Runs

The check run passes when `score_total >= org.score_threshold`. The default threshold is 60 and can be changed in Dashboard Settings. To enforce it, add the Skillayer check to branch protection.

## Webhook Settings

Webhook URL: `https://api.skillayer.com/webhook/github`

Events: push, pull_request, installation, installation_repositories.

## Troubleshooting

If comments do not appear, check GitHub webhook delivery logs and the Skillayer recent runs list. If checks do not appear, verify the app has Checks write permission. If score is stale, trigger Analyse Now from the dashboard.
