from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.org import Org


class SourceConnection(Base):
    __tablename__ = "source_connections"
    __table_args__ = (UniqueConstraint("org_id", "source_type", name="uq_source_connections_org_source_type"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"), index=True)
    source_type: Mapped[str] = mapped_column(String(80), index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="connected")
    encrypted_params: Mapped[str] = mapped_column(Text)
    params_hint: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True, default=dict)
    last_tested_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_connected_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    org: Mapped["Org"] = relationship(back_populates="source_connections")
