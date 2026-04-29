from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class CoverageGap(Base):
    __tablename__ = "coverage_gaps"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"), index=True)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), index=True)
    domain: Mapped[str] = mapped_column(String(80), index=True)
    gap_type: Mapped[str] = mapped_column(String(32), default="missing")
    status: Mapped[str] = mapped_column(String(32), default="open", index=True)
    skill_id: Mapped[str | None] = mapped_column(ForeignKey("skills.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)
