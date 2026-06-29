from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InvoiceCreate(BaseModel):
    tenant_id: uuid.UUID
    subscription_id: Optional[uuid.UUID] = None
    amount_due: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="USD", max_length=10)
    due_date: Optional[date] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    billing_details: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    amount_due: Optional[Decimal] = Field(None, ge=0)
    amount_paid: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    due_date: Optional[date] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    line_items: Optional[List[Dict[str, Any]]] = None
    billing_details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class InvoiceStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(draft|open|paid|void|uncollectible)$")
    amount_paid: Optional[Decimal] = Field(None, ge=0)
    paid_at: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    subscription_id: Optional[uuid.UUID]
    invoice_number: str
    status: str
    amount_due: Decimal
    amount_paid: Decimal
    currency: str
    due_date: Optional[date]
    paid_at: Optional[datetime]
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    line_items: List[Dict[str, Any]]
    billing_details: Dict[str, Any]
    notes: Optional[str]
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
