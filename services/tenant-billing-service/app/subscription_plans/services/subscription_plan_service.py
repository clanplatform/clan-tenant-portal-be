import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.subscription_plans.exceptions import PlanAlreadyExists, PlanNotFound
from app.subscription_plans.models.subscription_plan import SubscriptionPlan
from app.subscription_plans.schemas.subscription_plan import PlanCreate, PlanUpdate


def get_by_id(db: Session, plan_id: uuid.UUID) -> SubscriptionPlan:
    plan = (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.id == plan_id, SubscriptionPlan.is_deleted == False)
        .first()
    )
    if not plan:
        raise PlanNotFound(f"Subscription plan with id '{plan_id}' not found")
    return plan


def get_by_code(db: Session, code: str) -> SubscriptionPlan:
    plan = (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.code == code, SubscriptionPlan.is_deleted == False)
        .first()
    )
    if not plan:
        raise PlanNotFound(f"Subscription plan with code '{code}' not found")
    return plan


def list_active(db: Session, skip: int = 0, limit: int = 100) -> List[SubscriptionPlan]:
    return (
        db.query(SubscriptionPlan)
        .filter(
            SubscriptionPlan.is_active == True,
            SubscriptionPlan.is_deleted == False,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def list_all(db: Session, skip: int = 0, limit: int = 100) -> List[SubscriptionPlan]:
    return (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.is_deleted == False)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(db: Session, data: PlanCreate) -> SubscriptionPlan:
    existing = (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.code == data.code, SubscriptionPlan.is_deleted == False)
        .first()
    )
    if existing:
        raise PlanAlreadyExists(f"Subscription plan with code '{data.code}' already exists")

    plan = SubscriptionPlan(
        name=data.name,
        code=data.code,
        description=data.description,
        price_monthly=data.price_monthly,
        price_yearly=data.price_yearly,
        currency=data.currency,
        features=data.features,
        limits=data.limits,
        is_active=data.is_active,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update(db: Session, plan_id: uuid.UUID, data: PlanUpdate) -> SubscriptionPlan:
    plan = get_by_id(db, plan_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan


def soft_delete(db: Session, plan_id: uuid.UUID) -> SubscriptionPlan:
    plan = get_by_id(db, plan_id)
    plan.is_deleted = True
    plan.deleted_at = datetime.now(timezone.utc)
    plan.is_active = False
    db.commit()
    db.refresh(plan)
    return plan
