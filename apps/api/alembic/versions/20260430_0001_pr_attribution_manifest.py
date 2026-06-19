"""add signed provenance manifests to PR attributions

Revision ID: 20260430_0001
Revises: 20260429_0002
Create Date: 2026-04-30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260430_0001"
down_revision = "20260429_0002"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in set(inspector.get_table_names()):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    json_type = postgresql.JSONB(astext_type=sa.Text()) if bind.dialect.name == "postgresql" else sa.JSON()

    if not _has_column("pr_attributions", "signed_manifest"):
        op.add_column("pr_attributions", sa.Column("signed_manifest", json_type, nullable=True))
    if not _has_column("pr_attributions", "manifest_signed_at"):
        op.add_column("pr_attributions", sa.Column("manifest_signed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    if _has_column("pr_attributions", "manifest_signed_at"):
        op.drop_column("pr_attributions", "manifest_signed_at")
    if _has_column("pr_attributions", "signed_manifest"):
        op.drop_column("pr_attributions", "signed_manifest")
