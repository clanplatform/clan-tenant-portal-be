import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.invoices.exceptions import InvoiceAlreadyExists, InvoiceNotFound
from app.invoices.models.invoice import Invoice
from app.invoices.schemas.invoice import InvoiceCreate, InvoiceStatusUpdate, InvoiceUpdate


def generate_invoice_number(db: Session) -> str:
    count = db.query(Invoice).count()
    year = datetime.now(timezone.utc).year
    return f"INV-{year}-{str(count + 1).zfill(5)}"


def get_by_id(db: Session, invoice_id: uuid.UUID, tenant_id: Optional[uuid.UUID] = None) -> Invoice:
    query = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.is_deleted == False,
    )
    if tenant_id is not None:
        query = query.filter(Invoice.tenant_id == tenant_id)
    invoice = query.first()
    if not invoice:
        raise InvoiceNotFound(f"Invoice with id '{invoice_id}' not found")
    return invoice


def get_by_number(db: Session, invoice_number: str, tenant_id: Optional[uuid.UUID] = None) -> Invoice:
    query = db.query(Invoice).filter(
        Invoice.invoice_number == invoice_number,
        Invoice.is_deleted == False,
    )
    if tenant_id is not None:
        query = query.filter(Invoice.tenant_id == tenant_id)
    invoice = query.first()
    if not invoice:
        raise InvoiceNotFound(f"Invoice with number '{invoice_number}' not found")
    return invoice


def list_invoices(
    db: Session,
    tenant_id: uuid.UUID,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Invoice]:
    query = db.query(Invoice).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.is_deleted == False,
    )
    if status:
        query = query.filter(Invoice.status == status)
    return query.offset(skip).limit(limit).all()


def create(db: Session, data: InvoiceCreate) -> Invoice:
    invoice_number = generate_invoice_number(db)

    existing = (
        db.query(Invoice)
        .filter(Invoice.invoice_number == invoice_number, Invoice.is_deleted == False)
        .first()
    )
    if existing:
        raise InvoiceAlreadyExists(f"Invoice with number '{invoice_number}' already exists")

    invoice = Invoice(
        tenant_id=data.tenant_id,
        subscription_id=data.subscription_id,
        invoice_number=invoice_number,
        status="draft",
        amount_due=data.amount_due,
        amount_paid=0,
        currency=data.currency,
        due_date=data.due_date,
        period_start=data.period_start,
        period_end=data.period_end,
        line_items=data.line_items,
        billing_details=data.billing_details,
        notes=data.notes,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def update(
    db: Session,
    invoice_id: uuid.UUID,
    tenant_id: uuid.UUID,
    data: InvoiceUpdate,
) -> Invoice:
    invoice = get_by_id(db, invoice_id, tenant_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    db.commit()
    db.refresh(invoice)
    return invoice


def update_status(
    db: Session,
    invoice_id: uuid.UUID,
    tenant_id: uuid.UUID,
    data: InvoiceStatusUpdate,
) -> Invoice:
    invoice = get_by_id(db, invoice_id, tenant_id)
    invoice.status = data.status

    if data.status == "paid":
        invoice.paid_at = data.paid_at or datetime.now(timezone.utc)
        if data.amount_paid is not None:
            invoice.amount_paid = data.amount_paid
        else:
            invoice.amount_paid = invoice.amount_due
    elif data.status == "void":
        invoice.amount_paid = 0

    db.commit()
    db.refresh(invoice)
    return invoice


def void_invoice(
    db: Session,
    invoice_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> Invoice:
    invoice = get_by_id(db, invoice_id, tenant_id)
    invoice.status = "void"
    invoice.amount_paid = 0
    db.commit()
    db.refresh(invoice)
    return invoice
