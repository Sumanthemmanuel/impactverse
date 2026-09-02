from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_active_user
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshTokenRequest, TokenResponse, ChangePasswordRequest
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import SuccessResponse
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter()

@router.post('/register', response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, tokens = await service.register(data)
    return tokens

@router.post('/login', response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, tokens = await service.login(data)
    return tokens

@router.post('/refresh', response_model=TokenResponse)
async def refresh(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh_token(data.refresh_token)

@router.post('/logout', response_model=SuccessResponse)
async def logout(request: Request, current_user = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    # Assuming JTI is extracted in auth middleware or dependency. For now, simple implementation
    auth_header = request.headers.get("Authorization")
    jti = "mock_jti_from_token"  # Placeholder
    service = AuthService(db)
    await service.logout(jti)
    return SuccessResponse(message='Logged out successfully')

@router.get('/me', response_model=UserResponse)
async def get_me(current_user = Depends(get_current_active_user)):
    return current_user

@router.put('/me', response_model=UserResponse)
async def update_me(data: UserUpdate, current_user = Depends(get_current_active_user), db = Depends(get_db)):
    service = UserService(db)
    return await service.update_user(current_user.id, data)

@router.post('/change-password', response_model=SuccessResponse)
async def change_password(data: ChangePasswordRequest, current_user = Depends(get_current_active_user), db = Depends(get_db)):
    service = AuthService(db)
    await service.change_password(current_user.id, data.current_password, data.new_password)
    return SuccessResponse(message='Password changed successfully')
