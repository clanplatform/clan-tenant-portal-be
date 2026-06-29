from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.feature_flags.models.feature_flag import TenantFeatureFlag
from app.feature_flags.schemas.feature_flag import FeatureFlagUpsert


class FeatureFlagService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self, tenant_id: UUID) -> List[TenantFeatureFlag]:
        return (
            self.db.query(TenantFeatureFlag)
            .filter(TenantFeatureFlag.tenant_id == tenant_id)
            .order_by(TenantFeatureFlag.feature_key)
            .all()
        )

    def get_by_key(self, tenant_id: UUID, key: str) -> TenantFeatureFlag:
        obj = (
            self.db.query(TenantFeatureFlag)
            .filter(
                TenantFeatureFlag.tenant_id == tenant_id,
                TenantFeatureFlag.feature_key == key,
            )
            .first()
        )
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature flag '{key}' not found for tenant {tenant_id}",
            )
        return obj

    def upsert(
        self,
        tenant_id: UUID,
        key: str,
        data: FeatureFlagUpsert,
    ) -> TenantFeatureFlag:
        obj = (
            self.db.query(TenantFeatureFlag)
            .filter(
                TenantFeatureFlag.tenant_id == tenant_id,
                TenantFeatureFlag.feature_key == key,
            )
            .first()
        )
        if obj:
            obj.is_enabled = data.is_enabled
            obj.config = data.config or {}
            obj.description = data.description
        else:
            obj = TenantFeatureFlag(
                tenant_id=tenant_id,
                feature_key=key,
                is_enabled=data.is_enabled,
                config=data.config or {},
                description=data.description,
            )
            self.db.add(obj)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def is_enabled(self, tenant_id: UUID, key: str) -> bool:
        obj = (
            self.db.query(TenantFeatureFlag)
            .filter(
                TenantFeatureFlag.tenant_id == tenant_id,
                TenantFeatureFlag.feature_key == key,
            )
            .first()
        )
        if not obj:
            return False
        return obj.is_enabled
