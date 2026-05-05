from __future__ import annotations

import json
import random

import pytest

from apps.api.api.v8.audit.chain import DuplicateEventConflict, ReorgDetected, TamperDetected, append_events, verify_chain
from apps.api.api.v8.audit.verify_cli import main as verify_main, verify as verify_cli


def _event(index: int) -> dict[str, object]:
    return {"event_id": f"evt_{index}", "payload": {"index": index, "actor": f"user-{index % 3}", "value": random.randint(1, 1000)}}


def test_append_correctness_property() -> None:
    random.seed(42)
    entries = []
    events = [_event(index) for index in range(75)]
    for event in events:
        entries = append_events(entries, [event])
        assert entries[-1].event_id == event["event_id"]
        assert entries[-1].sequence == len(entries) - 1
        assert entries[-1].previous_hash == (entries[-2].root_hash if len(entries) > 1 else "0" * 64)
        assert verify_chain(entries) is True


def test_tamper_detection() -> None:
    entries = append_events([], [_event(1), _event(2)])
    tampered = [entry.__dict__ for entry in entries]
    tampered[1]["event_hash"] = "f" * 64
    with pytest.raises(TamperDetected):
        verify_chain(tampered)


def test_reorg_detection() -> None:
    entries = append_events([], [_event(1), _event(2), _event(3)])
    reordered = [entries[1].__dict__, entries[0].__dict__, entries[2].__dict__]
    with pytest.raises(ReorgDetected):
        verify_chain(reordered)


def test_duplicate_idempotency_and_conflict() -> None:
    event = {"event_id": "evt_dup", "payload": {"same": True}}
    entries = append_events([], [event])
    assert append_events(entries, [event]) == entries
    with pytest.raises(DuplicateEventConflict):
        append_events(entries, [{"event_id": "evt_dup", "payload": {"same": False}}])


def test_verifier_cli_passes_and_fails(tmp_path) -> None:
    entries = append_events([], [_event(1), _event(2), _event(3)])
    chain_path = tmp_path / "chain.ndjson"
    chain_path.write_text("\n".join(json.dumps(entry.__dict__) for entry in entries), encoding="utf-8")
    root_path = tmp_path / "root.json"
    root_path.write_text(json.dumps({"root_hash": entries[-1].root_hash, "end_sequence": entries[-1].sequence}), encoding="utf-8")

    assert verify_cli(str(root_path), chain_path) == (True, "pass")
    assert verify_main(["--root", str(root_path), "--chain", str(chain_path)]) == 0

    root_path.write_text(json.dumps({"root_hash": "0" * 64, "end_sequence": entries[-1].sequence}), encoding="utf-8")
    ok, message = verify_cli(str(root_path), chain_path)
    assert ok is False
    assert message == "root mismatch"
