# Dashboard Examples

These are committed, self-contained HTML dashboard snapshots generated with Skilgen and saved into the repo so people can inspect real output.

GitHub will show the HTML source in the repo view. Download the file or open it locally in a browser to see the full interactive dashboard.

## Anthropic claude-agent-sdk-python

- Source repo: [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)
- Source commit: `86d0ba2`
- Dashboard file: [`claude-agent-sdk-python-dashboard.html`](claude-agent-sdk-python-dashboard.html)

Generated from the upstream repository snapshot with the repo-native package planner. This example shows Skilgen moving from a repo-only baseline of `25 / 100` to a generated skill-system score of `95 / 100` by materializing package, testing, e2e, examples, scripts, and roadmap skills.

## LangChain

- Source repo: [langchain-ai/langchain](https://github.com/langchain-ai/langchain)
- Source commit: `8182d63`
- Dashboard file: [`langchain-dashboard.html`](langchain-dashboard.html)

Generated from the upstream repository snapshot with the current Skilgen dashboard command. This example is useful as a large polyglot/monorepo reference point.

## LibreChat

- Source repo: [danny-avila/LibreChat](https://github.com/danny-avila/LibreChat)
- Source commit: `5cc783b`
- Dashboard file: [`librechat-dashboard.html`](librechat-dashboard.html)
- Generated skill tree: [`librechat-skills.md`](librechat-skills.md)
- Live `skills/` snapshot: [`librechat-skill-tree/skills/MANIFEST.md`](librechat-skill-tree/skills/MANIFEST.md)

Generated from the upstream repository snapshot with the repo-native app planner. This example shows Skilgen moving from a repo-only baseline of `20 / 100` to a generated skill-system score of `87 / 100` by materializing `26` skills across `api`, `client`, `config`, `e2e`, `packages`, and `roadmap`.
