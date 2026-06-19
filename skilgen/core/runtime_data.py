from __future__ import annotations

import shutil
import time
from pathlib import Path

from skilgen.core.config import load_config


def runtime_data_root(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen"


def prune_runtime_data(project_root: str | Path) -> dict[str, object]:
    root = Path(project_root).resolve()
    config = load_config(root)
    retention_days = max(0, config.runtime_retention_days)
    runtime_root = runtime_data_root(root)
    if retention_days <= 0 or not runtime_root.exists():
        return {"retention_days": retention_days, "deleted_files": 0, "deleted_dirs": 0}
    cutoff = time.time() - (retention_days * 24 * 60 * 60)
    deleted_files = 0
    deleted_dirs = 0
    for path in sorted(runtime_root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        try:
            stat = path.stat()
        except OSError:
            continue
        if path.is_file() and stat.st_mtime < cutoff:
            path.unlink(missing_ok=True)
            deleted_files += 1
        elif path.is_dir():
            try:
                next(path.iterdir())
            except StopIteration:
                path.rmdir()
                deleted_dirs += 1
            except OSError:
                continue
    return {"retention_days": retention_days, "deleted_files": deleted_files, "deleted_dirs": deleted_dirs}


def purge_runtime_data(project_root: str | Path) -> dict[str, object]:
    runtime_root = runtime_data_root(project_root)
    if not runtime_root.exists():
        return {"removed": False, "path": str(runtime_root), "deleted_files": 0}
    deleted_files = sum(1 for path in runtime_root.rglob("*") if path.is_file())
    shutil.rmtree(runtime_root)
    return {"removed": True, "path": str(runtime_root), "deleted_files": deleted_files}
