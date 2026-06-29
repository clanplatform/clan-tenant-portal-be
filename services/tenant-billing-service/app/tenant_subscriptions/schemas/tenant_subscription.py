from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionCreate(BaseModel):
    tenant_id: uuid.UUID
    plan_id: uuid.UUID
    billing_cycle: str = Field(default="monthly", pattern="^(monthly|yearly)$")
    trial_end: Optional[datetime] = None
    payment_method_id: Optional[uuid.UUID] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SubscriptionUpdate(BaseModel):
    plan_id: Optional[uuid.UUID] = None
    billing_cycle: Optional[str] = Field(None, pattern="^(monthly|yearly)$")
    status: Optional[str] = Field(
        None, pattern="^(active|cancelled|past_due|trialing|expired)$"
    )
    trial_end: Optional[datetime] = None
    cancel_at: Optional[datetime] = None
    payment_method_id: Optional[uuid.UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class SubscriptionCancelRequest(BaseModel):
    cancel_at_period_end: bool = False
    reason: Optional[str] = None


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    plan_id: uuid.UUID
    status: str
    billing_cycle: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    trial_end: Optional[datetime]
    cancel_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    payment_method_id: Optional[uuid.UUID]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, obj: Any) -> "SubscriptionResponse":
        data = {
            "id": obj.id,
            "tenant_id": obj.tenant_id,
            "plan_id": obj.plan_id,
            "status": obj.status,
            "billing_cycle": obj.billing_cycle,
            "current_period_start": obj.current_period_start,
            "current_period_end": obj.current_period_end,
            "trial_end": obj.trial_end,
            "cancel_at": obj.cancel_at,
            "cancelled_at": obj.cancelled_at,
            "payment_method_id": obj.payment_method_id,
            "metadata": obj.metadata_ or {},
            "is_deleted": obj.is_deleted,
            "deleted_at": obj.deleted_at,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)
