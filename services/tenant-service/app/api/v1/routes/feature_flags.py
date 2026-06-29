from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.feature_flags.schemas.feature_flag import (
    FeatureFlagCheckResponse,
    FeatureFlagResponse,
    FeatureFlagUpsert,
)
from app.feature_flags.services.feature_flag_service import FeatureFlagService

router = APIRouter(prefix="/tenants", tags=["feature-flags"])


@router.get("/{tenant_id}/features", response_model=List[FeatureFlagResponse])
def list_feature_flags(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all feature flags for a tenant."""
    return FeatureFlagService(db).get_all(tenant_id)


@router.put("/{tenant_id}/features/{feature_key}", response_model=FeatureFlagResponse)
def upsert_feature_flag(
    tenant_id: UUID,
    feature_key: str,
    data: FeatureFlagUpsert,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create or update a feature flag for a tenant."""
    return FeatureFlagService(db).upsert(tenant_id, feature_key, data)


@router.get(
    "/{tenant_id}/features/{feature_key}/check",
    response_model=FeatureFlagCheckResponse,
)
def check_feature_flag(
    tenant_id: UUID,
    feature_key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Check whether a specific feature flag is enabled for a tenant."""
    enabled = FeatureFlagService(db).is_enabled(tenant_id, feature_key)
    return FeatureFlagCheckResponse(
        tenant_id=tenant_id,
        feature_key=feature_key,
        is_enabled=enabled,
    )
