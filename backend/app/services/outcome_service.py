import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.outcome import Outcome, BeneficiaryFeedback
from app.models.project import Project, ProjectStatus
from app.schemas.outcome import OutcomeCreate, OutcomeUpdate, FeedbackCreate
from app.core.exceptions import NotFoundError, ValidationError

class OutcomeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_outcome(self, data: OutcomeCreate, user_id: uuid.UUID) -> Outcome:
        stmt = select(Project).where(Project.id == data.project_id)
        project = (await self.db.execute(stmt)).scalar_one_or_none()
        if not project:
            raise NotFoundError("Project not found")
        if project.status not in [ProjectStatus.PILOT, ProjectStatus.DEPLOYED]:
            raise ValidationError("Project is not ready for outcomes")

        outcome = Outcome(**data.model_dump())
        self.db.add(outcome)
        
        if data.deployment_status != "NOT_STARTED" and project.status != ProjectStatus.DEPLOYED:
            project.status = ProjectStatus.DEPLOYED
            
        await self.db.commit()
        await self.db.refresh(outcome)
        return outcome

    async def get_outcome(self, project_id: uuid.UUID) -> Outcome:
        stmt = select(Outcome).options(selectinload(Outcome.feedback)).where(Outcome.project_id == project_id)
        outcome = (await self.db.execute(stmt)).scalar_one_or_none()
        if not outcome:
            raise NotFoundError("Outcome not found")
        return outcome

    async def update_outcome(self, outcome_id: uuid.UUID, data: OutcomeUpdate) -> Outcome:
        stmt = select(Outcome).where(Outcome.id == outcome_id)
        outcome = (await self.db.execute(stmt)).scalar_one_or_none()
        if not outcome:
            raise NotFoundError("Outcome not found")
            
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(outcome, key, value)
        await self.db.commit()
        await self.db.refresh(outcome)
        return outcome

    async def add_feedback(self, outcome_id: uuid.UUID, data: FeedbackCreate) -> BeneficiaryFeedback:
        feedback = BeneficiaryFeedback(outcome_id=outcome_id, **data.model_dump())
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def get_impact_ledger(self, page: int, page_size: int, domain: str | None = None) -> tuple[list[dict], int]:
        return [], 0
