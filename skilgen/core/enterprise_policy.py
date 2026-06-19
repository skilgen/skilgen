from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

from skilgen.core.dependency_risk import analyze_dependency_risks, dependency_report_to_dict
from skilgen.core.score import compute_skillgen_score
from skilgen.enterprise_skills import list_enterprise_skills
from skilgen.external_skills import active_external_skills


DEFAULT_BLOCKED_LICENSES = ["AGPL-3.0", "GPL-3.0"]
POLICY_RELATIVE_PATH = Path(".skilgen") / "policy.yml"


@dataclass(frozen=True)
class EnterprisePolicy:
    """Enterprise compliance thresholds loaded from .skilgen/policy.yml."""

    min_score: int = 60
    required_domains: list[str] | None = None
    max_stale_days: int = 30
    blocked_licenses: list[str] | None = None

    def normalized(self) -> "EnterprisePolicy":
        """Return a policy with list fields populated and strings normalized."""
        return EnterprisePolicy(
            min_score=self.min_score,
            required_domains=sorted(dict.fromkeys(self.required_domains or [])),
            max_stale_days=self.max_stale_days,
            blocked_licenses=list(
                dict.fromkeys(self.blocked_licenses if self.blocked_licenses is not None else DEFAULT_BLOCKED_LICENSES)
            ),
        )


@dataclass(frozen=True)
class PolicyCheck:
    """One human-readable enterprise policy check result."""

    name: str
    passed: bool
    message: str


def policy_path(project_root: str | Path) -> Path:
    """Return the enterprise policy path for a project root."""
    return Path(project_root).resolve() / POLICY_RELATIVE_PATH


def default_policy() -> EnterprisePolicy:
    """Return the default enterprise policy."""
    return EnterprisePolicy(
        min_score=60,
        required_domains=[],
        max_stale_days=30,
        blocked_licenses=DEFAULT_BLOCKED_LICENSES.copy(),
    )


def write_default_policy(project_root: str | Path) -> Path:
    """Create or replace .skilgen/policy.yml with enterprise defaults."""
    path = policy_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(asdict(default_policy()), sort_keys=False), encoding="utf-8")
    return path


def load_enterprise_policy(project_root: str | Path) -> EnterprisePolicy:
    """Load and validate the project enterprise policy."""
    path = policy_path(project_root)
    if not path.exists():
        raise ValueError(f"Enterprise policy not found at {path}. Run `skilgen enterprise policy init` first.")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Enterprise policy YAML is invalid: {exc}") from exc
    return validate_policy_payload(raw)


def validate_policy_payload(raw: Any) -> EnterprisePolicy:
    """Validate a raw YAML payload and return a typed enterprise policy."""
    if not isinstance(raw, dict):
        raise ValueError("Enterprise policy must be a YAML mapping.")
    allowed = {"min_score", "required_domains", "max_stale_days", "blocked_licenses"}
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ValueError(f"Unknown enterprise policy keys: {', '.join(unknown)}.")
    min_score = _int_field(raw, "min_score", default_policy().min_score, minimum=0, maximum=100)
    max_stale_days = _int_field(raw, "max_stale_days", default_policy().max_stale_days, minimum=0)
    required_domains = _string_list_field(raw, "required_domains")
    blocked_licenses = _string_list_field(raw, "blocked_licenses")
    return EnterprisePolicy(
        min_score=min_score,
        required_domains=required_domains,
        max_stale_days=max_stale_days,
        blocked_licenses=blocked_licenses,
    ).normalized()


def validate_policy_file(project_root: str | Path) -> tuple[bool, str]:
    """Validate policy.yml and return a CLI-friendly result tuple."""
    try:
        load_enterprise_policy(project_root)
    except ValueError as exc:
        return False, str(exc)
    return True, f"Enterprise policy is valid: {policy_path(project_root)}"


def enterprise_compliance_report(project_root: str | Path) -> dict[str, object]:
    """Build the enterprise compliance report used by policy checks and JSON output."""
    root = Path(project_root).resolve()
    policy = load_enterprise_policy(root)
    score_payload = compute_skillgen_score(root)
    score = int(round(float(score_payload["score"])))
    materialized_domains = _materialized_domains(root)
    missing_domains = [domain for domain in policy.required_domains or [] if domain not in materialized_domains]
    stale_skills = _stale_skills(root, policy.max_stale_days)
    dependency_report = analyze_dependency_risks(root)
    dependency_payload = dependency_report_to_dict(dependency_report)
    blocked_license_hits = _blocked_license_hits(root, policy.blocked_licenses or [])
    policy_violations: list[str] = []
    if score < policy.min_score:
        policy_violations.append(f"Skilgen Score {score}/100 is below required minimum {policy.min_score}/100.")
    for domain in missing_domains:
        policy_violations.append(f"Required domain is missing from generated skills: {domain}.")
    for skill in stale_skills:
        policy_violations.append(f"Skill is stale: {skill['path']}.")
    for hit in blocked_license_hits:
        policy_violations.append(f"Blocked license detected in {hit['source']}: {hit['license']}.")
    overall_status = "pass" if not policy_violations else "fail"
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "score": score,
        "policy_violations": policy_violations,
        "stale_skills": stale_skills,
        "missing_domains": missing_domains,
        "dependency_risks": {
            "risk_score": dependency_payload["risk_score"],
            "high_risk": dependency_payload["high_risk"],
            "medium_risk": dependency_payload["medium_risk"],
            "blocked_licenses": blocked_license_hits,
        },
        "overall_status": overall_status,
    }


