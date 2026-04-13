# GitHub Actions

Copy [`skilgen-sync.yml`](skilgen-sync.yml) into `.github/workflows/` in your own repo to:

- refresh the skill tree on pushes to `main`
- capture pre-refresh `skilgen diff`, then refresh the skill tree and score the refreshed state on pull requests
- post a PR comment with freshness and score context
- fail the PR if the score drops below your threshold

The example template installs the published `skilgen` package with `python -m pip install skilgen`, which is the right behavior for downstream repositories using Skilgen in CI.

## Secrets

Add one of these as a repository secret if you want the model-backed runtime in CI:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `HUGGINGFACEHUB_API_TOKEN`

The workflow still works in local-fallback mode if no provider secret is configured.

## How The PR Score Works

The pull-request job intentionally runs in this order:

1. `skilgen diff --project-root . --json`
2. `skilgen deliver --project-root .`
3. `skilgen score --project-root .`

That means:

- the PR comment still tells you what was stale before refresh
- the enforced threshold is evaluated against the refreshed skill tree
- the score gate does not fail just because the repo had not been regenerated yet
