import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.models.institution import Institution, Department, Lab
from app.schemas.institution import InstitutionCreate, InstitutionUpdate, DepartmentCreate, LabCreate
from app.core.exceptions import ConflictError, NotFoundError

class InstitutionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_institution(self, data: InstitutionCreate, admin_user_id: uuid.UUID) -> Institution:
        stmt = select(Institution).where(Institution.name == data.name)
        if (await self.db.execute(stmt)).scalar_one_or_none():
            raise ConflictError("Institution name already exists")

        geom = None
        if data.location is not None:
            geom = from_shape(Point(data.location.longitude, data.location.latitude), srid=4326)

        institution = Institution(
            name=data.name,
            institution_type=data.institution_type,
            address=data.address,
            district=data.district,
            state=data.state,
            website=data.website,
            established_year=data.established_year,
            accreditation=data.accreditation,
            incubation_facilities=data.incubation_facilities,
            total_faculty=data.total_faculty,
            total_students=data.total_students,
            location=geom,
            admin_user_id=admin_user_id
        )
        self.db.add(institution)
        await self.db.commit()
        await self.db.refresh(institution)
        return institution

    async def get_institution(self, institution_id: uuid.UUID) -> Institution:
        stmt = select(Institution).options(
            selectinload(Institution.departments).selectinload(Department.labs)
        ).where(Institution.id == institution_id)
        institution = (await self.db.execute(stmt)).scalar_one_or_none()
        if not institution:
            raise NotFoundError("Institution not found")
        return institution

    async def list_institutions(self, page: int, page_size: int, district: str | None = None, verified: bool | None = None) -> tuple[list[Institution], int]:
        stmt = select(Institution)
        if district:
            stmt = stmt.where(Institution.district == district)
        if verified is not None:
            stmt = stmt.where(Institution.verified == verified)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        institutions = (await self.db.execute(stmt)).scalars().all()
        return list(institutions), total_count

    async def update_institution(self, institution_id: uuid.UUID, data: InstitutionUpdate) -> Institution:
        institution = await self.get_institution(institution_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(institution, key, value)
        await self.db.commit()
        await self.db.refresh(institution)
        return institution

    async def add_department(self, institution_id: uuid.UUID, data: DepartmentCreate) -> Department:
        await self.get_institution(institution_id)
        department = Department(
            institution_id=institution_id,
            name=data.name,
            research_areas=data.research_areas
        )
        self.db.add(department)
        await self.db.commit()
        await self.db.refresh(department)
        return department

    async def add_lab(self, department_id: uuid.UUID, data: LabCreate) -> Lab:
        stmt = select(Department).where(Department.id == department_id)
        if not (await self.db.execute(stmt)).scalar_one_or_none():
            raise NotFoundError("Department not found")
            
        lab = Lab(
            department_id=department_id,
            name=data.name,
            description=data.description,
            equipment=data.equipment,
            specialization=data.specialization,
        )
        self.db.add(lab)
        await self.db.commit()
        await self.db.refresh(lab)
        return lab

    async def get_challenge_inbox(self, institution_id: uuid.UUID, page: int, page_size: int) -> tuple[list[dict], int]:
        return [], 0
