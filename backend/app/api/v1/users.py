from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, PaginationParams
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import PaginatedResponse
from app.services.user_service import UserService
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
