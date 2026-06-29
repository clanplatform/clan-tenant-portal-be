import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.tenant_subscriptions.schemas.tenant_subscription import (
    SubscriptionCancelRequest,
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
)
from app.tenant_subscriptions.services import tenant_subscription_service

router = APIRouter(prefix="/subscriptions", tags=["Tenant Subscriptions"])


def _resolve_tenant_id(current_user: dict, override: uuid.UUID = None) -> uuid.UUID:
    """Return the effective tenant_id, enforcing tenant isolation."""
    role = current_user.get("role")
    if role in ("internal", "admin") and override:
        return override

    jwt_tenant = current_user.get("tenant_id")
    if not jwt_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID not found in token",
        )
    try:
        return uuid.UUID(str(jwt_tenant))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid tenant_id in token",
        )


@router.get("/", response_model=List[SubscriptionResponse])
def list_subscriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    subs = tenant_subscription_service.get_by_tenant_id(db, tenant_id, skip=skip, limit=limit)
    return [SubscriptionResponse.from_orm_model(s) for s in subs]


@router.post("/", response_model=SubscriptionResponse, status_code=201)
def create_subscription(
    data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user, data.tenant_id)
    # Enforce tenant isolation — non-admins can only create for their own tenant
    role = current_user.get("role")
    if role not in ("internal", "admin"):
        data = data.model_copy(update={"tenant_id": tenant_id})
    sub = tenant_subscription_service.create(db, data)
    return SubscriptionResponse.from_orm_model(sub)


@router.get("/{sub_id}", response_model=SubscriptionResponse)
def get_subscription(
    sub_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    sub = tenant_subscription_service.get_by_id(db, sub_id, tenant_id)
    return SubscriptionResponse.from_orm_model(sub)


@router.put("/{sub_id}", response_model=SubscriptionResponse)
def update_subscription(
    sub_id: uuid.UUID,
    data: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    sub = tenant_subscription_service.update(db, sub_id, tenant_id, data)
    return SubscriptionResponse.from_orm_model(sub)


@router.post("/{sub_id}/cancel", response_model=SubscriptionResponse)
def cancel_subscription(
    sub_id: uuid.UUID,
    request: SubscriptionCancelRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    sub = tenant_subscription_service.cancel(db, sub_id, tenant_id, request)
    return SubscriptionResponse.from_orm_model(sub)
