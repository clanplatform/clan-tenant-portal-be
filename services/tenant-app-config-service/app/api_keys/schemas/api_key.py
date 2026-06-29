from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(..., max_length=255)
    scopes: List[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)


class ApiKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    scopes: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class ApiKeyResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    key_prefix: str
    scopes: List[str]
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreateResponse(ApiKeyResponse):
    """Returned only on creation — raw_key is shown once and never stored."""

    raw_key: str
