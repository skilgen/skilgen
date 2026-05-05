# PR-6 Insights Fixture Limitation

The PRD asks for performance verification under a 1M-event fixture where feasible.

This branch adds database-side SQL views for risky-agent and risky-repo rankings, but the local unit test suite does not currently provision a 1M-event Postgres fixture or sanitized staging clone. The included migration test verifies view creation and downgrade on SQLite, and the API contract tests verify the ranking formula and fallback behavior. Full `<2s` verification should be run against a seeded Postgres fixture or staging clone before default-on rollout.
