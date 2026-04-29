from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class PRReview(Base):
    """A saved PR-level review scan for an organization."""

    __tablename__ = "pr_reviews"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    pr_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    pr_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="complete", nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(128), nullable=True)
    findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skills_checked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lines_scanned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)


class PRReviewFinding(Base):
    """A persisted finding from a PR-level review scan."""

    __tablename__ = "pr_review_findings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    review_id: Mapped[str] = mapped_column(ForeignKey("pr_reviews.id", ondelete="CASCADE"), nullable=False)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str | None] = mapped_column(ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity: Mapped[str] = mapped_column(String(32), default="warning", nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    rule_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
