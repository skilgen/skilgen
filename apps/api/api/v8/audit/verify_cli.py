from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from apps.api.api.v8.audit.chain import ChainEntry, verify_chain
from apps.api.api.v8.audit.storage import read_root_document


def _read_chain(path: Path) -> list[ChainEntry]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        rows = json.loads(text)
    else:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [
        ChainEntry(
            event_id=str(row["event_id"]),
            sequence=int(row["sequence"]),
            event_hash=str(row["event_hash"]),
            previous_hash=str(row["previous_hash"]),
            root_hash=str(row["root_hash"]),
            merkle_proof=tuple(row.get("merkle_proof", []) or []),
        )
        for row in rows
    ]


def verify(root_location: str, chain_path: Path) -> tuple[bool, str]:
    root = read_root_document(root_location)
    entries = _read_chain(chain_path)
    if not entries:
        return False, "chain is empty"
    verify_chain(entries)
    if entries[-1].root_hash != root.get("root_hash"):
        return False, "root mismatch"
    if entries[-1].sequence != int(root.get("end_sequence", -1)):
        return False, "sequence mismatch"
    return True, "pass"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a Skillayer audit hash chain against a WORM root document.")
    parser.add_argument("--root", required=True, help="s3://bucket/key or local/file:// root JSON document")
    parser.add_argument("--chain", required=True, type=Path, help="Chain JSON or NDJSON fixture")
    args = parser.parse_args(argv)
    try:
        ok, message = verify(args.root, args.chain)
    except Exception as exc:
        ok, message = False, str(exc)
    print(f"{'PASS' if ok else 'FAIL'} {message}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
