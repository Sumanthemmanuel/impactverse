import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectStatus, ProjectMember, Milestone
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectMemberAdd, MilestoneCreate, MilestoneUpdate
from app.core.exceptions import NotFoundError, ValidationError

class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, data: ProjectCreate, user_id: uuid.UUID) -> Project:
        project = Project(**data.model_dump())
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_project(self, project_id: uuid.UUID) -> Project:
        stmt = select(Project).options(
            selectinload(Project.challenge),
            selectinload(Project.institution),
            selectinload(Project.members),
            selectinload(Project.milestones),
            selectinload(Project.partner_interests)
        ).where(Project.id == project_id)
        project = (await self.db.execute(stmt)).scalar_one_or_none()
        if not project:
            raise NotFoundError("Project not found")
        return project

    async def list_projects(self, page: int, page_size: int, status: str | None = None, institution_id: uuid.UUID | None = None) -> tuple[list[Project], int]:
        stmt = select(Project)
        if status:
            stmt = stmt.where(Project.status == ProjectStatus(status))
        if institution_id:
            stmt = stmt.where(Project.institution_id == institution_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        projects = (await self.db.execute(stmt)).scalars().all()
        return list(projects), total_count

    async def update_project(self, project_id: uuid.UUID, data: ProjectUpdate, user_id: uuid.UUID) -> Project:
        project = await self.get_project(project_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def add_member(self, project_id: uuid.UUID, data: ProjectMemberAdd, user_id: uuid.UUID) -> ProjectMember:
        await self.get_project(project_id)
        member = ProjectMember(project_id=project_id, **data.model_dump())
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def add_milestone(self, project_id: uuid.UUID, data: MilestoneCreate) -> Milestone:
        milestone = Milestone(project_id=project_id, **data.model_dump())
        self.db.add(milestone)
        await self.db.commit()
        await self.db.refresh(milestone)
        return milestone

    async def update_milestone(self, project_id: uuid.UUID, milestone_id: uuid.UUID, data: MilestoneUpdate) -> Milestone:
        stmt = select(Milestone).where(Milestone.id == milestone_id, Milestone.project_id == project_id)
        milestone = (await self.db.execute(stmt)).scalar_one_or_none()
        if not milestone:
            raise NotFoundError("Milestone not found")
            
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(milestone, key, value)
        await self.db.commit()
        await self.db.refresh(milestone)
        return milestone

    async def get_deployment_readiness(self, project_id: uuid.UUID) -> dict:
        return {"score": 0.0, "breakdown": {}, "recommendations": []}
