from __future__ import annotations

from dataclasses import dataclass


REPORT_VIEW_SQL = """
SELECT
    id,
    org_id,
    event_type,
    action,
    actor_login,
    repo_id,
    repo_name,
    skill_id,
    skill_domain,
    resource_type,
    resource_id,
    severity,
    summary,
    metadata,
    created_at,
    commit_sha,
    policy_id,
    policy_decision,
    control_mapping,
    agent_runtime,
    sensitivity_tier
FROM v8_audit_report_events
WHERE org_id = :org_id
  AND (:date_from IS NULL OR created_at >= :date_from)
  AND (:date_to IS NULL OR created_at <= :date_to)
  AND (:repo_id IS NULL OR repo_id = :repo_id)
  AND (:actor IS NULL OR actor_login ILIKE :actor_pattern)
"""


@dataclass(frozen=True)
class ReportDefinition:
    id: str
    title: str
    control_mapping: str
    description: str
    predicate_sql: str


REPORTS: tuple[ReportDefinition, ...] = (
    ReportDefinition(
        id="ai-assisted-change-log",
        title="AI-Assisted Change Log",
        control_mapping="SOC2 CC8.1, ISO 27001 A.12.1.2",
        description="All commits where an AI agent contributed, with attribution and approval evidence.",
        predicate_sql="AND (event_type LIKE 'analysis.%' OR event_type LIKE 'agent.%' OR metadata ->> 'commit_sha' IS NOT NULL)",
    ),
    ReportDefinition(
        id="privileged-action-report",
        title="Privileged Action Report",
        control_mapping="SOC2 CC6.1, NIST AC-6",
        description="All agent actions on privileged resources, with policy decisions.",
        predicate_sql="AND (severity IN ('warning', 'critical') OR metadata ->> 'sensitivity_tier' IN ('sensitive', 'regulated', 'privileged'))",
    ),
    ReportDefinition(
        id="dlp-triggered-events",
        title="DLP Triggered Events",
        control_mapping="HIPAA § 164.308(a)(1)",
        description="All redact and route_to_dlp events with disposition.",
        predicate_sql="AND (metadata ->> 'policy_decision' IN ('redact', 'route_to_dlp') OR event_type LIKE 'dlp.%')",
    ),
    ReportDefinition(
        id="skill-provenance-report",
        title="Skill Provenance Report",
        control_mapping="SOC2 CC2.1",
        description="Every skill version used in production, with provenance and signature chain.",
        predicate_sql="AND (skill_id IS NOT NULL OR event_type LIKE 'skill.%')",
    ),
    ReportDefinition(
        id="anomaly-report",
        title="Anomaly Report",
        control_mapping="Internal",
        description="Statistically anomalous agent behavior in the selected period.",
        predicate_sql="AND (severity = 'critical' OR event_type LIKE 'anomaly.%' OR metadata ->> 'anomaly_score' IS NOT NULL)",
    ),
)


REPORTS_BY_ID = {report.id: report for report in REPORTS}


def report_sql(report_id: str) -> str:
    report = REPORTS_BY_ID[report_id]
    return f"{REPORT_VIEW_SQL}\n{report.predicate_sql}\nORDER BY created_at DESC, id DESC\nLIMIT :limit"
