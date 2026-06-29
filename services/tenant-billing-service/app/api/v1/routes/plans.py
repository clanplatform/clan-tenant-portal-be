import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.subscription_plans.schemas.subscription_plan import (
    PlanCreate,
    PlanResponse,
    PlanUpdate,
)
from app.subscription_plans.services import subscription_plan_service

router = APIRouter(prefix="/plans", tags=["Subscription Plans"])


@router.get("/", response_model=List[PlanResponse])
def list_plans(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if active_only:
        return subscription_plan_service.list_active(db, skip=skip, limit=limit)
    return subscription_plan_service.list_all(db, skip=skip, limit=limit)


@router.post("/", response_model=PlanResponse, status_code=201)
def create_plan(
    data: PlanCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return subscription_plan_service.create(db, data)


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return subscription_plan_service.get_by_id(db, plan_id)


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: uuid.UUID,
    data: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return subscription_plan_service.update(db, plan_id, data)


@router.delete("/{plan_id}", response_model=PlanResponse)
def delete_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return subscription_plan_service.soft_delete(db, plan_id)
