import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.invoices.schemas.invoice import (
    InvoiceCreate,
    InvoiceResponse,
    InvoiceStatusUpdate,
    InvoiceUpdate,
)
from app.invoices.services import invoice_service

router = APIRouter(prefix="/invoices", tags=["Invoices"])


def _resolve_tenant_id(current_user: dict) -> uuid.UUID:
    jwt_tenant = current_user.get("tenant_id")
    role = current_user.get("role")
    if role == "internal":
        return None
    if not jwt_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID not found in token",
        )
    try:
        return uuid.UUID(str(jwt_tenant))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid tenant_id in token",
        )


@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(
    invoice_status: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id required for listing invoices",
        )
    return invoice_service.list_invoices(db, tenant_id, status=invoice_status, skip=skip, limit=limit)


@router.post("/", response_model=InvoiceResponse, status_code=201)
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    role = current_user.get("role")
    if role not in ("internal", "admin") and tenant_id is not None:
        data = data.model_copy(update={"tenant_id": tenant_id})
    return invoice_service.create(db, data)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    return invoice_service.get_by_id(db, invoice_id, tenant_id)


@router.put("/{invoice_id}/status", response_model=InvoiceResponse)
def update_invoice_status(
    invoice_id: uuid.UUID,
    data: InvoiceStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id required to update invoice status",
        )
    return invoice_service.update_status(db, invoice_id, tenant_id, data)
