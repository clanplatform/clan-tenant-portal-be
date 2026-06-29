from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.webhooks.schemas.webhook import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookCreateResponse,
)
from app.webhooks.services.webhook_service import webhook_service

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/", response_model=List[WebhookResponse])
def list_webhooks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return webhook_service.list(db, tenant_id)


@router.post("/", response_model=WebhookCreateResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    body: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    webhook, raw_secret = webhook_service.create(db, tenant_id, body)
    response_data = WebhookResponse.model_validate(webhook).model_dump()
    response_data["raw_secret"] = raw_secret
    return WebhookCreateResponse(**response_data)


@router.get("/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return webhook_service.get_by_id(db, webhook_id, tenant_id)


@router.put("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: UUID,
    body: WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    return webhook_service.update(db, webhook_id, tenant_id, body)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
    webhook_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = UUID(current_user["tenant_id"])
    webhook_service.soft_delete(db, webhook_id, tenant_id)


@router.post("/{webhook_id}/test")
def test_webhook(
    webhook_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    tenant_id = UUID(current_user["tenant_id"])
    return webhook_service.send_test(db, webhook_id, tenant_id)
