import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.usage_records.models.usage_record import UsageRecord
from app.usage_records.schemas.usage_record import UsageRecordCreate


def record(
    db: Session,
    data: UsageRecordCreate,
) -> UsageRecord:
    usage = UsageRecord(
        tenant_id=data.tenant_id,
        metric_key=data.metric_key,
        metric_value=data.metric_value,
        period_start=data.period_start,
        period_end=data.period_end,
        metadata_=data.metadata,
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return usage


def list_records(
    db: Session,
    tenant_id: uuid.UUID,
    metric_key: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[UsageRecord]:
    query = db.query(UsageRecord).filter(UsageRecord.tenant_id == tenant_id)

    if metric_key:
        query = query.filter(UsageRecord.metric_key == metric_key)
    if from_date:
        query = query.filter(UsageRecord.period_start >= from_date)
    if to_date:
        query = query.filter(UsageRecord.period_end <= to_date)

    return query.offset(skip).limit(limit).all()


def get_summary(
    db: Session,
    tenant_id: uuid.UUID,
    period_start: datetime,
    period_end: datetime,
) -> Dict[str, Decimal]:
    results = (
        db.query(
            UsageRecord.metric_key,
            func.sum(UsageRecord.metric_value).label("total"),
        )
        .filter(
            UsageRecord.tenant_id == tenant_id,
            UsageRecord.period_start >= period_start,
            UsageRecord.period_end <= period_end,
        )
        .group_by(UsageRecord.metric_key)
        .all()
    )

    return {row.metric_key: Decimal(str(row.total)) for row in results}
