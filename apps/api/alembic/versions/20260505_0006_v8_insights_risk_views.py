"""add v8 insights risky agent and repo views

Revision ID: 20260505_0006
Revises: 20260505_0005
Create Date: 2026-05-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260505_0006"
down_revision = "20260505_0005"
branch_labels = None
depends_on = None

REQUIRED_TABLES = {"repos", "pull_requests", "pr_attributions"}


def _json_violation_expr(dialect_name: str) -> str:
    if dialect_name == "postgresql":
        return "CASE WHEN jsonb_array_length(COALESCE(pa.skills_violated, '[]'::jsonb)) > 0 THEN 1 ELSE 0 END"
    return "CASE WHEN json_array_length(COALESCE(pa.skills_violated, '[]')) > 0 THEN 1 ELSE 0 END"


def _cutoff_expr(dialect_name: str) -> str:
    if dialect_name == "postgresql":
        return "CURRENT_TIMESTAMP - interval '30 days'"
    return "datetime('now', '-30 days')"


def _tier_expr(has_sensitivity_tier: bool) -> tuple[str, str]:
    if not has_sensitivity_tier:
        return "'unknown'", "1.0"
    tier = "LOWER(COALESCE(r.sensitivity_tier, 'internal'))"
    weight = (
        "CASE "
        f"WHEN {tier} = 'public' THEN 0.25 "
        f"WHEN {tier} = 'sensitive' THEN 2.0 "
        f"WHEN {tier} = 'regulated' THEN 3.0 "
        "ELSE 1.0 END"
    )
    return tier, weight


def risky_agents_view_sql(dialect_name: str = "postgresql", *, has_sensitivity_tier: bool = True) -> str:
    violation = _json_violation_expr(dialect_name)
    cutoff = _cutoff_expr(dialect_name)
    tier, weight = _tier_expr(has_sensitivity_tier)
    return f"""
CREATE VIEW v8_insights_risky_agents AS
WITH recent AS (
    SELECT
        r.org_id AS org_id,
        COALESCE(pa.primary_agent, 'human') AS agent_runtime,
        {violation} AS denied,
        {weight} AS scope_weight
    FROM pull_requests pr
    JOIN repos r ON r.id = pr.repo_id
    LEFT JOIN pr_attributions pa ON pa.pr_id = pr.id
    WHERE pr.opened_at >= {cutoff}
      AND r.is_active IS TRUE
)
SELECT
    org_id,
    agent_runtime,
    'mixed' AS sensitivity_tier,
    COUNT(*) AS volume,
    SUM(denied) AS denied_count,
    CASE WHEN COUNT(*) = 0 THEN 0 ELSE (SUM(denied) * 1.0 / COUNT(*)) END AS deny_rate,
    AVG(scope_weight) AS scope_sensitivity,
    (CASE WHEN COUNT(*) = 0 THEN 0 ELSE (SUM(denied) * 1.0 / COUNT(*)) END) * AVG(scope_weight) * COUNT(*) AS composite_risk,
    30 AS window_days
FROM recent
GROUP BY org_id, agent_runtime
"""


def risky_repos_view_sql(dialect_name: str = "postgresql", *, has_sensitivity_tier: bool = True) -> str:
    violation = _json_violation_expr(dialect_name)
    cutoff = _cutoff_expr(dialect_name)
    tier, weight = _tier_expr(has_sensitivity_tier)
    return f"""
CREATE VIEW v8_insights_risky_repos AS
WITH recent AS (
    SELECT
        r.org_id AS org_id,
        r.id AS repo_id,
        r.full_name AS repo_name,
        {tier} AS sensitivity_tier,
        {violation} AS denied,
        {weight} AS scope_weight
    FROM pull_requests pr
    JOIN repos r ON r.id = pr.repo_id
    LEFT JOIN pr_attributions pa ON pa.pr_id = pr.id
    WHERE pr.opened_at >= {cutoff}
      AND r.is_active IS TRUE
)
SELECT
    org_id,
    repo_id,
    repo_name,
    sensitivity_tier,
    COUNT(*) AS volume,
    SUM(denied) AS denied_count,
    CASE WHEN COUNT(*) = 0 THEN 0 ELSE (SUM(denied) * 1.0 / COUNT(*)) END AS deny_rate,
    AVG(scope_weight) AS scope_sensitivity,
    (CASE WHEN COUNT(*) = 0 THEN 0 ELSE (SUM(denied) * 1.0 / COUNT(*)) END) * AVG(scope_weight) * COUNT(*) AS composite_risk,
    30 AS window_days
FROM recent
GROUP BY org_id, repo_id, repo_name, sensitivity_tier
"""


def _drop_views() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS v8_insights_risky_agents"))
    op.execute(sa.text("DROP VIEW IF EXISTS v8_insights_risky_repos"))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if not REQUIRED_TABLES.issubset(tables):
        return
    repo_columns = {column["name"] for column in inspector.get_columns("repos")}
    has_sensitivity_tier = "sensitivity_tier" in repo_columns
    _drop_views()
    op.execute(sa.text(risky_agents_view_sql(bind.dialect.name, has_sensitivity_tier=has_sensitivity_tier)))
    op.execute(sa.text(risky_repos_view_sql(bind.dialect.name, has_sensitivity_tier=has_sensitivity_tier)))


def downgrade() -> None:
    _drop_views()
