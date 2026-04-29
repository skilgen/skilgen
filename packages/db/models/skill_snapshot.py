from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.repo import Repo
    from packages.db.models.skill import Skill


class SkillSnapshot(Base):
    __tablename__ = "skill_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    snapshot_type: Mapped[str] = mapped_column(String, default="auto", nullable=False)
    label: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    score_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_groundedness: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_coverage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_freshness: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_structure: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)

    skill: Mapped["Skill"] = relationship()
    repo: Mapped["Repo"] = relationship()
