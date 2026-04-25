from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class ReviewRun(Base):
    """One skill-aware code review scan against a pasted diff."""

    __tablename__ = "review_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    pr_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skills_checked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lines_scanned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
