from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql import func
import uuid

from app.models import Base

class AuditEvent(Base):
    __tablename__ = 'audit_events'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    before_snapshot = mapped_column(JSON, nullable=True)
    after_snapshot = mapped_column(JSON, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_audit_events_actor_id', 'actor_id'),
        Index('ix_audit_events_entity', 'entity_type', 'entity_id'),
        Index('ix_audit_events_timestamp', 'timestamp', postgresql_ops={'timestamp': 'DESC'}),
        Index('ix_audit_events_action', 'action'),
    )
