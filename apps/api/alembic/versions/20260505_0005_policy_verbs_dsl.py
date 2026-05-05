"""add v8 policy decision verbs and DSL metadata

Revision ID: 20260505_0005
Revises: 20260505_0004
Create Date: 2026-05-05
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260505_0005"
down_revision = "20260505_0004"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if not _has_table("org_policies"):
        return
    if not _has_column("org_policies", "decision"):
        op.add_column("org_policies", sa.Column("decision", sa.String(length=32), server_default="log_only", nullable=False))
    if not _has_column("org_policies", "deprecated_decision"):
        op.add_column("org_policies", sa.Column("deprecated_decision", sa.String(length=32), nullable=True))
    if not _has_column("org_policies", "dsl_yaml"):
        op.add_column("org_policies", sa.Column("dsl_yaml", sa.Text(), nullable=True))
    if not _has_column("org_policies", "dsl_version"):
        op.add_column("org_policies", sa.Column("dsl_version", sa.Integer(), server_default="1", nullable=False))
    if not _has_column("org_policies", "policy_pack"):
        op.add_column("org_policies", sa.Column("policy_pack", sa.String(length=64), nullable=True))
    _map_legacy_verbs_forward()
    _create_policy_violations_view()


def downgrade() -> None:
    if not _has_table("org_policies"):
        return
    _drop_policy_violations_view()
    _map_legacy_verbs_backward()
    for column_name in ("policy_pack", "dsl_version", "dsl_yaml", "deprecated_decision", "decision"):
        if _has_column("org_policies", column_name):
            op.drop_column("org_policies", column_name)


def _map_legacy_verbs_forward() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(
            sa.text(
                """
                UPDATE org_policies
                SET
                  deprecated_decision = CASE
                    WHEN rule_config->>'decision' IN ('block', 'warn', 'log') THEN rule_config->>'decision'
                    WHEN rule_config->>'action' IN ('block', 'warn', 'log') THEN rule_config->>'action'
                    ELSE deprecated_decision
                  END,
                  decision = CASE
                    WHEN rule_config->>'decision' = 'block' OR rule_config->>'action' = 'block' THEN 'deny'
                    WHEN rule_config->>'decision' = 'warn' OR rule_config->>'action' = 'warn' THEN 'require_approval'
                    WHEN rule_config->>'decision' = 'log' OR rule_config->>'action' = 'log' THEN 'log_only'
                    WHEN rule_config->>'decision' IN ('allow', 'deny', 'require_approval', 'log_only', 'redact', 'route_to_dlp') THEN rule_config->>'decision'
                    ELSE decision
                  END
                """
            )
        )
    else:
        bind.execute(
            sa.text(
                """
                UPDATE org_policies
                SET decision = CASE
                  WHEN decision IN ('block', 'deny') THEN 'deny'
                  WHEN decision IN ('warn', 'require_approval') THEN 'require_approval'
                  WHEN decision IN ('log', 'log_only') THEN 'log_only'
                  WHEN decision IN ('allow', 'redact', 'route_to_dlp') THEN decision
                  ELSE 'log_only'
                END
                """
            )
        )


def _map_legacy_verbs_backward() -> None:
    if not _has_column("org_policies", "decision"):
        return
    op.get_bind().execute(
        sa.text(
            """
            UPDATE org_policies
            SET decision = CASE
              WHEN decision = 'deny' THEN 'block'
              WHEN decision = 'require_approval' THEN 'warn'
              WHEN decision = 'log_only' THEN 'log'
              WHEN decision = 'allow' THEN 'log'
              WHEN decision = 'redact' THEN 'warn'
              WHEN decision = 'route_to_dlp' THEN 'warn'
              ELSE decision
            END
            """
        )
    )


def _create_policy_violations_view() -> None:
    bind = op.get_bind()
    _drop_policy_violations_view()
    if bind.dialect.name == "postgresql":
        bind.execute(
            sa.text(
                """
                CREATE VIEW policy_violations_v8 AS
                SELECT
                  id AS policy_id,
                  org_id,
                  name AS policy_name,
                  decision,
                  severity,
                  created_at AS sla_started_at,
                  CASE
                    WHEN decision = 'deny' THEN created_at + interval '4 hours'
                    WHEN decision = 'require_approval' THEN created_at + interval '2 hours'
                    ELSE created_at + interval '24 hours'
                  END AS sla_due_at,
                  true AS flagged
                FROM org_policies
                WHERE enabled = true
                  AND decision IN ('deny', 'require_approval', 'log_only')
                """
            )
        )
    else:
        bind.execute(
            sa.text(
                """
                CREATE VIEW policy_violations_v8 AS
                SELECT
                  id AS policy_id,
                  org_id,
                  name AS policy_name,
                  decision,
                  severity,
                  created_at AS sla_started_at,
                  created_at AS sla_due_at,
                  1 AS flagged
                FROM org_policies
                WHERE enabled = 1
                  AND decision IN ('deny', 'require_approval', 'log_only')
                """
            )
        )


def _drop_policy_violations_view() -> None:
    op.get_bind().execute(sa.text("DROP VIEW IF EXISTS policy_violations_v8"))
