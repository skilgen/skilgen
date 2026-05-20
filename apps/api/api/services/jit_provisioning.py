from __future__ import annotations

import hashlib
import secrets
from typing import Literal

from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.services.personal_domains import is_personal_domain
from apps.api.api.services import audit
from packages.db.models import Org, Role, RoleBinding, User


ProvisionSource = Literal["workos", "magic_link", "github_oauth"]


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _email_domain(email: str) -> str:
    if "@" not in email:
        return ""
    return email.rsplit("@", 1)[-1].strip().lower()


def _valid_email(email: str) -> bool:
    domain = _email_domain(email)
    return bool(domain and "." in domain and not any(char.isspace() for char in email))


def _generate_org_api_key() -> str:
    return f"sk-{secrets.token_urlsafe(32)}"


def _placeholder_github_org_id(seed: str) -> int:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)
    return -int(value or 1)


async def _ensure_role(
    db: AsyncSession,
    *,
    org_id: str,
    name: str,
    permissions: list[str],
    description: str | None = None,
) -> Role:
    existing = (await db.execute(select(Role).where(Role.org_id == org_id, Role.name == name))).scalar_one_or_none()
    if existing is not None:
        return existing
    role = Role(
        org_id=org_id,
        name=name,
        description=description,
        permissions=permissions,
    )
    db.add(role)
    await db.flush()
    return role


async def _ensure_binding(
    db: AsyncSession,
    *,
    org_id: str,
    role_id: str,
    principal_id: str,
) -> None:
    existing = (
        await db.execute(
            select(RoleBinding.id).where(
                RoleBinding.org_id == org_id,
                RoleBinding.role_id == role_id,
                RoleBinding.principal_type == "user",
                RoleBinding.principal_id == principal_id,
            )
        )
    ).scalar_one_or_none()
    if existing:
        return
    db.add(
        RoleBinding(
            org_id=org_id,
            role_id=role_id,
            principal_type="user",
            principal_id=principal_id,
            scope_expression={},
        )
    )


async def ensure_from_login(
    db: AsyncSession,
    *,
    email: str,
    name: str | None,
    source: ProvisionSource,
    request: Request | None = None,
) -> tuple[Org, User, bool]:
    normalized_email = _normalize_email(email)
    if not _valid_email(normalized_email):
        raise HTTPException(status_code=422, detail="Invalid email")

    domain = _email_domain(normalized_email)
    personal = is_personal_domain(domain)

    existing_user = (
        await db.execute(select(User).where(User.email == normalized_email).limit(1))
    ).scalar_one_or_none()
    if existing_user is not None:
        org = await db.get(Org, existing_user.org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Org not found")
        if org.is_suspended:
            raise HTTPException(status_code=403, detail="Org suspended")
        role_name = existing_user.role if existing_user.role in {"owner", "developer"} else "developer"
        permissions = ["*"] if role_name == "owner" else ["settings.read", "settings.connectors.manage"]
        role = await _ensure_role(db, org_id=org.id, name=role_name, permissions=permissions, description="Default self-serve role")
        await _ensure_binding(db, org_id=org.id, role_id=role.id, principal_id=existing_user.email)
        return org, existing_user, False

    org: Org | None = None
    domain_blocked = False
    if not personal:
        candidate = (await db.execute(select(Org).where(Org.login == domain).limit(1))).scalar_one_or_none()
        if candidate is not None:
            if candidate.is_suspended:
                raise HTTPException(status_code=403, detail="Org suspended")
            if bool(getattr(candidate, "auto_join_domain", True)):
                org = candidate
            else:
                domain_blocked = True

    created_org = False
    if org is None:
        created_org = True
        if personal:
            org_login = f"user-{hashlib.sha256(normalized_email.encode('utf-8')).hexdigest()[:12]}"
        elif domain_blocked:
            org_login = f"{domain}-{hashlib.sha256(normalized_email.encode('utf-8')).hexdigest()[:6]}"
        else:
            org_login = domain
        org = Org(
            github_org_id=_placeholder_github_org_id(org_login),
            login=org_login,
            name=str(domain or org_login),
            plan="free",
            seat_count=0,
            api_key=_generate_org_api_key(),
        )
        db.add(org)
        await db.flush()
        await audit.emit(
            db,
            org.id,
            "org.created",
            "created",
            f"Created org for {domain}",
            actor_login=normalized_email,
            actor_ip=request.client.host if request and request.client else None,
            resource_type="org",
            resource_id=org.id,
            metadata={"source": source, "email": normalized_email, "domain": domain},
        )

    role_name = "owner" if created_org else "developer"
    permissions = ["*"] if role_name == "owner" else ["settings.read", "settings.connectors.manage"]
    role = await _ensure_role(
        db,
        org_id=org.id,
        name=role_name,
        permissions=permissions,
        description="Default self-serve role",
    )

    user = User(
        org_id=org.id,
        email=normalized_email,
        name=name.strip() if isinstance(name, str) and name.strip() else None,
        role=role_name,
        source=source,
    )
    db.add(user)
    await db.flush()
    await _ensure_binding(db, org_id=org.id, role_id=role.id, principal_id=user.email)
    return org, user, created_org
