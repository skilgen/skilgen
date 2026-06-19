from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Any

from fastapi import Depends, HTTPException

from apps.api.api.auth import get_current_org_id


PermissionChecker = Callable[[str], Any]


def settings_rbac_available() -> bool:
    try:
        import_module("apps.api.api.v8.settings.rbac")
    except ModuleNotFoundError:
        return False
    return True


def require_policy_permission(permission: str):
    try:
        settings_rbac = import_module("apps.api.api.v8.settings.rbac")
        checker: PermissionChecker = getattr(settings_rbac, "require_permission")
        return checker(permission)
    except (ModuleNotFoundError, AttributeError):
        async def unavailable(current_org_id: str = Depends(get_current_org_id)) -> str:
            raise HTTPException(
                status_code=501,
                detail=f"Settings RBAC permission middleware is unavailable for {permission}",
            )

        return unavailable


async def report_policy_rbac_status() -> dict[str, str | bool]:
    return {
        "available": settings_rbac_available(),
        "integration": "apps.api.api.v8.settings.rbac.require_permission",
        "fallback": "approval mutations return 501 until Settings RBAC lands",
    }
