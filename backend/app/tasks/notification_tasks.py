from app.tasks.celery_app import celery_app
import structlog

logger = structlog.get_logger()

@celery_app.task
def send_challenge_submitted_notification(challenge_id: str, reporter_email: str | None):
    """Notify reporter that challenge was submitted."""
    logger.info('Notification: challenge submitted', challenge_id=challenge_id, email=reporter_email)
    # In production: send email via SMTP
    # For now, just log

@celery_app.task
def send_challenge_validated_notification(challenge_id: str, reporter_email: str | None):
    """Notify reporter that challenge was validated."""
    logger.info('Notification: challenge validated', challenge_id=challenge_id, email=reporter_email)

@celery_app.task
def send_match_found_notification(challenge_id: str, institution_ids: list[str]):
    """Notify matched institutions about a new challenge match."""
    logger.info('Notification: match found', challenge_id=challenge_id, institutions=institution_ids)

@celery_app.task
def send_project_status_notification(project_id: str, new_status: str, member_emails: list[str]):
    """Notify project members about status change."""
    logger.info('Notification: project status changed', project_id=project_id, status=new_status, members=member_emails)

@celery_app.task
def send_partner_interest_notification(project_id: str, partner_name: str, lead_email: str):
    """Notify project lead about new partner interest."""
    logger.info('Notification: partner interest', project_id=project_id, partner=partner_name, lead_email=lead_email)

@celery_app.task
def send_milestone_reminder(project_id: str, milestone_title: str, due_date: str, member_emails: list[str]):
    """Remind team about upcoming milestone deadline."""
    logger.info('Notification: milestone reminder', project_id=project_id, milestone=milestone_title, due_date=due_date)
