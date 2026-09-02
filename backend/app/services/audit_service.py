import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
import structlog

from app.models.audit import AuditEvent

logger = structlog.get_logger(__name__)

class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_event(self, actor_id: uuid.UUID | None, action: str, entity_type: str, entity_id: uuid.UUID, before_snapshot: dict | None = None, after_snapshot: dict | None = None, reason: str | None = None, ip_address: str | None = None, user_agent: str | None = None):
        try:
            event = AuditEvent(
                actor_id=actor_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                before_snapshot=before_snapshot,
                after_snapshot=after_snapshot,
                reason=reason,
                ip_address=ip_address,
                user_agent=user_agent
            )
            self.db.add(event)
            await self.db.commit()
        except Exception as e:
            logger.warning("Failed to log audit event", error=str(e))

    async def get_audit_log(self, page: int, page_size: int, entity_type: str | None = None, entity_id: uuid.UUID | None = None, actor_id: uuid.UUID | None = None, action: str | None = None) -> tuple[list[AuditEvent], int]:
        stmt = select(AuditEvent)
        if entity_type:
            stmt = stmt.where(AuditEvent.entity_type == entity_type)
        if entity_id:
            stmt = stmt.where(AuditEvent.entity_id == entity_id)
        if actor_id:
            stmt = stmt.where(AuditEvent.actor_id == actor_id)
        if action:
            stmt = stmt.where(AuditEvent.action == action)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(desc(AuditEvent.timestamp))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        events = (await self.db.execute(stmt)).scalars().all()
        return list(events), total_count
