from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, List
from app.core.constants import ChallengeDomain, ChallengeSeverity, ChallengeStatus
from app.schemas.common import GeoPoint, PaginatedResponse
from app.schemas.user import UserResponse

class ChallengeCreate(BaseModel):
    title: str = Field(..., min_length=10, max_length=500)
    narrative: str = Field(..., min_length=20)
    location: Optional[GeoPoint] = None
    address: Optional[str] = None
    district: Optional[str] = None
    domain: ChallengeDomain
    severity: ChallengeSeverity = ChallengeSeverity.MEDIUM
    is_anonymous: bool = False
    affected_population: Optional[int] = None

class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    narrative: Optional[str] = None
    domain: Optional[ChallengeDomain] = None
    severity: Optional[ChallengeSeverity] = None
    affected_population: Optional[int] = None

class ChallengeMediaResponse(BaseModel):
    id: UUID
    file_url: str
    file_type: str
    file_name: str
    file_size: int
    model_config = ConfigDict(from_attributes=True)

class ChallengeResponse(BaseModel):
    id: UUID
    title: str
    narrative: str
    location: Optional[GeoPoint] = None
    address: Optional[str] = None
    district: Optional[str] = None
    domain: ChallengeDomain
    severity: ChallengeSeverity
    is_anonymous: bool
    affected_population: Optional[int] = None
    ai_summary: Optional[str] = None
    ai_domain: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_tags: Optional[List[str]] = None
    impact_score: Optional[float] = None
    evidence_score: Optional[float] = None
    status: ChallengeStatus
    media: List[ChallengeMediaResponse] = []
    reporter: Optional[UserResponse] = None
    cluster_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ChallengeListResponse(PaginatedResponse[ChallengeResponse]):
    pass

class ChallengeVerifyRequest(BaseModel):
    action: Literal['approve', 'reject']
    domain_override: Optional[ChallengeDomain] = None
    severity_override: Optional[ChallengeSeverity] = None
    notes: Optional[str] = None

class ChallengeClusterResponse(BaseModel):
    id: UUID
    title: str
    domain: str
    district: str
    challenge_count: int
    challenges: List[ChallengeResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ChallengeSimilarResponse(BaseModel):
    challenge: ChallengeResponse
    similarity_score: float
    model_config = ConfigDict(from_attributes=True)

class ChallengeHeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    count: int
    domain: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ChallengeTimelineEntry(BaseModel):
    from_status: str
    to_status: str
    changed_by_name: Optional[str] = None
    reason: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class ChallengeFilterParams(BaseModel):
    domain: Optional[ChallengeDomain] = None
    severity: Optional[ChallengeSeverity] = None
    status: Optional[ChallengeStatus] = None
    district: Optional[str] = None
