from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class IntegrationCreate(BaseModel):
    integration_type: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    credentials: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="active", max_length=50)


class IntegrationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    credentials: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, max_length=50)
    error_message: Optional[str] = None


class IntegrationResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    integration_type: str
    name: str
    credentials: Dict[str, Any]
    settings: Dict[str, Any]
    status: str
    error_message: Optional[str]
    last_synced_at: Optional[datetime]
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IntegrationTestResult(BaseModel):
    success: bool
    message: str
