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
            
            import httpx
            from app.core.constants import ChallengeDomain, ChallengeSeverity
            from app.utils.geo import extract_lat_lng
            
            text = f"{challenge.title} {challenge.narrative}"

            # Extract lat/lng from the challenge's PostGIS geometry so the
            # classifier can run geo-validation, nearest-district hint, and
            # spatial deduplication.
            coords = extract_lat_lng(challenge.location) if challenge.location else None
            lat = coords[0] if coords else None
            lng = coords[1] if coords else None

            # Fallback: check the most-recently-uploaded image's EXIF GPS if
            # the challenge location geometry is not set yet.
            if lat is None:
                from sqlalchemy import select, desc
                from app.models.challenge import ChallengeMedia
                media_stmt = (
                    select(ChallengeMedia)
                    .where(ChallengeMedia.challenge_id == challenge.id)
                    .order_by(desc(ChallengeMedia.created_at))
                    .limit(1)
                )
                latest_media = session.execute(media_stmt).scalar_one_or_none()
                if latest_media and latest_media.metadata_json:
                    lat = latest_media.metadata_json.get("gps_latitude")
                    lng = latest_media.metadata_json.get("gps_longitude")
            
            try:
                with httpx.Client(timeout=15.0) as client:
                    response = client.post(
                        settings.CLASSIFIER_API_URL,
                        json={"text": text, "lat": lat, "lng": lng}
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Map domain string back to Enum if possible
                    # e.g., "Water Resources" -> ChallengeDomain.WATER_RESOURCES
                    domain_str = data.get("domain")
                    if domain_str:
                        # Find matching enum value
                        for d in ChallengeDomain:
                            if d.value.lower() == domain_str.lower():
                                challenge.ai_domain = d.value
                                challenge.domain = d
                                break
                    
                    challenge.ai_confidence = data.get("confidence")
                    
                    # Update impact score based on priority_score from microservice
                    if data.get("priority_score") is not None:
                        challenge.impact_score = float(data.get("priority_score"))
                    
                    # Map severity_boost to ChallengeSeverity
                    boost = data.get("severity_boost", 0.0)
                    if boost >= 10.0:
                        challenge.severity = ChallengeSeverity.CRITICAL
                    elif boost >= 6.0:
                        challenge.severity = ChallengeSeverity.HIGH
                    elif boost >= 3.0:
                        challenge.severity = ChallengeSeverity.MEDIUM
                    else:
                        challenge.severity = ChallengeSeverity.LOW

                    # Store district hint from geo-validation if challenge lacks one
                    geo_val = data.get("geo_validation") or {}
                    district_hint = geo_val.get("district_hint")
                    if district_hint and not challenge.district:
                        challenge.district = district_hint

                    # Basic tagging for the DB
                    if data.get("top_3_predictions"):
                        challenge.ai_tags = [p["domain"] for p in data["top_3_predictions"]]
                    
            except Exception as e:
                logger.error("Failed to call classifier microservice", error=str(e))
                # Fallback handled by Celery retry
                raise e
            
            session.commit()
            logger.info('Challenge enriched successfully via microservice', challenge_id=challenge_id, impact_score=challenge.impact_score)
            
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
    from app.database import async_session_maker
    from app.ai.capability_matcher import capability_matcher
    
    async with async_session_maker() as session:
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
