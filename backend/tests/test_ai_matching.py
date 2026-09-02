"""Focused tests for the model-backed challenge enrichment and assignment path.

These tests deliberately do not require a running Postgres, Redis, or model
download.  They exercise the same deterministic fallback used by the API when
the transformer model is not yet cached, which makes local and CI verification
reliable.
"""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.ai.capability_matcher import CapabilityMatcher
from app.ai.classifier import ChallengeClassifier
from app.ai.embeddings import EmbeddingService
from app.core.constants import ChallengeDomain


class _Result:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value

    def scalars(self):
        return self

    def all(self):
        return self.value


class _Session:
    """Minimal async-session stand-in for the two reads used by matching."""

    def __init__(self, *results):
        self._results = list(results)

    async def execute(self, _statement):
        return _Result(self._results.pop(0))


def _fallback_service() -> EmbeddingService:
    service = EmbeddingService()
    service._model = "fallback"
    service._using_fallback = True
    return service


def test_offline_embeddings_are_normalized_and_rank_related_text_higher():
    service = _fallback_service()
    challenge = service.get_embedding("unsafe drinking water pipeline contamination")
    related = service.get_embedding("water pipeline treatment and contamination")
    unrelated = service.get_embedding("solar energy battery installation")

    assert len(challenge) == EmbeddingService.DIMENSIONS
    assert service.compute_similarity(challenge, related) > service.compute_similarity(challenge, unrelated)
    assert service.compute_similarity(challenge, related) > 0.25


def test_classifier_assigns_a_clear_domain_with_explainable_confidence():
    classifier = ChallengeClassifier()

    domain, confidence = classifier.classify_domain(
        "The village drinking water pipeline is contaminated and families are ill."
    )

    assert domain is ChallengeDomain.WATER
    assert confidence >= 0.2


@pytest.mark.asyncio
async def test_assignment_model_ranks_the_best_equipped_institution_first(monkeypatch):
    fallback = _fallback_service()
    monkeypatch.setattr("app.ai.capability_matcher.embedding_service", fallback)

    challenge_text = "Drinking water contamination needs pipeline treatment in the village"
    challenge = SimpleNamespace(
        id=uuid4(),
        title="Contaminated water supply",
        narrative=challenge_text,
        embedding=fallback.get_embedding(challenge_text),
        domain=ChallengeDomain.WATER,
        location=None,
    )

    water_faculty = SimpleNamespace(
        id=uuid4(),
        expertise_tags=["water treatment", "groundwater quality"],
        expertise_embedding=None,
        past_projects_count=5,
        availability_status=True,
        user=SimpleNamespace(full_name="Dr. Water"),
    )
    water_department = SimpleNamespace(
        name="Water Resources Engineering",
        research_areas=["water supply", "water treatment", "pipeline rehabilitation"],
        capability_embedding=None,
        faculty=[water_faculty],
        labs=[SimpleNamespace(is_available=True, specialization="water treatment", name="Hydrology Lab")],
    )
    water_institution = SimpleNamespace(
        id=uuid4(),
        name="Water Technology Institute",
        departments=[water_department],
        incubation_facilities=True,
        location=None,
    )

    energy_department = SimpleNamespace(
        name="Renewable Energy Engineering",
        research_areas=["solar panels", "battery storage"],
        capability_embedding=None,
        faculty=[],
        labs=[SimpleNamespace(is_available=True, specialization="solar energy", name="Solar Lab")],
    )
    energy_institution = SimpleNamespace(
        id=uuid4(),
        name="Energy Innovation Institute",
        departments=[energy_department],
        incubation_facilities=False,
        location=None,
    )

    matches = await CapabilityMatcher().match_institutions(
        _Session(challenge, [energy_institution, water_institution]), challenge.id
    )

    assert [match["institution_name"] for match in matches] == [
        "Water Technology Institute",
        "Energy Innovation Institute",
    ]
    assert matches[0]["research_fit"] > matches[1]["research_fit"]
    assert "Water Resources Engineering" in matches[0]["matching_departments"]
    assert "Dr. Water" in matches[0]["matching_faculty"]
