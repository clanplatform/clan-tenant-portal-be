from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class WebhookCreate(BaseModel):
    name: str = Field(..., max_length=255)
    url: str = Field(..., max_length=500)
    events: List[str] = Field(default_factory=list)
    retry_count: int = Field(default=3, ge=0, le=10)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    description: Optional[str] = Field(None, max_length=500)


class WebhookUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=500)
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None
    retry_count: Optional[int] = Field(None, ge=0, le=10)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300)


class WebhookResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    url: str
    events: List[str]
    is_active: bool
    retry_count: int
    timeout_seconds: int
    last_triggered_at: Optional[datetime]
    last_status: Optional[str]
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WebhookCreateResponse(WebhookResponse):
    """Returned only on creation — raw_secret is shown once and never stored."""

    raw_secret: str
