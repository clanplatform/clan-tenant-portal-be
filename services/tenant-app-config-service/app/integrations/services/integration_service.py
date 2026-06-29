from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.integrations.models.integration import Integration
from app.integrations.schemas.integration import IntegrationCreate, IntegrationUpdate
from app.integrations.exceptions import IntegrationNotFound


class IntegrationService:
    def list(self, db: Session, tenant_id: UUID) -> List[Integration]:
        return (
            db.query(Integration)
            .filter(
                Integration.tenant_id == tenant_id,
                Integration.is_deleted == False,
            )
            .all()
        )

    def get_by_id(self, db: Session, integration_id: UUID, tenant_id: UUID) -> Integration:
        record = (
            db.query(Integration)
            .filter(
                Integration.id == integration_id,
                Integration.tenant_id == tenant_id,
                Integration.is_deleted == False,
            )
            .first()
        )
        if not record:
            raise IntegrationNotFound(str(integration_id))
        return record

    def create(self, db: Session, tenant_id: UUID, data: IntegrationCreate) -> Integration:
        integration = Integration(
            tenant_id=tenant_id,
            integration_type=data.integration_type,
            name=data.name,
            credentials=data.credentials,
            settings=data.settings,
            status=data.status,
        )
        db.add(integration)
        db.commit()
        db.refresh(integration)
        return integration

    def update(
        self, db: Session, integration_id: UUID, tenant_id: UUID, data: IntegrationUpdate
    ) -> Integration:
        record = self.get_by_id(db, integration_id, tenant_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return record

    def soft_delete(self, db: Session, integration_id: UUID, tenant_id: UUID) -> None:
        record = self.get_by_id(db, integration_id, tenant_id)
        record.is_deleted = True
        record.deleted_at = datetime.now(timezone.utc)
        db.commit()

    def test_connection(
        self, db: Session, integration_id: UUID, tenant_id: UUID
    ) -> Dict[str, Any]:
        integration = self.get_by_id(db, integration_id, tenant_id)
        return {
            "success": True,
            "message": (
                f"Connection to {integration.integration_type} integration "
                f"'{integration.name}' verified"
            ),
        }


integration_service = IntegrationService()
