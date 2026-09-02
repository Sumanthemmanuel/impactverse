from fastapi import APIRouter, Depends
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
