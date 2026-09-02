import os
import math

base_path = '/Users/mac/Impactverse/backend/app/api/v1'
os.makedirs(base_path, exist_ok=True)

files = {}

files['__init__.py'] = """from fastapi import APIRouter
from . import auth, users, challenges, institutions, matching, projects, partners, outcomes, analytics, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
api_router.include_router(institutions.router, prefix="/institutions", tags=["institutions"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(partners.router, prefix="/partners", tags=["partners"])
api_router.include_router(outcomes.router, prefix="/outcomes", tags=["outcomes"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
"""

files['auth.py'] = """from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_active_user
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshTokenRequest, TokenResponse, ChangePasswordRequest
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import SuccessResponse
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter()

@router.post('/register', response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, tokens = await service.register(data)
    return tokens

@router.post('/login', response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, tokens = await service.login(data)
    return tokens

@router.post('/refresh', response_model=TokenResponse)
async def refresh(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh_token(data.refresh_token)

@router.post('/logout', response_model=SuccessResponse)
async def logout(request: Request, current_user = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    # Assuming JTI is extracted in auth middleware or dependency. For now, simple implementation
    auth_header = request.headers.get("Authorization")
    jti = "mock_jti_from_token"  # Placeholder
    service = AuthService(db)
    await service.logout(jti)
    return SuccessResponse(message='Logged out successfully')

@router.get('/me', response_model=UserResponse)
async def get_me(current_user = Depends(get_current_active_user)):
    return current_user

@router.put('/me', response_model=UserResponse)
async def update_me(data: UserUpdate, current_user = Depends(get_current_active_user), db = Depends(get_db)):
    service = UserService(db)
    return await service.update_user(current_user.id, data)

@router.post('/change-password', response_model=SuccessResponse)
async def change_password(data: ChangePasswordRequest, current_user = Depends(get_current_active_user), db = Depends(get_db)):
    service = AuthService(db)
    await service.change_password(current_user.id, data.current_password, data.new_password)
    return SuccessResponse(message='Password changed successfully')
"""

files['users.py'] = """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, PaginationParams
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import PaginatedResponse
from app.services.user import UserService
import math

router = APIRouter()

@router.get('/', response_model=PaginatedResponse[UserResponse])
async def list_users(pagination: PaginationParams = Depends(), role: UserRole | None = None, is_active: bool | None = None, db = Depends(get_db), current_user = Depends(require_role(UserRole.PLATFORM_ADMIN, UserRole.GOVERNMENT))):
    service = UserService(db)
    users, total = await service.list_users(pagination.page, pagination.page_size, role, is_active)
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=users, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)

@router.get('/{user_id}', response_model=UserResponse)
async def get_user(user_id: UUID, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    service = UserService(db)
    return await service.get_user_by_id(user_id)

@router.patch('/{user_id}', response_model=UserResponse)
async def update_user(user_id: UUID, data: UserUpdate, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    if current_user.id != user_id and current_user.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(status_code=403, detail='Cannot update other users')
    service = UserService(db)
    return await service.update_user(user_id, data)
"""

