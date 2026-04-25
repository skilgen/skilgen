from __future__ import annotations

from datetime import datetime

from sqlalchemy import LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class OrgLLMConfig(Base):
    __tablename__ = "org_llm_configs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, default="skillayer")
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    endpoint_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    api_key_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    api_key_hint: Mapped[str | None] = mapped_column(String(16), nullable=True)
    azure_deployment: Mapped[str | None] = mapped_column(String(128), nullable=True)
    azure_api_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_configured: Mapped[bool] = mapped_column(nullable=False, default=False)
    last_tested_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_test_ok: Mapped[bool | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
