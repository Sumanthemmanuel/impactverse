from fastapi import APIRouter, Depends
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
