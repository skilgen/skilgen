from __future__ import annotations

import logging
from contextlib import contextmanager
import os

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.config import settings
from packages.db.models import OrgLLMConfig, Repo


LOGGER = logging.getLogger(__name__)
_EPHEMERAL_KEY: bytes | None = None


def _get_fernet_key() -> bytes:
    global _EPHEMERAL_KEY
    configured = settings.SKILLAYER_ENCRYPTION_KEY.strip()
    if configured:
        return configured.encode()
    if _EPHEMERAL_KEY is None:
        _EPHEMERAL_KEY = Fernet.generate_key()
        LOGGER.warning("WARNING: Using ephemeral encryption key. Set SKILLAYER_ENCRYPTION_KEY in prod.")
    return _EPHEMERAL_KEY


def encrypt_key(api_key: str) -> bytes:
    return Fernet(_get_fernet_key()).encrypt(api_key.encode())


def decrypt_key(encrypted: bytes) -> str:
    return Fernet(_get_fernet_key()).decrypt(encrypted).decode()


def key_hint(api_key: str) -> str:
    return "..." + api_key[-4:] if len(api_key) >= 4 else "****"


async def get_repo_llm_config(db: AsyncSession, repo_id: str) -> OrgLLMConfig | None:
    org_id = (
        await db.execute(select(Repo.org_id).where(Repo.id == repo_id))
    ).scalar_one_or_none()
    if not org_id:
        return None
    return (
        await db.execute(select(OrgLLMConfig).where(OrgLLMConfig.org_id == org_id))
    ).scalar_one_or_none()


@contextmanager
def configured_llm_environment(config: OrgLLMConfig | None):
    """Temporarily expose BYOK LLM settings to in-process Skilgen code."""
    if config is None or not config.is_configured or config.provider == "skillayer":
        yield
        return
    keys = {
        "SKILLGEN_LLM_PROVIDER": config.provider,
        "SKILLGEN_LLM_MODEL": config.model or "",
        "SKILLGEN_LLM_ENDPOINT": config.endpoint_url or "",
    }
    if config.api_key_encrypted:
        api_key = decrypt_key(config.api_key_encrypted)
        if config.provider == "anthropic":
            keys["ANTHROPIC_API_KEY"] = api_key
        elif config.provider in {"openai", "azure_openai", "custom"}:
            keys["OPENAI_API_KEY"] = api_key
    old = {key: os.environ.get(key) for key in keys}
    try:
        for key, value in keys.items():
            if value:
                os.environ[key] = value
        yield
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
