import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.challenge import Challenge, ChallengeStatus, ChallengeStatusHistory
from app.models.project import Project, ProjectStatus
from app.core.exceptions import ValidationError

class MatchingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_matches_for_challenge(self, challenge_id: uuid.UUID) -> list[dict]:
        return []

    async def accept_challenge(self, challenge_id: uuid.UUID, institution_id: uuid.UUID, user_id: uuid.UUID) -> Project:
        stmt = select(Challenge).where(Challenge.id == challenge_id)
        challenge = (await self.db.execute(stmt)).scalar_one_or_none()
        
        if not challenge or challenge.status not in [ChallengeStatus.VALIDATED, ChallengeStatus.MATCHED]:
            raise ValidationError("Challenge cannot be accepted")

        history = ChallengeStatusHistory(
            challenge_id=challenge.id,
            from_status=challenge.status,
            to_status=ChallengeStatus.MATCHED,
            changed_by_id=user_id
        )
        challenge.status = ChallengeStatus.MATCHED
        
        project = Project(
            challenge_id=challenge.id,
            institution_id=institution_id,
            status=ProjectStatus.PROPOSED,
            title=f"Project for {challenge.title}"
        )
        
        self.db.add(history)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def decline_challenge(self, challenge_id: uuid.UUID, institution_id: uuid.UUID, user_id: uuid.UUID, reason: str) -> Challenge:
        stmt = select(Challenge).where(Challenge.id == challenge_id)
        challenge = (await self.db.execute(stmt)).scalar_one_or_none()
        return challenge

    async def get_score_config(self) -> dict:
        return {}

    async def update_score_config(self, config: dict, user_id: uuid.UUID) -> dict:
        return config
