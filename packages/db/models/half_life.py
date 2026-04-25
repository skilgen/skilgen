from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class SkillHalfLife(Base):
    __tablename__ = "skill_half_lives"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"), unique=True, nullable=False)
    org_id: Mapped[str] = mapped_column(String, nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    commits_30d: Mapped[int] = mapped_column(default=0)
    commits_60d: Mapped[int] = mapped_column(default=0)
    commits_90d: Mapped[int] = mapped_column(default=0)
    file_churn_30d: Mapped[int] = mapped_column(default=0)
    predicted_decay_days: Mapped[float] = mapped_column(default=90.0)
    predicted_decay_date: Mapped[datetime | None] = mapped_column(nullable=True)
    decay_confidence: Mapped[float] = mapped_column(default=0.3)
    last_actual_decay_date: Mapped[datetime | None] = mapped_column(nullable=True)
    prediction_error_days: Mapped[float | None] = mapped_column(nullable=True)
    regeneration_buffer_hours: Mapped[int] = mapped_column(default=24)
    regen_queued: Mapped[bool] = mapped_column(default=False)
    regen_queued_at: Mapped[datetime | None] = mapped_column(nullable=True)
    computed_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
