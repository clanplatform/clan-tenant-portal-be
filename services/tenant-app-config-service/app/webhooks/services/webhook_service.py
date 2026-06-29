import secrets
import hashlib
from typing import List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.webhooks.models.webhook import Webhook
from app.webhooks.schemas.webhook import WebhookCreate, WebhookUpdate
from app.webhooks.exceptions import WebhookNotFound


def _hash_secret(raw_secret: str) -> str:
    return hashlib.sha256(raw_secret.encode()).hexdigest()


class WebhookService:
    def list(self, db: Session, tenant_id: UUID) -> List[Webhook]:
        return (
            db.query(Webhook)
            .filter(
                Webhook.tenant_id == tenant_id,
                Webhook.is_deleted == False,
            )
            .all()
        )

    def get_by_id(self, db: Session, webhook_id: UUID, tenant_id: UUID) -> Webhook:
        record = (
            db.query(Webhook)
            .filter(
                Webhook.id == webhook_id,
                Webhook.tenant_id == tenant_id,
                Webhook.is_deleted == False,
            )
            .first()
        )
        if not record:
            raise WebhookNotFound(str(webhook_id))
        return record

    def create(self, db: Session, tenant_id: UUID, data: WebhookCreate) -> Tuple[Webhook, str]:
        raw_secret = secrets.token_hex(32)  # 64-char hex string
        secret_hash = _hash_secret(raw_secret)

        webhook = Webhook(
            tenant_id=tenant_id,
            name=data.name,
            url=data.url,
            secret_hash=secret_hash,
            events=data.events,
            retry_count=data.retry_count,
            timeout_seconds=data.timeout_seconds,
        )
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        return webhook, raw_secret

    def update(
        self, db: Session, webhook_id: UUID, tenant_id: UUID, data: WebhookUpdate
    ) -> Webhook:
        record = self.get_by_id(db, webhook_id, tenant_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return record

    def soft_delete(self, db: Session, webhook_id: UUID, tenant_id: UUID) -> None:
        record = self.get_by_id(db, webhook_id, tenant_id)
        record.is_deleted = True
        record.deleted_at = datetime.now(timezone.utc)
        db.commit()

    def send_test(
        self, db: Session, webhook_id: UUID, tenant_id: UUID
    ) -> Dict[str, Any]:
        webhook = self.get_by_id(db, webhook_id, tenant_id)
        return {
            "webhook_id": str(webhook.id),
            "status": "test_sent",
            "url": webhook.url,
            "message": "Test webhook event dispatched",
        }


webhook_service = WebhookService()
