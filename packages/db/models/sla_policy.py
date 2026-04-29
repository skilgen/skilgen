from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class SLAPolicy(Base):
    __tablename__ = "sla_policies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"), nullable=False)
    repo_id: Mapped[str | None] = mapped_column(ForeignKey("repos.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    coverage_target_pct: Mapped[int] = mapped_column(nullable=False, default=80)
    alert_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    last_checked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
