from __future__ import annotations

from apps.api.api.v8.settings.connectors_registry import connector_registry


def test_compliance_connectors_are_first_class_entries() -> None:
    connectors = {connector["id"]: connector for connector in connector_registry()}

    for connector_id in ("openai-compliance", "anthropic-compliance", "claude-cowork-otel"):
        assert connector_id in connectors
        assert connectors[connector_id]["category"] == "compliance-telemetry"
        assert connectors[connector_id]["status"] == "planned"
        assert connectors[connector_id]["description"]
        assert connectors[connector_id]["capabilities"]


def test_agent_connectors_include_access_and_model_telemetry() -> None:
    connectors = {connector["id"]: connector for connector in connector_registry()}

    assert "model tier" in connectors["codex-cli"]["capabilities"]
    assert "full-access grants" in connectors["cursor"]["capabilities"]
    assert "permission decisions" in connectors["claude-code"]["capabilities"]
