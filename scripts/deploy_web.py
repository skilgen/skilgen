"""Deploy the Skillayer web app from the monorepo root."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_PROJECT_LINK = ROOT / "apps" / "web" / ".vercel" / "project.json"
ROOT_PROJECT_LINK = ROOT / ".vercel" / "project.json"
WEB_VERCEL_CONFIG = ROOT / "vercel.web.json"
REQUIRED_PROJECT_KEYS = {"projectId", "orgId", "projectName"}


def load_project_link(path: Path) -> dict[str, str]:
    """Load and validate a Vercel project link file."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED_PROJECT_KEYS.difference(payload)
    if missing:
        missing_keys = ", ".join(sorted(missing))
        raise ValueError(f"Vercel project link {path} is missing: {missing_keys}")
    return {key: str(payload[key]) for key in REQUIRED_PROJECT_KEYS}


def deploy_command(*, production: bool, config_path: Path = WEB_VERCEL_CONFIG) -> list[str]:
    """Build the Vercel CLI command for web deployment."""
    command = ["vercel", "deploy", "--local-config", str(config_path)]
    if production:
        command.append("--prod")
    return command


@contextmanager
def web_project_link(
    root_link: Path = ROOT_PROJECT_LINK,
    web_link: Path = WEB_PROJECT_LINK,
) -> Iterator[None]:
    """Temporarily point the repo-root Vercel link at the web project."""
    web_payload = load_project_link(web_link)
    backup = root_link.read_text(encoding="utf-8") if root_link.exists() else None
    root_link.parent.mkdir(parents=True, exist_ok=True)
    root_link.write_text(json.dumps(web_payload, separators=(",", ":")), encoding="utf-8")
    try:
        yield
    finally:
        if backup is None:
            root_link.unlink(missing_ok=True)
        else:
            root_link.write_text(backup, encoding="utf-8")


def deploy_web(*, production: bool, dry_run: bool) -> int:
    """Deploy the web app with the complete monorepo uploaded."""
    if not WEB_VERCEL_CONFIG.exists():
        raise FileNotFoundError(f"Missing web Vercel config: {WEB_VERCEL_CONFIG}")
    if dry_run:
        print(" ".join(deploy_command(production=production)))
        return 0
    with web_project_link():
        completed = subprocess.run(deploy_command(production=production), cwd=ROOT, check=False)
    return int(completed.returncode)


def parse_args() -> argparse.Namespace:
    """Parse command line options."""
    parser = argparse.ArgumentParser(description="Deploy Skillayer web app from the monorepo root.")
    parser.add_argument("--prod", action="store_true", help="Deploy to production.")
    parser.add_argument("--dry-run", action="store_true", help="Print the deploy command without running it.")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    return deploy_web(production=bool(args.prod), dry_run=bool(args.dry_run))


if __name__ == "__main__":
    raise SystemExit(main())
