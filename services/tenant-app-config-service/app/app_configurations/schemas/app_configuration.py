from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class AppConfigUpsert(BaseModel):
    config_key: str = Field(..., max_length=255)
    config_value: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    is_encrypted: bool = False


class AppConfigResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    app_id: UUID
    config_key: str
    config_value: Optional[str]
    is_encrypted: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
