import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.partner import Partner, PartnerInterest, InterestStatus
from app.schemas.partner import PartnerCreate, PartnerUpdate, PartnerInterestCreate, PartnerInterestUpdate
from app.core.exceptions import NotFoundError, ConflictError

class PartnerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_partner(self, data: PartnerCreate, user_id: uuid.UUID) -> Partner:
        partner = Partner(user_id=user_id, **data.model_dump())
        self.db.add(partner)
        await self.db.commit()
        await self.db.refresh(partner)
        return partner

    async def get_partner(self, partner_id: uuid.UUID) -> Partner:
        stmt = select(Partner).options(selectinload(Partner.interests)).where(Partner.id == partner_id)
        partner = (await self.db.execute(stmt)).scalar_one_or_none()
        if not partner:
            raise NotFoundError("Partner not found")
        return partner

    async def list_partners(self, page: int, page_size: int, partner_type: str | None = None, domain: str | None = None) -> tuple[list[Partner], int]:
        stmt = select(Partner)
        if partner_type:
            stmt = stmt.where(Partner.partner_type == partner_type)
        if domain:
            stmt = stmt.where(Partner.domains.contains([domain]))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        partners = (await self.db.execute(stmt)).scalars().all()
        return list(partners), total_count

    async def update_partner(self, partner_id: uuid.UUID, data: PartnerUpdate) -> Partner:
        partner = await self.get_partner(partner_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(partner, key, value)
        await self.db.commit()
        await self.db.refresh(partner)
        return partner

    async def create_interest(self, partner_id: uuid.UUID, data: PartnerInterestCreate, user_id: uuid.UUID) -> PartnerInterest:
        stmt = select(PartnerInterest).where(PartnerInterest.partner_id == partner_id, PartnerInterest.project_id == data.project_id)
        if (await self.db.execute(stmt)).scalar_one_or_none():
            raise ConflictError("Interest already exists")

        interest = PartnerInterest(partner_id=partner_id, status=InterestStatus.PENDING, **data.model_dump())
        self.db.add(interest)
        await self.db.commit()
        await self.db.refresh(interest)
        return interest

    async def list_interests_for_project(self, project_id: uuid.UUID) -> list[PartnerInterest]:
        stmt = select(PartnerInterest).where(PartnerInterest.project_id == project_id)
        interests = (await self.db.execute(stmt)).scalars().all()
        return list(interests)

    async def update_interest(self, interest_id: uuid.UUID, data: PartnerInterestUpdate, user_id: uuid.UUID) -> PartnerInterest:
        stmt = select(PartnerInterest).where(PartnerInterest.id == interest_id)
        interest = (await self.db.execute(stmt)).scalar_one_or_none()
        if not interest:
            raise NotFoundError("Interest not found")
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(interest, key, value)
        await self.db.commit()
        await self.db.refresh(interest)
        return interest
