from __future__ import annotations

from contextlib import contextmanager
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.llm_key import decrypt_key, encrypt_key as _encrypt_key, key_hint
from packages.db.models import OrgLLMConfig, Repo


def encrypt_key(raw_key: str) -> bytes:
    return _encrypt_key(raw_key).encode()


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
