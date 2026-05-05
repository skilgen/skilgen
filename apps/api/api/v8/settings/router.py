from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import desc, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from apps.api.api.services import audit
from apps.api.api.services.audit import get_actor_login
from apps.api.api.v8.flags import is_v8, request_flag_cache
from apps.api.api.v8.settings.connectors_registry import connector_registry
from apps.api.api.v8.settings.rbac import PERMISSIONS, has_permission
from packages.db.database import get_db
from packages.db.models import AuditEvent, DigestConfig, Org, Role, RoleBinding, SourceConnection


router = APIRouter(
    prefix="/v8/orgs/{org_id}/settings",
    tags=["v8-settings"],
    dependencies=[Depends(request_flag_cache)],
)

DEFAULT_DIGEST_WIDGETS = [
    "memory_score",
    "agent_loads",
    "active_repos",
    "top_skill",
    "skill_gaps",
    "roi_multiplier",
]


class RolePayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=512)
    permissions: list[str] = Field(default_factory=list)


class BindingPayload(BaseModel):
    role_id: str
    principal_type: Literal["user", "team"] = "user"
    principal_id: str = Field(min_length=1, max_length=255)
    scope_expression: dict[str, object] | str | None = Field(default_factory=dict)


class PermissionCheckPayload(BaseModel):
    principal_id: str
    permission: str
    scope: dict[str, object] = Field(default_factory=dict)


class DigestConfigPayload(BaseModel):
    title: str = Field(default="Weekly AI Readiness Digest", min_length=1, max_length=255)
    subject: str = Field(default="Your Weekly AI Readiness Report", min_length=1, max_length=255)
    frequency: str = Field(default="weekly", max_length=32)
    recipients: list[str] = Field(default_factory=list)
    widgets: list[str] = Field(default_factory=list)
    layout: dict[str, object] = Field(default_factory=dict)


async def _assert_v8_org(org_id: str, current_org_id: str, db: AsyncSession) -> None:
    if org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Org access denied")
    if not await is_v8(org_id, db):
        raise HTTPException(status_code=404, detail="v8 Settings is disabled")


def _role_response(role: Role) -> dict[str, object]:
    return {
        "id": role.id,
        "org_id": role.org_id,
        "name": role.name,
        "description": role.description,
        "permissions": list(role.permissions or []),
        "created_at": role.created_at,
        "updated_at": role.updated_at,
    }


def _binding_response(binding: RoleBinding, role: Role | None = None) -> dict[str, object]:
    return {
        "id": binding.id,
        "org_id": binding.org_id,
        "role_id": binding.role_id,
        "role_name": role.name if role else None,
        "principal_type": binding.principal_type,
        "principal_id": binding.principal_id,
        "scope_expression": binding.scope_expression or {},
        "created_at": binding.created_at,
        "updated_at": binding.updated_at,
    }


def _digest_response(config: DigestConfig) -> dict[str, object]:
    return {
        "id": config.id,
        "org_id": config.org_id,
        "title": config.title,
        "subject": config.subject,
        "frequency": config.frequency,
        "recipients": list(config.recipients or []),
        "widgets": list(config.widgets or DEFAULT_DIGEST_WIDGETS),
        "layout": dict(config.layout or {}),
        "created_at": config.created_at,
        "updated_at": config.updated_at,
    }


