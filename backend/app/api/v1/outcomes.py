from fastapi import APIRouter, Depends
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
