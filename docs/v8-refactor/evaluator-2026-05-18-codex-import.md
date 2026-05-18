# Evaluator — 2026-05-18 — Codex Desktop metadata importer

This evaluator pass reviews the Codex Desktop importer slice (no UX changes).

## Scope
- Adds `scripts/import_codex_sessions.py` to convert local Codex Desktop session JSONL into metadata-only `POST /orgs/{org_id}/agent-runs` payloads.
- Adds `tests/test_import_codex_sessions.py` to assert raw prompts/diffs are excluded while activity counters and file targets are preserved.
- Documents usage in `docs/v8-refactor/08-agent-compliance-ingestion.md`.

## Verification
- ✅ Unit test: `python -m pytest tests/test_import_codex_sessions.py -q`

## Data handling / privacy
- ✅ Metadata-only: importer does not emit raw prompts, chat content, patch diffs, file contents, or tool arguments.
- ✅ Sanitized details: command logging is redacted and file targets are normalized to project-relative paths when possible.

## PR readiness
- ✅ Ready to ship (backend-only helper; no new screenshots required).
