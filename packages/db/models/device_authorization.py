from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class DeviceAuthorization(Base):
    __tablename__ = "device_authorizations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    device_code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    user_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("orgs.id"), nullable=True, index=True)
    user_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    api_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_root: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    repo_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    repo_full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(nullable=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    last_polled_at: Mapped[datetime | None] = mapped_column(nullable=True)
