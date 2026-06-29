import secrets
import hashlib
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.api_keys.models.api_key import ApiKey
from app.api_keys.schemas.api_key import ApiKeyCreate, ApiKeyUpdate
from app.api_keys.exceptions import ApiKeyNotFound


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


class ApiKeyService:
    def list(self, db: Session, tenant_id: UUID) -> List[ApiKey]:
        return (
            db.query(ApiKey)
            .filter(
                ApiKey.tenant_id == tenant_id,
                ApiKey.is_active == True,
            )
            .all()
        )

    def create(self, db: Session, tenant_id: UUID, data: ApiKeyCreate) -> Tuple[ApiKey, str]:
        raw_key = secrets.token_hex(32)  # 64-char hex string
        key_hash = _hash_key(raw_key)
        key_prefix = raw_key[:8]

        api_key = ApiKey(
            tenant_id=tenant_id,
            name=data.name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=data.scopes,
            expires_at=data.expires_at,
            description=data.description,
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        return api_key, raw_key

    def get_by_id(self, db: Session, key_id: UUID, tenant_id: UUID) -> ApiKey:
        record = (
            db.query(ApiKey)
            .filter(
                ApiKey.id == key_id,
                ApiKey.tenant_id == tenant_id,
            )
            .first()
        )
        if not record:
            raise ApiKeyNotFound(str(key_id))
        return record

    def update(
        self, db: Session, key_id: UUID, tenant_id: UUID, data: ApiKeyUpdate
    ) -> ApiKey:
        record = self.get_by_id(db, key_id, tenant_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return record

    def revoke(self, db: Session, key_id: UUID, tenant_id: UUID) -> None:
        record = self.get_by_id(db, key_id, tenant_id)
        record.is_active = False
        db.commit()

    def verify_key(self, db: Session, raw_key: str) -> Optional[ApiKey]:
        key_hash = _hash_key(raw_key)
        record = (
            db.query(ApiKey)
            .filter(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active == True,
            )
            .first()
        )
        if record:
            record.last_used_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(record)
        return record


api_key_service = ApiKeyService()
