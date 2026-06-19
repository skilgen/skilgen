from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.org import Org


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("org_id", "name", name="uq_roles_org_name"),
        Index("ix_roles_org_id", "org_id"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    permissions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    org: Mapped["Org"] = relationship(back_populates="roles")
    bindings: Mapped[list["RoleBinding"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class RoleBinding(Base):
    __tablename__ = "role_bindings"
    __table_args__ = (
        Index("ix_role_bindings_org_principal", "org_id", "principal_type", "principal_id"),
        Index("ix_role_bindings_role_id", "role_id"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    principal_type: Mapped[str] = mapped_column(String(32), nullable=False)
    principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    scope_expression: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    org: Mapped["Org"] = relationship(back_populates="role_bindings")
    role: Mapped["Role"] = relationship(back_populates="bindings")
