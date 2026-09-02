from typing import Optional, List
from datetime import date, datetime
from sqlalchemy import String, Text, Float, Integer, ForeignKey, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models import Base, TimestampMixin
from app.core.constants import ProjectStatus, MilestoneStatus

class Project(Base, TimestampMixin):
    __tablename__ = 'projects'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('challenges.id'), nullable=False)
    institution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('institutions.id'), nullable=False)
    lead_faculty_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proposal_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(default=ProjectStatus.PROPOSED)
    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    funding_secured: Mapped[float] = mapped_column(Float, default=0.0)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    target_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    deployment_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    match_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    challenge = relationship("Challenge", back_populates="projects")
    institution = relationship("Institution")
    lead_faculty = relationship("User")
    members: Mapped[List["ProjectMember"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    milestones: Mapped[List["Milestone"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    partner_interests: Mapped[List["PartnerInterest"]] = relationship("PartnerInterest", back_populates="project")

class ProjectMember(Base):
    __tablename__ = 'project_members'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="members")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint('project_id', 'user_id', name='uq_project_user'),
    )

class Milestone(Base, TimestampMixin):
    __tablename__ = 'milestones'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[MilestoneStatus] = mapped_column(default=MilestoneStatus.PENDING)
    evidence_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped["Project"] = relationship(back_populates="milestones")
