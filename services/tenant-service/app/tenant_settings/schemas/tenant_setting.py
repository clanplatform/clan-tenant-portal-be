import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TenantSettingUpsert(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    is_encrypted: bool = False


class TenantSettingResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    key: str
    value: Optional[str] = None
    description: Optional[str] = None
    is_encrypted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
