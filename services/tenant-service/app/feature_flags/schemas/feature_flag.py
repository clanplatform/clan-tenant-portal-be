import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class FeatureFlagUpsert(BaseModel):
    is_enabled: bool = False
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    description: Optional[str] = Field(None, max_length=500)


class FeatureFlagResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    feature_key: str
    is_enabled: bool
    config: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FeatureFlagCheckResponse(BaseModel):
    tenant_id: uuid.UUID
    feature_key: str
    is_enabled: bool
