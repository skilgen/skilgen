# Diff And Auto-Update

`skilgen diff` shows what changed since the last generation and which skills are stale.

## Commands

```bash
skilgen diff --project-root .
skilgen diff --project-root . --json
```

## What it shows

- changed files
- change type (`added`, `modified`, `deleted`)
- impacted domains
- stale skill paths
- current domains that remain fresh
- freshness score and reason
- git-aware event context

## Auto-update

When `update_trigger: auto` is enabled, Skilgen watches for changes and refreshes the repo-local skill system in the background.

Skilgen now classifies git-aware events such as:

- manual edits
- staged changes
- new untracked files
- merge commits
- merge in progress
- rebase in progress
- history rewrites

This makes auto-refresh much easier to trust in real engineering workflows.