files['challenges.py'] = """from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, PaginationParams
from app.core.permissions import require_role
from app.core.constants import UserRole, ChallengeDomain, ChallengeStatus, ChallengeSeverity
from app.schemas.challenge import ChallengeCreate, ChallengeResponse, ChallengeUpdate, ChallengeMediaResponse, ChallengeVerifyRequest, ChallengeSimilarResponse, ChallengeTimelineEntry, ChallengeHeatmapPoint, ChallengeClusterResponse
from app.schemas.common import PaginatedResponse
from app.services.challenge import ChallengeService
from app.services.file import FileService
import math

router = APIRouter()

@router.post('/', response_model=ChallengeResponse, status_code=201)
async def create_challenge(data: ChallengeCreate, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    service = ChallengeService(db)
    reporter_id = None if data.is_anonymous else current_user.id
    challenge = await service.create_challenge(data, reporter_id)
    return challenge

@router.post('/{challenge_id}/media', response_model=ChallengeMediaResponse, status_code=201)
async def upload_media(challenge_id: UUID, file: UploadFile, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    file_service = FileService()
    file_info = await file_service.upload_file(file, folder=f'challenges/{challenge_id}')
    return ChallengeMediaResponse(**file_info)

@router.get('/', response_model=PaginatedResponse[ChallengeResponse])
async def list_challenges(pagination: PaginationParams = Depends(), domain: ChallengeDomain | None = None, status: ChallengeStatus | None = None, district: str | None = None, severity: ChallengeSeverity | None = None, sort_by: str = 'created_at', sort_order: str = 'desc', db = Depends(get_db)):
    service = ChallengeService(db)
    challenges, total = await service.list_challenges(pagination.page, pagination.page_size, domain, status, district, severity, sort_by, sort_order)
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=challenges, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)

@router.get('/data/heatmap', response_model=list[ChallengeHeatmapPoint])
async def get_heatmap(domain: ChallengeDomain | None = None, db = Depends(get_db)):
    service = ChallengeService(db)
    return await service.get_heatmap_data(domain)

@router.get('/data/clusters', response_model=PaginatedResponse[ChallengeClusterResponse])
async def get_clusters(pagination: PaginationParams = Depends(), db = Depends(get_db)):
    service = ChallengeService(db)
    clusters, total = await service.get_clusters(pagination.page, pagination.page_size)
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=clusters, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)

@router.get('/{challenge_id}', response_model=ChallengeResponse)
async def get_challenge(challenge_id: UUID, db = Depends(get_db)):
    service = ChallengeService(db)
    return await service.get_challenge(challenge_id)

@router.patch('/{challenge_id}', response_model=ChallengeResponse)
async def update_challenge(challenge_id: UUID, data: ChallengeUpdate, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    service = ChallengeService(db)
    return await service.update_challenge(challenge_id, data, current_user.id)

@router.post('/{challenge_id}/verify', response_model=ChallengeResponse)
async def verify_challenge(challenge_id: UUID, data: ChallengeVerifyRequest, db = Depends(get_db), current_user = Depends(require_role(UserRole.VERIFIER, UserRole.GOVERNMENT, UserRole.PLATFORM_ADMIN))):
    service = ChallengeService(db)
    return await service.verify_challenge(challenge_id, data.action, current_user.id, data.domain_override, data.severity_override, data.notes)

@router.get('/{challenge_id}/similar', response_model=list[ChallengeSimilarResponse])
async def get_similar_challenges(challenge_id: UUID, limit: int = 10, db = Depends(get_db)):
    service = ChallengeService(db)
    return await service.get_similar_challenges(challenge_id, limit)

@router.get('/{challenge_id}/timeline', response_model=list[ChallengeTimelineEntry])
async def get_challenge_timeline(challenge_id: UUID, db = Depends(get_db)):
    service = ChallengeService(db)
    return await service.get_challenge_timeline(challenge_id)
"""

files['institutions.py'] = """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, PaginationParams
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.schemas.institution import InstitutionCreate, InstitutionResponse, InstitutionUpdate, DepartmentCreate, DepartmentResponse, LabCreate, LabResponse
from app.schemas.common import PaginatedResponse
from app.services.institution import InstitutionService
import math

router = APIRouter()

@router.post('/', response_model=InstitutionResponse, status_code=201)
async def create_institution(data: InstitutionCreate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.PLATFORM_ADMIN))):
    service = InstitutionService(db)
    return await service.create_institution(data, current_user.id)

@router.get('/', response_model=PaginatedResponse[InstitutionResponse])
async def list_institutions(pagination: PaginationParams = Depends(), district: str | None = None, verified: bool | None = None, db = Depends(get_db)):
    service = InstitutionService(db)
    institutions, total = await service.list_institutions(pagination.page, pagination.page_size, district, verified)
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=institutions, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)

@router.get('/{institution_id}', response_model=InstitutionResponse)
async def get_institution(institution_id: UUID, db = Depends(get_db)):
    service = InstitutionService(db)
    return await service.get_institution(institution_id)

@router.patch('/{institution_id}', response_model=InstitutionResponse)
async def update_institution(institution_id: UUID, data: InstitutionUpdate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.PLATFORM_ADMIN))):
    service = InstitutionService(db)
    return await service.update_institution(institution_id, data)

@router.post('/{institution_id}/departments', response_model=DepartmentResponse, status_code=201)
async def add_department(institution_id: UUID, data: DepartmentCreate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.PLATFORM_ADMIN))):
    service = InstitutionService(db)
    return await service.add_department(institution_id, data)

@router.post('/{institution_id}/departments/{department_id}/labs', response_model=LabResponse, status_code=201)
async def add_lab(institution_id: UUID, department_id: UUID, data: LabCreate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.PLATFORM_ADMIN))):
    service = InstitutionService(db)
    return await service.add_lab(department_id, data)

@router.get('/{institution_id}/challenges')
async def get_challenge_inbox(institution_id: UUID, pagination: PaginationParams = Depends(), db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY))):
    service = InstitutionService(db)
    challenges, total = await service.get_challenge_inbox(institution_id, pagination.page, pagination.page_size)
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=challenges, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)
"""

