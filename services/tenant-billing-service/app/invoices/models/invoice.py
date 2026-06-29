import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), nullable=True)
    invoice_number = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), default="draft", nullable=False)
    amount_due = Column(Numeric(10, 2), default=0.00, nullable=False)
    amount_paid = Column(Numeric(10, 2), default=0.00, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    due_date = Column(Date, nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    line_items = Column(JSON, default=list, nullable=False)
    billing_details = Column(JSON, default=dict, nullable=False)
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
