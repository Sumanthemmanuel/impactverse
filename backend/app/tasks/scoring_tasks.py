from app.tasks.celery_app import celery_app
import structlog
from datetime import date

logger = structlog.get_logger()

@celery_app.task
def recompute_impact_scores():
    """Batch recalculate impact scores (e.g., when weights change)."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.challenge import Challenge
    from app.ai.impact_scorer import impact_scorer
    from app.ai.text_extractor import text_extractor
    
    sync_url = str(settings.DATABASE_URL).replace('+asyncpg', '')
    engine = create_engine(sync_url)
    
    try:
        with Session(engine) as session:
            challenges = session.execute(select(Challenge)).scalars().all()
            updated = 0
            
            for challenge in challenges:
                text = f"{challenge.title} {challenge.narrative}"
                urgency_count = text_extractor.count_urgency_indicators(text)
                media_count = len(challenge.media) if hasattr(challenge, 'media') and challenge.media else 0
                
                score, _ = impact_scorer.compute_impact_score(
                    severity=challenge.severity,
                    affected_population=challenge.affected_population,
                    urgency_keywords_found=urgency_count,
                    evidence_count=media_count,
                    has_location=challenge.location is not None,
                    has_media=media_count > 0,
                    domain=challenge.domain,
                )
                challenge.impact_score = score
                updated += 1
            
            session.commit()
            logger.info('Impact scores recomputed', challenges_updated=updated)
    except Exception as exc:
        logger.error('Impact score recomputation failed', error=str(exc))
    finally:
        engine.dispose()


@celery_app.task
def check_overdue_milestones():
    """Daily task to mark overdue milestones."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.project import Milestone
    from app.core.constants import MilestoneStatus
    
    sync_url = str(settings.DATABASE_URL).replace('+asyncpg', '')
    engine = create_engine(sync_url)
    
    try:
        with Session(engine) as session:
            today = date.today()
            overdue = session.execute(
                select(Milestone).where(
                    Milestone.due_date < today,
                    Milestone.status.in_([MilestoneStatus.PENDING, MilestoneStatus.IN_PROGRESS]),
                )
            ).scalars().all()
            
            for milestone in overdue:
                milestone.status = MilestoneStatus.OVERDUE
            
            session.commit()
            logger.info('Overdue milestones updated', count=len(overdue))
    except Exception as exc:
        logger.error('Overdue milestone check failed', error=str(exc))
    finally:
        engine.dispose()


@celery_app.task
def compute_deployment_readiness(project_id: str):
    """Compute deployment readiness score for a project."""
    from sqlalchemy import create_engine, select, func
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.project import Project, Milestone, ProjectMember
    from app.models.partner import PartnerInterest
    from app.core.constants import MilestoneStatus, InterestStatus
    from uuid import UUID
    
    sync_url = str(settings.DATABASE_URL).replace('+asyncpg', '')
    engine = create_engine(sync_url)
    
    try:
        with Session(engine) as session:
            project = session.get(Project, UUID(project_id))
            if not project:
                return
            
            # Milestones completion ratio (40%)
            total_milestones = session.execute(
                select(func.count()).select_from(Milestone).where(Milestone.project_id == project.id)
            ).scalar_one()
            completed_milestones = session.execute(
                select(func.count()).select_from(Milestone).where(
                    Milestone.project_id == project.id,
                    Milestone.status == MilestoneStatus.COMPLETED
                )
            ).scalar_one()
            milestone_ratio = completed_milestones / total_milestones if total_milestones > 0 else 0
            
            # Partner support (20%)
            accepted_interests = session.execute(
                select(func.count()).select_from(PartnerInterest).where(
                    PartnerInterest.project_id == project.id,
                    PartnerInterest.status == InterestStatus.ACCEPTED
                )
            ).scalar_one()
            partner_score = min(1.0, accepted_interests * 0.5)
            
            # Budget secured (15%)
            budget_ratio = project.funding_secured / project.budget if project.budget and project.budget > 0 else 0
            budget_ratio = min(1.0, budget_ratio)
            
            # Team completeness (10%)
            member_count = session.execute(
                select(func.count()).select_from(ProjectMember).where(ProjectMember.project_id == project.id)
            ).scalar_one()
            team_score = min(1.0, member_count / 3)  # At least 3 members for full score
            
            # Has field evidence (15%)
            evidence_milestones = session.execute(
                select(func.count()).select_from(Milestone).where(
                    Milestone.project_id == project.id,
                    Milestone.evidence_url.isnot(None)
                )
            ).scalar_one()
            evidence_score = min(1.0, evidence_milestones * 0.5)
            
            # Weighted sum
            readiness = (
                0.40 * milestone_ratio +
                0.20 * partner_score +
                0.15 * budget_ratio +
                0.15 * evidence_score +
                0.10 * team_score
            )
            
            project.deployment_readiness_score = round(readiness, 4)
            session.commit()
            logger.info('Deployment readiness computed', project_id=project_id, score=readiness)
    except Exception as exc:
        logger.error('Deployment readiness computation failed', project_id=project_id, error=str(exc))
    finally:
        engine.dispose()
