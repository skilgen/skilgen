from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.pr_attribution import PRAttribution
    from packages.db.models.repo import Repo


class PullRequest(Base):
    __tablename__ = "pull_requests"
    __table_args__ = (
        CheckConstraint("author_type IN ('User', 'Bot', 'App')", name="ck_pull_requests_author_type"),
        CheckConstraint("state IN ('open', 'closed', 'merged')", name="ck_pull_requests_state"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    github_pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    author_login: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    head_sha: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_sha: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str | None] = mapped_column(String(16), nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(nullable=True)
    merged_at: Mapped[datetime | None] = mapped_column(nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    additions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deletions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    changed_files: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow, nullable=False)

    repo: Mapped["Repo"] = relationship(back_populates="pull_requests")
    commits: Mapped[list["Commit"]] = relationship(back_populates="pull_request")
    attribution: Mapped["PRAttribution | None"] = relationship(back_populates="pull_request", uselist=False)


class Commit(Base):
    __tablename__ = "commits"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    sha: Mapped[str] = mapped_column(Text, nullable=False)
    author_login: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_email: Mapped[str | None] = mapped_column(Text, nullable=True)
    committer_login: Mapped[str | None] = mapped_column(Text, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    authored_at: Mapped[datetime | None] = mapped_column(nullable=True)
    committed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    additions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deletions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pr_id: Mapped[str | None] = mapped_column(ForeignKey("pull_requests.id", ondelete="SET NULL"), nullable=True)
    raw: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow, nullable=False)

    repo: Mapped["Repo"] = relationship(back_populates="commits")
    pull_request: Mapped["PullRequest | None"] = relationship(back_populates="commits")
