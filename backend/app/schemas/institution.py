from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, List
from app.schemas.common import GeoPoint
from app.schemas.user import UserResponse

class LabCreate(BaseModel):
    name: str
    description: str
    equipment: Optional[List[str]] = None
    specialization: str

class LabResponse(BaseModel):
    id: UUID
    name: str
    description: str
    equipment: Optional[List[str]] = None
    specialization: str
    model_config = ConfigDict(from_attributes=True)

class DepartmentCreate(BaseModel):
    name: str
    research_areas: Optional[List[str]] = None
    faculty_count: int
    student_count: int

class DepartmentResponse(BaseModel):
    id: UUID
    name: str
    research_areas: Optional[List[str]] = None
    faculty_count: int
    student_count: int
    labs: List[LabResponse] = []
    model_config = ConfigDict(from_attributes=True)

class FacultyProfileCreate(BaseModel):
    department_id: UUID
    title: str
    expertise_tags: Optional[List[str]] = None
    publications_count: int
    patents_count: int
    past_projects_count: int
    h_index: float
    mentor_capacity: int

class FacultyProfileResponse(BaseModel):
    id: UUID
    department_id: UUID
    title: str
    expertise_tags: Optional[List[str]] = None
    publications_count: int
    patents_count: int
    past_projects_count: int
    h_index: float
    mentor_capacity: int
    user: UserResponse
    department: DepartmentResponse
    model_config = ConfigDict(from_attributes=True)

class InstitutionCreate(BaseModel):
    name: str
    institution_type: str
    address: str
    district: str
    state: str
    website: Optional[str] = None
    established_year: int
    accreditation: Optional[str] = None
    incubation_facilities: bool
    total_faculty: int
    total_students: int
    location: Optional[GeoPoint] = None

class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    institution_type: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    website: Optional[str] = None
    established_year: Optional[int] = None
    accreditation: Optional[str] = None
    incubation_facilities: Optional[bool] = None
    total_faculty: Optional[int] = None
    total_students: Optional[int] = None
    location: Optional[GeoPoint] = None

class InstitutionResponse(BaseModel):
    id: UUID
    name: str
    institution_type: str
    address: str
    district: str
    state: str
    website: Optional[str] = None
    established_year: int
    accreditation: Optional[str] = None
    incubation_facilities: bool
    total_faculty: int
    total_students: int
    location: Optional[GeoPoint] = None
    departments: List[DepartmentResponse] = []
    admin_user: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)

class InstitutionMiniResponse(BaseModel):
    id: UUID
    name: str
    model_config = ConfigDict(from_attributes=True)
