from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    DEBUG: bool = False

    GITHUB_APP_ID: str = ""
    GITHUB_APP_PRIVATE_KEY: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""

    WORKOS_API_KEY: str = ""
    WORKOS_CLIENT_ID: str = ""

    OIDC_ISSUER_URL: str = ""
    OIDC_AUDIENCE: str = ""
    OIDC_JWKS_URI: str = ""

    REDIS_URL: str = "redis://localhost:6379/0"

    QSTASH_TOKEN: str = ""
    QSTASH_CURRENT_SIGNING_KEY: str = ""
    QSTASH_NEXT_SIGNING_KEY: str = ""

    DEPLOYMENT_MODE: str = "saas"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
