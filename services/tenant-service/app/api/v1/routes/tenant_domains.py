from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.tenant_domains.schemas.tenant_domain import (
    DomainVerifyConfirm,
    TenantDomainCreate,
    TenantDomainResponse,
)
from app.tenant_domains.services.tenant_domain_service import TenantDomainService

router = APIRouter(prefix="/tenants", tags=["tenant-domains"])


@router.get("/{tenant_id}/domains", response_model=List[TenantDomainResponse])
def list_domains(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all domains for a tenant."""
    return TenantDomainService(db).list(tenant_id)


@router.post(
    "/{tenant_id}/domains",
    response_model=TenantDomainResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_domain(
    tenant_id: UUID,
    data: TenantDomainCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Add a new domain to a tenant."""
    return TenantDomainService(db).add(tenant_id, data)


@router.post(
    "/{tenant_id}/domains/{domain_id}/verify",
    response_model=TenantDomainResponse,
)
def verify_domain(
    tenant_id: UUID,
    domain_id: UUID,
    data: DomainVerifyConfirm | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Initiate or confirm domain verification.
    - Without a body (or token=None): generates and returns a verification token.
    - With body containing token: confirms verification by checking the token.
    """
    service = TenantDomainService(db)
    if data and data.token:
        return service.confirm_verify(tenant_id, domain_id, data.token)
    return service.initiate_verify(tenant_id, domain_id)


@router.put(
    "/{tenant_id}/domains/{domain_id}/primary",
    response_model=TenantDomainResponse,
)
def set_primary_domain(
    tenant_id: UUID,
    domain_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Set a verified domain as the primary domain for the tenant."""
    return TenantDomainService(db).set_primary(tenant_id, domain_id)


@router.delete(
    "/{tenant_id}/domains/{domain_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_domain(
    tenant_id: UUID,
    domain_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Remove a domain from a tenant."""
    TenantDomainService(db).remove(tenant_id, domain_id)
