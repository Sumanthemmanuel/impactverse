from pydantic import BaseModel, ConfigDict, Field, field_validator
from uuid import UUID
from typing import Optional, List, Dict, Any
from app.schemas.common import PaginatedResponse

class OutcomeCreate(BaseModel):
    project_id: UUID
    deployment_status: str
    beneficiaries_count: int
    target_beneficiaries: int
    kpi_values: Optional[Dict[str, Any]] = None
    evidence_urls: Optional[List[str]] = None
    cost_saved: float
    environmental_impact: str
    social_impact: str

class OutcomeUpdate(BaseModel):
    deployment_status: Optional[str] = None
    beneficiaries_count: Optional[int] = None
    target_beneficiaries: Optional[int] = None
    kpi_values: Optional[Dict[str, Any]] = None
    evidence_urls: Optional[List[str]] = None
    cost_saved: Optional[float] = None
    environmental_impact: Optional[str] = None
    social_impact: Optional[str] = None

class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    respondent_type: Optional[str] = None

    @field_validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class FeedbackResponse(BaseModel):
    id: UUID
    rating: int
    comment: Optional[str] = None
    respondent_type: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class OutcomeResponse(BaseModel):
    id: UUID
    project_id: UUID
    deployment_status: str
    beneficiaries_count: int
    target_beneficiaries: int
    kpi_values: Optional[Dict[str, Any]] = None
    evidence_urls: Optional[List[str]] = None
    cost_saved: float
    environmental_impact: str
    social_impact: str
    project_title: str
    feedback: List[FeedbackResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ImpactLedgerEntry(BaseModel):
    project_id: UUID
    project_title: str
    institution_name: str
    domain: str
    beneficiaries_count: int
    deployment_status: str
    cost_saved: float
    rating_avg: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class ImpactLedgerResponse(PaginatedResponse[ImpactLedgerEntry]):
    pass
