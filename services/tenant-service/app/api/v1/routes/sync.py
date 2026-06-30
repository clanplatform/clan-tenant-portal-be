"""
Inbound sync endpoint — receives tenant data pushed from platform-domain-be (admin-service).

Route:  POST /api/v1/sync/tenants
Auth:   x-internal-key header (service-to-service only, no JWT needed)
"""
import re
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.tenants.models.tenant import Tenant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])


# ──────────────────────────────── helpers ─────────────────────────────


def _slugify(value: str) -> str:
    """Convert a string to a URL-safe slug."""
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    return re.sub(r"^-+|-+$", "", value)


def _unique_slug(base: str, db: Session) -> str:
    """Return a slug that doesn't collide with any existing tenant row."""
    slug = _slugify(base)
    counter = 1
    while db.query(Tenant).filter(Tenant.slug == slug).first():
        slug = f"{_slugify(base)}-{counter}"
        counter += 1
    return slug


# ──────────────────────────────── schema ──────────────────────────────


class AdminTenantPayload(BaseModel):
    """Data sent by platform-domain-be when its Tenant record changes."""
    tenant_id: str               # admin-service PK — stored in metadata.admin_tenant_id
    tenant_name: str
    tenant_code: Optional[str] = None   # used as slug seed when creating
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    subscription_plan: Optional[str] = None
    is_active: bool = True


# ──────────────────────────────── endpoint ────────────────────────────


@router.post(
    "/tenants",
    status_code=status.HTTP_200_OK,
)
def sync_tenant_from_admin(
    payload: AdminTenantPayload,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),   # validates x-internal-key (or JWT)
):
    """
    Receive a tenant push from platform-domain-be.

    • If a matching tenant is found (via metadata.admin_tenant_id), update it.
    • If no match, create a new Tenant record and return its id so the admin-service
      can store it as gateway_tenant_ref via the _store_gateway_ref() back-fill.
    """
    # Find existing by stored admin_tenant_id in JSON metadata
    try:
        tenant = (
            db.query(Tenant)
            .filter(text("metadata->>'admin_tenant_id' = :aid"))
            .params(aid=payload.tenant_id)
            .first()
        )
    except Exception:
        tenant = None

    portal_status = "active" if payload.is_active else "suspended"

    if tenant:
        tenant.name = payload.tenant_name
        if payload.contact_email:
            tenant.contact_email = payload.contact_email
        if payload.contact_phone:
            tenant.contact_phone = payload.contact_phone
        tenant.status = portal_status

        # Merge metadata — preserve existing keys, update known ones
        meta = dict(tenant.metadata_ or {})
        meta["admin_tenant_id"] = payload.tenant_id
        if payload.subscription_plan:
            meta["subscription_plan"] = payload.subscription_plan
        tenant.metadata_ = meta

        db.commit()
        db.refresh(tenant)
        logger.info("[sync-inbound] updated portal tenant %s from admin", tenant.id)
    else:
        # Create a new tenant record seeded from admin data
        slug_seed = payload.tenant_code or payload.tenant_name
        slug = _unique_slug(slug_seed, db)

        tenant = Tenant(
            name=payload.tenant_name,
            display_name=payload.tenant_name,
            slug=slug,
            contact_email=payload.contact_email,
            contact_phone=payload.contact_phone,
            status=portal_status,
            metadata_={
                "admin_tenant_id": payload.tenant_id,
                "subscription_plan": payload.subscription_plan,
            },
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        logger.info("[sync-inbound] created portal tenant %s from admin %s", tenant.id, payload.tenant_id)

    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "slug": tenant.slug,
        "status": tenant.status,
    }
