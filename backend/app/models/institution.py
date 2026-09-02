from typing import Optional, List
from sqlalchemy import String, Boolean, Text, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from geoalchemy2 import Geography
from pgvector.sqlalchemy import Vector
import uuid

from app.models import Base, TimestampMixin

class Institution(Base, TimestampMixin):
    __tablename__ = 'institutions'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    institution_type: Mapped[str] = mapped_column(String(100), default='University')
    location = mapped_column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), default='Jharkhand')
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    established_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    accreditation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    incubation_facilities: Mapped[bool] = mapped_column(Boolean, default=False)
    capacity_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_faculty: Mapped[int] = mapped_column(Integer, default=0)
    total_students: Mapped[int] = mapped_column(Integer, default=0)
    admin_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    departments: Mapped[List["Department"]] = relationship(back_populates="institution")
    admin_user = relationship("User")

class Department(Base, TimestampMixin):
    __tablename__ = 'departments'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('institutions.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    research_areas: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    capability_embedding = mapped_column(Vector(384), nullable=True)
    faculty_count: Mapped[int] = mapped_column(Integer, default=0)
    student_count: Mapped[int] = mapped_column(Integer, default=0)

    institution: Mapped["Institution"] = relationship(back_populates="departments")
    labs: Mapped[List["Lab"]] = relationship(back_populates="department")
    faculty: Mapped[List["FacultyProfile"]] = relationship(back_populates="department")

class Lab(Base, TimestampMixin):
    __tablename__ = 'labs'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    equipment: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    specialization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    department: Mapped["Department"] = relationship(back_populates="labs")

class FacultyProfile(Base, TimestampMixin):
    __tablename__ = 'faculty_profiles'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True, nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    expertise_tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    expertise_embedding = mapped_column(Vector(384), nullable=True)
    publications_count: Mapped[int] = mapped_column(Integer, default=0)
    patents_count: Mapped[int] = mapped_column(Integer, default=0)
    past_projects_count: Mapped[int] = mapped_column(Integer, default=0)
    h_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    availability_status: Mapped[bool] = mapped_column(Boolean, default=True)
    mentor_capacity: Mapped[int] = mapped_column(Integer, default=2)
    current_mentees: Mapped[int] = mapped_column(Integer, default=0)

    user = relationship("User")
    department: Mapped["Department"] = relationship(back_populates="faculty")
