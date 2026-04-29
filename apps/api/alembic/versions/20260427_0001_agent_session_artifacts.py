"""add_agent_session_artifacts

Revision ID: 20260427_0001
Revises: 20260426_0007_debt_dependency
Create Date: 2026-04-27 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260427_0001"
down_revision: Union[str, Sequence[str], None] = "20260426_0007_debt_dependency"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _has_column("agent_sessions", "produced_artifacts"):
        op.add_column(
            "agent_sessions",
            sa.Column("produced_artifacts", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        )
    if not _has_column("agent_sessions", "produced_file_hashes"):
        op.add_column(
            "agent_sessions",
            sa.Column("produced_file_hashes", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        )
    if not _has_column("agent_sessions", "closed_at"):
        op.add_column("agent_sessions", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))
    if not _has_column("agent_sessions", "inactivity_timeout_minutes"):
        op.add_column(
            "agent_sessions",
            sa.Column("inactivity_timeout_minutes", sa.Integer(), server_default="30", nullable=False),
        )
    if not _has_column("agent_sessions", "last_artifact_at"):
        op.add_column("agent_sessions", sa.Column("last_artifact_at", sa.DateTime(timezone=True), nullable=True))
    if not _has_index("agent_sessions", "ix_agent_sessions_open_artifact_lookup"):
        op.create_index(
            "ix_agent_sessions_open_artifact_lookup",
            "agent_sessions",
            ["org_id", "repo_id", "agent_runtime", "closed_at", "last_artifact_at"],
        )


def downgrade() -> None:
    if _has_index("agent_sessions", "ix_agent_sessions_open_artifact_lookup"):
        op.drop_index("ix_agent_sessions_open_artifact_lookup", table_name="agent_sessions")
    for column_name in (
        "last_artifact_at",
        "inactivity_timeout_minutes",
        "closed_at",
        "produced_file_hashes",
        "produced_artifacts",
    ):
        if _has_column("agent_sessions", column_name):
            op.drop_column("agent_sessions", column_name)
