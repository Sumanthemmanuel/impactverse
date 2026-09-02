from typing import Optional
from sqlalchemy import String, Boolean, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models import Base, TimestampMixin
from app.core.constants import UserRole

class User(Base, TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(nullable=False, default=UserRole.CITIZEN)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    language_preference: Mapped[str] = mapped_column(String(10), default='en')
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), default='Jharkhand')
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index('ix_users_role', 'role'),
        Index('ix_users_is_active', 'is_active'),
    )
