from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
import logging
import os
import smtplib
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import AgentSession, Org, PRAttribution, PullRequest, Repo


logger = logging.getLogger(__name__)
APP_BASE_URL = os.getenv("NEXT_PUBLIC_DASHBOARD_URL") or os.getenv("NEXT_PUBLIC_APP_URL") or "https://app.skillayer.com"


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _dt_naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=None) if value.tzinfo else value


def _runtime_display_name(runtime: str | None) -> str:
    value = str(runtime or "human").replace("_", " ").replace("-", " ").strip()
    if not value:
        return "Human"
    if value.lower() == "claude code":
        return "Claude Code"
    return value.title()


def _severity_bucket(item: dict[str, Any]) -> str:
    severity = str(item.get("severity") or "warning").lower()
    if severity in {"critical", "error", "fatal", "failure", "high", "violation"}:
        return "violation"
    return "warning"


def _finding_counts(attribution: PRAttribution | None) -> tuple[int, int]:
    findings = attribution.skills_violated if attribution and isinstance(attribution.skills_violated, list) else []
    violations = 0
    warnings = 0
    for item in findings:
        if not isinstance(item, dict):
            continue
        if _severity_bucket(item) == "violation":
            violations += 1
        else:
            warnings += 1
    return violations, warnings


def _skill_name(item: object) -> str | None:
    if isinstance(item, str):
        value = item.strip()
        return value or None
    if isinstance(item, dict):
        for key in ("skill_name", "name", "title", "skill_id", "domain"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _top_counts(counts: dict[str, int], limit: int) -> list[str]:
    return [name for name, _count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def _risk_tier(attribution: PRAttribution | None) -> str:
    tier = str(attribution.risk_tier or "").lower() if attribution else ""
    if tier in {"green", "yellow", "red"}:
        return tier
    risk_score = int(attribution.risk_score or 0) if attribution else 0
    if risk_score >= 70:
        return "red"
    if risk_score >= 40:
        return "yellow"
    return "green"


async def collect_agent_scorecard(org_id: str, db: AsyncSession, window_days: int = 30) -> dict[str, Any]:
    generated_at = _now()
    cutoff = generated_at - timedelta(days=window_days)
    repos = list((await db.execute(select(Repo).where(Repo.org_id == org_id))).scalars().all())
    repo_ids = [repo.id for repo in repos]
    if not repo_ids:
        return {
            "window_days": window_days,
            "days": window_days,
            "generated_at": generated_at.isoformat(),
            "summary": {"total_prs": 0, "total_merged": 0, "total_violations": 0, "avg_compliance_percent": 0.0, "avg_risk": 0.0},
            "agents": [],
        }

    prs = list(
        (
            await db.execute(
                select(PullRequest).where(
                    PullRequest.repo_id.in_(repo_ids),
                    PullRequest.opened_at >= cutoff,
                )
            )
        )
        .scalars()
        .all()
    )
    prs = [pr for pr in prs if _dt_naive(pr.opened_at) is not None and _dt_naive(pr.opened_at) >= cutoff]
    pr_ids = [pr.id for pr in prs]
    attributions = (
        list((await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_(pr_ids)))).scalars().all())
        if pr_ids
        else []
    )
    attr_by_pr = {attr.pr_id: attr for attr in attributions}

    agents: dict[str, dict[str, Any]] = {}
    risk_sums: dict[str, int] = defaultdict(int)
    violation_prs: dict[str, int] = defaultdict(int)
    violation_skill_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for pr in prs:
        attribution = attr_by_pr.get(pr.id)
        agent = str(attribution.primary_agent if attribution else "human")
        row = agents.setdefault(
            agent,
            {
                "agent": agent,
                "agent_runtime": agent,
                "display_name": _runtime_display_name(agent),
                "agent_label": _runtime_display_name(agent),
                "prs": 0,
                "prs_total": 0,
                "merged": 0,
                "prs_merged": 0,
                "violations": 0,
                "violations_total": 0,
                "avg_risk": 0.0,
                "avg_risk_score": 0.0,
                "compliance_percent": 100.0,
                "compliance_pct": 100.0,
                "risk_distribution": {"green": 0, "yellow": 0, "red": 0},
                "top_violations": [],
            },
        )
        row["prs"] += 1
        row["prs_total"] = row["prs"]
        if pr.merged_at is not None or pr.state == "merged":
            row["merged"] += 1
            row["prs_merged"] = row["merged"]
        violations, _warnings = _finding_counts(attribution)
        row["violations"] += violations
        row["violations_total"] = row["violations"]
        if violations > 0:
            violation_prs[agent] += 1
        tier = _risk_tier(attribution)
        row["risk_distribution"][tier] += 1
        risk_sums[agent] += int(attribution.risk_score or 0) if attribution else 0
        if attribution and isinstance(attribution.skills_violated, list):
            for finding in attribution.skills_violated:
                if isinstance(finding, dict) and _severity_bucket(finding) == "violation":
                    name = _skill_name(finding)
                    if name:
                        violation_skill_counts[agent][name] += 1

    rows = []
    for agent, row in agents.items():
        prs_total = int(row["prs"])
        row["compliance_percent"] = round((1 - (violation_prs[agent] / prs_total)) * 100, 1) if prs_total else 100.0
        row["compliance_pct"] = row["compliance_percent"]
        row["avg_risk"] = round(risk_sums[agent] / prs_total, 1) if prs_total else 0.0
        row["avg_risk_score"] = row["avg_risk"]
        row["top_violations"] = _top_counts(violation_skill_counts[agent], 5)
        rows.append(row)
    rows.sort(key=lambda item: (-int(item["prs"]), str(item["agent"])))

    summary = {
        "total_prs": sum(int(row["prs"]) for row in rows),
        "total_merged": sum(int(row["merged"]) for row in rows),
        "total_violations": sum(int(row["violations"]) for row in rows),
        "avg_compliance_percent": round(sum(float(row["compliance_percent"]) for row in rows) / len(rows), 1) if rows else 0.0,
        "avg_risk": round(sum(float(row["avg_risk"]) for row in rows) / len(rows), 1) if rows else 0.0,
    }
    return {"window_days": window_days, "days": window_days, "generated_at": generated_at.isoformat(), "summary": summary, "agents": rows}


