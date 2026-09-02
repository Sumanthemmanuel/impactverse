from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, List
from app.core.constants import PartnerType, SupportType, InterestStatus
from app.schemas.user import UserResponse

class PartnerCreate(BaseModel):
    organization_name: str
    partner_type: PartnerType
    domains: Optional[List[str]] = None
    description: str
    website: str
    geography: str
    funding_capability: str

class PartnerUpdate(BaseModel):
    organization_name: Optional[str] = None
    partner_type: Optional[PartnerType] = None
    domains: Optional[List[str]] = None
    description: Optional[str] = None
    website: Optional[str] = None
    geography: Optional[str] = None
    funding_capability: Optional[str] = None

class PartnerResponse(BaseModel):
    id: UUID
    organization_name: str
    partner_type: PartnerType
    domains: Optional[List[str]] = None
    description: str
    website: str
    geography: str
    funding_capability: str
    user: UserResponse
    model_config = ConfigDict(from_attributes=True)

class PartnerMiniResponse(BaseModel):
    id: UUID
    organization_name: str
    model_config = ConfigDict(from_attributes=True)

class PartnerInterestCreate(BaseModel):
    project_id: UUID
    support_type: SupportType
    contribution_details: str
    funding_amount: Optional[float] = None

class PartnerInterestUpdate(BaseModel):
    status: InterestStatus
    response_notes: Optional[str] = None

class PartnerInterestResponse(BaseModel):
    id: UUID
    project_id: UUID
    support_type: SupportType
    contribution_details: str
    funding_amount: Optional[float] = None
    status: InterestStatus
    response_notes: Optional[str] = None
    partner: PartnerMiniResponse
    project_title: str
    model_config = ConfigDict(from_attributes=True)
