# GitHub Actions

Copy [`skilgen-sync.yml`](skilgen-sync.yml) into `.github/workflows/` in your own repo to:

- refresh the skill tree on pushes to `main`
- compute `skilgen diff` and `skilgen score` on pull requests
- post a PR comment with freshness and score context
- fail the PR if the score drops below your threshold

## Secrets

Add one of these as a repository secret if you want the model-backed runtime in CI:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `HUGGINGFACEHUB_API_TOKEN`

The workflow still works in local-fallback mode if no provider secret is configured.
