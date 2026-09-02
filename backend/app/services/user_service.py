import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User, UserRole
from app.schemas.user import UserUpdate
from app.core.exceptions import NotFoundError

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = await self.get_user_by_id(user_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def list_users(self, page: int, page_size: int, role: UserRole | None = None, is_active: bool | None = None) -> tuple[list[User], int]:
        stmt = select(User)
        if role:
            stmt = stmt.where(User.role == role)
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        users = (await self.db.execute(stmt)).scalars().all()
        return list(users), total_count

    async def update_user_role(self, user_id: uuid.UUID, new_role: UserRole) -> User:
        user = await self.get_user_by_id(user_id)
        user.role = new_role
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def toggle_user_status(self, user_id: uuid.UUID, is_active: bool) -> User:
        user = await self.get_user_by_id(user_id)
        user.is_active = is_active
        await self.db.commit()
        await self.db.refresh(user)
        return user
