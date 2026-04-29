from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid


class CrossRepoOpportunity(Base):
    __tablename__ = "cross_repo_opportunities"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    source_skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    target_repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)
