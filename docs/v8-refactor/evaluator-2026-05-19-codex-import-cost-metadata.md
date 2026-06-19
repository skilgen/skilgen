# Evaluator — 2026-05-19 — Codex import cost + token metadata

Status: PASS

## Scope reviewed
- `scripts/import_codex_sessions.py` emits richer token + cost provenance metadata for imported Codex / Claude Code sessions.
- `apps/api/api/routes/agent_runs.py` preserves the new metadata fields in the `agent.compliance` audit event envelope.
- Tests updated/added to cover the new metadata envelope.
- Docs updated to reinforce provenance rules and cross-link the enterprise ingestion roadmap.

## Verification
- `python -m pytest apps/api/tests/test_agent_runs.py tests/test_import_codex_sessions.py -q` (pass).

## UX / screenshots
- Not applicable (backend + docs slice only).

## Notes
- Usage/cost provenance is explicitly labeled (`cost_source`, `cost_estimate`) and does not imply provider-billed cost.

