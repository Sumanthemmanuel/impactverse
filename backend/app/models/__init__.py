from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

from app.models.user import User
from app.models.challenge import Challenge, ChallengeMedia, ChallengeCluster, ChallengeStatusHistory
from app.models.institution import Institution, Department, Lab, FacultyProfile
from app.models.project import Project, ProjectMember, Milestone
from app.models.partner import Partner, PartnerInterest
from app.models.outcome import Outcome, BeneficiaryFeedback
from app.models.audit import AuditEvent
