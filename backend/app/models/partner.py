from typing import Optional, List
from sqlalchemy import String, Text, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY, UUID
import uuid

from app.models import Base, TimestampMixin
from app.core.constants import PartnerType, SupportType, InterestStatus

class Partner(Base, TimestampMixin):
    __tablename__ = 'partners'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True, nullable=False)
    organization_name: Mapped[str] = mapped_column(String(500), nullable=False)
    partner_type: Mapped[PartnerType] = mapped_column(nullable=False)
    domains: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    geography: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    funding_capability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User")
    interests: Mapped[List["PartnerInterest"]] = relationship(back_populates="partner")

class PartnerInterest(Base, TimestampMixin):
    __tablename__ = 'partner_interests'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('partners.id', ondelete='CASCADE'), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    support_type: Mapped[SupportType] = mapped_column(nullable=False)
    contribution_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    funding_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[InterestStatus] = mapped_column(default=InterestStatus.PENDING)
    response_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    partner: Mapped["Partner"] = relationship(back_populates="interests")
    project = relationship("Project", back_populates="partner_interests")

    __table_args__ = (
        UniqueConstraint('partner_id', 'project_id', 'support_type', name='uq_partner_project_support'),
    )
