import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.infrastructure.database.base import Base


class AppConfiguration(Base):
    __tablename__ = "app_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    app_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    config_key = Column(String(255), nullable=False)
    config_value = Column(Text, nullable=True)
    is_encrypted = Column(Boolean, default=False, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "app_id", "config_key", name="uq_app_config_tenant_app_key"),
    )
