from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from skilgen.api.service import (
    analyze_payload,
    cancel_job_payload,
    decision_payload,
    create_deliver_job,
    deliver_payload,
    doctor_payload,
    features_payload,
    fingerprint_payload,
    health_payload,
    intent_payload,
    jobs_payload,
    job_status_payload,
    map_payload,
    plan_payload,
    preview_payload,
    resume_job_payload,
    report_payload,
    skills_activate_payload,
    skills_active_payload,
    skills_deactivate_payload,
    skills_detect_payload,
    skills_install_payload,
    skills_list_payload,
    skills_lock_payload,
    skills_remove_payload,
    skills_show_payload,
    skills_sync_payload,
    status_payload,
    validate_payload,
)


def _json_response(handler: BaseHTTPRequestHandler, status_code: int, payload: dict[str, object]) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    length = int(handler.headers.get("Content-Length", "0"))
    body = handler.rfile.read(length) if length else b"{}"
    return json.loads(body.decode("utf-8") or "{}")


def create_handler() -> type[BaseHTTPRequestHandler]:
    class SkilgenHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            if parsed.path == "/health":
                _json_response(self, 200, health_payload())
                return
            if parsed.path == "/status":
                _json_response(self, 200, status_payload(query.get("project_root", ["."])[0]))
                return
            if parsed.path == "/doctor":
                _json_response(self, 200, doctor_payload(query.get("project_root", ["."])[0]))
                return
            if parsed.path == "/skills":
                _json_response(
                    self,
                    200,
                    skills_list_payload(
                        query.get("project_root", ["."])[0],
                        query.get("ecosystem", [None])[0],
                        query.get("search", [None])[0],
                    ),
                )
                return
            if parsed.path == "/skills/detect":
                _json_response(self, 200, skills_detect_payload(query.get("project_root", ["."])[0]))
                return
            if parsed.path == "/skills/active":
                _json_response(self, 200, skills_active_payload(query.get("project_root", ["."])[0]))
                return
            if parsed.path == "/skills/lock":
                _json_response(self, 200, skills_lock_payload(query.get("project_root", ["."])[0]))
                return
            if parsed.path.startswith("/skills/"):
                _json_response(self, 200, skills_show_payload(parsed.path.split("/")[-1], query.get("project_root", ["."])[0]))
                return
            if parsed.path == "/decide":
                _json_response(
                    self,
                    200,
                    decision_payload(query.get("project_root", ["."])[0], query.get("requirements", [None])[0]),
                )
                return
            if parsed.path == "/jobs":
                _json_response(self, 200, jobs_payload(query.get("project_root", [None])[0]))
                return
            if parsed.path.startswith("/jobs/"):
                _json_response(self, 200, job_status_payload(parsed.path.split("/")[-1], query.get("project_root", [None])[0]))
                return
            if parsed.path == "/report":
                _json_response(self, 200, report_payload(query.get("project_root", ["."])[0]))
                return
            if parsed.path == "/validate":
                _json_response(self, 200, validate_payload(query.get("project_root", ["."])[0]))
                return
            _json_response(self, 404, {"error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802
            data = _read_json(self)
            if self.path == "/fingerprint":
                _json_response(self, 200, fingerprint_payload(str(data.get("project_root", "."))))
                return
            if self.path == "/map":
                _json_response(self, 200, map_payload(str(data.get("project_root", "."))))
                return
            if self.path == "/analyze":
                _json_response(
                    self,
                    200,
                    analyze_payload(str(data.get("project_root", ".")), str(data["requirements"]) if "requirements" in data else None),
                )
                return
            if self.path == "/decide":
                _json_response(
                    self,
                    200,
                    decision_payload(str(data.get("project_root", ".")), str(data["requirements"]) if "requirements" in data else None),
                )
                return
            if self.path == "/intent":
                _json_response(self, 200, intent_payload(str(data["requirements"])))
                return
            if self.path == "/plan":
                _json_response(self, 200, plan_payload(str(data["requirements"]) if "requirements" in data else None, str(data.get("project_root", "."))))
                return
            if self.path == "/features":
                _json_response(self, 200, features_payload(str(data["requirements"]) if "requirements" in data else None, str(data.get("project_root", "."))))
                return
            if self.path == "/deliver":
                _json_response(self, 200, deliver_payload(str(data["requirements"]) if "requirements" in data else None, str(data.get("project_root", "."))))
                return
            if self.path == "/preview":
                targets = tuple(data.get("targets", ("docs", "skills")))
                domains = tuple(data.get("domains", ()))
                _json_response(
                    self,
                    200,
                    preview_payload(
                        str(data["requirements"]) if "requirements" in data else None,
                        str(data.get("project_root", ".")),
                        targets=targets,
                        domains=domains,
                    ),
                )
                return
            if self.path == "/skills/install":
                _json_response(
                    self,
                    200,
                    skills_install_payload(
                        str(data.get("project_root", ".")),
                        slug=str(data["slug"]) if "slug" in data and data.get("slug") is not None else None,
                        git_url=str(data["git_url"]) if "git_url" in data and data.get("git_url") is not None else None,
                        name=str(data["name"]) if "name" in data and data.get("name") is not None else None,
                        force=bool(data.get("force", False)),
                        ref=str(data["ref"]) if "ref" in data and data.get("ref") is not None else None,
                        active=data.get("active") if isinstance(data.get("active"), bool) else None,
                    ),
                )
                return
            if self.path == "/skills/sync":
                _json_response(
                    self,
                    200,
                    skills_sync_payload(
                        str(data.get("project_root", ".")),
                        str(data["slug"]) if "slug" in data and data.get("slug") is not None else None,
                        all_sources=bool(data.get("all", False)),
                    ),
                )
                return
            if self.path == "/skills/remove":
                _json_response(self, 200, skills_remove_payload(str(data.get("project_root", ".")), str(data["slug"])))
                return
            if self.path == "/skills/activate":
                _json_response(self, 200, skills_activate_payload(str(data.get("project_root", ".")), str(data["slug"])))
                return
            if self.path == "/skills/deactivate":
                _json_response(self, 200, skills_deactivate_payload(str(data.get("project_root", ".")), str(data["slug"])))
                return
            if self.path == "/jobs/deliver":
                _json_response(self, 202, create_deliver_job(str(data["requirements"]) if "requirements" in data else None, str(data.get("project_root", "."))))
                return
            if self.path.startswith("/jobs/") and self.path.endswith("/cancel"):
                parts = self.path.strip("/").split("/")
                _json_response(self, 200, cancel_job_payload(parts[1], str(data.get("project_root", "."))))
                return
            if self.path.startswith("/jobs/") and self.path.endswith("/resume"):
                parts = self.path.strip("/").split("/")
                _json_response(self, 202, resume_job_payload(parts[1], str(data.get("project_root", "."))))
                return
            _json_response(self, 404, {"error": "not_found"})

        def log_message(self, format: str, *args: object) -> None:  # noqa: A003
            return

    return SkilgenHandler


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), create_handler())


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = create_server(host, port)
    try:
        server.serve_forever()
    finally:
        server.server_close()
