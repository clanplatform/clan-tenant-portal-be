from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.app_configurations.models.app_configuration import AppConfiguration
from app.app_configurations.exceptions import ConfigNotFound


class AppConfigurationService:
    def get_all(self, db: Session, tenant_id: UUID, app_id: UUID) -> List[AppConfiguration]:
        return (
            db.query(AppConfiguration)
            .filter(
                AppConfiguration.tenant_id == tenant_id,
                AppConfiguration.app_id == app_id,
            )
            .all()
        )

    def get(self, db: Session, tenant_id: UUID, app_id: UUID, config_key: str) -> AppConfiguration:
        record = (
            db.query(AppConfiguration)
            .filter(
                AppConfiguration.tenant_id == tenant_id,
                AppConfiguration.app_id == app_id,
                AppConfiguration.config_key == config_key,
            )
            .first()
        )
        if not record:
            raise ConfigNotFound(config_key)
        return record

    def upsert(
        self,
        db: Session,
        tenant_id: UUID,
        app_id: UUID,
        config_key: str,
        config_value: Optional[str],
        description: Optional[str],
        is_encrypted: bool,
    ) -> AppConfiguration:
        existing = (
            db.query(AppConfiguration)
            .filter(
                AppConfiguration.tenant_id == tenant_id,
                AppConfiguration.app_id == app_id,
                AppConfiguration.config_key == config_key,
            )
            .first()
        )
        if existing:
            existing.config_value = config_value
            existing.description = description
            existing.is_encrypted = is_encrypted
            db.commit()
            db.refresh(existing)
            return existing
        else:
            new_config = AppConfiguration(
                tenant_id=tenant_id,
                app_id=app_id,
                config_key=config_key,
                config_value=config_value,
                description=description,
                is_encrypted=is_encrypted,
            )
            db.add(new_config)
            db.commit()
            db.refresh(new_config)
            return new_config

    def delete(self, db: Session, tenant_id: UUID, app_id: UUID, config_key: str) -> None:
        record = (
            db.query(AppConfiguration)
            .filter(
                AppConfiguration.tenant_id == tenant_id,
                AppConfiguration.app_id == app_id,
                AppConfiguration.config_key == config_key,
            )
            .first()
        )
        if not record:
            raise ConfigNotFound(config_key)
        db.delete(record)
        db.commit()


app_configuration_service = AppConfigurationService()