files['matching.py'] = """from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone
from app.api.deps import get_db, get_current_active_user
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.schemas.matching import MatchResponse, ScoreConfigResponse, ScoreConfig
from app.schemas.project import ProjectResponse
from app.services.matching import MatchingService

router = APIRouter()

@router.get('/challenges/{challenge_id}/institutions', response_model=MatchResponse)
async def get_matches(challenge_id: UUID, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    service = MatchingService(db)
    matches = await service.get_matches_for_challenge(challenge_id)
    return MatchResponse(challenge_id=challenge_id, matches=matches, computed_at=datetime.now(timezone.utc))

@router.post('/challenges/{challenge_id}/accept', response_model=ProjectResponse, status_code=201)
async def accept_challenge(challenge_id: UUID, institution_id: UUID = Body(...), db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY))):
    service = MatchingService(db)
    return await service.accept_challenge(challenge_id, institution_id, current_user.id)

@router.post('/challenges/{challenge_id}/decline')
async def decline_challenge(challenge_id: UUID, institution_id: UUID = Body(...), reason: str = Body(...), db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY))):
    service = MatchingService(db)
    return await service.decline_challenge(challenge_id, institution_id, current_user.id, reason)

@router.get('/score-config', response_model=ScoreConfigResponse)
async def get_score_config(db = Depends(get_db), current_user = Depends(require_role(UserRole.GOVERNMENT, UserRole.PLATFORM_ADMIN))):
    service = MatchingService(db)
    return await service.get_score_config()

@router.put('/score-config', response_model=ScoreConfigResponse)
async def update_score_config(config: ScoreConfig, db = Depends(get_db), current_user = Depends(require_role(UserRole.GOVERNMENT, UserRole.PLATFORM_ADMIN))):
    service = MatchingService(db)
    return await service.update_score_config(config.model_dump(), current_user.id)
"""

files['projects.py'] = """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, PaginationParams
from app.core.permissions import require_role
from app.core.constants import UserRole, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectMemberAdd, ProjectMemberResponse, MilestoneCreate, MilestoneResponse, MilestoneUpdate
from app.schemas.common import PaginatedResponse
from app.services.project import ProjectService
import math

router = APIRouter()

@router.post('/', response_model=ProjectResponse, status_code=201)
async def create_project(data: ProjectCreate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY))):
    service = ProjectService(db)
    return await service.create_project(data, current_user.id)

@router.get('/', response_model=PaginatedResponse[ProjectResponse])
async def list_projects(pagination: PaginationParams = Depends(), status: ProjectStatus | None = None, institution_id: UUID | None = None, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    service = ProjectService(db)
    projects, total = await service.list_projects(pagination.page, pagination.page_size, status, institution_id)
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=projects, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)

@router.get('/{project_id}', response_model=ProjectResponse)
async def get_project(project_id: UUID, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    service = ProjectService(db)
    return await service.get_project(project_id)

@router.patch('/{project_id}', response_model=ProjectResponse)
async def update_project(project_id: UUID, data: ProjectUpdate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY))):
    service = ProjectService(db)
    return await service.update_project(project_id, data, current_user.id)

@router.post('/{project_id}/members', response_model=ProjectMemberResponse, status_code=201)
async def add_member(project_id: UUID, data: ProjectMemberAdd, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY))):
    service = ProjectService(db)
    return await service.add_member(project_id, data, current_user.id)

@router.post('/{project_id}/milestones', response_model=MilestoneResponse, status_code=201)
async def add_milestone(project_id: UUID, data: MilestoneCreate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY))):
    service = ProjectService(db)
    return await service.add_milestone(project_id, data)

@router.patch('/{project_id}/milestones/{milestone_id}', response_model=MilestoneResponse)
async def update_milestone(project_id: UUID, milestone_id: UUID, data: MilestoneUpdate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY, UserRole.STUDENT))):
    service = ProjectService(db)
    return await service.update_milestone(project_id, milestone_id, data)

@router.get('/{project_id}/deployment-readiness')
async def get_deployment_readiness(project_id: UUID, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    service = ProjectService(db)
    return await service.get_deployment_readiness(project_id)
"""

