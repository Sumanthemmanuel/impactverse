import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.challenge import Challenge
from app.models.project import Project

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview(self) -> dict:
        total_challenges = (await self.db.execute(select(func.count()).select_from(Challenge))).scalar_one()
        total_projects = (await self.db.execute(select(func.count()).select_from(Project))).scalar_one()
        return {
            "total_challenges": total_challenges,
            "total_projects": total_projects,
            "validated_challenges": 0,
            "deployed_projects": 0,
            "institutions_count": 0,
            "partners_count": 0,
            "beneficiaries": 0,
            "avg_impact_score": 0.0
        }

    async def get_domain_distribution(self) -> list[dict]:
        stmt = select(Challenge.domain, func.count(Challenge.id)).group_by(Challenge.domain)
        result = await self.db.execute(stmt)
        return [{"domain": row[0], "count": row[1]} for row in result.all()]

    async def get_district_distribution(self) -> list[dict]:
        return []

    async def get_pipeline_funnel(self) -> dict:
        return {}

    async def get_sla_metrics(self) -> dict:
        return {}

    async def get_institution_participation(self) -> list[dict]:
        return []

    async def get_impact_summary(self) -> dict:
        return {}
