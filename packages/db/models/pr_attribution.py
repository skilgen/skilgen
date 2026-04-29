from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.pull_request import PullRequest


class PRAttribution(Base):
    __tablename__ = "pr_attributions"
    __table_args__ = (
        CheckConstraint(
            "primary_agent IN ('claude_code', 'codex', 'cursor', 'copilot', 'devin', 'human', 'mixed')",
            name="ck_pr_attributions_primary_agent",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    pr_id: Mapped[str] = mapped_column(ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False)
    primary_agent: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    lines_by_agent: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    lines_by_human: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sessions: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    skills_loaded: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    skills_violated: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    risk_tier: Mapped[str] = mapped_column(String(16), default="green", nullable=False)
    risk_breakdown: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow, nullable=False)

    pull_request: Mapped["PullRequest"] = relationship(back_populates="attribution")
