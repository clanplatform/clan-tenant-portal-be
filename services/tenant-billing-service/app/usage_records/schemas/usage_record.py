from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class UsageRecordCreate(BaseModel):
    tenant_id: uuid.UUID
    metric_key: str = Field(..., max_length=255)
    metric_value: Decimal = Field(..., ge=0)
    period_start: datetime
    period_end: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UsageRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    metric_key: str
    metric_value: Decimal
    period_start: datetime
    period_end: datetime
    recorded_at: datetime
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime

    @classmethod
    def from_orm_model(cls, obj: Any) -> "UsageRecordResponse":
        return cls(
            id=obj.id,
            tenant_id=obj.tenant_id,
            metric_key=obj.metric_key,
            metric_value=obj.metric_value,
            period_start=obj.period_start,
            period_end=obj.period_end,
            recorded_at=obj.recorded_at,
            metadata=obj.metadata_ or {},
            created_at=obj.created_at,
        )


class UsageSummaryResponse(BaseModel):
    tenant_id: uuid.UUID
    period_start: datetime
    period_end: datetime
    summary: Dict[str, Decimal]
