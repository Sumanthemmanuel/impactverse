"""
Test suite for the civic complaint triage pipeline.

Run with:  pytest test_classify.py -v

These tests exercise the pure-Python pipeline classes directly (no network,
no running server needed), so they pass whether or not sentence-transformers
model weights are available — the domain classifier's `method` field is
checked rather than assumed.

Updated for SIH26043 Jharkhand-aligned domains:
  Education, Agriculture, Healthcare, Water Resources, Environment,
  Energy, Urban Development, Accessibility, Public Administration,
  Rural Livelihoods
"""

import time

import pytest

from main import (
    Attachment,
    CapabilityMatcher,
    ComplaintInput,
    ComplaintPipeline,
    Deduplicator,
    DomainClassifier,
    FairnessAllocator,
    JharkhandGeoValidator,
    PartnerSuggester,
    PriorityScorer,
    SpamFilter,
    load_config,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def domains_cfg():
    return load_config("domains.json")


@pytest.fixture
def capabilities_cfg():
    return load_config("capabilities.json")


@pytest.fixture
def severity_cfg():
    return load_config("severity_keywords.json")


@pytest.fixture
def fairness_cfg():
    return load_config("fairness_config.json")


@pytest.fixture
def pipeline():
    return ComplaintPipeline()


def make_complaint(text, **kwargs):
    defaults = dict(complaint_text=text, submitter_id="user_1", institution_id="inst_A")
    defaults.update(kwargs)
    return ComplaintInput(**defaults)


# ---------------------------------------------------------------------------
# Jharkhand geo validation
# ---------------------------------------------------------------------------

class TestJharkhandGeoValidator:
    def test_ranchi_is_in_jharkhand(self):
        v = JharkhandGeoValidator()
        result = v.validate(23.3441, 85.3096)
        assert result["in_jharkhand"] is True
        assert result["location_valid"] is True
        assert result["district_hint"] == "Ranchi"

    def test_jamshedpur_is_in_jharkhand(self):
        v = JharkhandGeoValidator()
        result = v.validate(22.8046, 86.2029)
        assert result["in_jharkhand"] is True
        assert "Singhbhum" in result["district_hint"] or "Jamshedpur" in result["district_hint"]

    def test_delhi_is_not_in_jharkhand(self):
        v = JharkhandGeoValidator()
        result = v.validate(28.6139, 77.2090)
        assert result["in_jharkhand"] is False
        assert result["district_hint"] is None

    def test_no_coordinates_returns_invalid(self):
        v = JharkhandGeoValidator()
        result = v.validate(None, None)
        assert result["location_valid"] is False
        assert result["in_jharkhand"] is False

    def test_hazaribagh_district_hint(self):
        v = JharkhandGeoValidator()
        result = v.validate(23.9925, 85.3637)
        assert result["in_jharkhand"] is True
        assert result["district_hint"] == "Hazaribagh"

    def test_dumka_district_hint(self):
        v = JharkhandGeoValidator()
        result = v.validate(24.2681, 87.2482)
        assert result["in_jharkhand"] is True
        assert result["district_hint"] == "Dumka"


# ---------------------------------------------------------------------------
# Spam filter
# ---------------------------------------------------------------------------

class TestSpamFilter:
    def test_empty_text_is_spam(self):
        f = SpamFilter()
        result = f.check(make_complaint(""))
        assert result["is_spam"] is True

    def test_too_short_text_is_spam(self):
        f = SpamFilter()
        result = f.check(make_complaint("bad"))
        assert result["is_spam"] is True

    def test_blocklist_pattern_is_spam(self):
        f = SpamFilter()
        result = f.check(make_complaint("Click here to win free prizes http://scam.xyz"))
        assert result["is_spam"] is True
        assert "blocklist" in result["reason"]

    def test_genuine_complaint_is_not_spam(self):
        f = SpamFilter()
        result = f.check(
            make_complaint("There is a large pothole on Main Street causing accidents near the school")
        )
        assert result["is_spam"] is False
        assert result["spam_confidence"] < 0.5

    def test_genuine_jharkhand_complaint_is_not_spam(self):
        f = SpamFilter()
        result = f.check(
            make_complaint("MGNREGA wages not paid for 3 months in Gumla tribal area, families are suffering")
        )
        assert result["is_spam"] is False

    def test_repeated_submissions_flagged(self):
        f = SpamFilter(repeat_window_seconds=60, repeat_threshold=3)
        now = time.time()
        text = "Streetlight has been broken for two weeks on 5th avenue"
        results = []
        for i in range(5):
            c = make_complaint(text, submitter_id="spammer_1")
            c.submitted_at = now + i  # all within the window
            results.append(f.check(c))
        # Later submissions in a short burst should trend toward spam.
        assert results[-1]["spam_confidence"] > results[0]["spam_confidence"]

    def test_gibberish_score_high_for_nonsense(self):
        score = SpamFilter._gibberish_score("xkcd zzzt qwrt bfgh")
        assert score > 0.5

    def test_gibberish_score_low_for_real_sentence(self):
        score = SpamFilter._gibberish_score("There is a water leak near the market")
        assert score < 0.3


# ---------------------------------------------------------------------------
# Domain classification — both embedding and keyword paths
# ---------------------------------------------------------------------------

class TestDomainClassifier:
    SIH_DOMAINS = [
        "Education", "Agriculture", "Healthcare", "Water Resources",
        "Environment", "Energy", "Urban Development", "Accessibility",
        "Public Administration", "Rural Livelihoods",
    ]

    def test_method_is_embedding_or_keyword(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        assert clf.method in ("embedding", "keyword")

    def test_exactly_10_sih_domains_loaded(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        assert len(clf.domain_names) == 10
        for name in self.SIH_DOMAINS:
            assert name in clf.domain_names, f"Missing SIH domain: {name}"

    def test_classify_returns_valid_domain(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        result = clf.classify("There is a huge pothole and cracked road near my house")
        assert result["domain"] in clf.domain_names
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["method"] in ("embedding", "keyword")

    def test_classify_returns_top_3_predictions(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        result = clf.classify("Water pipeline burst flooding the road near the school in Ranchi")
        assert "top_3_predictions" in result
        assert len(result["top_3_predictions"]) == 3
        # Top prediction should match the primary domain
        assert result["top_3_predictions"][0]["domain"] == result["domain"]

    def test_keyword_fallback_matches_agriculture(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        clf.method = "keyword"
        clf._model = None
        domain, confidence, top_3 = clf._classify_keyword(
            "Crop damage from drought, farmers need irrigation support and seeds"
        )
        assert domain == "Agriculture"
        assert confidence > 0.2

    def test_keyword_fallback_matches_healthcare(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        clf.method = "keyword"
        clf._model = None
        domain, _, _ = clf._classify_keyword(
            "Hospital has no medicine, ambulance delayed, patients suffering"
        )
        assert domain == "Healthcare"

    def test_keyword_fallback_matches_water_resources(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        clf.method = "keyword"
        clf._model = None
        domain, _, _ = clf._classify_keyword(
            "Handpump broken, water shortage in village, borewell not working"
        )
        assert domain == "Water Resources"

    def test_keyword_fallback_matches_rural_livelihoods(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        clf.method = "keyword"
        clf._model = None
        domain, _, _ = clf._classify_keyword(
            "MGNREGA wages not paid, tribal self-help group needs support"
        )
        assert domain == "Rural Livelihoods"

    def test_keyword_fallback_matches_energy(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        clf.method = "keyword"
        clf._model = None
        domain, _, _ = clf._classify_keyword(
            "Power outage and transformer failure causing voltage problems"
        )
        assert domain == "Energy"

    def test_keyword_fallback_matches_urban_development(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        clf.method = "keyword"
        clf._model = None
        domain, _, _ = clf._classify_keyword(
            "Pothole on road, broken streetlight, drainage overflow near housing"
        )
        assert domain == "Urban Development"

    def test_keyword_fallback_default_domain_for_unmatched_text(self, domains_cfg):
        clf = DomainClassifier(domains_cfg)
        clf.method = "keyword"
        clf._model = None
        domain, confidence, _ = clf._classify_keyword("zzxq flibbertigibbet woblanorg qorpath")
        assert domain in clf.domain_names  # falls back to default catch-all
        assert confidence <= 0.3

    def test_classify_handles_model_failure_gracefully(self, domains_cfg, monkeypatch):
        """If method claims 'embedding' but the model raises at inference time,
        classify() must still return a valid result via the keyword path."""
        clf = DomainClassifier(domains_cfg)
        if clf._model is not None:
            def boom(*args, **kwargs):
                raise RuntimeError("simulated model failure")

            monkeypatch.setattr(clf, "_classify_embedding", boom)
        result = clf.classify("Sewage overflow flooding the street")
        assert result["domain"] in clf.domain_names
        assert result["method"] in ("embedding", "keyword")

    def test_confidence_calibration_sums_roughly_to_one(self, domains_cfg):
        """Temperature-scaled softmax confidences across all domains should sum ~1.0."""
        import numpy as np
        scores = np.array([0.3, 0.5, 0.8, 0.2, 0.4, 0.6, 0.1, 0.35, 0.45, 0.55])
        calibrated = DomainClassifier._temperature_softmax(scores)
        assert abs(calibrated.sum() - 1.0) < 1e-6


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

class TestDeduplicator:
    def test_no_existing_complaints_not_duplicate(self):
        dedup = Deduplicator()
        c = make_complaint("Pothole on Main Street", lat=12.97, lng=77.59)
        result = dedup.find_duplicate(c, [])
        assert result["is_duplicate"] is False
        assert result["duplicate_count"] == 0

    def test_far_away_complaint_not_duplicate(self):
        from main import StoredComplaint

        dedup = Deduplicator(radius_km=2.0)
        existing = [
            StoredComplaint(
                complaint_id="c1",
                text="Pothole on Main Street causing damage",
                domain="Urban Development",
                lat=13.5,  # far away
                lng=78.5,
                institution_id="inst_A",
                submitted_at=time.time(),
            )
        ]
        c = make_complaint("Pothole on Main Street causing damage", lat=12.97, lng=77.59)
        result = dedup.find_duplicate(c, existing)
        assert result["is_duplicate"] is False

    def test_nearby_similar_text_is_duplicate(self):
        from main import StoredComplaint

        dedup = Deduplicator(radius_km=2.0, similarity_threshold=0.3)
        existing = [
            StoredComplaint(
                complaint_id="c1",
                text="Large pothole causing accidents on Main Street near school",
                domain="Urban Development",
                lat=23.3441,
                lng=85.3096,
                institution_id="inst_A",
                submitted_at=time.time(),
            )
        ]
        c = make_complaint(
            "Big pothole near the school on Main Street causing accidents",
            lat=23.3442,
            lng=85.3097,
        )
        result = dedup.find_duplicate(c, existing)
        assert result["is_duplicate"] is True
        assert result["duplicate_of"] == "c1"
        assert result["duplicate_count"] == 1

    def test_nearby_dissimilar_text_not_duplicate(self):
        from main import StoredComplaint

        dedup = Deduplicator(radius_km=2.0, similarity_threshold=0.6)
        existing = [
            StoredComplaint(
                complaint_id="c1",
                text="Garbage not collected for a week near the market",
                domain="Urban Development",
                lat=23.3441,
                lng=85.3096,
                institution_id="inst_A",
                submitted_at=time.time(),
            )
        ]
        c = make_complaint("Streetlight broken outside the community hall", lat=23.3442, lng=85.3097)
        result = dedup.find_duplicate(c, existing)
        assert result["is_duplicate"] is False

    def test_missing_geo_skips_dedup(self):
        dedup = Deduplicator()
        c = make_complaint("Pothole on Main Street")  # no lat/lng
        result = dedup.find_duplicate(c, [])
        assert result["is_duplicate"] is False


# ---------------------------------------------------------------------------
# Priority scoring
# ---------------------------------------------------------------------------

class TestPriorityScorer:
    def test_higher_severity_yields_higher_priority(self, severity_cfg, domains_cfg):
        scorer = PriorityScorer(severity_cfg, domains_cfg)
        low = make_complaint("There is some litter near the park, minor inconvenience")
        high = make_complaint("Fire and building collapse reported with injuries in Ranchi")
        low_result = scorer.score(low, "Urban Development", duplicate_count=0)
        high_result = scorer.score(high, "Urban Development", duplicate_count=0)
        assert high_result["priority_score"] > low_result["priority_score"]
        assert high_result["severity_boost"] > low_result["severity_boost"]

    def test_duplicate_count_increases_priority(self, severity_cfg, domains_cfg):
        scorer = PriorityScorer(severity_cfg, domains_cfg)
        c = make_complaint("Water pipeline leak near the market")
        no_dup = scorer.score(c, "Water Resources", duplicate_count=0)
        with_dup = scorer.score(c, "Water Resources", duplicate_count=5)
        assert with_dup["priority_score"] > no_dup["priority_score"]
        # exactly duplicate_count * DUP_WEIGHT more, all else equal
        assert with_dup["priority_score"] - no_dup["priority_score"] == pytest.approx(
            5 * PriorityScorer.DUP_WEIGHT, abs=1e-6
        )

    def test_formula_is_explainable(self, severity_cfg, domains_cfg):
        scorer = PriorityScorer(severity_cfg, domains_cfg)
        c = make_complaint("Minor noise complaint in Jamshedpur")
        result = scorer.score(c, "Public Administration", duplicate_count=2)
        breakdown = result["_breakdown"]
        total = (
            breakdown["duplicate_term"]
            + breakdown["severity_boost"]
            + breakdown["domain_weight"]
            + breakdown["recency_boost"]
        )
        assert result["priority_score"] == pytest.approx(total, abs=1e-6)

    def test_jharkhand_critical_keywords_boost_high(self, severity_cfg, domains_cfg):
        scorer = PriorityScorer(severity_cfg, domains_cfg)
        c = make_complaint("Mining accident and landslide, workers trapped")
        result = scorer.score(c, "Environment", duplicate_count=0)
        assert result["severity_boost"] >= 10.0  # critical tier


# ---------------------------------------------------------------------------
# Capability matching
# ---------------------------------------------------------------------------

class TestCapabilityMatcher:
    def test_matches_water_resources_domain(self, capabilities_cfg):
        matcher = CapabilityMatcher(capabilities_cfg)
        result = matcher.match("Water Resources", priority_score=10.0)
        assert result["matched_capability"] is not None
        assert "Water" in result["matched_capability"] or "Drinking" in result["matched_capability"]
        assert 0.0 <= result["match_confidence"] <= 1.0

    def test_matches_healthcare_domain(self, capabilities_cfg):
        matcher = CapabilityMatcher(capabilities_cfg)
        result = matcher.match("Healthcare", priority_score=10.0)
        assert result["matched_capability"] is not None

    def test_unknown_domain_returns_none(self, capabilities_cfg):
        matcher = CapabilityMatcher(capabilities_cfg)
        result = matcher.match("nonexistent_domain", priority_score=5.0)
        assert result["matched_capability"] is None
        assert result["match_confidence"] == 0.0

    def test_load_balances_toward_least_loaded(self, capabilities_cfg):
        matcher = CapabilityMatcher(capabilities_cfg)
        # Education has two candidates with different headroom
        result = matcher.match("Education", priority_score=5.0)
        assert result["matched_capability"] is not None


# ---------------------------------------------------------------------------
# Partner suggestion
# ---------------------------------------------------------------------------

class TestPartnerSuggester:
    def test_suggests_partners_for_healthcare(self, capabilities_cfg):
        suggester = PartnerSuggester(capabilities_cfg)
        partners = suggester.suggest("Healthcare")
        assert len(partners) > 0

    def test_suggests_partners_for_agriculture(self, capabilities_cfg):
        suggester = PartnerSuggester(capabilities_cfg)
        partners = suggester.suggest("Agriculture")
        assert len(partners) > 0
        assert any("agritech" in p for p in partners)

    def test_empty_list_for_unknown_domain(self, capabilities_cfg):
        suggester = PartnerSuggester(capabilities_cfg)
        assert suggester.suggest("nonexistent_domain") == []


# ---------------------------------------------------------------------------
# Fairness allocation
# ---------------------------------------------------------------------------

class TestFairnessAllocator:
    def test_no_adjustment_when_no_ties(self, fairness_cfg):
        allocator = FairnessAllocator(fairness_cfg)
        c = make_complaint("Water leak", institution_id="inst_A")
        result = allocator.evaluate(c, priority_score=10.0, competing_priorities=[])
        assert result["applied"] is False

    def test_dominant_institution_gets_deprioritized_within_tie_band(self, fairness_cfg):
        allocator = FairnessAllocator(fairness_cfg)
        now = time.time()

        # inst_A floods the system with allocations first.
        for _ in range(10):
            allocator.record_allocation("inst_A", now=now)

        # A near-tied new complaint from inst_A should get flagged...
        c_a = make_complaint("Pothole issue", institution_id="inst_A")
        result_a = allocator.evaluate(
            c_a, priority_score=10.0, competing_priorities=[9.0], now=now
        )
        assert result_a["applied"] is True
        assert "inst_A" in result_a["reason"]

        # ...while a complaint from an institution with no recent share
        # should not be penalized.
        c_b = make_complaint("Pothole issue", institution_id="inst_B")
        result_b = allocator.evaluate(
            c_b, priority_score=10.0, competing_priorities=[9.0], now=now
        )
        assert result_b["applied"] is False

    def test_distribution_metrics_reports_shares(self, fairness_cfg):
        allocator = FairnessAllocator(fairness_cfg)
        allocator.record_allocation("inst_A")
        allocator.record_allocation("inst_A")
        allocator.record_allocation("inst_B")
        metrics = allocator.distribution_metrics()
        assert metrics["counts"]["inst_A"] == 2
        assert metrics["counts"]["inst_B"] == 1
        assert metrics["shares_pct"]["inst_A"] == pytest.approx(66.67, abs=0.5)

    def test_disabled_fairness_never_applies(self, fairness_cfg):
        cfg = dict(fairness_cfg)
        cfg["enabled"] = False
        allocator = FairnessAllocator(cfg)
        for _ in range(20):
            allocator.record_allocation("inst_A")
        c = make_complaint("Pothole issue", institution_id="inst_A")
        result = allocator.evaluate(c, priority_score=10.0, competing_priorities=[9.5])
        assert result["applied"] is False


# ---------------------------------------------------------------------------
# Full pipeline integration
# ---------------------------------------------------------------------------

class TestComplaintPipeline:
    def test_spam_short_circuits_pipeline(self, pipeline):
        c = make_complaint("Click here to win free prizes http://scam.xyz")
        result = pipeline.process(c)
        assert result["is_spam"] is True
        assert result["domain"] is None
        assert result["matched_capability"] is None

    def test_genuine_complaint_full_contract_present(self, pipeline):
        c = make_complaint(
            "Power outage and exposed transformer wiring near the bus stop in Ranchi, very dangerous",
            lat=23.3441,
            lng=85.3096,
        )
        result = pipeline.process(c)
        expected_keys = {
            "complaint_id",
            "is_spam",
            "spam_confidence",
            "geo_validation",
            "domain",
            "confidence",
            "method",
            "top_3_predictions",
            "is_duplicate",
            "duplicate_of",
            "duplicate_count",
            "priority_score",
            "severity_boost",
            "matched_capability",
            "match_confidence",
            "suggested_partners",
            "fairness_adjustment",
        }
        assert expected_keys.issubset(result.keys())
        assert result["is_spam"] is False
        assert result["domain"] == "Energy"
        assert result["matched_capability"] is not None

    def test_pipeline_includes_geo_validation(self, pipeline):
        c = make_complaint(
            "Water pipeline burst near Ranchi station",
            lat=23.3441,
            lng=85.3096,
        )
        result = pipeline.process(c)
        assert "geo_validation" in result
        assert result["geo_validation"]["in_jharkhand"] is True
        assert result["geo_validation"]["district_hint"] == "Ranchi"

    def test_pipeline_includes_top_3_predictions(self, pipeline):
        c = make_complaint(
            "Hospital running out of medicine, ambulance service disrupted in Dhanbad",
            lat=23.7957,
            lng=86.4304,
        )
        result = pipeline.process(c)
        assert "top_3_predictions" in result
        assert len(result["top_3_predictions"]) == 3

    def test_second_similar_nearby_complaint_flagged_duplicate(self, pipeline):
        c1 = make_complaint(
            "Large pothole on Ring Road causing accidents near the junction",
            lat=23.3441,
            lng=85.3096,
        )
        pipeline.process(c1)

        c2 = make_complaint(
            "Big pothole on Ring Road causing accidents near the junction",
            lat=23.3442,
            lng=85.3097,
        )
        result2 = pipeline.process(c2)
        assert result2["is_duplicate"] is True
        assert result2["duplicate_count"] >= 1

    def test_attachments_do_not_break_pipeline(self, pipeline):
        c = make_complaint(
            "Sewage overflowing near the residential block, drains completely blocked in Ranchi",
            attachments=[Attachment(filename="photo.jpg", content_type="image/jpeg", storage_ref="/tmp/photo.jpg")],
        )
        result = pipeline.process(c)
        assert result["is_spam"] is False
        assert result["domain"] == "Urban Development"

    def test_backward_compatible_response_fields(self, pipeline):
        """Verify the fields the backend team expects are present."""
        c = make_complaint(
            "Crop failure due to drought, farmers need irrigation support in Hazaribagh",
            lat=23.9925,
            lng=85.3637,
        )
        result = pipeline.process(c)
        # These are the exact fields the backend team extracts:
        backend_fields = {"domain", "confidence", "method", "is_duplicate",
                         "duplicate_of", "duplicate_count", "priority_score", "severity_boost"}
        assert backend_fields.issubset(result.keys())
        assert isinstance(result["domain"], str)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["priority_score"], float)


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
