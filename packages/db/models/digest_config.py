from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.org import Org


class DigestConfig(Base):
    __tablename__ = "digest_configs"
    __table_args__ = (UniqueConstraint("org_id", name="uq_digest_configs_org_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), default="Weekly AI Readiness Digest", nullable=False)
    subject: Mapped[str] = mapped_column(String(255), default="Your Weekly AI Readiness Report", nullable=False)
    frequency: Mapped[str] = mapped_column(String(32), default="weekly", nullable=False)
    recipients: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    widgets: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    layout: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow, nullable=False)

    org: Mapped["Org"] = relationship(back_populates="digest_config")
