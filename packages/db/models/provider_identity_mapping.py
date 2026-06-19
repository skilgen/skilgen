from __future__ import annotations

from datetime import datetime

from sqlalchemy import Float, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class ProviderIdentityMapping(Base):
    __tablename__ = "provider_identity_mappings"
    __table_args__ = (
        UniqueConstraint("org_id", "provider", "provider_user_id", name="uq_provider_identity_user_id"),
        Index("ix_provider_identity_mappings_org_provider", "org_id", "provider"),
        Index("ix_provider_identity_mappings_org_email", "org_id", "canonical_email"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    canonical_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github_login: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sso_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_actor_login: Mapped[str | None] = mapped_column(String(255), nullable=True)
    local_identity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    match_method: Mapped[str] = mapped_column(String(64), default="admin", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="mapped", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow, nullable=False)
