from datetime import datetime, timezone
from typing import List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.tenants.exceptions import TenantAlreadyExists, TenantInvalidStatus, TenantNotFound
from app.tenants.models.tenant import Tenant
from app.tenants.schemas.tenant import TenantCreate, TenantStatusUpdate, TenantUpdate

VALID_STATUSES = {"active", "suspended", "trial", "cancelled"}


class TenantService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, tenant_id: UUID) -> Tenant:
        obj = (
            self.db.query(Tenant)
            .filter(Tenant.id == tenant_id, Tenant.is_deleted == False)  # noqa: E712
            .first()
        )
        if not obj:
            raise TenantNotFound(f"Tenant {tenant_id} not found")
        return obj

    def get_by_slug(self, slug: str) -> Tenant:
        obj = (
            self.db.query(Tenant)
            .filter(Tenant.slug == slug, Tenant.is_deleted == False)  # noqa: E712
            .first()
        )
        if not obj:
            raise TenantNotFound(f"Tenant with slug '{slug}' not found")
        return obj

    def list(self, skip: int = 0, limit: int = 100) -> Tuple[List[Tenant], int]:
        query = self.db.query(Tenant).filter(Tenant.is_deleted == False)  # noqa: E712
        total = query.count()
        items = query.order_by(Tenant.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def create(self, data: TenantCreate) -> Tenant:
        existing = (
            self.db.query(Tenant)
            .filter(Tenant.slug == data.slug, Tenant.is_deleted == False)  # noqa: E712
            .first()
        )
        if existing:
            raise TenantAlreadyExists(f"Slug '{data.slug}' is already taken")

        if data.status not in VALID_STATUSES:
            raise TenantInvalidStatus(
                f"Status '{data.status}' is invalid. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
            )

        obj = Tenant(
            slug=data.slug,
            name=data.name,
            display_name=data.display_name,
            description=data.description,
            status=data.status,
            plan_id=data.plan_id,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            logo_url=data.logo_url,
            timezone=data.timezone,
            locale=data.locale,
            max_users=data.max_users,
            metadata_=data.metadata_ or {},
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, tenant_id: UUID, data: TenantUpdate) -> Tenant:
        obj = self.get_by_id(tenant_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def soft_delete(self, tenant_id: UUID) -> None:
        obj = self.get_by_id(tenant_id)
        obj.is_deleted = True
        obj.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

    def change_status(self, tenant_id: UUID, data: TenantStatusUpdate) -> Tenant:
        if data.status not in VALID_STATUSES:
            raise TenantInvalidStatus(
                f"Status '{data.status}' is invalid. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
            )
        obj = self.get_by_id(tenant_id)
        obj.status = data.status
        self.db.commit()
        self.db.refresh(obj)
        return obj
