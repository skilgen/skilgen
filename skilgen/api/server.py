from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from skilgen.api.service import (
    analytics_payload,
    analyze_payload,
    architecture_payload,
    dashboard_payload,
    cancel_job_payload,
    connectors_activate_payload,
    connectors_active_payload,
    connectors_deactivate_payload,
    connectors_list_payload,
    connectors_recommend_payload,
    create_deliver_job,
    decision_payload,
    deliver_payload,
    diff_payload,
    doctor_payload,
    enterprise_generate_payload,
    enterprise_ingest_payload,
    enterprise_list_payload,
    features_payload,
    fingerprint_payload,
    health_payload,
    intent_payload,
    jobs_payload,
    job_status_payload,
    map_payload,
    plan_payload,
    preview_payload,
    report_payload,
    resume_job_payload,
    score_badge_payload,
    score_payload,
    skills_activate_payload,
    skills_active_payload,
    skills_deactivate_payload,
    skills_detect_payload,
    skills_import_payload,
    skills_install_payload,
    skills_list_payload,
    skills_lock_export_payload,
    skills_lock_import_payload,
    skills_lock_payload,
    skills_policy_payload,
    skills_rank_payload,
    skills_remove_payload,
    skills_show_payload,
    skills_sync_payload,
    status_payload,
    validate_payload,
)
from skilgen.core.audit import append_audit_event
from skilgen.core.runtime_data import prune_runtime_data


LOGGER = logging.getLogger("skilgen.api")
_LOGGING_READY = False
_METRICS_LOCK = threading.Lock()
_METRICS = {
    "requests_total": 0,
    "requests_by_status": {},
    "durations_ms": [],
}


def _ensure_logging() -> None:
    global _LOGGING_READY
    if _LOGGING_READY:
        return
    handler = logging.StreamHandler()

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            payload = {
                "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
                "level": record.levelname.lower(),
                "logger": record.name,
                "message": record.getMessage(),
            }
            if hasattr(record, "event"):
                payload["event"] = record.event
            if hasattr(record, "request_id"):
                payload["request_id"] = record.request_id
            if hasattr(record, "method"):
                payload["method"] = record.method
            if hasattr(record, "path"):
                payload["path"] = record.path
            if hasattr(record, "status"):
                payload["status"] = record.status
            if hasattr(record, "duration_ms"):
                payload["duration_ms"] = record.duration_ms
            if hasattr(record, "remote_addr"):
                payload["remote_addr"] = record.remote_addr
            return json.dumps(payload, sort_keys=True)

    handler.setFormatter(JsonFormatter())
    LOGGER.setLevel(logging.INFO)
    LOGGER.handlers[:] = [handler]
    LOGGER.propagate = False
    _LOGGING_READY = True


def _record_metrics(status_code: int, duration_ms: float) -> None:
    with _METRICS_LOCK:
        _METRICS["requests_total"] += 1
        _METRICS["requests_by_status"][status_code] = _METRICS["requests_by_status"].get(status_code, 0) + 1
        durations = _METRICS["durations_ms"]
        durations.append(duration_ms)
        if len(durations) > 256:
            del durations[:-256]


def _metrics_payload() -> str:
    with _METRICS_LOCK:
        requests_total = int(_METRICS["requests_total"])
        requests_by_status = dict(_METRICS["requests_by_status"])
        durations = list(_METRICS["durations_ms"])
    avg_duration = (sum(durations) / len(durations)) if durations else 0.0
    lines = [
        "# HELP skilgen_http_requests_total Total HTTP requests handled by the API server.",
        "# TYPE skilgen_http_requests_total counter",
        f"skilgen_http_requests_total {requests_total}",
        "# HELP skilgen_http_request_duration_average_ms Average request duration in milliseconds.",
        "# TYPE skilgen_http_request_duration_average_ms gauge",
        f"skilgen_http_request_duration_average_ms {avg_duration:.2f}",
    ]
    for status_code, count in sorted(requests_by_status.items()):
        lines.append(f'skilgen_http_requests_by_status_total{{status="{status_code}"}} {count}')
    return "\n".join(lines) + "\n"


