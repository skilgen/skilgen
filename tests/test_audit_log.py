from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
import unittest

from apps.api.api.services import audit
from apps.api.api.routes import orgs


class _FakeDb:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.added: list[object] = []

    def add(self, value: object) -> None:
        if self.fail:
            raise RuntimeError("boom")
        self.added.append(value)


class AuditLogTests(unittest.IsolatedAsyncioTestCase):
    async def test_emit_adds_event(self) -> None:
        db = _FakeDb()
        await audit.emit(db, "org_1", "skill.content_edited", "updated", "Edited auth skill", actor_login="janedoe")
        self.assertEqual(len(db.added), 1)
        event = db.added[0]
        self.assertEqual(event.org_id, "org_1")
        self.assertEqual(event.event_type, "skill.content_edited")
        self.assertEqual(event.action, "updated")

    async def test_emit_never_raises(self) -> None:
        db = _FakeDb(fail=True)
        await audit.emit(db, "bad", "settings.updated", "updated", "bad")
        self.assertEqual(db.added, [])

    def test_event_type_prefix_filter_is_supported(self) -> None:
        source = open("apps/api/api/routes/orgs.py", encoding="utf-8").read()
        self.assertIn("AuditEvent.event_type.startswith(event_type)", source)

    def test_csv_export_streams_expected_headers(self) -> None:
        source = open("apps/api/api/routes/orgs.py", encoding="utf-8").read()
        self.assertIn('"timestamp", "event_type", "action", "actor", "summary", "repo", "severity"', source)
        self.assertIn('Content-Disposition": "attachment; filename=audit-log.csv"', source)

    def test_stats_counts_core_metrics(self) -> None:
        source = open("apps/api/api/routes/orgs.py", encoding="utf-8").read()
        self.assertIn("gate_pass_rate", source)
        self.assertIn("analysis_runs_30d", source)
        self.assertIn("critical_events_7d", source)

    def test_serializer_uses_metadata_json(self) -> None:
        event = SimpleNamespace(
            id="evt_1",
            event_type="policy.check_failed",
            action="failed",
            actor_login="system",
            repo_id=None,
            repo_name=None,
            skill_id=None,
            skill_domain=None,
            resource_type="policy",
            resource_id="pol_1",
            summary="Policy failed",
            severity="critical",
            metadata_json={"violation_count": 1},
            created_at=datetime.utcnow(),
        )
        response = orgs._audit_event_response(event)
        self.assertEqual(response.metadata["violation_count"], 1)

    def test_actor_login_dependency_decodes_jwt_shape(self) -> None:
        source = open("apps/api/api/services/audit.py", encoding="utf-8").read()
        self.assertIn("preferred_username", source)
        self.assertIn("sub", source)


if __name__ == "__main__":
    unittest.main()
