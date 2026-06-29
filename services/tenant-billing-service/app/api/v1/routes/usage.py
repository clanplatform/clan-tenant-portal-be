import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.usage_records.schemas.usage_record import (
    UsageRecordCreate,
    UsageRecordResponse,
    UsageSummaryResponse,
)
from app.usage_records.services import usage_record_service

router = APIRouter(prefix="/usage", tags=["Usage Records"])


def _resolve_tenant_id(current_user: dict) -> uuid.UUID:
    jwt_tenant = current_user.get("tenant_id")
    role = current_user.get("role")
    if role == "internal":
        return None  # internal callers may pass tenant_id in the body
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


@router.get("/", response_model=List[UsageRecordResponse])
def list_usage(
    metric_key: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id required for listing usage",
        )
    records = usage_record_service.list_records(
        db,
        tenant_id=tenant_id,
        metric_key=metric_key,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit,
    )
    return [UsageRecordResponse.from_orm_model(r) for r in records]


@router.post("/", response_model=UsageRecordResponse, status_code=201)
def record_usage(
    data: UsageRecordCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    # Non-internal users can only record for their own tenant
    role = current_user.get("role")
    if role not in ("internal", "admin") and tenant_id is not None:
        data = data.model_copy(update={"tenant_id": tenant_id})
    record = usage_record_service.record(db, data)
    return UsageRecordResponse.from_orm_model(record)


@router.get("/summary", response_model=UsageSummaryResponse)
def get_usage_summary(
    period_start: datetime = Query(...),
    period_end: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id required for usage summary",
        )
    summary = usage_record_service.get_summary(db, tenant_id, period_start, period_end)
    return UsageSummaryResponse(
        tenant_id=tenant_id,
        period_start=period_start,
        period_end=period_end,
        summary=summary,
    )
