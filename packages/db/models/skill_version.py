from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.skill import Skill


class SkillVersion(Base):
    __tablename__ = "skill_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"))
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id"))
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"))
    domain: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    version_number: Mapped[int] = mapped_column(default=1)
    is_latest: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    skill: Mapped["Skill"] = relationship(back_populates="versions")
