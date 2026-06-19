from __future__ import annotations

from datetime import datetime

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class HalfLifeCache(Base):
    __tablename__ = "half_life_cache"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    commit_velocity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    predicted_half_life_days: Mapped[float] = mapped_column(Float, default=90.0, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
