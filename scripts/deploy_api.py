"""Deploy the Skillayer API from the monorepo root with shared packages bundled."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_PROJECT_LINK = ROOT / "apps" / "api" / ".vercel" / "project.json"
ROOT_PROJECT_LINK = ROOT / ".vercel" / "project.json"
API_VERCEL_CONFIG = ROOT / "vercel.api.json"
REQUIRED_PROJECT_KEYS = {"projectId", "orgId", "projectName"}


def load_project_link(path: Path) -> dict[str, str]:
    """Load and validate a Vercel project link file."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED_PROJECT_KEYS.difference(payload)
    if missing:
        missing_keys = ", ".join(sorted(missing))
        raise ValueError(f"Vercel project link {path} is missing: {missing_keys}")
    return {key: str(payload[key]) for key in REQUIRED_PROJECT_KEYS}


def deploy_command(*, production: bool, config_path: Path) -> list[str]:
    """Build the Vercel CLI command for the API deployment."""
    command = ["vercel", "deploy", "--local-config", str(config_path)]
    if production:
        command.append("--prod")
    return command


@contextmanager
def api_project_link(root_link: Path = ROOT_PROJECT_LINK, api_link: Path = API_PROJECT_LINK) -> Iterator[None]:
    """Temporarily point the repo-root Vercel link at the API project."""
    api_payload = load_project_link(api_link)
    backup = root_link.read_text(encoding="utf-8") if root_link.exists() else None
    root_link.parent.mkdir(parents=True, exist_ok=True)
    root_link.write_text(json.dumps(api_payload, separators=(",", ":")), encoding="utf-8")
    try:
        yield
    finally:
        if backup is None:
            root_link.unlink(missing_ok=True)
        else:
            root_link.write_text(backup, encoding="utf-8")


def deploy_api(*, production: bool, dry_run: bool) -> int:
    """Deploy the API through Vercel without invoking the monorepo JavaScript build."""
    if not API_VERCEL_CONFIG.exists():
        raise FileNotFoundError(f"Missing API Vercel config: {API_VERCEL_CONFIG}")
    if dry_run:
        print(" ".join(deploy_command(production=production, config_path=API_VERCEL_CONFIG)))
        return 0
    with api_project_link():
        completed = subprocess.run(
            deploy_command(production=production, config_path=API_VERCEL_CONFIG),
            cwd=ROOT,
            check=False,
        )
    return int(completed.returncode)


def parse_args() -> argparse.Namespace:
    """Parse command line options."""
    parser = argparse.ArgumentParser(description="Deploy Skillayer API from the monorepo root.")
    parser.add_argument("--prod", action="store_true", help="Deploy to production.")
    parser.add_argument("--dry-run", action="store_true", help="Print the deploy command without running it.")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    return deploy_api(production=bool(args.prod), dry_run=bool(args.dry_run))


if __name__ == "__main__":
    raise SystemExit(main())
