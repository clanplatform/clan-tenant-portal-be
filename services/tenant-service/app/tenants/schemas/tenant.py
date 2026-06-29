import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


VALID_STATUSES = {"active", "suspended", "trial", "cancelled"}


class TenantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    logo_url: Optional[str] = Field(None, max_length=500)
    timezone: str = Field(default="UTC", max_length=100)
    locale: str = Field(default="en-US", max_length=20)
    max_users: int = Field(default=5, ge=1)
    metadata_: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="metadata")

    model_config = {"populate_by_name": True}


class TenantCreate(TenantBase):
    status: str = Field(default="active")
    plan_id: Optional[uuid.UUID] = None


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    logo_url: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=100)
    locale: Optional[str] = Field(None, max_length=20)
    max_users: Optional[int] = Field(None, ge=1)
    plan_id: Optional[uuid.UUID] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")

    model_config = {"populate_by_name": True}


class TenantStatusUpdate(BaseModel):
    status: str = Field(..., description="One of: active, suspended, trial, cancelled")


class TenantResponse(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    status: str
    plan_id: Optional[uuid.UUID] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    logo_url: Optional[str] = None
    timezone: str
    locale: str
    max_users: int
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata_")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class TenantListResponse(BaseModel):
    items: List[TenantResponse]
    total: int
    skip: int
    limit: int
