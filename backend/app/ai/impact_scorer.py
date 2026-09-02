import math
from typing import Tuple, Dict, Optional
from app.core.constants import ChallengeSeverity, ChallengeDomain

class ImpactScorer:
    SEVERITY_WEIGHT = 0.25
    PEOPLE_AFFECTED_WEIGHT = 0.20
    URGENCY_WEIGHT = 0.15
    EVIDENCE_QUALITY_WEIGHT = 0.15
    GEOGRAPHIC_SPREAD_WEIGHT = 0.10
    FEASIBILITY_WEIGHT = 0.10
    STRATEGIC_RELEVANCE_WEIGHT = 0.05

    def compute_impact_score(
        self,
        severity: ChallengeSeverity,
        affected_population: Optional[int],
        urgency_keywords_found: int,
        evidence_count: int,
        has_location: bool,
        has_media: bool,
        domain: ChallengeDomain,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Tuple[float, Dict[str, float]]:
        weights = custom_weights or {
            "severity": self.SEVERITY_WEIGHT,
            "people_affected": self.PEOPLE_AFFECTED_WEIGHT,
            "urgency": self.URGENCY_WEIGHT,
            "evidence_quality": self.EVIDENCE_QUALITY_WEIGHT,
            "geographic_spread": self.GEOGRAPHIC_SPREAD_WEIGHT,
            "feasibility": self.FEASIBILITY_WEIGHT,
            "strategic_relevance": self.STRATEGIC_RELEVANCE_WEIGHT
        }

        # Severity score
        severity_map = {
            ChallengeSeverity.CRITICAL: 1.0,
            ChallengeSeverity.HIGH: 0.75,
            ChallengeSeverity.MEDIUM: 0.5,
            ChallengeSeverity.LOW: 0.25
        }
        severity_score = severity_map.get(severity, 0.5)

        # People affected score
        if affected_population is None or affected_population <= 0:
            people_affected_score = 0.0
        else:
            people_affected_score = min(1.0, math.log10(affected_population + 1) / 5)

        # Urgency score
        urgency_score = min(1.0, urgency_keywords_found * 0.25)

        # Evidence quality score
        evidence_quality_score = 0.0
        if has_location:
            evidence_quality_score += 0.3
        if has_media:
            evidence_quality_score += 0.3
        evidence_quality_score += 0.4 * min(1.0, evidence_count / 3)

        # Geographic spread score
        geographic_spread_score = 0.5 if has_location else 0.0

        # Feasibility score
        feasibility_score = 0.5

        # Strategic relevance score
        high_priority = [ChallengeDomain.WATER, ChallengeDomain.HEALTHCARE, ChallengeDomain.EDUCATION]
        strategic_relevance_score = 0.8 if domain in high_priority else 0.4

        components = {
            "severity_score": severity_score,
            "people_affected_score": people_affected_score,
            "urgency_score": urgency_score,
            "evidence_quality_score": evidence_quality_score,
            "geographic_spread_score": geographic_spread_score,
            "feasibility_score": feasibility_score,
            "strategic_relevance_score": strategic_relevance_score
        }

        final_score = (
            severity_score * weights["severity"] +
            people_affected_score * weights["people_affected"] +
            urgency_score * weights["urgency"] +
            evidence_quality_score * weights["evidence_quality"] +
            geographic_spread_score * weights["geographic_spread"] +
            feasibility_score * weights["feasibility"] +
            strategic_relevance_score * weights["strategic_relevance"]
        )

        return float(final_score), components

    def compute_evidence_score(self, media_count: int, has_location: bool, narrative_length: int) -> float:
        score = 0.0
        if has_location:
            score += 0.3
        score += min(0.4, media_count * 0.2)
        score += min(0.3, narrative_length / 1000.0)
        return min(1.0, score)

impact_scorer = ImpactScorer()
