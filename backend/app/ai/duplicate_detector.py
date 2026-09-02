import math
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from app.models import Challenge, ChallengeCluster
from app.ai.embeddings import embedding_service

class DuplicateDetector:
    async def find_duplicates(
        self,
        db: AsyncSession,
        challenge_text: str,
        challenge_embedding: List[float],
        location_lat: Optional[float],
        location_lng: Optional[float],
        threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        # Using raw SQL with pgvector distance operator <=>
        query_str = """
            SELECT id, title, (1 - (embedding <=> :embedding)) AS similarity_score
            FROM challenges
            WHERE (1 - (embedding <=> :embedding)) > :threshold
        """
        
        params = {
            "embedding": str(challenge_embedding),
            "threshold": threshold
        }
        
        result = await db.execute(text(query_str), params)
        duplicates = []
        
        for row in result:
            similarity = float(row.similarity_score)
            challenge_id = row.id
            title = row.title
            
            # Simple Haversine for distance if both lat/lng provided
            distance_km = None
            if location_lat is not None and location_lng is not None:
                # In real app we would get the location from the challenge, 
                # for now assuming we check distance at application level or augment query.
                distance_km = 0.0 # Placeholder: implement actual distance check

            duplicates.append({
                "challenge_id": challenge_id,
                "title": title,
                "similarity_score": similarity,
                "distance_km": distance_km
            })
            
        return duplicates

    async def find_cluster(
        self,
        db: AsyncSession,
        challenge_embedding: List[float],
        domain: str,
        district: Optional[str]
    ) -> Optional[UUID]:
        query_str = """
            SELECT id, (1 - (centroid_embedding <=> :embedding)) AS similarity_score
            FROM challenge_clusters
            WHERE domain = :domain
              AND (1 - (centroid_embedding <=> :embedding)) > 0.80
        """
        params = {
            "embedding": str(challenge_embedding),
            "domain": domain
        }
        result = await db.execute(text(query_str), params)
        row = result.first()
        if row:
            return row.id
        return None

    async def assign_to_cluster(
        self,
        db: AsyncSession,
        challenge_id: UUID,
        cluster_id: Optional[UUID],
        challenge_embedding: List[float],
        domain: str,
        district: Optional[str]
    ) -> UUID:
        if cluster_id:
            # Update existing cluster
            cluster_stmt = select(ChallengeCluster).where(ChallengeCluster.id == cluster_id)
            result = await db.execute(cluster_stmt)
            cluster = result.scalar_one_or_none()
            if cluster:
                # Naive average for centroid
                old_count = cluster.challenge_count
                new_count = old_count + 1
                new_centroid = [
                    (c * old_count + e) / new_count
                    for c, e in zip(cluster.centroid_embedding, challenge_embedding)
                ]
                cluster.centroid_embedding = new_centroid
                cluster.challenge_count = new_count
                
                # Assign challenge
                challenge_stmt = select(Challenge).where(Challenge.id == challenge_id)
                ch_result = await db.execute(challenge_stmt)
                challenge = ch_result.scalar_one_or_none()
                if challenge:
                    challenge.cluster_id = cluster.id
                    
                await db.commit()
                return cluster.id

        # Create new cluster
        new_cluster = ChallengeCluster(
            domain=domain,
            district=district,
            centroid_embedding=challenge_embedding,
            challenge_count=1
        )
        db.add(new_cluster)
        await db.commit()
        await db.refresh(new_cluster)
        
        # Assign challenge
        challenge_stmt = select(Challenge).where(Challenge.id == challenge_id)
        ch_result = await db.execute(challenge_stmt)
        challenge = ch_result.scalar_one_or_none()
        if challenge:
            challenge.cluster_id = new_cluster.id
            await db.commit()
            
        return new_cluster.id

duplicate_detector = DuplicateDetector()
