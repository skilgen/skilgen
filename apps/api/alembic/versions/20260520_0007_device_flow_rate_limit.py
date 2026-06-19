"""device flow ip rate limit metadata

Revision ID: 20260520_0007
Revises: 20260520_0006
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260520_0007"
down_revision = "20260520_0006"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _has_index(table_name: str, index_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return index_name in {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    if _has_table("device_authorizations") and not _has_column("device_authorizations", "client_ip"):
        op.add_column("device_authorizations", sa.Column("client_ip", sa.String(length=64), nullable=True))
    if not _has_index("device_authorizations", "ix_device_authorizations_client_ip"):
        op.create_index("ix_device_authorizations_client_ip", "device_authorizations", ["client_ip"])


def downgrade() -> None:
    if _has_index("device_authorizations", "ix_device_authorizations_client_ip"):
        op.drop_index("ix_device_authorizations_client_ip", table_name="device_authorizations")
    if _has_column("device_authorizations", "client_ip"):
        op.drop_column("device_authorizations", "client_ip")
