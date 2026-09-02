from pydantic import BaseModel, ConfigDict, model_validator
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class MatchResult(BaseModel):
    institution_id: UUID
    institution_name: str
    overall_score: float
    research_fit: float
    faculty_fit: float
    lab_fit: float
    past_projects_score: float
    team_capacity_score: float
    geographic_proximity_score: float
    incubation_readiness_score: float
    explanation: str
    matching_departments: List[str]
    matching_faculty: List[str]
    model_config = ConfigDict(from_attributes=True)

class MatchResponse(BaseModel):
    challenge_id: UUID
    matches: List[MatchResult]
    computed_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ScoreConfig(BaseModel):
    severity_weight: float = 0.25
    people_affected_weight: float = 0.20
    urgency_weight: float = 0.15
    evidence_quality_weight: float = 0.15
    geographic_spread_weight: float = 0.10
    feasibility_weight: float = 0.10
    strategic_relevance_weight: float = 0.05

    @model_validator(mode='after')
    def validate_weights_sum(self) -> 'ScoreConfig':
        total = sum([
            self.severity_weight,
            self.people_affected_weight,
            self.urgency_weight,
            self.evidence_quality_weight,
            self.geographic_spread_weight,
            self.feasibility_weight,
            self.strategic_relevance_weight
        ])
        if not abs(total - 1.0) < 1e-6:
            raise ValueError('Score config weights must sum to 1.0')
        return self

class ScoreConfigResponse(BaseModel):
    config: ScoreConfig
    version: int
    updated_at: datetime
    updated_by: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
