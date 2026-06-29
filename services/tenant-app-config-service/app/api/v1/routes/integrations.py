from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.integrations.schemas.integration import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationResponse,
    IntegrationTestResult,
)
from app.integrations.services.integration_service import integration_service

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/", response_model=List[IntegrationResponse])
def list_integrations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return integration_service.list(db, tenant_id)


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
def create_integration(
    body: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return integration_service.create(db, tenant_id, body)


@router.get("/{integration_id}", response_model=IntegrationResponse)
def get_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return integration_service.get_by_id(db, integration_id, tenant_id)


@router.put("/{integration_id}", response_model=IntegrationResponse)
def update_integration(
    integration_id: UUID,
    body: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return integration_service.update(db, integration_id, tenant_id, body)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    integration_service.soft_delete(db, integration_id, tenant_id)


@router.post("/{integration_id}/test", response_model=IntegrationTestResult)
def test_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    result = integration_service.test_connection(db, integration_id, tenant_id)
    return IntegrationTestResult(**result)
