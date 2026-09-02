from fastapi import APIRouter, Depends, Body
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
