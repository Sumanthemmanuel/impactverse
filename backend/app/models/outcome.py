from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
import uuid

from app.models import Base, TimestampMixin
from app.core.constants import DeploymentStatus

class Outcome(Base, TimestampMixin):
    __tablename__ = 'outcomes'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('projects.id'), unique=True, nullable=False)
    deployment_status: Mapped[DeploymentStatus] = mapped_column(default=DeploymentStatus.NOT_STARTED)
    beneficiaries_count: Mapped[int] = mapped_column(Integer, default=0)
    target_beneficiaries: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    kpi_values = mapped_column(JSON, nullable=True)
    evidence_urls: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    cost_saved: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    environmental_impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    social_impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    measured_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    project = relationship("Project")
    feedback: Mapped[List["BeneficiaryFeedback"]] = relationship(back_populates="outcome", cascade="all, delete-orphan")

class BeneficiaryFeedback(Base, TimestampMixin):
    __tablename__ = 'beneficiary_feedback'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    outcome_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('outcomes.id', ondelete='CASCADE'), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    respondent_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    outcome: Mapped["Outcome"] = relationship(back_populates="feedback")
