from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.repo import Repo


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"))
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id"))
    domain: Mapped[str] = mapped_column(String(255))
    skill_path: Mapped[str] = mapped_column(String(512))
    score_total: Mapped[int] = mapped_column(default=0)
    score_groundedness: Mapped[int] = mapped_column(default=0)
    score_coverage: Mapped[int] = mapped_column(default=0)
    score_freshness: Mapped[int] = mapped_column(default=0)
    score_structure: Mapped[int] = mapped_column(default=0)
    is_stale: Mapped[bool] = mapped_column(default=False)
    load_count_30d: Mapped[int] = mapped_column(default=0)
    last_loaded_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    repo: Mapped["Repo"] = relationship(back_populates="skills")