async def collect_developer_leaderboard(org_id: str, db: AsyncSession, window_days: int = 30) -> dict[str, Any]:
    generated_at = _now()
    cutoff = generated_at - timedelta(days=window_days)
    repos = list((await db.execute(select(Repo).where(Repo.org_id == org_id, Repo.is_active.is_(True)))).scalars().all())
    repo_ids = [repo.id for repo in repos]
    if not repo_ids:
        return {"window_days": window_days, "generated_at": generated_at.isoformat(), "developers": []}

    sessions = list(
        (
            await db.execute(
                select(AgentSession).where(
                    AgentSession.repo_id.in_(repo_ids),
                    AgentSession.session_start >= cutoff,
                    AgentSession.engineer_login.is_not(None),
                )
            )
        )
        .scalars()
        .all()
    )
    prs = list(
        (
            await db.execute(
                select(PullRequest).where(
                    PullRequest.repo_id.in_(repo_ids),
                    PullRequest.opened_at >= cutoff,
                )
            )
        )
        .scalars()
        .all()
    )
    prs = [pr for pr in prs if str(pr.author_login or "").strip() and _dt_naive(pr.opened_at) is not None and _dt_naive(pr.opened_at) >= cutoff]
    pr_ids = [pr.id for pr in prs]
    attributions = (
        list((await db.execute(select(PRAttribution).where(PRAttribution.pr_id.in_(pr_ids)))).scalars().all())
        if pr_ids
        else []
    )
    attr_by_pr = {attr.pr_id: attr for attr in attributions}

    developers: dict[str, dict[str, Any]] = {}
    risk_sums: dict[str, int] = defaultdict(int)
    risk_counts: dict[str, int] = defaultdict(int)
    clean_prs: dict[str, int] = defaultdict(int)

    def row_for(login: str) -> dict[str, Any]:
        return developers.setdefault(
            login,
            {
                "login": login,
                "sessions_count": 0,
                "files_touched": 0,
                "lines_changed": 0,
                "prs_opened": 0,
                "prs_merged": 0,
                "prs_reverted": 0,
                "violations_total": 0,
                "warnings_total": 0,
                "compliance_pct": 100.0,
                "avg_risk_score": 0.0,
            },
        )

    for session in sessions:
        login = str(session.engineer_login or "").strip()
        if not login or _dt_naive(session.session_start) is None or _dt_naive(session.session_start) < cutoff:
            continue
        row = row_for(login)
        row["sessions_count"] += 1
        if isinstance(session.files_touched, list):
            row["files_touched"] += len({str(path) for path in session.files_touched if path})

    for pr in prs:
        login = str(pr.author_login or "").strip()
        row = row_for(login)
        row["prs_opened"] += 1
        row["lines_changed"] += int(pr.additions or 0) + int(pr.deletions or 0)
        if pr.merged_at is not None or pr.state == "merged":
            row["prs_merged"] += 1
        elif pr.closed_at is not None or pr.state == "closed":
            row["prs_reverted"] += 1
        attribution = attr_by_pr.get(pr.id)
        violations, warnings = _finding_counts(attribution)
        row["violations_total"] += violations
        row["warnings_total"] += warnings
        if violations == 0:
            clean_prs[login] += 1
        risk_sums[login] += int(attribution.risk_score or 0) if attribution else 0
        risk_counts[login] += 1

    rows = []
    for login, row in developers.items():
        prs_opened = int(row["prs_opened"])
        row["compliance_pct"] = round((clean_prs[login] / prs_opened) * 100, 1) if prs_opened else 100.0
        row["avg_risk_score"] = round(risk_sums[login] / risk_counts[login], 1) if risk_counts[login] else 0.0
        rows.append(row)
    rows.sort(key=lambda item: (-float(item["compliance_pct"]), -int(item["prs_merged"]), -int(item["sessions_count"]), str(item["login"])))
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return {"window_days": window_days, "generated_at": generated_at.isoformat(), "developers": rows}


