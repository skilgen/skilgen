from __future__ import annotations

import base64
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _int_to_base64url(value: int) -> str:
    length = max(1, (value.bit_length() + 7) // 8)
    return _base64url_encode(value.to_bytes(length, "big"))


def generate_rsa_signing_material(*, kid: str = "test-key") -> tuple[rsa.RSAPrivateKey, dict[str, Any]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()
    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": kid,
                "n": _int_to_base64url(public_numbers.n),
                "e": _int_to_base64url(public_numbers.e),
            }
        ]
    }
    return private_key, jwks


def mint_rs256_token(
    private_key: rsa.RSAPrivateKey,
    *,
    kid: str,
    principal: str,
    scope: str,
    ttl_seconds: float = 300,
    expires_at: float | int | None = None,
    issued_at: float | int | None = None,
    not_before: float | int | None = None,
    allowed_project_roots: list[str | Path] | None = None,
    tenant: str | None = None,
    issuer: str | None = None,
    audience: str | list[str] | None = None,
    allow_insecure_transport: bool = False,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    issued_at_value = int(issued_at if issued_at is not None else time.time())
    expires_at_value = int(expires_at if expires_at is not None else issued_at_value + ttl_seconds)
    payload: dict[str, Any] = {
        "sub": principal,
        "scope": scope,
        "iat": issued_at_value,
        "exp": expires_at_value,
    }
    if not_before is not None:
        payload["nbf"] = int(not_before)
    if allowed_project_roots:
        payload["roots"] = [str(Path(item).resolve()) for item in allowed_project_roots]
    if tenant:
        payload["tenant"] = tenant
    if issuer:
        payload["iss"] = issuer
    if audience:
        payload["aud"] = audience
    if allow_insecure_transport:
        payload["allow_insecure_transport"] = True
    if extra_claims:
        payload.update(extra_claims)
    header = {"alg": "RS256", "typ": "JWT", "kid": kid}
    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}"


class LocalOidcServer:
    def __init__(self, *, jwks: dict[str, Any], issuer_path: str = "/issuer") -> None:
        self._jwks = jwks
        self._issuer_path = "/" + issuer_path.strip("/")
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.issuer: str | None = None
        self.jwks_url: str | None = None

    def __enter__(self) -> LocalOidcServer:
        issuer_path = self._issuer_path

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                if self.path == f"{issuer_path}/.well-known/openid-configuration":
                    payload = {
                        "issuer": self.server.issuer,  # type: ignore[attr-defined]
                        "jwks_uri": self.server.jwks_url,  # type: ignore[attr-defined]
                    }
                    body = json.dumps(payload).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                if self.path == f"{issuer_path}/jwks.json":
                    body = json.dumps(self.server.jwks).encode("utf-8")  # type: ignore[attr-defined]
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                self.send_response(404)
                self.end_headers()

            def log_message(self, format: str, *args: object) -> None:  # noqa: A003
                return

        self._server = HTTPServer(("127.0.0.1", 0), Handler)
        host, port = self._server.server_address
        self.issuer = f"http://{host}:{port}{issuer_path}"
        self.jwks_url = f"http://{host}:{port}{issuer_path}/jwks.json"
        self._server.issuer = self.issuer  # type: ignore[attr-defined]
        self._server.jwks_url = self.jwks_url  # type: ignore[attr-defined]
        self._server.jwks = self._jwks  # type: ignore[attr-defined]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)