def _json_response(handler: BaseHTTPRequestHandler, status_code: int, payload: dict[str, object], *, request_id: str) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("X-Request-Id", request_id)
    handler.end_headers()
    handler.wfile.write(body)


def _svg_response(handler: BaseHTTPRequestHandler, status_code: int, body: str, *, request_id: str) -> None:
    payload = body.encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "image/svg+xml")
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("X-Request-Id", request_id)
    handler.end_headers()
    handler.wfile.write(payload)


def _text_response(handler: BaseHTTPRequestHandler, status_code: int, body: str, *, content_type: str, request_id: str) -> None:
    payload = body.encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("X-Request-Id", request_id)
    handler.end_headers()
    handler.wfile.write(payload)


def _configured_api_token() -> str | None:
    return os.getenv("SKILGEN_API_TOKEN")


def _max_body_bytes() -> int:
    raw = os.getenv("SKILGEN_API_MAX_BODY_BYTES", "10485760")
    try:
        return max(1024, int(raw))
    except ValueError:
        return 10 * 1024 * 1024


def _allowed_project_roots() -> list[Path]:
    raw = os.getenv("SKILGEN_ALLOWED_PROJECT_ROOTS")
    if not raw:
        return [Path.cwd().resolve()]
    roots: list[Path] = []
    for value in raw.split(","):
        stripped = value.strip()
        if stripped:
            roots.append(Path(stripped).resolve())
    return roots or [Path.cwd().resolve()]


def _resolve_project_root(raw_value: str | None) -> Path:
    candidate = Path(raw_value or ".").resolve()
    for allowed_root in _allowed_project_roots():
        if candidate == allowed_root or allowed_root in candidate.parents:
            return candidate
    raise PermissionError(f"project_root `{candidate}` is outside the configured allowlist")


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    length = int(handler.headers.get("Content-Length", "0"))
    if length > _max_body_bytes():
        raise ValueError("payload_too_large")
    body = handler.rfile.read(length) if length else b"{}"
    return json.loads(body.decode("utf-8") or "{}")


def _require_authorization(handler: BaseHTTPRequestHandler, *, request_id: str) -> bool:
    expected = _configured_api_token()
    if not expected:
        _json_response(handler, 503, {"error": "server_auth_not_configured"}, request_id=request_id)
        return False
    header = handler.headers.get("Authorization", "")
    if not header.startswith("Bearer ") or header.removeprefix("Bearer ").strip() != expected:
        _json_response(handler, 401, {"error": "unauthorized"}, request_id=request_id)
        return False
    return True


class BoundedThreadPoolHTTPServer(HTTPServer):
    def __init__(self, server_address: tuple[str, int], request_handler_class: type[BaseHTTPRequestHandler]) -> None:
        super().__init__(server_address, request_handler_class)
        max_workers = int(os.getenv("SKILGEN_SERVER_MAX_WORKERS", "8"))
        max_queue = int(os.getenv("SKILGEN_SERVER_MAX_QUEUE", "32"))
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="skilgen-api")
        self._request_slots = threading.BoundedSemaphore(max_workers + max_queue)

    def process_request(self, request, client_address) -> None:  # type: ignore[override]
        if not self._request_slots.acquire(blocking=False):
            try:
                request.sendall(
                    b"HTTP/1.1 503 Service Unavailable\r\n"
                    b"Content-Type: application/json\r\n"
                    b"Connection: close\r\n\r\n"
                    b"{\"error\":\"server_busy\"}"
                )
            except OSError:
                pass
            self.shutdown_request(request)
            return
        self._executor.submit(self._process_request_task, request, client_address)

    def _process_request_task(self, request, client_address) -> None:
        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
        finally:
            self._request_slots.release()

    def server_close(self) -> None:
        self._executor.shutdown(wait=True, cancel_futures=True)
        super().server_close()