files['partners.py'] = """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, PaginationParams
from app.core.permissions import require_role
from app.core.constants import UserRole, PartnerType
from app.schemas.partner import PartnerCreate, PartnerResponse, PartnerUpdate, PartnerInterestCreate, PartnerInterestResponse, PartnerInterestUpdate
from app.schemas.common import PaginatedResponse
from app.services.partner import PartnerService
import math

router = APIRouter()

@router.post('/', response_model=PartnerResponse, status_code=201)
async def create_partner(data: PartnerCreate, db = Depends(get_db), current_user = Depends(require_role(UserRole.INDUSTRY, UserRole.CSR))):
    service = PartnerService(db)
    return await service.create_partner(data, current_user.id)

@router.get('/', response_model=PaginatedResponse[PartnerResponse])
async def list_partners(pagination: PaginationParams = Depends(), partner_type: PartnerType | None = None, domain: str | None = None, db = Depends(get_db)):
    service = PartnerService(db)
    partners, total = await service.list_partners(pagination.page, pagination.page_size, partner_type, domain)
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=partners, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)

@router.get('/projects/{project_id}/interests', response_model=list[PartnerInterestResponse])
async def list_project_interests(project_id: UUID, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    service = PartnerService(db)
    return await service.list_interests_for_project(project_id)

@router.get('/{partner_id}', response_model=PartnerResponse)
async def get_partner(partner_id: UUID, db = Depends(get_db)):
    service = PartnerService(db)
    return await service.get_partner(partner_id)

@router.patch('/{partner_id}', response_model=PartnerResponse)
async def update_partner(partner_id: UUID, data: PartnerUpdate, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    service = PartnerService(db)
    return await service.update_partner(partner_id, data)

@router.post('/{partner_id}/interests', response_model=PartnerInterestResponse, status_code=201)
async def create_interest(partner_id: UUID, data: PartnerInterestCreate, db = Depends(get_db), current_user = Depends(require_role(UserRole.INDUSTRY, UserRole.CSR))):
    service = PartnerService(db)
    return await service.create_interest(partner_id, data, current_user.id)

@router.patch('/interests/{interest_id}', response_model=PartnerInterestResponse)
async def update_interest(interest_id: UUID, data: PartnerInterestUpdate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY, UserRole.PLATFORM_ADMIN))):
    service = PartnerService(db)
    return await service.update_interest(interest_id, data, current_user.id)
"""

files['outcomes.py'] = """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, PaginationParams
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.schemas.outcome import OutcomeCreate, OutcomeResponse, OutcomeUpdate, FeedbackCreate, FeedbackResponse, ImpactLedgerResponse
from app.schemas.common import PaginatedResponse
from app.services.outcome import OutcomeService
import math

router = APIRouter()

@router.get('/impact-ledger', response_model=PaginatedResponse[ImpactLedgerResponse])
async def get_impact_ledger(pagination: PaginationParams = Depends(), domain: str | None = None, db = Depends(get_db)):
    service = OutcomeService(db)
    entries, total = await service.get_impact_ledger(pagination.page, pagination.page_size, domain)
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=entries, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)

@router.post('/', response_model=OutcomeResponse, status_code=201)
async def create_outcome(data: OutcomeCreate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY, UserRole.GOVERNMENT))):
    service = OutcomeService(db)
    return await service.create_outcome(data, current_user.id)

@router.get('/project/{project_id}', response_model=OutcomeResponse)
async def get_outcome(project_id: UUID, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    service = OutcomeService(db)
    return await service.get_outcome(project_id)

@router.patch('/{outcome_id}', response_model=OutcomeResponse)
async def update_outcome(outcome_id: UUID, data: OutcomeUpdate, db = Depends(get_db), current_user = Depends(require_role(UserRole.HEI_ADMIN, UserRole.FACULTY, UserRole.GOVERNMENT))):
    service = OutcomeService(db)
    return await service.update_outcome(outcome_id, data)

@router.post('/{outcome_id}/feedback', response_model=FeedbackResponse, status_code=201)
async def add_feedback(outcome_id: UUID, data: FeedbackCreate, db = Depends(get_db)):
    service = OutcomeService(db)
    return await service.add_feedback(outcome_id, data)
"""

