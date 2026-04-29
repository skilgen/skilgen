from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class LoginEvent(Base):
    __tablename__ = "login_events"
    __table_args__ = (
        Index("ix_login_events_org_id", "org_id", "created_at"),
        Index("ix_login_events_user_login", "user_login", "created_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("orgs.id", ondelete="SET NULL"), nullable=True)
    user_login: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_email: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
