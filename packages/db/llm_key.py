from __future__ import annotations

import base64
import hashlib
import logging
import os

from cryptography.fernet import Fernet, InvalidToken


LOGGER = logging.getLogger(__name__)
_FALLBACK_PREFIX = b"b64:"
_warned_fallback = False


def _warn_fallback() -> None:
    global _warned_fallback
    if not _warned_fallback:
        LOGGER.warning("LLM_ENCRYPTION_SECRET is not set; using deterministic base64 fallback for LLM keys.")
        _warned_fallback = True


def _fernet() -> Fernet | None:
    secret = os.environ.get("LLM_ENCRYPTION_SECRET", "").strip()
    if not secret:
        return None
    try:
        return Fernet(secret.encode())
    except ValueError:
        key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
        return Fernet(key)


def encrypt_key(raw_key: str) -> str:
    fernet = _fernet()
    if fernet is not None:
        return fernet.encrypt(raw_key.encode()).decode()
    _warn_fallback()
    return (_FALLBACK_PREFIX + base64.urlsafe_b64encode(raw_key.encode())).decode()


def decrypt_key(encrypted: bytes | str) -> str:
    token = encrypted.encode() if isinstance(encrypted, str) else encrypted
    if token.startswith(_FALLBACK_PREFIX):
        _warn_fallback()
        return base64.urlsafe_b64decode(token[len(_FALLBACK_PREFIX):]).decode()
    fernet = _fernet()
    if fernet is None:
        _warn_fallback()
        try:
            return base64.urlsafe_b64decode(token).decode()
        except Exception:
            return token.decode()
    try:
        return fernet.decrypt(token).decode()
    except InvalidToken:
        try:
            return base64.urlsafe_b64decode(token).decode()
        except Exception:
            raise


def key_hint(api_key: str) -> str:
    return "..." + api_key[-4:] if len(api_key) >= 4 else "****"
