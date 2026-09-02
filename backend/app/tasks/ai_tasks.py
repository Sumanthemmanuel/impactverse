from app.tasks.celery_app import celery_app
import structlog

logger = structlog.get_logger()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def enrich_challenge(self, challenge_id: str):
    """
    Run full AI enrichment pipeline on a challenge:
    1. Generate semantic embedding
    2. Classify domain
    3. Estimate severity
    4. Generate AI summary
    5. Extract tags and entities
    6. Compute impact score
    7. Detect duplicates
    8. Assign to cluster
    """
    # Use synchronous DB session since Celery tasks are sync
    # Import here to avoid circular imports
    import asyncio
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.config import settings
    from uuid import UUID
    
    # Create sync engine for Celery
    sync_url = str(settings.DATABASE_URL).replace('+asyncpg', '')
    engine = create_engine(sync_url)
    
    try:
        with Session(engine) as session:
            from app.models.challenge import Challenge
            challenge = session.get(Challenge, UUID(challenge_id))
            if not challenge:
                logger.warning('Challenge not found for enrichment', challenge_id=challenge_id)
                return
            
            # 1. Generate embedding
            from app.ai.embeddings import embedding_service
            text = f"{challenge.title} {challenge.narrative}"
            embedding = embedding_service.get_embedding(text)
            challenge.embedding = embedding
            
            # 2. Classify domain
            from app.ai.classifier import classifier
            domain, confidence = classifier.classify_domain(text)
            challenge.ai_domain = domain.value
            challenge.ai_confidence = confidence
            
            # 3. Extract tags
            tags = classifier.extract_tags(text)
            challenge.ai_tags = tags
            
            # 4. Generate summary
            summary = classifier.generate_summary(text)
            challenge.ai_summary = summary
            
            # 5. Impact score
            from app.ai.impact_scorer import impact_scorer
            from app.ai.text_extractor import text_extractor
            urgency_count = text_extractor.count_urgency_indicators(text)
            media_count = 0  # Will be updated when media is attached
            has_location = challenge.location is not None
            
            score, breakdown = impact_scorer.compute_impact_score(
                severity=challenge.severity,
                affected_population=challenge.affected_population,
                urgency_keywords_found=urgency_count,
                evidence_count=media_count,
                has_location=has_location,
                has_media=False,
                domain=challenge.domain,
            )
            challenge.impact_score = score
            challenge.evidence_score = impact_scorer.compute_evidence_score(
                media_count=media_count,
                has_location=has_location,
                narrative_length=len(challenge.narrative),
            )
            
            session.commit()
            logger.info('Challenge enriched successfully', challenge_id=challenge_id, impact_score=score)
            
    except Exception as exc:
        logger.error('Challenge enrichment failed', challenge_id=challenge_id, error=str(exc))
        raise self.retry(exc=exc)
    finally:
        engine.dispose()


@celery_app.task(bind=True, max_retries=2)
def compute_capability_matches(self, challenge_id: str):
    """
    Compute and cache capability matches for a validated challenge.
    """
    import asyncio
    from uuid import UUID
    
    try:
        # Run async matching in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(_async_compute_matches(UUID(challenge_id)))
            logger.info('Capability matches computed', challenge_id=challenge_id, match_count=len(result))
        finally:
            loop.close()
    except Exception as exc:
        logger.error('Match computation failed', challenge_id=challenge_id, error=str(exc))
        raise self.retry(exc=exc)


async def _async_compute_matches(challenge_id):
    """Async helper for computing matches."""
    from app.database import async_session_factory
    from app.ai.capability_matcher import capability_matcher
    
    async with async_session_factory() as session:
        matches = await capability_matcher.match_institutions(session, challenge_id)
        return matches


@celery_app.task
def recompute_cluster_centroids():
    """
    Periodic task to recompute cluster centroids based on member challenge embeddings.
    """
    from sqlalchemy import create_engine, select, func
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.challenge import Challenge, ChallengeCluster
    import numpy as np
    
    sync_url = str(settings.DATABASE_URL).replace('+asyncpg', '')
    engine = create_engine(sync_url)
    
    try:
        with Session(engine) as session:
            clusters = session.execute(select(ChallengeCluster)).scalars().all()
            updated = 0
            
            for cluster in clusters:
                # Get all challenge embeddings in this cluster
                challenges = session.execute(
                    select(Challenge.embedding).where(
                        Challenge.cluster_id == cluster.id,
                        Challenge.embedding.isnot(None)
                    )
                ).scalars().all()
                
                if challenges:
                    # Compute mean centroid
                    embeddings = [e for e in challenges if e is not None]
                    if embeddings:
                        centroid = np.mean(embeddings, axis=0).tolist()
                        cluster.centroid_embedding = centroid
                        cluster.challenge_count = len(embeddings)
                        updated += 1
            
            session.commit()
            logger.info('Cluster centroids recomputed', clusters_updated=updated)
    except Exception as exc:
        logger.error('Cluster centroid recomputation failed', error=str(exc))
    finally:
        engine.dispose()
