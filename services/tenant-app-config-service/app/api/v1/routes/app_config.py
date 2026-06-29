from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.app_configurations.schemas.app_configuration import AppConfigUpsert, AppConfigResponse
from app.app_configurations.services.app_configuration_service import app_configuration_service

router = APIRouter(prefix="/config", tags=["app-config"])


@router.get("/{app_id}", response_model=List[AppConfigResponse])
def get_all_config(
    app_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return app_configuration_service.get_all(db, tenant_id, app_id)


@router.get("/{app_id}/{config_key}", response_model=AppConfigResponse)
def get_config(
    app_id: UUID,
    config_key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return app_configuration_service.get(db, tenant_id, app_id, config_key)


@router.put("/{app_id}/{config_key}", response_model=AppConfigResponse)
def upsert_config(
    app_id: UUID,
    config_key: str,
    body: AppConfigUpsert,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return app_configuration_service.upsert(
        db,
        tenant_id,
        app_id,
        config_key=config_key,
        config_value=body.config_value,
        description=body.description,
        is_encrypted=body.is_encrypted,
    )


@router.delete("/{app_id}/{config_key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(
    app_id: UUID,
    config_key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    app_configuration_service.delete(db, tenant_id, app_id, config_key)
