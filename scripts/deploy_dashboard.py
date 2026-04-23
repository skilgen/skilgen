"""Deploy the Skillayer dashboard from the monorepo root."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PROJECT_LINK = ROOT / "apps" / "dashboard" / ".vercel" / "project.json"
ROOT_PROJECT_LINK = ROOT / ".vercel" / "project.json"
REQUIRED_PROJECT_KEYS = {"projectId", "orgId", "projectName"}


def load_project_link(path: Path) -> dict[str, str]:
    """Load and validate a Vercel project link file."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED_PROJECT_KEYS.difference(payload)
    if missing:
        missing_keys = ", ".join(sorted(missing))
        raise ValueError(f"Vercel project link {path} is missing: {missing_keys}")
    return {key: str(payload[key]) for key in REQUIRED_PROJECT_KEYS}


def deploy_command(*, production: bool) -> list[str]:
    """Build the Vercel CLI command for dashboard deployment."""
    command = ["vercel", "deploy"]
    if production:
        command.append("--prod")
    return command


@contextmanager
def dashboard_project_link(
    root_link: Path = ROOT_PROJECT_LINK,
    dashboard_link: Path = DASHBOARD_PROJECT_LINK,
) -> Iterator[None]:
    """Temporarily point the repo-root Vercel link at the dashboard project."""
    dashboard_payload = load_project_link(dashboard_link)
    backup = root_link.read_text(encoding="utf-8") if root_link.exists() else None
    root_link.parent.mkdir(parents=True, exist_ok=True)
    root_link.write_text(json.dumps(dashboard_payload, separators=(",", ":")), encoding="utf-8")
    try:
        yield
    finally:
        if backup is None:
            root_link.unlink(missing_ok=True)
        else:
            root_link.write_text(backup, encoding="utf-8")


def deploy_dashboard(*, production: bool, dry_run: bool) -> int:
    """Deploy the dashboard with the complete monorepo uploaded."""
    if dry_run:
        print(" ".join(deploy_command(production=production)))
        return 0
    with dashboard_project_link():
        completed = subprocess.run(deploy_command(production=production), cwd=ROOT, check=False)
    return int(completed.returncode)


def parse_args() -> argparse.Namespace:
    """Parse command line options."""
    parser = argparse.ArgumentParser(description="Deploy Skillayer dashboard from the monorepo root.")
    parser.add_argument("--prod", action="store_true", help="Deploy to production.")
    parser.add_argument("--dry-run", action="store_true", help="Print the deploy command without running it.")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    return deploy_dashboard(production=bool(args.prod), dry_run=bool(args.dry_run))


if __name__ == "__main__":
    raise SystemExit(main())
