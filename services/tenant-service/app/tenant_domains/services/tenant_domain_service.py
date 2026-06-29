import secrets
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.tenant_domains.models.tenant_domain import TenantDomain
from app.tenant_domains.schemas.tenant_domain import TenantDomainCreate


class TenantDomainService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, tenant_id: UUID) -> List[TenantDomain]:
        return (
            self.db.query(TenantDomain)
            .filter(TenantDomain.tenant_id == tenant_id)
            .order_by(TenantDomain.created_at.desc())
            .all()
        )

    def _get_domain_for_tenant(self, tenant_id: UUID, domain_id: UUID) -> TenantDomain:
        obj = (
            self.db.query(TenantDomain)
            .filter(TenantDomain.id == domain_id, TenantDomain.tenant_id == tenant_id)
            .first()
        )
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Domain {domain_id} not found for tenant {tenant_id}",
            )
        return obj

    def add(self, tenant_id: UUID, data: TenantDomainCreate) -> TenantDomain:
        existing = (
            self.db.query(TenantDomain)
            .filter(TenantDomain.domain == data.domain)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Domain '{data.domain}' is already registered",
            )
        obj = TenantDomain(
            tenant_id=tenant_id,
            domain=data.domain,
            is_verified=False,
            is_primary=False,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def initiate_verify(self, tenant_id: UUID, domain_id: UUID) -> TenantDomain:
        obj = self._get_domain_for_tenant(tenant_id, domain_id)
        if obj.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain is already verified",
            )
        obj.verification_token = secrets.token_urlsafe(32)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def confirm_verify(self, tenant_id: UUID, domain_id: UUID, token: str) -> TenantDomain:
        obj = self._get_domain_for_tenant(tenant_id, domain_id)
        if obj.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain is already verified",
            )
        if not obj.verification_token or obj.verification_token != token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token",
            )
        obj.is_verified = True
        obj.verified_at = datetime.now(timezone.utc)
        obj.verification_token = None
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def set_primary(self, tenant_id: UUID, domain_id: UUID) -> TenantDomain:
        obj = self._get_domain_for_tenant(tenant_id, domain_id)
        if not obj.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain must be verified before setting as primary",
            )
        # Clear existing primary for this tenant
        self.db.query(TenantDomain).filter(
            TenantDomain.tenant_id == tenant_id,
            TenantDomain.is_primary == True,  # noqa: E712
        ).update({"is_primary": False})

        obj.is_primary = True
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def remove(self, tenant_id: UUID, domain_id: UUID) -> None:
        obj = self._get_domain_for_tenant(tenant_id, domain_id)
        if obj.is_primary:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the primary domain. Set another domain as primary first.",
            )
        self.db.delete(obj)
        self.db.commit()