async def _load_or_create_digest_config(db: AsyncSession, org_id: str) -> DigestConfig:
    config = (await db.execute(select(DigestConfig).where(DigestConfig.org_id == org_id))).scalar_one_or_none()
    if config is not None:
        if not config.widgets:
            config.widgets = DEFAULT_DIGEST_WIDGETS
        return config
    config = DigestConfig(
        org_id=org_id,
        widgets=DEFAULT_DIGEST_WIDGETS,
        recipients=[],
        layout={"columns": 2},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(config)
    await db.flush()
    return config


@router.get("")
async def get_settings_home(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    return {
        "org": {
            "id": org.id,
            "name": org.name,
            "login": org.login,
            "plan": org.plan,
        },
        "tabs": ["teams", "rbac", "sso", "connectors", "admin-audit", "billing", "notifications"],
    }


@router.get("/teams")
async def get_settings_teams(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    from apps.api.api.routes.orgs import _team_rows

    rows = await _team_rows(org_id, db)
    return {"teams": rows, "total": len(rows)}


@router.get("/rbac")
async def list_rbac(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    roles = (await db.execute(select(Role).where(Role.org_id == org_id).order_by(Role.name))).scalars().all()
    binding_rows = (
        await db.execute(
            select(RoleBinding, Role)
            .join(Role, Role.id == RoleBinding.role_id)
            .where(RoleBinding.org_id == org_id)
            .order_by(RoleBinding.created_at.desc())
        )
    ).all()
    return {
        "permissions": PERMISSIONS,
        "roles": [_role_response(role) for role in roles],
        "bindings": [_binding_response(binding, role) for binding, role in binding_rows],
    }


@router.post("/rbac/roles", status_code=201)
async def create_role(
    org_id: str,
    payload: RolePayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    invalid = [permission for permission in payload.permissions if permission not in PERMISSIONS and not permission.endswith("*")]
    if invalid:
        raise HTTPException(status_code=422, detail=f"Unknown permissions: {', '.join(invalid)}")
    role = Role(org_id=org_id, name=payload.name.strip(), description=payload.description, permissions=payload.permissions)
    db.add(role)
    try:
        await db.flush()
        await audit.emit(
            db,
            org_id,
            "settings.rbac_role_created",
            "created",
            f"Created RBAC role {role.name}",
            actor_login=get_actor_login(request),
            resource_type="role",
            resource_id=role.id,
            metadata={"permissions": role.permissions},
        )
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not create role") from exc
    return _role_response(role)


@router.post("/rbac/bindings", status_code=201)
async def create_binding(
    org_id: str,
    payload: BindingPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    role = await db.get(Role, payload.role_id)
    if role is None or role.org_id != org_id:
        raise HTTPException(status_code=404, detail="Role not found")
    binding = RoleBinding(
        org_id=org_id,
        role_id=role.id,
        principal_type=payload.principal_type,
        principal_id=payload.principal_id,
        scope_expression=payload.scope_expression or {},
    )
    db.add(binding)
    try:
        await db.flush()
        await audit.emit(
            db,
            org_id,
            "settings.rbac_binding_created",
            "created",
            f"Bound role {role.name} to {binding.principal_id}",
            actor_login=get_actor_login(request),
            resource_type="role_binding",
            resource_id=binding.id,
            metadata={"role_id": role.id, "scope_expression": binding.scope_expression or {}},
        )
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not create role binding") from exc
    return _binding_response(binding, role)


@router.post("/rbac/check")
async def check_permission(
    org_id: str,
    payload: PermissionCheckPayload,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    allowed = await has_permission(
        db,
        org_id=org_id,
        principal_id=payload.principal_id,
        permission=payload.permission,
        scope=payload.scope,
    )
    return {"allowed": allowed}


@router.get("/sso")
async def get_sso(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    settings = org.settings if isinstance(org.settings, dict) else {}
    return {
        "workos_org_id": org.workos_org_id,
        "saml_enabled": bool(org.workos_org_id),
        "oidc_enabled": bool(settings.get("oidc_enabled")),
        "scim_enabled": bool(settings.get("scim_enabled")),
        "managed_by": "WorkOS",
    }


@router.get("/connectors")
async def get_connectors(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    connections = (
        await db.execute(select(SourceConnection).where(SourceConnection.org_id == org_id))
    ).scalars().all()
    by_source_type = {connection.source_type: connection for connection in connections}
    connectors = []
    for item in connector_registry():
        source_type = item.get("source_type")
        connection = by_source_type.get(str(source_type)) if source_type else None
        connectors.append(
            {
                **item,
                "connected": connection is not None,
                "connection_status": connection.status if connection else None,
                "last_connected_at": connection.last_connected_at if connection else None,
            }
        )
    return {"connectors": connectors}


@router.get("/admin-audit")
async def get_admin_audit(
    org_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    try:
        events = (
            await db.execute(
                select(AuditEvent)
                .where(
                    AuditEvent.org_id == org_id,
                    or_(
                        AuditEvent.event_type.like("settings.%"),
                        AuditEvent.event_type.like("member.%"),
                        AuditEvent.event_type == "api_key_rotated",
                    ),
                )
                .order_by(desc(AuditEvent.created_at))
                .limit(max(1, min(limit, 100)))
            )
        ).scalars().all()
    except SQLAlchemyError:
        events = []
    return {
        "events": [
            {
                "id": event.id,
                "event_type": event.event_type,
                "actor_login": event.actor_login,
                "action": event.action,
                "summary": event.summary,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "severity": event.severity,
                "created_at": event.created_at,
            }
            for event in events
        ]
    }


@router.get("/billing")
async def get_billing(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    org = await db.get(Org, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Org not found")
    return {
        "plan": org.plan,
        "seat_count": org.seat_count,
        "seat_limit": org.plan_seat_limit,
        "stripe_customer_id": org.stripe_customer_id,
        "stripe_subscription_id": org.stripe_subscription_id,
        "stripe_subscription_status": org.stripe_subscription_status,
    }


@router.get("/notifications/digest")
async def get_notifications_digest(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    config = await _load_or_create_digest_config(db, org_id)
    await db.commit()
    return _digest_response(config)


@router.put("/notifications/digest")
async def update_notifications_digest(
    org_id: str,
    payload: DigestConfigPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_org_id: str = Depends(get_current_org_id),
) -> dict[str, object]:
    await _assert_v8_org(org_id, current_org_id, db)
    config = await _load_or_create_digest_config(db, org_id)
    config.title = payload.title
    config.subject = payload.subject
    config.frequency = payload.frequency or "weekly"
    config.recipients = [recipient.strip() for recipient in payload.recipients if recipient.strip()]
    config.widgets = payload.widgets or DEFAULT_DIGEST_WIDGETS
    config.layout = payload.layout or {}
    config.updated_at = datetime.utcnow()
    await audit.emit(
        db,
        org_id,
        "settings.notifications_updated",
        "updated",
        "Updated digest notification settings",
        actor_login=get_actor_login(request),
        resource_type="digest_config",
        resource_id=config.id,
        metadata={"frequency": config.frequency, "recipient_count": len(config.recipients)},
    )
    await db.commit()
    return _digest_response(config)
