# PostToolUse Hook Manual Verification

Use this procedure to verify Claude Code writes session artifacts into Skillayer.

## Setup

1. Open a sandbox repo connected to Skillayer.
2. Ensure `.claude/settings.json` contains both hooks:
   - `PreToolUse` for `Edit|Write|NotebookEdit`
   - `PostToolUse` for `Read|Edit|Write|NotebookEdit`
3. Export:

```bash
export SKILLAYER_API_KEY=sk-...
export SKILLAYER_REPO_ID=<repo-id>
export CLAUDE_SESSION_ID=manual-artifact-test
```

## Exercise

1. Start Claude Code in the sandbox repo.
2. Ask it to make three small edits in three different files.
3. Wait at least one hook round trip after the final edit.
4. Close the session explicitly:

```bash
curl -X POST \
  -H "Authorization: Bearer $SKILLAYER_API_KEY" \
  "https://api.skillayer.com/repos/$SKILLAYER_REPO_ID/sessions/manual-artifact-test/close"
```

## Expected Results

1. The matching `AgentSession` has three `produced_artifacts` entries.
2. Each artifact includes `file_path`, `tool`, `before_hash`, `after_hash`, `diff`, and `ts`.
3. `produced_file_hashes` contains one SHA-256 value for each edited file.
4. `closed_at` is set after the close call.
5. Session knowledge extraction starts automatically after close.

If artifacts are missing, check that the hook receives JSON event files from Claude Code and that both PreToolUse and PostToolUse entries use the same command.
