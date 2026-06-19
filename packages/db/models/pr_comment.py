from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.pull_request import PullRequest


class PRComment(Base):
    __tablename__ = "pr_comments"
    __table_args__ = (
        Index("ix_pr_comments_pr_violation_hash", "pr_id", "violation_hash", unique=True),
        Index("ix_pr_comments_github_comment_id", "github_comment_id"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    pr_id: Mapped[str] = mapped_column(ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False)
    github_comment_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    violation_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow, nullable=False)

    pull_request: Mapped["PullRequest"] = relationship()
