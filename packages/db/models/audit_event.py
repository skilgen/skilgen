from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_events_org_created_at", "org_id", "created_at"),
        Index("ix_audit_events_org_event_type_created_at", "org_id", "event_type", "created_at"),
        Index("ix_audit_events_org_repo_created_at", "org_id", "repo_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(String, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_login: Mapped[str | None] = mapped_column(String(128), nullable=True)
    actor_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    repo_id: Mapped[str | None] = mapped_column(String, nullable=True)
    repo_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    skill_id: Mapped[str | None] = mapped_column(String, nullable=True)
    skill_domain: Mapped[str | None] = mapped_column(String(256), nullable=True)
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String, nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(String(512), nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="info")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
