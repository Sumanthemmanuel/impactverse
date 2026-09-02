from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, PaginationParams
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.schemas.institution import InstitutionCreate, InstitutionResponse, InstitutionUpdate, DepartmentCreate, DepartmentResponse, LabCreate, LabResponse
from app.schemas.common import PaginatedResponse
from app.services.institution_service import InstitutionService
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
