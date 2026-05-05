from __future__ import annotations

import csv
from datetime import datetime
from io import BytesIO, StringIO
import json
from pathlib import Path
from zipfile import ZipFile

from apps.api.api.v8.audit.evidence import build_evidence_package_zip
from apps.api.api.v8.audit.reports import REPORTS, REPORT_VIEW_SQL, report_sql
from apps.api.api.v8.audit.router import _csv_body, _siem_body
from apps.api.api.v8.audit.storage import publish_worm_root, read_root_document, root_document
from packages.db.models import AuditEvent


def _audit_event(event_id: str = "evt_1") -> AuditEvent:
    return AuditEvent(
        id=event_id,
        org_id="org_1",
        event_type="audit.export.created",
        action="exported",
        actor_login="ravi",
        repo_name="payments",
        summary="Exported audit events",
        severity="info",
        metadata_json={"policy_decision": "allow"},
        created_at=datetime(2026, 5, 1, 12, 0, 0),
    )


def test_report_sql_snapshots_cover_five_prd_reports() -> None:
    assert [report.id for report in REPORTS] == [
        "ai-assisted-change-log",
        "privileged-action-report",
        "dlp-triggered-events",
        "skill-provenance-report",
        "anomaly-report",
    ]
    assert "FROM v8_audit_report_events" in REPORT_VIEW_SQL
    for report in REPORTS:
        sql = report_sql(report.id)
        assert "WHERE org_id = :org_id" in sql
        assert "ORDER BY created_at DESC" in sql


def test_export_csv_roundtrip_and_siem_shapes() -> None:
    body = _csv_body([_audit_event()])
    rows = list(csv.DictReader(StringIO(body)))
    assert rows[0]["id"] == "evt_1"
    assert rows[0]["event_type"] == "audit.export.created"
    assert rows[0]["metadata"] == '{"policy_decision": "allow"}'

    splunk = _siem_body("splunk_hec", [_audit_event()])
    assert isinstance(splunk, list)
    assert splunk[0]["sourcetype"] == "skillayer:audit"
    sentinel = _siem_body("microsoft_sentinel", [_audit_event()])
    assert isinstance(sentinel, dict)
    assert sentinel["records"][0]["SourceSystem"] == "Skillayer"


def test_worm_root_contains_no_event_payload_and_uses_s3_object_lock(monkeypatch, tmp_path: Path) -> None:
    document = root_document(
        org_id="org_1",
        root_hash="a" * 64,
        start_sequence=0,
        end_sequence=3,
        event_count=4,
        merkle_proof=[{"side": "left", "hash": "b" * 64}],
        cadence="hourly",
    )
    assert "events" not in document
    assert document["storage_provider"] == "s3_object_lock"
    monkeypatch.delenv("AUDIT_WORM_S3_BUCKET", raising=False)
    object_key, status = publish_worm_root(document)
    assert object_key is None
    assert status == "pending"
    root_path = tmp_path / "root.json"
    root_path.write_text(json.dumps(document), encoding="utf-8")
    assert read_root_document(str(root_path))["root_hash"] == "a" * 64


def test_evidence_package_zip_uses_html_fallback_index() -> None:
    package = build_evidence_package_zip(
        org_id="org_1",
        control="SOC2 CC8.1",
        period_start="2026-01-01T00:00:00",
        period_end="2026-03-31T23:59:59",
        events=[{"id": "evt_1"}],
        chain_root={"root_hash": "a" * 64},
        policies=[{"id": "pol_1"}],
        skills=[{"id": "skill_1"}],
    )
    with ZipFile(BytesIO(package)) as archive:
        assert "index.html" in archive.namelist()
        manifest = archive.read("manifest.json").decode("utf-8")
        assert '"index_format": "html"' in manifest
        assert "SOC2 CC8.1" in archive.read("index.html").decode("utf-8")
