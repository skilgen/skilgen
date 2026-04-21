from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class ScoreHistory(Base):
    __tablename__ = "score_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"))
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id"))
    score_total: Mapped[int]
    score_groundedness: Mapped[int]
    score_coverage: Mapped[int]
    score_freshness: Mapped[int]
    score_structure: Mapped[int]
    recorded_at: Mapped[datetime] = mapped_column(default=utcnow)
