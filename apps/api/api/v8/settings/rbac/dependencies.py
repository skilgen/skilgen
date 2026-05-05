from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id, get_current_user
from apps.api.api.v8.settings.rbac.expressions import matches_scope_expression, permission_matches
from packages.db.database import get_db
from packages.db.models import Role, RoleBinding


PERMISSIONS = [
    "settings.read",
    "settings.write",
    "settings.teams.manage",
    "settings.rbac.manage",
    "settings.sso.read",
    "settings.connectors.manage",
    "settings.admin_audit.read",
    "settings.billing.read",
    "settings.notifications.manage",
    "policy.approvals.approve",
]


def principal_id_from_user(user: dict[str, Any]) -> str:
    return str(user.get("email") or user.get("preferred_username") or user.get("sub") or "unknown")


async def has_permission(
    db: AsyncSession,
    *,
    org_id: str,
    principal_id: str,
    permission: str,
    scope: dict[str, Any] | None = None,
) -> bool:
    stmt = (
        select(Role, RoleBinding)
        .join(RoleBinding, RoleBinding.role_id == Role.id)
        .where(
            Role.org_id == org_id,
            RoleBinding.org_id == org_id,
            RoleBinding.principal_type == "user",
            RoleBinding.principal_id == principal_id,
        )
    )
    rows = (await db.execute(stmt)).all()
    for role, binding in rows:
        permissions = role.permissions if isinstance(role.permissions, list) else []
        if not any(permission_matches(str(granted), permission) for granted in permissions):
            continue
        expression = binding.scope_expression if isinstance(binding.scope_expression, (dict, str)) else None
        if matches_scope_expression(expression, scope or {}):
            return True
    return False


def require_permission(permission: str, scope_factory: Callable[[], dict[str, Any]] | None = None):
    async def dependency(
        db: AsyncSession = Depends(get_db),
        current_org_id: str = Depends(get_current_org_id),
        user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        principal_id = principal_id_from_user(user)
        allowed = await has_permission(
            db,
            org_id=current_org_id,
            principal_id=principal_id,
            permission=permission,
            scope=scope_factory() if scope_factory else {},
        )
        if not allowed:
            raise HTTPException(status_code=403, detail="RBAC permission denied")
        return {"principal_id": principal_id, "permission": permission}

    return dependency
