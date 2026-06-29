from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.api_keys.schemas.api_key import (
    ApiKeyCreate,
    ApiKeyUpdate,
    ApiKeyResponse,
    ApiKeyCreateResponse,
)
from app.api_keys.services.api_key_service import api_key_service

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.get("/", response_model=List[ApiKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return api_key_service.list(db, tenant_id)


@router.post("/", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    body: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    api_key, raw_key = api_key_service.create(db, tenant_id, body)
    response_data = ApiKeyResponse.model_validate(api_key).model_dump()
    response_data["raw_key"] = raw_key
    return ApiKeyCreateResponse(**response_data)


@router.get("/{key_id}", response_model=ApiKeyResponse)
def get_api_key(
    key_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return api_key_service.get_by_id(db, key_id, tenant_id)


@router.put("/{key_id}", response_model=ApiKeyResponse)
def update_api_key(
    key_id: UUID,
    body: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return api_key_service.update(db, key_id, tenant_id, body)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(
    key_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    api_key_service.revoke(db, key_id, tenant_id)
