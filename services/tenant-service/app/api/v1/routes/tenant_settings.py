from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.tenant_settings.schemas.tenant_setting import TenantSettingResponse, TenantSettingUpsert
from app.tenant_settings.services.tenant_setting_service import TenantSettingService

router = APIRouter(prefix="/tenants", tags=["tenant-settings"])


@router.get("/{tenant_id}/settings", response_model=List[TenantSettingResponse])
def list_settings(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all settings for a tenant."""
    return TenantSettingService(db).get_all(tenant_id)


@router.get("/{tenant_id}/settings/{key}", response_model=TenantSettingResponse)
def get_setting(
    tenant_id: UUID,
    key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific setting by key for a tenant."""
    return TenantSettingService(db).get_by_key(tenant_id, key)


@router.put("/{tenant_id}/settings/{key}", response_model=TenantSettingResponse)
def upsert_setting(
    tenant_id: UUID,
    key: str,
    data: TenantSettingUpsert,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create or update a setting for a tenant."""
    return TenantSettingService(db).upsert(tenant_id, key, data)


@router.delete(
    "/{tenant_id}/settings/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_setting(
    tenant_id: UUID,
    key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a setting for a tenant."""
    TenantSettingService(db).delete(tenant_id, key)
