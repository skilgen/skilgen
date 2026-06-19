"""Parser for OpenAPI 3.x and Swagger 2.0 API specifications."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

from skilgen.parsers import ApiSpecFinding, ApiSpecItem, ApiSpecParseResult, ApiSpecParserError


HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
PII_KEYS = {
    "accountNumber",
    "birthDate",
    "creditCard",
    "creditCardNumber",
    "dateOfBirth",
    "dob",
    "email",
    "phone",
    "ssn",
    "socialSecurityNumber",
    "taxId",
}
PII_VALUE_PATTERNS = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
)


def parse_openapi_spec(path: str | Path) -> ApiSpecParseResult:
    """Parse an OpenAPI or Swagger specification file."""

    spec_path = Path(path)
    payload = _load_mapping(spec_path)
    version = _spec_version(payload, spec_path)
    title = _title(payload, spec_path)
    paths = payload.get("paths")
    if not isinstance(paths, dict) or not paths:
        raise ApiSpecParserError(f"OpenAPI parser expected a non-empty 'paths' object in {spec_path}")

    auth_schemes = _auth_schemes(payload)
    global_security = _security_names(payload.get("security"))
    global_rate_limits = _rate_limits(payload)
    schema_names = _schema_names(payload)
    evidence = [f"version:{version}", *[f"schema:{name}" for name in schema_names]]
    groups: dict[str, list[ApiSpecItem]] = {}
    rate_limits: list[str] = list(global_rate_limits)
    error_responses: list[str] = []
    examples: list[str] = []
    patterns: list[ApiSpecFinding] = []
    anti_patterns: list[ApiSpecFinding] = []

    for route, path_item in paths.items():
        if not isinstance(route, str) or not isinstance(path_item, dict):
            continue
        group = _path_group(route)
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            operation_name = str(operation.get("operationId") or f"{method.upper()} {route}")
            operation_security = operation.get("security", path_item.get("security", payload.get("security")))
            auth = _security_names(operation_security)
            if operation_security is None:
                auth = global_security
            operation_rate_limits = _rate_limits(operation)
            operation_error_responses = _error_responses(operation, method.upper(), route)
            operation_examples = _examples(operation)
            operation_evidence = [f"{method.upper()} {route}"]

            operation_id = operation.get("operationId")
            if isinstance(operation_id, str) and operation_id.strip():
                evidence.append(f"operationId:{operation_id}")
                operation_evidence.append(f"operationId:{operation_id}")
            for ref_name in _schema_refs(operation):
                evidence.append(f"schema:{ref_name}")
                operation_evidence.append(f"schema:{ref_name}")
            for example in operation_examples:
                evidence.append(f"example:{example}")
                operation_evidence.append(f"example:{example}")

            if operation.get("deprecated") is True:
                anti_patterns.append(
                    ApiSpecFinding(
                        category="deprecated-endpoint",
                        message=f"{method.upper()} {route} is marked deprecated.",
                        evidence=operation_evidence[:6],
                        location=route,
                    )
                )
            if not auth:
                anti_patterns.append(
                    ApiSpecFinding(
                        category="no-auth",
                        message=f"{method.upper()} {route} has no operation-level or global security requirement.",
                        evidence=operation_evidence[:6],
                        location=route,
                    )
                )
            pii = _raw_pii_examples(operation)
            if pii:
                anti_patterns.append(
                    ApiSpecFinding(
                        category="raw-pii-example",
                        message=f"{method.upper()} {route} includes raw PII-like example values.",
                        evidence=pii[:6],
                        location=route,
                    )
                )

            item = ApiSpecItem(
                group=group,
                name=operation_name,
                kind="endpoint",
                path=route,
                method=method.upper(),
                operation_id=operation_id if isinstance(operation_id, str) else None,
                auth=auth,
                deprecated=operation.get("deprecated") is True,
                rate_limits=operation_rate_limits,
                error_responses=operation_error_responses,
                examples=operation_examples,
                evidence=operation_evidence,
            )
            groups.setdefault(group, []).append(item)
            rate_limits.extend(operation_rate_limits)
            error_responses.extend(operation_error_responses)
            examples.extend(operation_examples)

    if not groups:
        raise ApiSpecParserError(f"OpenAPI parser found no HTTP operations in {spec_path}")
    if auth_schemes:
        patterns.append(
            ApiSpecFinding(
                category="auth-schemes",
                message=f"Defines authentication schemes: {', '.join(auth_schemes)}.",
                evidence=[f"auth:{scheme}" for scheme in auth_schemes],
            )
        )
    if rate_limits:
        patterns.append(
            ApiSpecFinding(
                category="rate-limits",
                message="Documents throttling or rate-limit behavior.",
                evidence=_unique(rate_limits)[:8],
            )
        )
    patterns.append(
        ApiSpecFinding(
            category="endpoint-groups",
            message="Groups endpoints by first path segment.",
            evidence=[f"{group}:{len(items)}" for group, items in groups.items()],
        )
    )

    return ApiSpecParseResult(
        source_type="openapi",
        title=title,
        version=version,
        groups=groups,
        auth_schemes=auth_schemes,
        rate_limits=_unique(rate_limits),
        error_responses=_unique(error_responses),
        examples=_unique(examples),
        patterns=patterns,
        anti_patterns=anti_patterns,
        evidence=_unique(evidence),
    )


def parse_openapi(path: str | Path) -> ApiSpecParseResult:
    """Alias for :func:`parse_openapi_spec`."""

    return parse_openapi_spec(path)


def parse(path: str | Path) -> ApiSpecParseResult:
    """Parse an OpenAPI or Swagger specification file."""

    return parse_openapi_spec(path)


def _load_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ApiSpecParserError(f"OpenAPI parser could not find file: {path}")
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if not raw.strip():
        raise ApiSpecParserError(f"OpenAPI parser cannot parse empty input: {path}")
    try:
        payload = json.loads(raw) if path.suffix.lower() == ".json" else yaml.safe_load(raw)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ApiSpecParserError(f"OpenAPI parser could not decode {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ApiSpecParserError(f"OpenAPI parser expected a mapping at the document root in {path}")
    return payload


def _spec_version(payload: dict[str, Any], path: Path) -> str:
    version = payload.get("openapi") or payload.get("swagger")
    if not isinstance(version, str):
        raise ApiSpecParserError(f"OpenAPI parser expected 'openapi' or 'swagger' version in {path}")
    if not (version.startswith("3.") or version == "2.0"):
        raise ApiSpecParserError(f"OpenAPI parser supports OpenAPI 3.x and Swagger 2.0, got {version!r} in {path}")
    return version


def _title(payload: dict[str, Any], path: Path) -> str:
    info = payload.get("info")
    if isinstance(info, dict) and isinstance(info.get("title"), str):
        return info["title"]
    return path.stem


def _path_group(route: str) -> str:
    parts = [part for part in route.strip("/").split("/") if part]
    return parts[0] if parts else "root"


def _auth_schemes(payload: dict[str, Any]) -> list[str]:
    schemes = payload.get("components", {}).get("securitySchemes") if isinstance(payload.get("components"), dict) else None
    if not isinstance(schemes, dict):
        schemes = payload.get("securityDefinitions")
    if not isinstance(schemes, dict):
        return []
    rendered: list[str] = []
    for name, value in schemes.items():
        if isinstance(value, dict):
            scheme_type = value.get("type") or value.get("scheme") or value.get("in")
            rendered.append(f"{name}:{scheme_type}" if scheme_type else str(name))
        else:
            rendered.append(str(name))
    return sorted(rendered)


def _security_names(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    names: list[str] = []
    for entry in value:
        if isinstance(entry, dict):
            names.extend(str(name) for name in entry)
    return sorted(set(names))


def _rate_limits(value: object) -> list[str]:
    limits: list[str] = []
    for key, nested in _walk_pairs(value):
        lowered = key.lower()
        if "rate" in lowered and ("limit" in lowered or "throttle" in lowered):
            limits.append(f"{key}:{_compact(nested)}")
        if key == "429":
            limits.append(f"429:{_compact(nested)}")
    return _unique(limits)


def _error_responses(operation: dict[str, Any], method: str, route: str) -> list[str]:
    responses = operation.get("responses")
    if not isinstance(responses, dict):
        return []
    errors: list[str] = []
    for status, response in responses.items():
        status_text = str(status)
        if status_text != "default" and not (status_text.isdigit() and int(status_text) >= 400):
            continue
        details = _compact(response)
        refs = ", ".join(_schema_refs(response))
        suffix = f" schema={refs}" if refs else ""
        errors.append(f"{method} {route} {status_text}: {details}{suffix}".strip())
    return errors


def _examples(value: object) -> list[str]:
    examples: list[str] = []
    for key, nested in _walk_pairs(value):
        if key in {"example", "examples"}:
            examples.append(_compact(nested))
    return _unique(examples)


def _raw_pii_examples(value: object) -> list[str]:
    hits: list[str] = []
    for key, nested in _walk_pairs(value):
        if key in PII_KEYS and nested not in {None, ""}:
            hits.append(f"{key}:{_compact(nested)}")
        if isinstance(nested, str) and any(pattern.search(nested) for pattern in PII_VALUE_PATTERNS):
            hits.append(f"{key}:{nested}")
    return _unique(hits)


def _schema_names(payload: dict[str, Any]) -> list[str]:
    components = payload.get("components")
    if isinstance(components, dict) and isinstance(components.get("schemas"), dict):
        return sorted(str(name) for name in components["schemas"])
    definitions = payload.get("definitions")
    if isinstance(definitions, dict):
        return sorted(str(name) for name in definitions)
    return []


def _schema_refs(value: object) -> list[str]:
    refs: list[str] = []
    for key, nested in _walk_pairs(value):
        if key == "$ref" and isinstance(nested, str):
            refs.append(nested.rsplit("/", 1)[-1])
    return _unique(refs)


def _walk_pairs(value: object) -> Iterable[tuple[str, object]]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key), nested
            yield from _walk_pairs(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_pairs(nested)


def _compact(value: object, *, limit: int = 120) -> str:
    if isinstance(value, str):
        rendered = value
    else:
        rendered = json.dumps(value, sort_keys=True, default=str)
    rendered = " ".join(rendered.split())
    return rendered[: limit - 1] + "..." if len(rendered) > limit else rendered


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))
