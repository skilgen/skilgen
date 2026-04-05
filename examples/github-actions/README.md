# GitHub Action Templates

These templates help teams run Skilgen in CI so the repo-local skill system stays current without relying on manual local runs.

## `skilgen-sync.yml`

Copy `examples/github-actions/skilgen-sync.yml` into your repository as:

```text
.github/workflows/skilgen-sync.yml
```

What it does:
- on pushes to `main`, runs `skilgen deliver`, then commits refreshed `skills/` files and generated markdown docs back to the branch
- on pull requests, runs `skilgen diff` and `skilgen score`, posts a PR comment with the current scorecard, and fails the PR if the score falls below the configured threshold

## Required secrets

Use one provider secret so Skilgen can run in model-backed mode:

- `OPENAI_API_KEY`
- or `ANTHROPIC_API_KEY`

The workflow automatically exposes whichever of those secrets you configure.

## Optional configuration

- `SKILGEN_SCORE_THRESHOLD`
  - default: `70`
  - the PR job fails if the score falls below this threshold

## Notes

- the sync job uses the built-in `GITHUB_TOKEN` with `contents: write` so it can push refreshed skill files
- the PR comment job uses `pull-requests: write` so it can leave the score summary directly on the pull request
