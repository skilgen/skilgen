from __future__ import annotations

import unittest


class AgentRunsSmokeTests(unittest.TestCase):
    def test_agent_run_ingest_creates_session_from_http_payload(self) -> None:
        from apps.api.tests import test_agent_runs

        test_agent_runs.test_agent_run_ingest_creates_session_from_http_payload()

    def test_agent_run_ingest_updates_existing_audit_event_idempotently(self) -> None:
        from apps.api.tests import test_agent_runs

        test_agent_runs.test_agent_run_ingest_updates_existing_audit_event_idempotently()


if __name__ == "__main__":
    unittest.main()

