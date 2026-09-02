import math
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Challenge, Institution, Department, FacultyProfile, Lab
from app.ai.embeddings import embedding_service

class CapabilityMatcher:
    RESEARCH_FIT_WEIGHT = 0.30
    FACULTY_EXPERTISE_WEIGHT = 0.20
    LAB_FIT_WEIGHT = 0.15
    PAST_PROJECTS_WEIGHT = 0.10
    TEAM_CAPACITY_WEIGHT = 0.10
    GEOGRAPHIC_PROXIMITY_WEIGHT = 0.05
    INCUBATION_READINESS_WEIGHT = 0.10
    FACULTY_MATCH_THRESHOLD = 0.15

    async def match_institutions(self, db: AsyncSession, challenge_id: UUID) -> List[Dict[str, Any]]:
        # Load Challenge
        challenge_stmt = select(Challenge).where(Challenge.id == challenge_id)
        result = await db.execute(challenge_stmt)
        challenge = result.scalar_one_or_none()
        
        if not challenge:
            return []

        challenge_embedding = challenge.embedding or embedding_service.get_embedding(
            f"{challenge.title} {challenge.narrative}"
        )

        # Load Institutions
        inst_stmt = select(Institution).where(Institution.is_verified.is_(True)).options(
            selectinload(Institution.departments).selectinload(Department.faculty).selectinload(FacultyProfile.user),
            selectinload(Institution.departments).selectinload(Department.labs),
        )
        result = await db.execute(inst_stmt)
        institutions = result.scalars().all()

        matches = []
        for inst in institutions:
            departments = list(inst.departments or [])
            faculty = [member for department in departments for member in (department.faculty or [])]
            labs = [lab for department in departments for lab in (department.labs or []) if lab.is_available]

            research_fit, matching_deps = self._compute_research_fit(challenge_embedding, departments)
            faculty_fit, matching_fac = self._compute_faculty_fit(challenge_embedding, faculty)
            domain_name = self._domain_name(challenge.domain)
            lab_fit = self._compute_lab_fit(domain_name, labs)
            
            # Faculty past projects
            past_projects_count = sum(f.past_projects_count or 0 for f in faculty)
            past_projects_score = min(1.0, past_projects_count / 10.0)
            
            # Team capacity
            available_faculty = sum(1 for f in faculty if f.availability_status)
            team_capacity_score = min(1.0, available_faculty / 5.0)
            
            # Geo proximity
            geo_score = self._compute_geographic_score(
                self._coordinates(challenge),
                self._coordinates(inst),
            )
            
            # Incubation
            incubation_score = 1.0 if inst.incubation_facilities else 0.3
            
            overall_score = (
                research_fit * self.RESEARCH_FIT_WEIGHT +
                faculty_fit * self.FACULTY_EXPERTISE_WEIGHT +
                lab_fit * self.LAB_FIT_WEIGHT +
                past_projects_score * self.PAST_PROJECTS_WEIGHT +
                team_capacity_score * self.TEAM_CAPACITY_WEIGHT +
                geo_score * self.GEOGRAPHIC_PROXIMITY_WEIGHT +
                incubation_score * self.INCUBATION_READINESS_WEIGHT
            )
            
            capacity_str = "available" if available_faculty > 0 else "limited"
            explanation = (
                f"{int(overall_score * 100)}% fit — "
                f"{matching_deps[0] if matching_deps else 'Institution'}, "
                f"{len(labs)} labs, {len(matching_fac)} faculty experts, "
                f"{past_projects_count} prior projects, {capacity_str} capacity"
            )

            matches.append({
                "institution_id": inst.id,
                "institution_name": inst.name,
                "overall_score": overall_score,
                "research_fit": research_fit,
                "faculty_fit": faculty_fit,
                "lab_fit": lab_fit,
                "past_projects_score": past_projects_score,
                "team_capacity_score": team_capacity_score,
                "geographic_proximity_score": geo_score,
                "incubation_readiness_score": incubation_score,
                "explanation": explanation,
                "matching_departments": matching_deps,
                "matching_faculty": matching_fac
            })

        matches.sort(key=lambda x: x["overall_score"], reverse=True)
        return matches[:10]

    @staticmethod
    def _domain_name(domain: Any) -> str:
        return (getattr(domain, "value", domain) or "").lower()

    @staticmethod
    def _coordinates(entity: Any) -> Tuple[Optional[float], Optional[float]]:
        """Read coordinates when available, otherwise leave geo scoring neutral."""
        if hasattr(entity, "location_lat") and hasattr(entity, "location_lng"):
            return entity.location_lat, entity.location_lng
        location = getattr(entity, "location", None)
        if location is None:
            return None, None
        try:
            from geoalchemy2.shape import to_shape

            point = to_shape(location)
            return point.y, point.x
        except Exception:
            return None, None

    def _compute_research_fit(self, challenge_embedding: List[float], departments: List[Department]) -> Tuple[float, List[str]]:
        best_score = 0.0
        matching = []
        for dep in departments:
            profile = " ".join([dep.name, *(dep.research_areas or [])])
            embedding = dep.capability_embedding or embedding_service.get_embedding(profile)
            score = max(0.0, embedding_service.compute_similarity(challenge_embedding, embedding))
            if score > best_score:
                best_score = score
                matching = [dep.name]
            elif score == best_score and score > 0:
                matching.append(dep.name)
        return best_score, matching

    def _compute_faculty_fit(self, challenge_embedding: List[float], faculty_profiles: List[FacultyProfile]) -> Tuple[float, List[str]]:
        best_score = 0.0
        matching = []
        for fac in faculty_profiles:
            profile = " ".join(fac.expertise_tags or [])
            embedding = fac.expertise_embedding or embedding_service.get_embedding(profile)
            score = max(0.0, embedding_service.compute_similarity(challenge_embedding, embedding))
            faculty_name = getattr(getattr(fac, "user", None), "full_name", None) or str(fac.id)
            if score >= self.FACULTY_MATCH_THRESHOLD:
                matching.append(faculty_name)
            if score > best_score:
                best_score = score
        return best_score, matching

    def _compute_lab_fit(self, challenge_domain: str, labs: List[Lab]) -> float:
        if not labs or not challenge_domain:
            return 0.0
        score = 0.0
        for lab in labs:
            if challenge_domain.lower() in (lab.specialization or "").lower():
                score = max(score, 1.0)
        return score

    def _compute_geographic_score(self, challenge_loc: Tuple[Optional[float], Optional[float]], inst_loc: Tuple[Optional[float], Optional[float]]) -> float:
        c_lat, c_lng = challenge_loc
        i_lat, i_lng = inst_loc
        if None in (c_lat, c_lng, i_lat, i_lng):
            return 0.5
        
        # Haversine
        R = 6371.0
        lat1, lon1 = math.radians(c_lat), math.radians(c_lng)
        lat2, lon2 = math.radians(i_lat), math.radians(i_lng)
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return max(0.0, 1.0 - distance / 500.0)

capability_matcher = CapabilityMatcher()