def _count_all_violations(scorecard: dict[str, Any]) -> list[tuple[str, int]]:
    counts: dict[str, int] = defaultdict(int)
    for agent in scorecard.get("agents", []):
        if not isinstance(agent, dict):
            continue
        for name in agent.get("top_violations", []) or []:
            counts[str(name)] += 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:5]


def _tone_color(value: float, kind: str) -> str:
    if kind == "risk":
        if value >= 70:
            return "#dc2626"
        if value >= 40:
            return "#b7791f"
        return "#15803d"
    if value >= 90:
        return "#15803d"
    if value >= 75:
        return "#b7791f"
    return "#dc2626"


def build_digest_html(org_name: str, scorecard: dict[str, Any], leaderboard: dict[str, Any], window_days: int, date_label: str) -> str:
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    dashboard_url = f"{APP_BASE_URL}/dashboard/agent-scorecard"
    settings_url = f"{APP_BASE_URL}/dashboard/settings?tab=notifications"
    agents = [item for item in scorecard.get("agents", []) if isinstance(item, dict)]
    developers = [item for item in leaderboard.get("developers", []) if isinstance(item, dict)][:5]
    violations = _count_all_violations(scorecard)

    agent_rows = ""
    if agents:
        for index, agent in enumerate(agents):
            bg = "#ffffff" if index % 2 == 0 else "#f8fafc"
            compliance = float(agent.get("compliance_percent", agent.get("compliance_pct", 0)) or 0)
            risk = float(agent.get("avg_risk", agent.get("avg_risk_score", 0)) or 0)
            agent_rows += (
                f"<tr style=\"background:{bg};\">"
                f"<td style=\"padding:10px;border-bottom:1px solid #e5e7eb;font-weight:600;color:#111827;\">{escape(str(agent.get('agent_label') or agent.get('display_name') or agent.get('agent') or 'Unknown'))}</td>"
                f"<td style=\"padding:10px;border-bottom:1px solid #e5e7eb;text-align:right;color:#374151;\">{int(agent.get('prs') or agent.get('prs_total') or 0)}</td>"
                f"<td style=\"padding:10px;border-bottom:1px solid #e5e7eb;text-align:right;color:#374151;\">{int(agent.get('merged') or agent.get('prs_merged') or 0)}</td>"
                f"<td style=\"padding:10px;border-bottom:1px solid #e5e7eb;text-align:right;font-weight:700;color:{_tone_color(compliance, 'compliance')};\">{compliance:.1f}%</td>"
                f"<td style=\"padding:10px;border-bottom:1px solid #e5e7eb;text-align:right;color:#374151;\">{int(agent.get('violations') or agent.get('violations_total') or 0)}</td>"
                f"<td style=\"padding:10px;border-bottom:1px solid #e5e7eb;text-align:right;font-weight:700;color:{_tone_color(risk, 'risk')};\">{risk:.1f}</td>"
                "</tr>"
            )
    else:
        agent_rows = "<tr><td colspan=\"6\" style=\"padding:16px;color:#6b7280;text-align:center;\">No agent PR activity for this window.</td></tr>"

    developer_items = "".join(
        f"<li style=\"margin:0 0 10px 0;color:#111827;\"><strong>{escape(str(item.get('login') or 'Unknown'))}</strong>"
        f"<span style=\"color:#6b7280;\"> - {int(item.get('prs_merged') or 0)} merged PRs, {float(item.get('compliance_pct') or 0):.1f}% compliance</span></li>"
        for item in developers
    ) or "<li style=\"color:#6b7280;\">No developer activity for this window.</li>"

    if violations:
        violation_html = "".join(
            f"<tr><td style=\"padding:8px 0;color:#111827;\">{escape(name)}</td><td style=\"padding:8px 0;text-align:right;color:#dc2626;font-weight:700;\">{count}</td></tr>"
            for name, count in violations
        )
        violations_block = f"<table role=\"presentation\" style=\"width:100%;border-collapse:collapse;\">{violation_html}</table>"
    else:
        violations_block = (
            "<div style=\"border:1px solid #bbf7d0;background:#f0fdf4;color:#166534;border-radius:8px;padding:14px;font-weight:700;\">"
            "No skill violations detected this week."
            "</div>"
        )

    return f"""<!doctype html>
<html>
  <body style="margin:0;background:#f3f4f6;font-family:Arial,Helvetica,sans-serif;color:#111827;">
    <div style="max-width:600px;margin:0 auto;background:#ffffff;">
      <div style="padding:28px 28px 18px;border-bottom:1px solid #e5e7eb;">
        <div style="font-size:22px;font-weight:800;color:#111827;">Skillayer</div>
        <div style="margin-top:6px;font-size:14px;color:#6b7280;">Weekly Agent Intelligence Digest</div>
        <div style="margin-top:14px;font-size:13px;color:#374151;">Week of {escape(date_label)} / {escape(org_name)} / {window_days} days</div>
      </div>
      <div style="padding:24px 28px;">
        <h2 style="margin:0 0 12px;font-size:18px;color:#111827;">Agent Performance</h2>
        <table role="presentation" style="width:100%;border-collapse:collapse;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;font-size:13px;">
          <thead>
            <tr style="background:#111827;color:#ffffff;">
              <th align="left" style="padding:10px;">Agent</th>
              <th align="right" style="padding:10px;">PRs</th>
              <th align="right" style="padding:10px;">Merged</th>
              <th align="right" style="padding:10px;">Compliance</th>
              <th align="right" style="padding:10px;">Violations</th>
              <th align="right" style="padding:10px;">Avg Risk</th>
            </tr>
          </thead>
          <tbody>{agent_rows}</tbody>
        </table>
      </div>
      <div style="padding:0 28px 24px;">
        <h2 style="margin:0 0 12px;font-size:18px;color:#111827;">Top Developers</h2>
        <ol style="margin:0;padding-left:22px;font-size:14px;">{developer_items}</ol>
      </div>
      <div style="padding:0 28px 28px;">
        <h2 style="margin:0 0 12px;font-size:18px;color:#111827;">Violations This Week</h2>
        {violations_block}
      </div>
      <div style="padding:22px 28px;border-top:1px solid #e5e7eb;background:#f9fafb;">
        <div style="margin-bottom:16px;">
          <a href="{dashboard_url}" style="display:inline-block;background:#111827;color:#ffffff;text-decoration:none;border-radius:6px;padding:10px 14px;font-weight:700;font-size:13px;">View Dashboard</a>
          <a href="{settings_url}" style="display:inline-block;margin-left:8px;color:#374151;text-decoration:underline;font-size:13px;">Unsubscribe/settings</a>
        </div>
        <div style="font-size:12px;color:#6b7280;">Generated by Skillayer at {generated_at}</div>
      </div>
    </div>
  </body>
</html>"""


