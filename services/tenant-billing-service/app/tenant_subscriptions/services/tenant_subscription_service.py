import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.tenant_subscriptions.exceptions import (
    SubscriptionAlreadyExists,
    SubscriptionNotFound,
)
from app.tenant_subscriptions.models.tenant_subscription import TenantSubscription
from app.tenant_subscriptions.schemas.tenant_subscription import (
    SubscriptionCancelRequest,
    SubscriptionCreate,
    SubscriptionUpdate,
)


def get_by_id(db: Session, subscription_id: uuid.UUID, tenant_id: Optional[uuid.UUID] = None) -> TenantSubscription:
    query = db.query(TenantSubscription).filter(
        TenantSubscription.id == subscription_id,
        TenantSubscription.is_deleted == False,
    )
    if tenant_id is not None:
        query = query.filter(TenantSubscription.tenant_id == tenant_id)
    sub = query.first()
    if not sub:
        raise SubscriptionNotFound(f"Subscription with id '{subscription_id}' not found")
    return sub


def get_by_tenant_id(
    db: Session,
    tenant_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> List[TenantSubscription]:
    return (
        db.query(TenantSubscription)
        .filter(
            TenantSubscription.tenant_id == tenant_id,
            TenantSubscription.is_deleted == False,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_active_for_tenant(db: Session, tenant_id: uuid.UUID) -> Optional[TenantSubscription]:
    return (
        db.query(TenantSubscription)
        .filter(
            TenantSubscription.tenant_id == tenant_id,
            TenantSubscription.status == "active",
            TenantSubscription.is_deleted == False,
        )
        .first()
    )


def create(db: Session, data: SubscriptionCreate) -> TenantSubscription:
    existing = get_active_for_tenant(db, data.tenant_id)
    if existing:
        raise SubscriptionAlreadyExists(
            f"An active subscription already exists for tenant '{data.tenant_id}'"
        )

    now = datetime.now(timezone.utc)
    if data.billing_cycle == "yearly":
        period_end = now + timedelta(days=365)
    else:
        period_end = now + timedelta(days=30)

    sub = TenantSubscription(
        tenant_id=data.tenant_id,
        plan_id=data.plan_id,
        billing_cycle=data.billing_cycle,
        status="active",
        current_period_start=now,
        current_period_end=period_end,
        trial_end=data.trial_end,
        payment_method_id=data.payment_method_id,
        metadata_=data.metadata,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def update(
    db: Session,
    subscription_id: uuid.UUID,
    tenant_id: uuid.UUID,
    data: SubscriptionUpdate,
) -> TenantSubscription:
    sub = get_by_id(db, subscription_id, tenant_id)
    update_data = data.model_dump(exclude_unset=True)

    if "metadata" in update_data:
        sub.metadata_ = update_data.pop("metadata")

    for field, value in update_data.items():
        setattr(sub, field, value)

    db.commit()
    db.refresh(sub)
    return sub


def cancel(
    db: Session,
    subscription_id: uuid.UUID,
    tenant_id: uuid.UUID,
    request: SubscriptionCancelRequest,
) -> TenantSubscription:
    sub = get_by_id(db, subscription_id, tenant_id)
    now = datetime.now(timezone.utc)

    if request.cancel_at_period_end:
        sub.cancel_at = sub.current_period_end
        sub.status = "active"
    else:
        sub.status = "cancelled"
        sub.cancelled_at = now
        sub.cancel_at = now

    db.commit()
    db.refresh(sub)
    return sub


def upgrade_plan(
    db: Session,
    subscription_id: uuid.UUID,
    tenant_id: uuid.UUID,
    new_plan_id: uuid.UUID,
    billing_cycle: Optional[str] = None,
) -> TenantSubscription:
    sub = get_by_id(db, subscription_id, tenant_id)
    sub.plan_id = new_plan_id
    if billing_cycle:
        sub.billing_cycle = billing_cycle
        now = datetime.now(timezone.utc)
        sub.current_period_start = now
        if billing_cycle == "yearly":
            sub.current_period_end = now + timedelta(days=365)
        else:
            sub.current_period_end = now + timedelta(days=30)
    db.commit()
    db.refresh(sub)
    return sub