def create_handler() -> type[BaseHTTPRequestHandler]:
    class SkilgenHandler(BaseHTTPRequestHandler):
        def _finish_request(self, *, status_code: int, request_id: str, project_root: Path | None, start_time: float) -> None:
            duration_ms = round((time.monotonic() - start_time) * 1000, 2)
            _record_metrics(status_code, duration_ms)
            LOGGER.info(
                "request_complete",
                extra={
                    "event": "access",
                    "request_id": request_id,
                    "method": self.command,
                    "path": self.path,
                    "status": status_code,
                    "duration_ms": duration_ms,
                    "remote_addr": self.client_address[0],
                },
            )
            if project_root is not None:
                append_audit_event(
                    project_root,
                    action=f"http_{self.command.lower()}",
                    outcome=str(status_code),
                    source="api",
                    actor=self.client_address[0],
                    request_id=request_id,
                    details={"path": self.path, "status": status_code},
                )

        def _handle_exception(self, exc: Exception, *, request_id: str, project_root: Path | None) -> int:
            if isinstance(exc, PermissionError):
                _json_response(self, 403, {"error": "forbidden", "message": str(exc)}, request_id=request_id)
                return 403
            if isinstance(exc, ValueError) and str(exc) == "payload_too_large":
                _json_response(self, 413, {"error": "payload_too_large"}, request_id=request_id)
                return 413
            if isinstance(exc, json.JSONDecodeError):
                _json_response(self, 400, {"error": "invalid_json"}, request_id=request_id)
                return 400
            LOGGER.exception("request_failed", extra={"event": "request_error", "request_id": request_id, "path": self.path})
            _json_response(self, 500, {"error": "internal_error"}, request_id=request_id)
            return 500

        def _project_root_from_query(self, query: dict[str, list[str]]) -> Path | None:
            if "project_root" not in query:
                return None
            return _resolve_project_root(query.get("project_root", ["."])[0])

        def _project_root_from_data(self, data: dict[str, object]) -> Path | None:
            if "project_root" not in data:
                return None
            return _resolve_project_root(str(data.get("project_root", ".")))

        def do_GET(self) -> None:  # noqa: N802
            _ensure_logging()
            request_id = uuid.uuid4().hex
            start_time = time.monotonic()
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            project_root: Path | None = None
            status_code = 500
            try:
                if parsed.path == "/health":
                    _json_response(self, 200, health_payload(), request_id=request_id)
                    status_code = 200
                    return
                if not _require_authorization(self, request_id=request_id):
                    status_code = 401
                    return
                if parsed.path == "/metrics":
                    _text_response(self, 200, _metrics_payload(), content_type="text/plain; version=0.0.4", request_id=request_id)
                    status_code = 200
                    return
                project_root = self._project_root_from_query(query)
                if project_root is not None:
                    prune_runtime_data(project_root)
                if parsed.path == "/status":
                    _json_response(self, 200, status_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/score":
                    _json_response(
                        self,
                        200,
                        score_payload(
                            project_root or Path("."),
                            query.get("badge_file", [None])[0],
                            history=query.get("history", ["0"])[0] not in {"0", "false", "False", ""},
                            history_limit=int(query.get("history_limit", ["10"])[0]),
                        ),
                        request_id=request_id,
                    )
                    status_code = 200
                    return
                if parsed.path == "/analytics":
                    _json_response(self, 200, analytics_payload(project_root or Path("."), limit=int(query.get("limit", ["10"])[0])), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/badge.svg":
                    _svg_response(self, 200, score_badge_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/doctor":
                    _json_response(self, 200, doctor_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/diff":
                    _json_response(self, 200, diff_payload(project_root or Path("."), query.get("requirements", [None])[0]), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills":
                    _json_response(self, 200, skills_list_payload(project_root or Path("."), query.get("ecosystem", [None])[0], query.get("search", [None])[0]), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/detect":
                    _json_response(self, 200, skills_detect_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/active":
                    _json_response(self, 200, skills_active_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/lock":
                    _json_response(self, 200, skills_lock_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/lock/export":
                    _json_response(self, 200, skills_lock_export_payload(project_root or Path("."), query.get("output_path", [None])[0]), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/policy":
                    _json_response(self, 200, skills_policy_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/skills/rank":
                    _json_response(self, 200, skills_rank_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/enterprise":
                    _json_response(self, 200, enterprise_list_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/connectors":
                    _json_response(self, 200, connectors_list_payload(query.get("system", [None])[0], query.get("search", [None])[0]), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/connectors/recommend":
                    _json_response(self, 200, connectors_recommend_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/connectors/active":
                    _json_response(self, 200, connectors_active_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path.startswith("/skills/"):
                    _json_response(self, 200, skills_show_payload(parsed.path.split("/")[-1], project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/decide":
                    _json_response(self, 200, decision_payload(project_root or Path("."), query.get("requirements", [None])[0]), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/architecture":
                    _json_response(self, 200, architecture_payload(project_root or Path("."), query.get("requirements", [None])[0]), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/dashboard":
                    _json_response(self, 200, dashboard_payload(project_root or Path("."), query.get("requirements", [None])[0]), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/jobs":
                    _json_response(self, 200, jobs_payload(project_root), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path.startswith("/jobs/"):
                    _json_response(self, 200, job_status_payload(parsed.path.split("/")[-1], project_root), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/report":
                    _json_response(self, 200, report_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if parsed.path == "/validate":
                    _json_response(self, 200, validate_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                _json_response(self, 404, {"error": "not_found"}, request_id=request_id)
                status_code = 404
            except Exception as exc:  # noqa: BLE001
                status_code = self._handle_exception(exc, request_id=request_id, project_root=project_root)
            finally:
                self._finish_request(status_code=status_code, request_id=request_id, project_root=project_root, start_time=start_time)

        def do_POST(self) -> None:  # noqa: N802
            _ensure_logging()
            request_id = uuid.uuid4().hex
            start_time = time.monotonic()
            project_root: Path | None = None
            status_code = 500
            try:
                if not _require_authorization(self, request_id=request_id):
                    status_code = 401
                    return
                data = _read_json(self)
                project_root = self._project_root_from_data(data)
                if project_root is not None:
                    prune_runtime_data(project_root)
                if self.path == "/fingerprint":
                    _json_response(self, 200, fingerprint_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/map":
                    _json_response(self, 200, map_payload(project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/analyze":
                    _json_response(self, 200, analyze_payload(project_root or Path("."), str(data["requirements"]) if "requirements" in data else None), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/architecture":
                    _json_response(self, 200, architecture_payload(project_root or Path("."), str(data["requirements"]) if "requirements" in data else None), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/dashboard":
                    _json_response(self, 200, dashboard_payload(project_root or Path("."), str(data["requirements"]) if "requirements" in data else None), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/decide":
                    _json_response(self, 200, decision_payload(project_root or Path("."), str(data["requirements"]) if "requirements" in data else None), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/intent":
                    _json_response(self, 200, intent_payload(str(data["requirements"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/plan":
                    _json_response(self, 200, plan_payload(str(data["requirements"]) if "requirements" in data else None, project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/features":
                    _json_response(self, 200, features_payload(str(data["requirements"]) if "requirements" in data else None, project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/deliver":
                    _json_response(self, 200, deliver_payload(str(data["requirements"]) if "requirements" in data else None, project_root or Path(".")), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/preview":
                    targets = tuple(data.get("targets", ("docs", "skills")))
                    domains = tuple(data.get("domains", ()))
                    _json_response(self, 200, preview_payload(str(data["requirements"]) if "requirements" in data else None, project_root or Path("."), targets=targets, domains=domains), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/install":
                    _json_response(
                        self,
                        200,
                        skills_install_payload(
                            project_root or Path("."),
                            slug=str(data["slug"]) if "slug" in data and data.get("slug") is not None else None,
                            git_url=str(data["git_url"]) if "git_url" in data and data.get("git_url") is not None else None,
                            name=str(data["name"]) if "name" in data and data.get("name") is not None else None,
                            force=bool(data.get("force", False)),
                            ref=str(data["ref"]) if "ref" in data and data.get("ref") is not None else None,
                            active=data.get("active") if isinstance(data.get("active"), bool) else None,
                        ),
                        request_id=request_id,
                    )
                    status_code = 200
                    return
                if self.path == "/skills/import":
                    _json_response(self, 200, skills_import_payload(project_root or Path("."), str(data["slug"]), limit=int(data.get("limit", 5)), active=data.get("active") if isinstance(data.get("active"), bool) else None), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/lock/import":
                    _json_response(self, 200, skills_lock_import_payload(project_root or Path("."), str(data["input_path"]), sync_existing=bool(data.get("sync_existing", False))), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/sync":
                    _json_response(self, 200, skills_sync_payload(project_root or Path("."), str(data["slug"]) if "slug" in data and data.get("slug") is not None else None, all_sources=bool(data.get("all", False))), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/remove":
                    _json_response(self, 200, skills_remove_payload(project_root or Path("."), str(data["slug"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/activate":
                    _json_response(self, 200, skills_activate_payload(project_root or Path("."), str(data["slug"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/skills/deactivate":
                    _json_response(self, 200, skills_deactivate_payload(project_root or Path("."), str(data["slug"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/enterprise/ingest":
                    _json_response(
                        self,
                        200,
                        enterprise_ingest_payload(
                            project_root or Path("."),
                            name=str(data["name"]),
                            path=str(data["path"]) if "path" in data and data.get("path") is not None else None,
                            git_url=str(data["git_url"]) if "git_url" in data and data.get("git_url") is not None else None,
                            url=str(data["url"]) if "url" in data and data.get("url") is not None else None,
                            ref=str(data["ref"]) if "ref" in data and data.get("ref") is not None else None,
                            activate=data.get("activate") if isinstance(data.get("activate"), bool) else None,
                            kind=str(data.get("kind", "enterprise")),
                        ),
                        request_id=request_id,
                    )
                    status_code = 200
                    return
                if self.path == "/enterprise/generate":
                    _json_response(self, 200, enterprise_generate_payload(project_root or Path("."), name=str(data["name"]), source_paths=[str(item) for item in data.get("source_paths", [])], kind=str(data.get("kind", "domain")), activate=bool(data.get("activate", True))), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/connectors/activate":
                    _json_response(self, 200, connectors_activate_payload(project_root or Path("."), str(data["slug"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/connectors/deactivate":
                    _json_response(self, 200, connectors_deactivate_payload(project_root or Path("."), str(data["slug"])), request_id=request_id)
                    status_code = 200
                    return
                if self.path == "/jobs/deliver":
                    _json_response(self, 202, create_deliver_job(str(data["requirements"]) if "requirements" in data else None, project_root or Path(".")), request_id=request_id)
                    status_code = 202
                    return
                if self.path.startswith("/jobs/") and self.path.endswith("/cancel"):
                    parts = self.path.strip("/").split("/")
                    _json_response(self, 200, cancel_job_payload(parts[1], project_root), request_id=request_id)
                    status_code = 200
                    return
                if self.path.startswith("/jobs/") and self.path.endswith("/resume"):
                    parts = self.path.strip("/").split("/")
                    _json_response(self, 202, resume_job_payload(parts[1], project_root), request_id=request_id)
                    status_code = 202
                    return
                _json_response(self, 404, {"error": "not_found"}, request_id=request_id)
                status_code = 404
            except Exception as exc:  # noqa: BLE001
                status_code = self._handle_exception(exc, request_id=request_id, project_root=project_root)
            finally:
                self._finish_request(status_code=status_code, request_id=request_id, project_root=project_root, start_time=start_time)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A003
            return

    return SkilgenHandler


def create_server(host: str = "127.0.0.1", port: int = 8000) -> BoundedThreadPoolHTTPServer:
    _ensure_logging()
    os.environ.setdefault("SKILGEN_REDACT_MODEL_ERRORS", "1")
    for allowed_root in _allowed_project_roots():
        prune_runtime_data(allowed_root)
    return BoundedThreadPoolHTTPServer((host, port), create_handler())


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = create_server(host, port)
    try:
        server.serve_forever()
    finally:
        server.server_close()
