from typing import Optional
import redis.asyncio as redis
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

async def get_redis_client():
    client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> dict:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid token payload")
        
        # Simulating user fetch from DB. 
        # In actual implementation, query the User model:
        # user = await db.get(User, user_id)
        # if not user:
        #     raise UnauthorizedError("User not found")
        
        # For now, returning decoded payload as mock user dict
        user = {
            "id": user_id,
            "role": payload.get("role"),
            "is_active": True, # Mock
            **payload
        }
        
        return user
    except ValueError as e:
        raise UnauthorizedError(str(e))
    except Exception as e:
        raise UnauthorizedError("Could not validate credentials")

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    if not current_user.get("is_active", True):
        raise ForbiddenError("Inactive user")
    return current_user

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
        self.limit = page_size
