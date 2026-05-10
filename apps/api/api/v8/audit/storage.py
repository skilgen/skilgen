from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
from typing import Any, Literal


WormStorageProvider = Literal["s3_object_lock", "gcs_bucket_lock", "azure_immutable_blob"]

WORM_STORAGE_TARGETS: dict[WormStorageProvider, dict[str, str]] = {
    "s3_object_lock": {
        "label": "S3 Object Lock",
        "bucket_env": "AUDIT_WORM_S3_BUCKET",
        "prefix_env": "AUDIT_WORM_S3_PREFIX",
        "default_prefix": "audit-roots",
        "uri_scheme": "s3",
    },
    "gcs_bucket_lock": {
        "label": "GCS Bucket Lock",
        "bucket_env": "AUDIT_WORM_GCS_BUCKET",
        "prefix_env": "AUDIT_WORM_GCS_PREFIX",
        "default_prefix": "audit-roots",
        "uri_scheme": "gs",
    },
    "azure_immutable_blob": {
        "label": "Azure Immutable Blob",
        "bucket_env": "AUDIT_WORM_AZURE_CONTAINER",
        "prefix_env": "AUDIT_WORM_AZURE_PREFIX",
        "default_prefix": "audit-roots",
        "uri_scheme": "azblob",
    },
}


def worm_target_status() -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for provider, config in WORM_STORAGE_TARGETS.items():
        bucket = os.getenv(config["bucket_env"])
        prefix = os.getenv(config["prefix_env"], config["default_prefix"]).strip("/")
        targets.append(
            {
                "provider": provider,
                "label": config["label"],
                "configured": bool(bucket),
                "bucket_env": config["bucket_env"],
                "prefix_env": config["prefix_env"],
                "prefix": prefix,
                "status": "configured" if bucket else "pending",
                "content_retention": "root-and-proof-only",
            }
        )
    return targets


def root_document(
    *,
    org_id: str,
    root_hash: str,
    start_sequence: int,
    end_sequence: int,
    event_count: int,
    merkle_proof: list[dict[str, str]],
    cadence: str,
    storage_provider: WormStorageProvider = "s3_object_lock",
) -> dict[str, Any]:
    return {
        "version": "1",
        "storage_provider": storage_provider,
        "org_id": org_id,
        "root_hash": root_hash,
        "start_sequence": start_sequence,
        "end_sequence": end_sequence,
        "event_count": event_count,
        "merkle_proof": merkle_proof,
        "cadence": cadence,
        "published_at": datetime.now(UTC).isoformat(),
    }


def _object_key(document: dict[str, Any], *, provider: WormStorageProvider, bucket: str | None = None, prefix: str | None = None) -> tuple[str | None, str | None]:
    config = WORM_STORAGE_TARGETS[provider]
    bucket = bucket or os.getenv(config["bucket_env"])
    prefix = (prefix if prefix is not None else os.getenv(config["prefix_env"], config["default_prefix"])).strip("/")
    key = f"{prefix}/{document['org_id']}/{document['root_hash']}.json" if prefix else f"{document['org_id']}/{document['root_hash']}.json"
    return bucket, key


def publish_worm_root(
    document: dict[str, Any],
    *,
    provider: WormStorageProvider | None = None,
    bucket: str | None = None,
    prefix: str | None = None,
) -> tuple[str | None, str]:
    """Publish a root/proof document to a WORM-capable target.

    The body intentionally contains only the chain root and Merkle proof. Event
    payloads are not accepted by this function.
    """
    if "events" in document or "payload" in document:
        raise ValueError("WORM root documents must not contain event payloads")
    provider = provider or str(document.get("storage_provider") or "s3_object_lock")  # type: ignore[assignment]
    if provider not in WORM_STORAGE_TARGETS:
        raise ValueError(f"Unsupported WORM storage provider: {provider}")
    document["storage_provider"] = provider
    bucket, key = _object_key(document, provider=provider, bucket=bucket, prefix=prefix)  # type: ignore[arg-type]
    if not bucket:
        return None, "pending"
    location = f"{WORM_STORAGE_TARGETS[provider]['uri_scheme']}://{bucket}/{key}"
    if provider != "s3_object_lock":
        return location, "pending"
    try:
        import boto3  # type: ignore[import-not-found]
    except Exception:
        return location, "pending"
    client = boto3.client("s3")
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(document, sort_keys=True).encode("utf-8"),
        ContentType="application/json",
        ObjectLockMode="GOVERNANCE",
    )
    return location, "published"


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
