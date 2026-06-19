from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Sequence


GENESIS_HASH = "0" * 64


class ChainError(ValueError):
    pass


class TamperDetected(ChainError):
    pass


class ReorgDetected(ChainError):
    pass


class DuplicateEventConflict(ChainError):
    pass


@dataclass(frozen=True)
class EventInput:
    event_id: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ChainEntry:
    event_id: str
    sequence: int
    event_hash: str
    previous_hash: str
    root_hash: str
    merkle_proof: tuple[dict[str, str], ...] = ()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def sha256_hex(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


def event_hash(event_id: str, payload: dict[str, Any]) -> str:
    return sha256_hex(canonical_json({"event_id": event_id, "payload": payload}))


def chain_root(previous_hash: str, event_hash_value: str, sequence: int) -> str:
    return sha256_hex(canonical_json({"event_hash": event_hash_value, "previous_hash": previous_hash, "sequence": sequence}))


def merkle_root(hashes: Sequence[str]) -> str:
    if not hashes:
        return GENESIS_HASH
    level = list(hashes)
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [sha256_hex(level[index] + level[index + 1]) for index in range(0, len(level), 2)]
    return level[0]


def merkle_proof(hashes: Sequence[str], index: int) -> tuple[dict[str, str], ...]:
    if index < 0 or index >= len(hashes):
        raise IndexError("Merkle proof index outside hash list")
    proof: list[dict[str, str]] = []
    position = index
    level = list(hashes)
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        sibling = position ^ 1
        proof.append({"side": "left" if sibling < position else "right", "hash": level[sibling]})
        position //= 2
        level = [sha256_hex(level[item] + level[item + 1]) for item in range(0, len(level), 2)]
    return tuple(proof)


def verify_merkle_proof(leaf_hash: str, proof: Iterable[dict[str, str]], expected_root: str) -> bool:
    current = leaf_hash
    for item in proof:
        side = item.get("side")
        sibling = item.get("hash")
        if not sibling or side not in {"left", "right"}:
            return False
        current = sha256_hex(sibling + current) if side == "left" else sha256_hex(current + sibling)
    return current == expected_root


def _rehydrate_entries(entries: Iterable[ChainEntry | dict[str, Any]]) -> list[ChainEntry]:
    result: list[ChainEntry] = []
    for entry in entries:
        if isinstance(entry, ChainEntry):
            result.append(entry)
            continue
        result.append(
            ChainEntry(
                event_id=str(entry["event_id"]),
                sequence=int(entry["sequence"]),
                event_hash=str(entry["event_hash"]),
                previous_hash=str(entry["previous_hash"]),
                root_hash=str(entry["root_hash"]),
                merkle_proof=tuple(dict(item) for item in entry.get("merkle_proof", []) or []),
            )
        )
    return result


def append_events(existing: Iterable[ChainEntry | dict[str, Any]], events: Iterable[EventInput | dict[str, Any]]) -> list[ChainEntry]:
    entries = _rehydrate_entries(existing)
    verify_chain(entries)
    by_id = {entry.event_id: entry for entry in entries}
    next_sequence = entries[-1].sequence + 1 if entries else 0
    previous = entries[-1].root_hash if entries else GENESIS_HASH

    for raw in events:
        event = raw if isinstance(raw, EventInput) else EventInput(event_id=str(raw["event_id"]), payload=dict(raw.get("payload", {})))
        digest = event_hash(event.event_id, event.payload)
        duplicate = by_id.get(event.event_id)
        if duplicate:
            if duplicate.event_hash != digest:
                raise DuplicateEventConflict(f"event {event.event_id} already exists with a different hash")
            continue
        root = chain_root(previous, digest, next_sequence)
        entry = ChainEntry(event_id=event.event_id, sequence=next_sequence, event_hash=digest, previous_hash=previous, root_hash=root)
        entries.append(entry)
        by_id[event.event_id] = entry
        previous = root
        next_sequence += 1

    root_hashes = [entry.root_hash for entry in entries]
    return [
        ChainEntry(
            event_id=entry.event_id,
            sequence=entry.sequence,
            event_hash=entry.event_hash,
            previous_hash=entry.previous_hash,
            root_hash=entry.root_hash,
            merkle_proof=merkle_proof(root_hashes, index) if root_hashes else (),
        )
        for index, entry in enumerate(entries)
    ]


def verify_chain(entries: Iterable[ChainEntry | dict[str, Any]], payloads: dict[str, dict[str, Any]] | None = None) -> bool:
    previous = GENESIS_HASH
    seen_ids: set[str] = set()
    seen_sequences: set[int] = set()
    for expected_sequence, entry in enumerate(_rehydrate_entries(entries)):
        if entry.event_id in seen_ids or entry.sequence in seen_sequences or entry.sequence != expected_sequence:
            raise ReorgDetected("audit chain sequence was reordered or duplicated")
        if entry.previous_hash != previous:
            raise ReorgDetected("audit chain previous hash does not match prior root")
        if chain_root(entry.previous_hash, entry.event_hash, entry.sequence) != entry.root_hash:
            raise TamperDetected("audit chain root does not match event hash")
        if payloads is not None:
            payload = payloads.get(entry.event_id)
            if payload is None or event_hash(entry.event_id, payload) != entry.event_hash:
                raise TamperDetected("audit event payload no longer matches chain hash")
        seen_ids.add(entry.event_id)
        seen_sequences.add(entry.sequence)
        previous = entry.root_hash
    return True
