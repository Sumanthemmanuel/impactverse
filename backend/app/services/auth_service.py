import uuid
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError, NotFoundError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def register(self, data: RegisterRequest) -> tuple[User, TokenResponse]:
        stmt = select(User).where(User.email == data.email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise ConflictError("Email already registered")

        if data.phone:
            stmt = select(User).where(User.phone == data.phone)
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                raise ConflictError("Phone number already registered")

        hashed_password = pwd_context.hash(data.password)

        user = User(
            email=data.email,
            phone=data.phone,
            password_hash=hashed_password,
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        tokens = await self._generate_tokens(user)
        return user, tokens

    async def login(self, data: LoginRequest) -> tuple[User, TokenResponse]:
        stmt = select(User).where(User.email == data.email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not pwd_context.verify(data.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("User is inactive")

        tokens = await self._generate_tokens(user)
        return user, tokens

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti")
            user_id = payload.get("sub")
        except jwt.PyJWTError:
            raise UnauthorizedError("Invalid refresh token")

        is_blacklisted = await self.redis.get(f"bl_{jti}")
        if is_blacklisted:
            raise UnauthorizedError("Token is blacklisted")

        await self.redis.setex(f"bl_{jti}", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "1")

        stmt = select(User).where(User.id == uuid.UUID(user_id))
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        return await self._generate_tokens(user)

    async def logout(self, access_token_jti: str, refresh_token: str | None = None):
        await self.redis.setex(f"bl_{access_token_jti}", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "1")
        if refresh_token:
            try:
                payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
                jti = payload.get("jti")
                if jti:
                    await self.redis.setex(f"bl_{jti}", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "1")
            except jwt.PyJWTError:
                pass

    async def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str):
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError("User not found")

        if not pwd_context.verify(current_password, user.password_hash):
            raise UnauthorizedError("Invalid current password")

        user.password_hash = pwd_context.hash(new_password)
        await self.db.commit()

    async def _generate_tokens(self, user: User) -> TokenResponse:
        access_jti = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        access_payload = {
            "sub": str(user.id),
            "role": user.role.name,
            "jti": access_jti,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": now,
        }
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm="HS256")

        refresh_payload = {
            "sub": str(user.id),
            "jti": refresh_jti,
            "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": now,
        }
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")

        await self.redis.setex(f"rt_{refresh_jti}", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            token_type="Bearer"
        )