files['analytics.py'] = """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_active_user
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.schemas.analytics import OverviewStats, DomainDistribution, DistrictDistribution, PipelineFunnel, SLAMetrics, InstitutionParticipation, ImpactSummary
from app.services.analytics import AnalyticsService

router = APIRouter()

@router.get('/overview', response_model=OverviewStats)
async def get_overview(db = Depends(get_db), current_user = Depends(require_role(UserRole.GOVERNMENT, UserRole.PLATFORM_ADMIN))):
    service = AnalyticsService(db)
    return await service.get_overview()

@router.get('/challenges/by-domain', response_model=list[DomainDistribution])
async def get_domain_distribution(db = Depends(get_db), current_user = Depends(require_role(UserRole.GOVERNMENT, UserRole.PLATFORM_ADMIN))):
    service = AnalyticsService(db)
    return await service.get_domain_distribution()

@router.get('/challenges/by-district', response_model=list[DistrictDistribution])
async def get_district_distribution(db = Depends(get_db), current_user = Depends(require_role(UserRole.GOVERNMENT, UserRole.PLATFORM_ADMIN))):
    service = AnalyticsService(db)
    return await service.get_district_distribution()

@router.get('/pipeline', response_model=PipelineFunnel)
async def get_pipeline(db = Depends(get_db), current_user = Depends(require_role(UserRole.GOVERNMENT, UserRole.PLATFORM_ADMIN))):
    service = AnalyticsService(db)
    return await service.get_pipeline_funnel()

@router.get('/sla', response_model=SLAMetrics)
async def get_sla(db = Depends(get_db), current_user = Depends(require_role(UserRole.GOVERNMENT, UserRole.PLATFORM_ADMIN))):
    service = AnalyticsService(db)
    return await service.get_sla_metrics()

@router.get('/institutions/participation', response_model=list[InstitutionParticipation])
async def get_participation(db = Depends(get_db), current_user = Depends(require_role(UserRole.GOVERNMENT, UserRole.PLATFORM_ADMIN))):
    service = AnalyticsService(db)
    return await service.get_institution_participation()

@router.get('/impact-summary', response_model=ImpactSummary)
async def get_impact_summary(db = Depends(get_db), current_user = Depends(require_role(UserRole.GOVERNMENT, UserRole.PLATFORM_ADMIN))):
    service = AnalyticsService(db)
    return await service.get_impact_summary()
"""

files['admin.py'] = """from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, PaginationParams, get_redis_client
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.schemas.user import UserResponse
from app.schemas.challenge import ChallengeResponse
from app.schemas.common import PaginatedResponse
from app.services.user import UserService
from app.services.challenge import ChallengeService
from app.services.audit import AuditService
import math

router = APIRouter()

@router.get('/users', response_model=PaginatedResponse[UserResponse])
async def admin_list_users(pagination: PaginationParams = Depends(), role: UserRole | None = None, is_active: bool | None = None, db = Depends(get_db), current_user = Depends(require_role(UserRole.PLATFORM_ADMIN))):
    service = UserService(db)
    users, total = await service.list_users(pagination.page, pagination.page_size, role, is_active)
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=users, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)

@router.patch('/users/{user_id}/role', response_model=UserResponse)
async def update_user_role(user_id: UUID, role: UserRole = Body(..., embed=True), db = Depends(get_db), current_user = Depends(require_role(UserRole.PLATFORM_ADMIN))):
    service = UserService(db)
    return await service.update_user_role(user_id, role)

@router.patch('/users/{user_id}/status', response_model=UserResponse)
async def toggle_user_status(user_id: UUID, is_active: bool = Body(..., embed=True), db = Depends(get_db), current_user = Depends(require_role(UserRole.PLATFORM_ADMIN))):
    service = UserService(db)
    return await service.toggle_user_status(user_id, is_active)

@router.get('/moderation-queue', response_model=PaginatedResponse[ChallengeResponse])
async def get_moderation_queue(pagination: PaginationParams = Depends(), db = Depends(get_db), current_user = Depends(require_role(UserRole.PLATFORM_ADMIN, UserRole.VERIFIER))):
    service = ChallengeService(db)
    challenges, total = await service.list_challenges(pagination.page, pagination.page_size, status='SUBMITTED')
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=challenges, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)

@router.get('/audit-log')
async def get_audit_log(pagination: PaginationParams = Depends(), entity_type: str | None = None, action: str | None = None, db = Depends(get_db), current_user = Depends(require_role(UserRole.PLATFORM_ADMIN))):
    service = AuditService(db)
    events, total = await service.get_audit_log(pagination.page, pagination.page_size, entity_type=entity_type, action=action)
    total_pages = math.ceil(total / pagination.page_size) if pagination.page_size else 0
    return PaginatedResponse(data=events, total=total, page=pagination.page, page_size=pagination.page_size, total_pages=total_pages)

@router.get('/system-health')
async def system_health(current_user = Depends(require_role(UserRole.PLATFORM_ADMIN))):
    from app.database import check_db_connection
    db_ok = await check_db_connection()
    try:
        redis = await get_redis_client()
        await redis.ping()
        redis_ok = True
    except Exception:
        redis_ok = False
    return {
        'database': 'healthy' if db_ok else 'unhealthy',
        'redis': 'healthy' if redis_ok else 'unhealthy',
        'status': 'healthy' if (db_ok and redis_ok) else 'degraded'
    }
"""

for name, content in files.items():
    with open(os.path.join(base_path, name), 'w') as f:
        f.write(content)

