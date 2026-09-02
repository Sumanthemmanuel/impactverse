from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Float, Integer, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from geoalchemy2 import Geography
from pgvector.sqlalchemy import Vector
import uuid

from app.models import Base, TimestampMixin
from app.core.constants import ChallengeDomain, ChallengeSeverity, ChallengeStatus, MediaType

class ChallengeCluster(Base, TimestampMixin):
    __tablename__ = 'challenge_clusters'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    master_challenge_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('challenges.id'), nullable=True)
    domain: Mapped[Optional[ChallengeDomain]] = mapped_column(nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    centroid_embedding = mapped_column(Vector(384), nullable=True)
    challenge_count: Mapped[int] = mapped_column(Integer, default=1)

    challenges: Mapped[List["Challenge"]] = relationship(
        back_populates="cluster",
        foreign_keys="Challenge.cluster_id",
    )

class Challenge(Base, TimestampMixin):
    __tablename__ = 'challenges'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    narrative: Mapped[str] = mapped_column(Text, nullable=False)
    reporter_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    location = mapped_column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), default='Jharkhand')
    domain: Mapped[ChallengeDomain] = mapped_column(nullable=False)
    severity: Mapped[ChallengeSeverity] = mapped_column(default=ChallengeSeverity.MEDIUM)
    status: Mapped[ChallengeStatus] = mapped_column(default=ChallengeStatus.SUBMITTED)
    evidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_domain: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    cluster_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('challenge_clusters.id'), nullable=True)
    affected_population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    embedding = mapped_column(Vector(384), nullable=True)

    cluster: Mapped[Optional["ChallengeCluster"]] = relationship(back_populates="challenges", foreign_keys=[cluster_id])
    reporter = relationship("User")
    media: Mapped[List["ChallengeMedia"]] = relationship(back_populates="challenge", cascade="all, delete-orphan")
    status_history: Mapped[List["ChallengeStatusHistory"]] = relationship(back_populates="challenge", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="challenge")

    __table_args__ = (
        Index('ix_challenges_domain', 'domain'),
        Index('ix_challenges_status', 'status'),
        Index('ix_challenges_district', 'district'),
        Index('ix_challenges_severity', 'severity'),
        Index('ix_challenges_impact_score', 'impact_score', postgresql_ops={'impact_score': 'DESC'}),
        Index('ix_challenges_location', 'location', postgresql_using='gist'),
    )

class ChallengeMedia(Base, TimestampMixin):
    __tablename__ = 'challenge_media'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('challenges.id', ondelete='CASCADE'), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[MediaType] = mapped_column(nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_json = mapped_column(JSON, nullable=True)

    challenge: Mapped["Challenge"] = relationship(back_populates="media")

class ChallengeStatusHistory(Base):
    __tablename__ = 'challenge_status_history'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('challenges.id', ondelete='CASCADE'), nullable=False)
    from_status: Mapped[Optional[ChallengeStatus]] = mapped_column(nullable=True)
    to_status: Mapped[ChallengeStatus] = mapped_column(nullable=False)
    changed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    challenge: Mapped["Challenge"] = relationship(back_populates="status_history")
