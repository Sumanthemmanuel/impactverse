import uuid
import structlog

logger = structlog.get_logger(__name__)

class NotificationService:
    """Handles sending notifications via email, SMS, push.
    For now, logs notifications. Production would use actual providers."""

    @staticmethod
    async def notify_challenge_submitted(challenge_id: uuid.UUID, reporter_email: str | None):
        logger.info("Notification sent", event="challenge_submitted", challenge_id=str(challenge_id), to=reporter_email)

    @staticmethod
    async def notify_challenge_validated(challenge_id: uuid.UUID, reporter_email: str | None):
        logger.info("Notification sent", event="challenge_validated", challenge_id=str(challenge_id), to=reporter_email)

    @staticmethod
    async def notify_match_found(challenge_id: uuid.UUID, institution_ids: list[uuid.UUID]):
        logger.info("Notification sent", event="match_found", challenge_id=str(challenge_id), institutions=[str(id) for id in institution_ids])

    @staticmethod
    async def notify_project_status_change(project_id: uuid.UUID, new_status: str):
        logger.info("Notification sent", event="project_status_change", project_id=str(project_id), new_status=new_status)

    @staticmethod
    async def notify_partner_interest(project_id: uuid.UUID, partner_name: str):
        logger.info("Notification sent", event="partner_interest", project_id=str(project_id), partner_name=partner_name)
