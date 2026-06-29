from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.tenant_settings.models.tenant_setting import TenantSetting
from app.tenant_settings.schemas.tenant_setting import TenantSettingUpsert


class TenantSettingService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self, tenant_id: UUID) -> List[TenantSetting]:
        return (
            self.db.query(TenantSetting)
            .filter(TenantSetting.tenant_id == tenant_id)
            .order_by(TenantSetting.key)
            .all()
        )

    def get_by_key(self, tenant_id: UUID, key: str) -> TenantSetting:
        obj = (
            self.db.query(TenantSetting)
            .filter(TenantSetting.tenant_id == tenant_id, TenantSetting.key == key)
            .first()
        )
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting '{key}' not found for tenant {tenant_id}",
            )
        return obj

    def upsert(
        self,
        tenant_id: UUID,
        key: str,
        data: TenantSettingUpsert,
    ) -> TenantSetting:
        obj = (
            self.db.query(TenantSetting)
            .filter(TenantSetting.tenant_id == tenant_id, TenantSetting.key == key)
            .first()
        )
        if obj:
            obj.value = data.value
            obj.description = data.description
            obj.is_encrypted = data.is_encrypted
        else:
            obj = TenantSetting(
                tenant_id=tenant_id,
                key=key,
                value=data.value,
                description=data.description,
                is_encrypted=data.is_encrypted,
            )
            self.db.add(obj)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, tenant_id: UUID, key: str) -> None:
        obj = (
            self.db.query(TenantSetting)
            .filter(TenantSetting.tenant_id == tenant_id, TenantSetting.key == key)
            .first()
        )
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting '{key}' not found for tenant {tenant_id}",
            )
        self.db.delete(obj)
        self.db.commit()
