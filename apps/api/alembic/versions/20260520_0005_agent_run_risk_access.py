"""persist run-level risk/access/compliance fields for indexed run detail

Revision ID: 20260520_0005
Revises: 20260520_0002
Create Date: 2026-05-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260520_0005"
down_revision = "20260520_0002"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _policy_violations_type() -> sa.types.TypeEngine:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        from sqlalchemy.dialects import postgresql

        return postgresql.JSONB()
    return sa.JSON()


def _json_empty_array_default() -> sa.text:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return sa.text("'[]'::jsonb")
    return sa.text("'[]'")


def upgrade() -> None:
    if not _has_table("agent_sessions"):
        return

    defaults = {
        "risk_score": sa.text("0"),
        "risk_level": sa.text("'unknown'"),
        "compliance_status": sa.text("'unknown'"),
        "full_access": sa.text("false"),
        "external_api_call_count": sa.text("0"),
        "command_count": sa.text("0"),
        "mcp_tools_count": sa.text("0"),
        "file_targets_count": sa.text("0"),
    }

    if not _has_column("agent_sessions", "risk_score"):
        op.add_column("agent_sessions", sa.Column("risk_score", sa.Integer(), nullable=False, server_default=defaults["risk_score"]))
    if not _has_column("agent_sessions", "risk_level"):
        op.add_column("agent_sessions", sa.Column("risk_level", sa.String(length=16), nullable=False, server_default=defaults["risk_level"]))
    if not _has_column("agent_sessions", "compliance_status"):
        op.add_column(
            "agent_sessions",
            sa.Column("compliance_status", sa.String(length=16), nullable=False, server_default=defaults["compliance_status"]),
        )
    if not _has_column("agent_sessions", "permission_profile"):
        op.add_column("agent_sessions", sa.Column("permission_profile", sa.String(length=64), nullable=True))
    if not _has_column("agent_sessions", "approval_policy"):
        op.add_column("agent_sessions", sa.Column("approval_policy", sa.String(length=64), nullable=True))
    if not _has_column("agent_sessions", "sandbox_policy"):
        op.add_column("agent_sessions", sa.Column("sandbox_policy", sa.String(length=64), nullable=True))
    if not _has_column("agent_sessions", "access_scope"):
        op.add_column("agent_sessions", sa.Column("access_scope", sa.String(length=64), nullable=True))
    if not _has_column("agent_sessions", "full_access"):
        op.add_column("agent_sessions", sa.Column("full_access", sa.Boolean(), nullable=False, server_default=defaults["full_access"]))
    if not _has_column("agent_sessions", "external_api_call_count"):
        op.add_column(
            "agent_sessions",
            sa.Column("external_api_call_count", sa.Integer(), nullable=False, server_default=defaults["external_api_call_count"]),
        )
    if not _has_column("agent_sessions", "command_count"):
        op.add_column("agent_sessions", sa.Column("command_count", sa.Integer(), nullable=False, server_default=defaults["command_count"]))
    if not _has_column("agent_sessions", "mcp_tools_count"):
        op.add_column("agent_sessions", sa.Column("mcp_tools_count", sa.Integer(), nullable=False, server_default=defaults["mcp_tools_count"]))
    if not _has_column("agent_sessions", "file_targets_count"):
        op.add_column("agent_sessions", sa.Column("file_targets_count", sa.Integer(), nullable=False, server_default=defaults["file_targets_count"]))
    if not _has_column("agent_sessions", "policy_violations"):
        op.add_column(
            "agent_sessions",
            sa.Column("policy_violations", _policy_violations_type(), nullable=False, server_default=_json_empty_array_default()),
        )


def downgrade() -> None:
    if not _has_table("agent_sessions"):
        return

    for column in (
        "policy_violations",
        "file_targets_count",
        "mcp_tools_count",
        "command_count",
        "external_api_call_count",
        "full_access",
        "access_scope",
        "sandbox_policy",
        "approval_policy",
        "permission_profile",
        "compliance_status",
        "risk_level",
        "risk_score",
    ):
        if _has_column("agent_sessions", column):
            op.drop_column("agent_sessions", column)

