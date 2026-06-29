import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TenantDomainCreate(BaseModel):
    domain: str = Field(..., min_length=3, max_length=255)


class TenantDomainResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    domain: str
    is_verified: bool
    is_primary: bool
    verification_token: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DomainVerifyConfirm(BaseModel):
    token: str = Field(..., min_length=1)