def enterprise_policy_checks(project_root: str | Path) -> list[PolicyCheck]:
    """Evaluate enterprise policy checks for human-readable CLI output."""
    report = enterprise_compliance_report(project_root)
    policy = load_enterprise_policy(project_root)
    dependency_risks = report["dependency_risks"]
    blocked_count = len(dependency_risks["blocked_licenses"])
    return [
        PolicyCheck(
            "score threshold",
            int(report["score"]) >= policy.min_score,
            f"Skilgen Score {report['score']}/100, required {policy.min_score}/100",
        ),
        PolicyCheck(
            "required domains",
            not report["missing_domains"],
            "All required domains are present."
            if not report["missing_domains"]
            else f"Missing domains: {', '.join(str(item) for item in report['missing_domains'])}",
        ),
        PolicyCheck(
            "skill freshness",
            not report["stale_skills"],
            "All generated skills are within freshness policy."
            if not report["stale_skills"]
            else f"Stale skills: {', '.join(str(item['path']) for item in report['stale_skills'])}",
        ),
        PolicyCheck(
            "license compliance",
            blocked_count == 0,
            "No blocked licenses detected."
            if blocked_count == 0
            else f"Blocked licenses detected: {blocked_count}",
        ),
    ]


def render_policy_checks(checks: list[PolicyCheck]) -> str:
    """Render policy check results with pass/fail markers."""
    lines = ["Enterprise policy check"]
    for check in checks:
        marker = "✓" if check.passed else "✗"
        lines.append(f"{marker} {check.name}: {check.message}")
    return "\n".join(lines)


def _int_field(raw: dict[str, Any], key: str, default: int, *, minimum: int, maximum: int | None = None) -> int:
    value = raw.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"`{key}` must be an integer.")
    if value < minimum:
        raise ValueError(f"`{key}` must be at least {minimum}.")
    if maximum is not None and value > maximum:
        raise ValueError(f"`{key}` must be at most {maximum}.")
    return value


def _string_list_field(raw: dict[str, Any], key: str) -> list[str]:
    value = raw.get(key, getattr(default_policy(), key))
    if not isinstance(value, list):
        raise ValueError(f"`{key}` must be a list.")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"`{key}` must contain only strings.")
    cleaned = [item.strip() for item in value]
    if any(not item for item in cleaned):
        raise ValueError(f"`{key}` cannot contain empty values.")
    return cleaned


def _materialized_domains(project_root: Path) -> list[str]:
    skills_root = project_root / "skills"
    if not skills_root.exists():
        return []
    return sorted(
        {
            path.relative_to(skills_root).parts[0]
            for path in skills_root.rglob("SKILL.md")
            if path.relative_to(skills_root).parts
        }
    )


def _skill_last_updated(skill_path: Path) -> date | None:
    try:
        lines = skill_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines[:40]:
        if not line.strip().startswith("last_updated:"):
            continue
        raw = line.split(":", 1)[1].strip().strip("'\"")
        try:
            return date.fromisoformat(raw[:10])
        except ValueError:
            return None
    return None


def _stale_skills(project_root: Path, max_stale_days: int) -> list[dict[str, object]]:
    today = datetime.now(UTC).date()
    skills_root = project_root / "skills"
    if not skills_root.exists():
        return []
    stale: list[dict[str, object]] = []
    for skill_path in sorted(skills_root.rglob("SKILL.md")):
        relative = skill_path.relative_to(project_root).as_posix()
        last_updated = _skill_last_updated(skill_path)
        if last_updated is None:
            stale.append({"path": relative, "last_updated": None, "age_days": None, "reason": "missing_last_updated"})
            continue
        age_days = (today - last_updated).days
        if age_days > max_stale_days:
            stale.append({"path": relative, "last_updated": last_updated.isoformat(), "age_days": age_days, "reason": "too_old"})
    return stale


def _blocked_license_hits(project_root: Path, blocked_licenses: list[str]) -> list[dict[str, str]]:
    blocked = {_normalize_license(item) for item in blocked_licenses}
    hits: list[dict[str, str]] = []
    for source, license_value in _license_sources(project_root):
        normalized = _normalize_license(license_value)
        if any(blocked_item in normalized or normalized in blocked_item for blocked_item in blocked):
            hits.append({"source": source, "license": license_value})
    return hits


def _license_sources(project_root: Path) -> list[tuple[str, str]]:
    sources: list[tuple[str, str]] = []
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
        license_path = project_root / name
        if license_path.exists():
            first_line = next(
                (line.strip() for line in license_path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()),
                "",
            )
            if first_line:
                sources.append((name, first_line))
    for entry in active_external_skills(project_root):
        license_value = _license_summary(entry.get("license") or entry.get("lock_metadata", {}).get("license"))
        if license_value:
            sources.append((f"external skill {entry.get('slug', 'unknown')}", license_value))
    for entry in list_enterprise_skills(project_root):
        license_value = _license_summary(entry.get("license"))
        if license_value:
            sources.append((f"enterprise skill {entry.get('slug', 'unknown')}", license_value))
    return sources


def _license_summary(value: object) -> str | None:
    if isinstance(value, dict):
        summary = value.get("summary") or value.get("name") or value.get("id")
        return str(summary) if summary else None
    if isinstance(value, str):
        return value
    return None


def _normalize_license(value: str) -> str:
    return value.lower().replace("license", "").replace(" ", "").replace("_", "-")
