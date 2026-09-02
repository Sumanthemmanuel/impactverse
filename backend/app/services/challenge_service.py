import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
import structlog

from app.models.challenge import Challenge, ChallengeStatus, ChallengeStatusHistory, ChallengeCluster
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate
from app.core.exceptions import NotFoundError, ValidationError

logger = structlog.get_logger(__name__)

class ChallengeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_challenge(self, data: ChallengeCreate, reporter_id: uuid.UUID | None) -> Challenge:
        geom = None
        if data.latitude is not None and data.longitude is not None:
            geom = from_shape(Point(data.longitude, data.latitude), srid=4326)

        challenge = Challenge(
            title=data.title,
            narrative=data.narrative,
            reporter_id=reporter_id,
            status=ChallengeStatus.SUBMITTED,
            location=geom,
            district=data.district
        )
        self.db.add(challenge)
        await self.db.commit()
        await self.db.refresh(challenge)

        history = ChallengeStatusHistory(
            challenge_id=challenge.id,
            to_status=ChallengeStatus.SUBMITTED,
            changed_by_id=reporter_id
        )
        self.db.add(history)
        await self.db.commit()

        try:
            challenge = await self._run_ai_enrichment(challenge)
        except Exception as e:
            logger.warning("AI enrichment failed", challenge_id=str(challenge.id), error=str(e))

        return challenge

    async def get_challenge(self, challenge_id: uuid.UUID) -> Challenge:
        stmt = select(Challenge).options(
            selectinload(Challenge.reporter),
            selectinload(Challenge.cluster),
            selectinload(Challenge.status_history)
        ).where(Challenge.id == challenge_id)
        result = await self.db.execute(stmt)
        challenge = result.scalar_one_or_none()
        if not challenge:
            raise NotFoundError("Challenge not found")
        return challenge

    async def list_challenges(self, page: int, page_size: int, domain: str | None = None, status: str | None = None, district: str | None = None, severity: str | None = None, sort_by: str = 'created_at', sort_order: str = 'desc') -> tuple[list[Challenge], int]:
        stmt = select(Challenge)
        if domain:
            stmt = stmt.where(Challenge.domain == domain)
        if status:
            stmt = stmt.where(Challenge.status == ChallengeStatus(status))
        if district:
            stmt = stmt.where(Challenge.district == district)
        if severity:
            stmt = stmt.where(Challenge.severity == severity)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = (await self.db.execute(count_stmt)).scalar_one()

        order_col = getattr(Challenge, sort_by)
        if sort_order == 'desc':
            stmt = stmt.order_by(desc(order_col))
        else:
            stmt = stmt.order_by(order_col)

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        challenges = (await self.db.execute(stmt)).scalars().all()
        return list(challenges), total_count

    async def update_challenge(self, challenge_id: uuid.UUID, data: ChallengeUpdate, user_id: uuid.UUID) -> Challenge:
        challenge = await self.get_challenge(challenge_id)
        update_data = data.model_dump(exclude_unset=True)
        needs_ai = 'domain' in update_data or 'narrative' in update_data
        
        for key, value in update_data.items():
            setattr(challenge, key, value)
            
        await self.db.commit()
        await self.db.refresh(challenge)

        if needs_ai:
            try:
                challenge = await self._run_ai_enrichment(challenge)
            except Exception as e:
                logger.warning("AI enrichment failed after update", challenge_id=str(challenge.id), error=str(e))

        return challenge

    async def verify_challenge(self, challenge_id: uuid.UUID, action: str, user_id: uuid.UUID, domain_override: str | None = None, severity_override: str | None = None, notes: str | None = None) -> Challenge:
        challenge = await self.get_challenge(challenge_id)
        if challenge.status not in [ChallengeStatus.SUBMITTED, ChallengeStatus.UNDER_REVIEW]:
            raise ValidationError("Challenge is not in a verifiable state")

        new_status = ChallengeStatus.VALIDATED if action == 'approve' else ChallengeStatus.REJECTED
        
        if action == 'approve':
            if domain_override:
                challenge.domain = domain_override
            if severity_override:
                challenge.severity = severity_override

        history = ChallengeStatusHistory(
            challenge_id=challenge.id,
            from_status=challenge.status,
            to_status=new_status,
            changed_by_id=user_id,
            notes=notes
        )
        challenge.status = new_status
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(challenge)
        return challenge

    async def get_similar_challenges(self, challenge_id: uuid.UUID, limit: int = 10) -> list[dict]:
        return []

    async def get_challenge_timeline(self, challenge_id: uuid.UUID) -> list[dict]:
        stmt = select(ChallengeStatusHistory).where(ChallengeStatusHistory.challenge_id == challenge_id).order_by(ChallengeStatusHistory.created_at)
        result = await self.db.execute(stmt)
        return [{"status": h.to_status.value, "timestamp": h.created_at, "notes": h.notes} for h in result.scalars().all()]

    async def get_heatmap_data(self, domain: str | None = None) -> list[dict]:
        return []

    async def get_clusters(self, page: int, page_size: int) -> tuple[list[ChallengeCluster], int]:
        return [], 0

    async def _run_ai_enrichment(self, challenge: Challenge) -> Challenge:
        return challenge
