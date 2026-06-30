import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.infrastructure.admin_sync_client import sync_to_admin
from app.tenants.exceptions import TenantAlreadyExists, TenantInvalidStatus, TenantNotFound
from app.tenants.models.tenant import Tenant
from app.tenants.schemas.tenant import (
    TenantCreate,
    TenantListResponse,
    TenantResponse,
    TenantStatusUpdate,
    TenantUpdate,
)
from app.tenants.services.tenant_service import TenantService

router = APIRouter(prefix="/tenants", tags=["tenants"])


def _admin_id(tenant: Tenant) -> str | None:
    """Extract stored admin_tenant_id from tenant metadata, if present."""
    meta = tenant.metadata_ or {}
    return meta.get("admin_tenant_id")


@router.get("/", response_model=TenantListResponse)
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all tenants with pagination."""
    items, total = TenantService(db).list(skip=skip, limit=limit)
    return TenantListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new tenant."""
    tenant = TenantService(db).create(data)
    asyncio.create_task(sync_to_admin(
        portal_tenant_id=str(tenant.id),
        admin_tenant_id=_admin_id(tenant),
        name=tenant.name,
        slug=tenant.slug,
        contact_email=tenant.contact_email,
        contact_phone=tenant.contact_phone,
        status=tenant.status,
        subscription_plan=(tenant.metadata_ or {}).get("subscription_plan"),
    ))
    return tenant


@router.get("/slug/{slug}", response_model=TenantResponse)
def get_tenant_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a tenant by its URL slug."""
    return TenantService(db).get_by_slug(slug)


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a tenant by ID."""
    return TenantService(db).get_by_id(tenant_id)


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update tenant details."""
    tenant = TenantService(db).update(tenant_id, data)
    asyncio.create_task(sync_to_admin(
        portal_tenant_id=str(tenant.id),
        admin_tenant_id=_admin_id(tenant),
        name=tenant.name,
        slug=tenant.slug,
        contact_email=tenant.contact_email,
        contact_phone=tenant.contact_phone,
        status=tenant.status,
        subscription_plan=(tenant.metadata_ or {}).get("subscription_plan"),
    ))
    return tenant


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Soft-delete a tenant."""
    TenantService(db).soft_delete(tenant_id)


@router.put("/{tenant_id}/status", response_model=TenantResponse)
async def change_tenant_status(
    tenant_id: UUID,
    data: TenantStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Change the status of a tenant (active/suspended/trial/cancelled)."""
    tenant = TenantService(db).change_status(tenant_id, data)
    asyncio.create_task(sync_to_admin(
        portal_tenant_id=str(tenant.id),
        admin_tenant_id=_admin_id(tenant),
        name=tenant.name,
        slug=tenant.slug,
        contact_email=tenant.contact_email,
        contact_phone=tenant.contact_phone,
        status=tenant.status,
        subscription_plan=(tenant.metadata_ or {}).get("subscription_plan"),
    ))
    return tenant
