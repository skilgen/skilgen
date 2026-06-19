from __future__ import annotations

from datetime import datetime

from sqlalchemy import Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class AuditHashChain(Base):
    __tablename__ = "audit_hash_chain"
    __table_args__ = (
        UniqueConstraint("org_id", "event_id", name="uq_audit_hash_chain_org_event"),
        UniqueConstraint("org_id", "sequence", name="uq_audit_hash_chain_org_sequence"),
        Index("ix_audit_hash_chain_org_sequence", "org_id", "sequence"),
        Index("ix_audit_hash_chain_org_root", "org_id", "root_hash"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(String, nullable=False)
    event_id: Mapped[str] = mapped_column(String, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    root_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    merkle_proof: Mapped[list[dict[str, str]]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)


class AuditWormRoot(Base):
    __tablename__ = "audit_worm_roots"
    __table_args__ = (
        UniqueConstraint("org_id", "root_hash", name="uq_audit_worm_roots_org_root"),
        Index("ix_audit_worm_roots_org_created_at", "org_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(String, nullable=False)
    root_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    start_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    end_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_count: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(32), nullable=False, default="s3_object_lock")
    object_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    cadence: Mapped[str] = mapped_column(String(32), nullable=False, default="daily")
    merkle_proof: Mapped[list[dict[str, str]]] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
