from fastapi import APIRouter, Depends, UploadFile
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
