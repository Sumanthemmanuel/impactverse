from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.api.deps import get_db, get_current_active_user, PaginationParams, get_redis_client
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.schemas.user import UserResponse
from app.schemas.challenge import ChallengeResponse
from app.schemas.common import PaginatedResponse
from app.services.user import UserService
from app.services.challenge_service import ChallengeService
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
