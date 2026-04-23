"""Parser for Postman Collection v2.1 JSON exports."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from skilgen.parsers import ApiSpecFinding, ApiSpecItem, ApiSpecParseResult, ApiSpecParserError


ENV_VAR_RE = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_.-]*)\s*}}")
TOKEN_RE = re.compile(r"\b(?:Bearer\s+)?(?:sk|pk|pat|ghp|xox[baprs])_[A-Za-z0-9_-]{12,}\b")
AUTH_HEADER_RE = re.compile(r"\bAuthorization\s*:\s*(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{12,}", re.IGNORECASE)


def parse_postman_collection(path: str | Path) -> ApiSpecParseResult:
    """Parse a Postman Collection v2.1 JSON file."""

    collection_path = Path(path)
    payload = _load_collection(collection_path)
    info = payload.get("info")
    if not isinstance(info, dict):
        raise ApiSpecParserError(f"Postman parser expected an 'info' object in {collection_path}")
    schema = str(info.get("schema", ""))
    if "collection/v2.1" not in schema:
        raise ApiSpecParserError(f"Postman parser supports Collection v2.1, got schema {schema!r} in {collection_path}")
    items = payload.get("item")
    if not isinstance(items, list) or not items:
        raise ApiSpecParserError(f"Postman parser expected a non-empty top-level 'item' list in {collection_path}")

    title = str(info.get("name") or collection_path.stem)
    collection_auth = _auth_names(payload.get("auth"))
    groups: dict[str, list[ApiSpecItem]] = {}
    auth_schemes: list[str] = list(collection_auth)
    env_vars: set[str] = set()
    evidence: list[str] = [f"collection:{title}"]
    anti_patterns: list[ApiSpecFinding] = []

    for request_item in _iter_requests(items, folder_path=[], inherited_auth=collection_auth):
        group = request_item["group"]
        name = request_item["name"]
        request = request_item["request"]
        auth = request_item["auth"]
        method = _method(request)
        url = _url(request)
        scripts = _scripts(request_item["events"])
        script_vars: set[str] = set()
        for script in scripts:
            script_vars.update(ENV_VAR_RE.findall(script))
        request_vars = sorted(set(ENV_VAR_RE.findall(url)) | script_vars)
        env_vars.update(request_vars)
        auth_schemes.extend(auth)
        evidence.extend([f"request:{name}", f"url:{url}", *[f"env:{var}" for var in request_vars]])
        if scripts:
            evidence.extend(f"script:{line}" for line in scripts[:4])

        hardcoded_urls = _hardcoded_urls(url)
        if hardcoded_urls:
            anti_patterns.append(
                ApiSpecFinding(
                    category="hardcoded-url",
                    message=f"Request {name} uses hardcoded URL values instead of environment variables.",
                    evidence=hardcoded_urls,
                    location=name,
                )
            )
        hardcoded_tokens = _hardcoded_tokens(request, scripts)
        if hardcoded_tokens:
            anti_patterns.append(
                ApiSpecFinding(
                    category="hardcoded-token",
                    message=f"Request {name} includes token-like literals in auth, headers, or scripts.",
                    evidence=hardcoded_tokens[:6],
                    location=name,
                )
            )

        groups.setdefault(group, []).append(
            ApiSpecItem(
                group=group,
                name=name,
                kind="request",
                path=name,
                method=method,
                url=url,
                auth=auth,
                scripts=scripts,
                evidence=[f"request:{name}", f"url:{url}", *[f"auth:{scheme}" for scheme in auth]],
            )
        )

    if not groups:
        raise ApiSpecParserError(f"Postman parser found no requests in {collection_path}")

    patterns = [
        ApiSpecFinding(
            category="folders",
            message="Groups requests by Postman folder.",
            evidence=[f"{group}:{len(group_items)}" for group, group_items in groups.items()],
        )
    ]
    unique_auth = _unique(auth_schemes)
    if unique_auth:
        patterns.append(
            ApiSpecFinding(
                category="auth",
                message=f"Auth configuration detected: {', '.join(unique_auth)}.",
                evidence=[f"auth:{scheme}" for scheme in unique_auth],
            )
        )
    if env_vars:
        patterns.append(
            ApiSpecFinding(
                category="environment-variables",
                message="Collection uses environment variables for reusable values.",
                evidence=[f"env:{var}" for var in sorted(env_vars)],
            )
        )

    return ApiSpecParseResult(
        source_type="postman",
        title=title,
        version="2.1",
        groups=groups,
        auth_schemes=unique_auth,
        patterns=patterns,
        anti_patterns=anti_patterns,
        evidence=_unique(evidence),
    )


def parse_postman(path: str | Path) -> ApiSpecParseResult:
    """Alias for :func:`parse_postman_collection`."""

    return parse_postman_collection(path)


def parse(path: str | Path) -> ApiSpecParseResult:
    """Parse a Postman collection file."""

    return parse_postman_collection(path)


def _load_collection(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ApiSpecParserError(f"Postman parser could not find file: {path}")
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if not raw.strip():
        raise ApiSpecParserError(f"Postman parser cannot parse empty input: {path}")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ApiSpecParserError(f"Postman parser could not decode JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ApiSpecParserError(f"Postman parser expected a JSON object at the document root in {path}")
    return payload


def _iter_requests(items: list[object], *, folder_path: list[str], inherited_auth: list[str]) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "Unnamed request")
        local_auth = _auth_names(item.get("auth")) or inherited_auth
        if isinstance(item.get("request"), dict):
            requests.append(
                {
                    "group": "/".join(folder_path) if folder_path else "root",
                    "name": name,
                    "request": item["request"],
                    "auth": _auth_names(item["request"].get("auth")) or local_auth,
                    "events": _event_list(item.get("event")) + _event_list(item["request"].get("event")),
                }
            )
            continue
        children = item.get("item")
        if isinstance(children, list):
            folder_events = _event_list(item.get("event"))
            for child in _iter_requests(children, folder_path=[*folder_path, name], inherited_auth=local_auth):
                child["events"] = folder_events + child["events"]
                requests.append(child)
    return requests


def _auth_names(value: object) -> list[str]:
    if not isinstance(value, dict):
        return []
    auth_type = value.get("type")
    if not isinstance(auth_type, str) or auth_type == "noauth":
        return []
    return [auth_type]


def _method(request: dict[str, Any]) -> str | None:
    method = request.get("method")
    return str(method).upper() if method else None


def _url(request: dict[str, Any]) -> str:
    value = request.get("url")
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        raw = value.get("raw")
        if isinstance(raw, str) and raw:
            return raw
        protocol = str(value.get("protocol") or "https")
        host = value.get("host")
        path = value.get("path")
        host_text = ".".join(str(part) for part in host) if isinstance(host, list) else str(host or "")
        path_text = "/".join(str(part) for part in path) if isinstance(path, list) else str(path or "")
        if host_text:
            return f"{protocol}://{host_text}/{path_text}".rstrip("/")
    return ""


def _event_list(value: object) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _scripts(events: list[dict[str, Any]]) -> list[str]:
    scripts: list[str] = []
    for event in events:
        listen = event.get("listen")
        script = event.get("script")
        if not isinstance(listen, str) or listen not in {"prerequest", "test"} or not isinstance(script, dict):
            continue
        exec_lines = script.get("exec")
        if isinstance(exec_lines, list):
            scripts.extend(f"{listen}:{str(line).strip()}" for line in exec_lines if str(line).strip())
        elif isinstance(exec_lines, str) and exec_lines.strip():
            scripts.append(f"{listen}:{exec_lines.strip()}")
    return scripts


def _hardcoded_urls(url: str) -> list[str]:
    if ENV_VAR_RE.search(url):
        return []
    if url.startswith(("http://", "https://")):
        return [url]
    return []


def _hardcoded_tokens(request: dict[str, Any], scripts: list[str]) -> list[str]:
    rendered = json.dumps({"auth": request.get("auth"), "header": request.get("header"), "scripts": scripts}, sort_keys=True, default=str)
    hits = TOKEN_RE.findall(rendered)
    hits.extend(AUTH_HEADER_RE.findall(rendered))
    return _unique(hits)


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))