def send_digest_email(to_email: str, subject: str, html: str) -> bool:
    host = os.getenv("SMTP_HOST")
    if not host:
        logger.warning("SMTP_HOST is not configured; digest email not sent to %s", to_email)
        return False
    port = int(os.getenv("SMTP_PORT") or "587")
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_FROM") or "digest@skillayer.com"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email
    message.attach(MIMEText(html, "html"))

    try:
        logger.info("Sending digest email to %s via %s:%s from %s", to_email, host, port, from_email)
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            smtp.starttls()
            if username and password:
                smtp.login(username, password)
            smtp.sendmail(from_email, [to_email], message.as_string())
        return True
    except Exception:
        logger.exception("Digest email send failed for %s via %s:%s from %s", to_email, host, port, from_email)
        return False


async def build_and_send_org_digest(org_id: str, db: AsyncSession) -> bool:
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    if not org.digest_email:
        raise HTTPException(status_code=400, detail="Digest email is not configured")

    scorecard = await collect_agent_scorecard(org_id, db, 30)
    leaderboard = await collect_developer_leaderboard(org_id, db, 30)
    date_label = datetime.now(UTC).date().isoformat()
    org_name = str(org.name or org.login or "Skillayer")
    html = build_digest_html(org_name, scorecard, leaderboard, 30, date_label)
    sent = send_digest_email(str(org.digest_email), f"Skillayer Weekly Agent Intelligence Digest - {org_name}", html)
    if sent:
        settings_payload = dict(org.settings or {})
        settings_payload["digest_last_sent_at"] = datetime.now(UTC).isoformat()
        org.settings = settings_payload
        await db.commit()
    return sent
