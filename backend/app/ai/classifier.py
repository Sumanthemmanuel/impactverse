import re
from typing import Tuple, List, Optional
from app.models import ChallengeDomain, ChallengeSeverity
from app.ai.embeddings import embedding_service

class ChallengeClassifier:
    DOMAIN_KEYWORDS = {
        ChallengeDomain.WATER: ['water', 'drinking water', 'groundwater', 'well', 'borewell', 'water supply', 'water contamination', 'water scarcity', 'pipeline', 'waterlogging', 'flood'],
        ChallengeDomain.SANITATION: ['sanitation', 'toilet', 'sewage', 'drainage', 'waste', 'garbage', 'open defecation', 'hygiene'],
        ChallengeDomain.HEALTHCARE: ['health', 'hospital', 'doctor', 'medicine', 'disease', 'clinic', 'medical', 'ambulance', 'vaccination'],
        ChallengeDomain.EDUCATION: ['school', 'education', 'teacher', 'college', 'student', 'classroom', 'literacy', 'learning'],
        ChallengeDomain.INFRASTRUCTURE: ['road', 'bridge', 'building', 'construction', 'electricity', 'power', 'streetlight'],
        ChallengeDomain.AGRICULTURE: ['farming', 'crop', 'irrigation', 'fertilizer', 'agriculture', 'harvest', 'soil'],
        ChallengeDomain.ENVIRONMENT: ['pollution', 'deforestation', 'climate', 'wildlife', 'air quality', 'carbon'],
        ChallengeDomain.ENERGY: ['solar', 'energy', 'renewable', 'gas', 'fuel', 'electricity supply'],
        ChallengeDomain.TRANSPORT: ['transport', 'bus', 'railway', 'road connectivity', 'traffic'],
        ChallengeDomain.DIGITAL_SERVICES: ['internet', 'digital', 'mobile', 'connectivity', 'IT', 'online'],
        ChallengeDomain.PUBLIC_SAFETY: ['crime', 'safety', 'police', 'fire', 'disaster', 'accident'],
        ChallengeDomain.GOVERNANCE: ['governance', 'corruption', 'transparency', 'policy', 'administration'],
        ChallengeDomain.OTHER: []
    }

    def classify_domain(self, text: str) -> Tuple[ChallengeDomain, float]:
        text_lower = text.lower()
        best_domain = ChallengeDomain.OTHER
        max_score = 0.0

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > max_score:
                max_score = score
                best_domain = domain

        if max_score > 0:
            confidence = min(max_score * 0.2, 0.9)
            return best_domain, confidence

        # Fallback to embeddings
        text_emb = embedding_service.get_embedding(text)
        best_sim = 0.0
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if not keywords:
                continue
            desc = f"Challenges related to {domain.name.lower()} such as " + ", ".join(keywords[:5])
            desc_emb = embedding_service.get_embedding(desc)
            sim = embedding_service.compute_similarity(text_emb, desc_emb)
            if sim > best_sim:
                best_sim = sim
                best_domain = domain

        return best_domain, float(best_sim)

    def estimate_severity(self, text: str, affected_population: Optional[int] = None) -> ChallengeSeverity:
        text_lower = text.lower()
        if affected_population is not None and affected_population > 10000:
            return ChallengeSeverity.CRITICAL
        if any(kw in text_lower for kw in ['death', 'emergency', 'life-threatening', 'epidemic', 'flood', 'collapse']):
            return ChallengeSeverity.CRITICAL

        if affected_population is not None and affected_population > 1000:
            return ChallengeSeverity.HIGH
        if any(kw in text_lower for kw in ['urgent', 'danger', 'serious', 'contaminated', 'broken']):
            return ChallengeSeverity.HIGH

        if any(kw in text_lower for kw in ['minor', 'cosmetic', 'suggestion', 'improvement']):
            return ChallengeSeverity.LOW

        return ChallengeSeverity.MEDIUM

    def extract_tags(self, text: str) -> List[str]:
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        return list(set(words))

    def generate_summary(self, text: str, max_length: int = 200) -> str:
        sentences = re.split(r'(?<=[.!?]) +', text)
        summary = " ".join(sentences[:3])
        if len(summary) > max_length:
            return summary[:max_length-3] + "..."
        return summary

classifier = ChallengeClassifier()
