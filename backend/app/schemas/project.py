from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List
from app.core.constants import ProjectStatus
from app.schemas.user import UserResponse
from app.schemas.challenge import ChallengeResponse
from app.schemas.institution import InstitutionResponse, FacultyProfileResponse

class MilestoneCreate(BaseModel):
    title: str
    description: str
    due_date: date
    sort_order: int

class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    evidence_url: Optional[str] = None
    reviewer_notes: Optional[str] = None

class MilestoneResponse(BaseModel):
    id: UUID
    title: str
    description: str
    due_date: date
    sort_order: int
    status: str
    evidence_url: Optional[str] = None
    reviewer_notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ProjectMemberAdd(BaseModel):
    user_id: UUID
    role: str

class ProjectMemberResponse(BaseModel):
    id: UUID
    user: UserResponse
    role: str
    joined_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProjectCreate(BaseModel):
    challenge_id: UUID
    institution_id: UUID
    title: str
    description: str
    proposal_text: str
    budget: float
    start_date: date
    target_end_date: date

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    proposal_text: Optional[str] = None
    budget: Optional[float] = None
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(BaseModel):
    id: UUID
    challenge_id: UUID
    institution_id: UUID
    title: str
    description: str
    proposal_text: str
    budget: float
    start_date: date
    target_end_date: date
    status: ProjectStatus
    challenge: ChallengeResponse
    institution: InstitutionResponse
    lead_faculty: Optional[FacultyProfileResponse] = None
    members: List[ProjectMemberResponse] = []
    milestones: List[MilestoneResponse] = []
    match_score: Optional[float] = None
    match_explanation: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
