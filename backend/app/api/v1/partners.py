from fastapi import APIRouter, Depends
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
