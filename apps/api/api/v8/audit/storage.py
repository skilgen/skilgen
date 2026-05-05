from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
from typing import Any


def root_document(
    *,
    org_id: str,
    root_hash: str,
    start_sequence: int,
    end_sequence: int,
    event_count: int,
    merkle_proof: list[dict[str, str]],
    cadence: str,
) -> dict[str, Any]:
    return {
        "version": "1",
        "storage_provider": "s3_object_lock",
        "org_id": org_id,
        "root_hash": root_hash,
        "start_sequence": start_sequence,
        "end_sequence": end_sequence,
        "event_count": event_count,
        "merkle_proof": merkle_proof,
        "cadence": cadence,
        "published_at": datetime.now(UTC).isoformat(),
    }


def publish_worm_root(document: dict[str, Any], *, bucket: str | None = None, prefix: str | None = None) -> tuple[str | None, str]:
    """Publish a root/proof document to S3 Object Lock.

    The body intentionally contains only the chain root and Merkle proof. Event
    payloads are not accepted by this function.
    """
    if "events" in document or "payload" in document:
        raise ValueError("WORM root documents must not contain event payloads")
    bucket = bucket or os.getenv("AUDIT_WORM_S3_BUCKET")
    prefix = (prefix if prefix is not None else os.getenv("AUDIT_WORM_S3_PREFIX", "audit-roots")).strip("/")
    key = f"{prefix}/{document['org_id']}/{document['root_hash']}.json" if prefix else f"{document['org_id']}/{document['root_hash']}.json"
    if not bucket:
        return None, "pending"
    try:
        import boto3  # type: ignore[import-not-found]
    except Exception:
        return key, "pending"
    client = boto3.client("s3")
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(document, sort_keys=True).encode("utf-8"),
        ContentType="application/json",
        ObjectLockMode="GOVERNANCE",
    )
    return key, "published"


def read_root_document(location: str) -> dict[str, Any]:
    if location.startswith("s3://"):
        try:
            import boto3  # type: ignore[import-not-found]
        except Exception as exc:
            raise RuntimeError("boto3 is required to read s3:// WORM roots") from exc
        bucket_key = location.removeprefix("s3://")
        bucket, _, key = bucket_key.partition("/")
        body = boto3.client("s3").get_object(Bucket=bucket, Key=key)["Body"].read()
        return json.loads(body.decode("utf-8"))
    path = Path(location.removeprefix("file://"))
    return json.loads(path.read_text(encoding="utf-8"))
