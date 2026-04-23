"""Database model for dependency risk findings captured during analysis runs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.analysis_run import AnalysisRun
    from packages.db.models.repo import Repo


class Dependency(Base):
    """Persisted dependency risk finding for a repository analysis run."""

    __tablename__ = "dependencies"
    __table_args__ = (
        Index("ix_dependencies_repo_id", "repo_id"),
        Index("ix_dependencies_run_id", "run_id"),
        Index("ix_dependencies_risk_level", "risk_level"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ecosystem: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)
    cves: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    latest_version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    license: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)

    repo: Mapped["Repo"] = relationship(back_populates="dependencies")
    run: Mapped["AnalysisRun"] = relationship(back_populates="dependencies")
