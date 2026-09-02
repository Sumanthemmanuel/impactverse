from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.core.constants import UserRole
from app.schemas.common import PaginatedResponse

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    language_preference: str
    avatar_url: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language_preference: Optional[str] = None
    avatar_url: Optional[str] = None
    district: Optional[str] = None
    bio: Optional[str] = None

class UserListResponse(PaginatedResponse[UserResponse]):
    pass
