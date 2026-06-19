from __future__ import annotations

import importlib
from pathlib import Path


def test_audit_migration_has_reversible_hash_chain_objects() -> None:
    migration = importlib.import_module("apps.api.alembic.versions.20260505_0003_audit_hash_chain")
    source = Path(migration.__file__ or "").read_text(encoding="utf-8")
    assert migration.down_revision == "20260505_0002"
    assert "audit_hash_chain" in source
    assert "audit_worm_roots" in source
    assert "CREATE OR REPLACE VIEW v8_audit_report_events" in source
    assert "DROP VIEW IF EXISTS v8_audit_report_events" in source
    assert 'op.drop_table("audit_hash_chain")' in source
