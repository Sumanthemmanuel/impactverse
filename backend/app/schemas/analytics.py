from pydantic import BaseModel, ConfigDict
from uuid import UUID

class OverviewStats(BaseModel):
    total_challenges: int
    total_validated: int
    total_projects: int
    total_deployed: int
    total_institutions: int
    total_partners: int
    total_beneficiaries: int
    avg_impact_score: float
    model_config = ConfigDict(from_attributes=True)

class DomainDistribution(BaseModel):
    domain: str
    count: int
    percentage: float
    model_config = ConfigDict(from_attributes=True)

class DistrictDistribution(BaseModel):
    district: str
    count: int
    validated: int
    in_progress: int
    deployed: int
    model_config = ConfigDict(from_attributes=True)

class PipelineFunnel(BaseModel):
    submitted: int
    validated: int
    matched: int
    in_progress: int
    deployed: int
    measuring: int
    model_config = ConfigDict(from_attributes=True)

class SLAMetrics(BaseModel):
    avg_time_to_validate_hours: float
    avg_time_to_match_hours: float
    avg_time_to_deploy_days: float
    overdue_challenges: int
    bottleneck_stage: str
    model_config = ConfigDict(from_attributes=True)

class InstitutionParticipation(BaseModel):
    institution_id: UUID
    name: str
    challenges_accepted: int
    projects_active: int
    projects_completed: int
    avg_response_days: float
    model_config = ConfigDict(from_attributes=True)

class ImpactSummary(BaseModel):
    total_beneficiaries: int
    total_cost_saved: float
    projects_deployed: int
    avg_rating: float
    domains_covered: int
    model_config = ConfigDict(from_attributes=True)
