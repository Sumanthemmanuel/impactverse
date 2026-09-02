from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, PaginationParams
from app.core.permissions import require_role
from app.core.constants import UserRole, ChallengeDomain, ChallengeStatus, ChallengeSeverity, MediaType
from app.schemas.challenge import ChallengeCreate, ChallengeResponse, ChallengeUpdate, ChallengeMediaResponse, ChallengeVerifyRequest, ChallengeSimilarResponse, ChallengeTimelineEntry, ChallengeHeatmapPoint, ChallengeClusterResponse
from app.schemas.common import PaginatedResponse
from app.services.challenge_service import ChallengeService
from app.services.file_service import FileService
from app.models.challenge import Challenge, ChallengeMedia
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
    """
    Upload a photo/video/document for a challenge.

    - Saves the file to local storage.
    - For JPEG/PNG images: reads EXIF GPS geotag automatically.
      If the challenge has no location yet, the extracted GPS coordinates are
      written back to the challenge so it appears on the heatmap immediately.
    - Creates a ChallengeMedia DB row with any extracted metadata.
    """
    file_service = FileService()
    file_info = await file_service.upload_file(file, folder=f'challenges/{challenge_id}')

    # Persist media record
    media = ChallengeMedia(
        challenge_id=challenge_id,
        file_url=file_info["file_url"],
        file_type=MediaType(file_info["file_type"]),
        file_name=file_info.get("file_name"),
        file_size=file_info.get("file_size"),
        metadata_json={
            k: v for k, v in file_info.items()
            if k not in ("file_url", "file_type", "file_name", "file_size")
        } or None,
    )
    db.add(media)

    # If EXIF GPS was extracted and the challenge lacks a location, update it
    if "gps_latitude" in file_info and "gps_longitude" in file_info:
        from sqlalchemy import select
        from geoalchemy2.shape import from_shape
        from shapely.geometry import Point

        stmt = select(Challenge).where(Challenge.id == challenge_id)
        challenge = (await db.execute(stmt)).scalar_one_or_none()
        if challenge and challenge.location is None:
            challenge.location = from_shape(
                Point(file_info["gps_longitude"], file_info["gps_latitude"]),
                srid=4326,
            )

    await db.commit()
    await db.refresh(media)
    return ChallengeMediaResponse.model_validate(media)

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
