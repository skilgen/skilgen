from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.dependency import Dependency
    from packages.db.models.repo import Repo


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"))
    trigger: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="queued")
    commit_sha: Mapped[str | None] = mapped_column(String(255), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pr_number: Mapped[int | None] = mapped_column(nullable=True, default=None)
    score_total: Mapped[int | None] = mapped_column(nullable=True)
    score_groundedness: Mapped[int | None] = mapped_column(nullable=True)
    score_coverage: Mapped[int | None] = mapped_column(nullable=True)
    score_freshness: Mapped[int | None] = mapped_column(nullable=True)
    score_structure: Mapped[int | None] = mapped_column(nullable=True)
    domain_count: Mapped[int | None] = mapped_column(nullable=True)
    skill_count: Mapped[int | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    repo: Mapped["Repo"] = relationship(back_populates="runs")
    dependencies: Mapped[list["Dependency"]] = relationship(back_populates="run")
