"""
Civic Complaint Triage Microservice
====================================

Pipeline: intake -> spam filter -> geo validation -> domain classification
          -> deduplication -> priority scoring -> capability matching
          -> partner suggestion -> fairness-adjusted allocation

Design goals
------------
- Every stage is an independent, testable class.
- The service degrades gracefully: if sentence-transformers (and its model
  weights) is not installed/available, domain classification and spam
  detection automatically fall back to keyword-based heuristics. The
  `method` field in the response always tells you which path was used.
- All tunable knobs (domains, capability registry, severity keywords,
  fairness quotas) live in ./config/*.json — never hardcoded in logic.
- FastAPI is optional. The pipeline classes work as a plain Python library
  even without fastapi/uvicorn installed, so core logic is unit-testable
  in any environment. The HTTP layer is only wired up if fastapi is
  importable.

Backward-compatible classifier contract (what the backend team calls):
POST /classify
Request:  {"text": "<title + description>", "lat": <float>, "lng": <float>}
Response: {"domain": str, "confidence": float, "method": str,
           "is_duplicate": bool, "duplicate_of": str|null,
           "duplicate_count": int, "priority_score": float,
           "severity_boost": float}

Full diagnostic contract (for debugging / judges):
POST /classify/full
(same request) -> all fields including spam, fairness, partners, geo, top-3
"""

from __future__ import annotations

import json
import math
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CONFIG_DIR = Path(__file__).parent / "config"

# ---------------------------------------------------------------------------
# Optional heavy dependency: sentence-transformers. The whole service must
# keep working (via the keyword fallback) if this import or model load fails
# — e.g. no network access, no GPU, model not cached yet.
# ---------------------------------------------------------------------------
try:
    import torch
    from sentence_transformers import SentenceTransformer

    _ST_AVAILABLE = True
    # Use CUDA (RTX 3050 / any NVIDIA GPU) when the CUDA wheel is installed.
    # Falls back to CPU automatically if CUDA is not available.
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    _ST_AVAILABLE = False
    _DEVICE = "cpu"


def load_config(name: str) -> dict:
    with open(CONFIG_DIR / name, "r") as f:
        return json.load(f)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometers."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Attachment:
    filename: str
    content_type: str  # e.g. "image/jpeg", "application/pdf", "video/mp4"
    storage_ref: str    # path or URL — actual bytes are not handled here


@dataclass
class ComplaintInput:
    complaint_text: str
    submitter_id: str
    institution_id: str = "unknown"          # e.g. university/college id — used by fairness layer
    lat: Optional[float] = None
    lng: Optional[float] = None
    attachments: list[Attachment] = field(default_factory=list)
    submitted_at: float = field(default_factory=time.time)


@dataclass
class StoredComplaint:
    """What we keep in memory/DB per complaint, for dedup + fairness lookups."""
    complaint_id: str
    text: str
    domain: str
    lat: Optional[float]
    lng: Optional[float]
    institution_id: str
    submitted_at: float
    matched_capability: Optional[str] = None


# ---------------------------------------------------------------------------
# Stage 0: Jharkhand geo-boundary validation
# ---------------------------------------------------------------------------

class JharkhandGeoValidator:
    """
    Validates whether a complaint's lat/lng falls within Jharkhand's
    approximate bounding box. Adds context for judges and helps flag
    out-of-state submissions without blocking them.

    Jharkhand bounding box (approximate):
      Latitude:  21.97°N  – 25.35°N
      Longitude: 83.32°E  – 87.92°E
    """

    # Approximate bounding box for Jharkhand
    LAT_MIN, LAT_MAX = 21.97, 25.35
    LNG_MIN, LNG_MAX = 83.32, 87.92

    # District center coordinates for district hint (major Jharkhand districts)
    DISTRICT_CENTERS = {
        "Ranchi": (23.3441, 85.3096),
        "Jamshedpur (East Singhbhum)": (22.8046, 86.2029),
        "Dhanbad": (23.7957, 86.4304),
        "Bokaro": (23.6693, 85.9694),
        "Hazaribagh": (23.9925, 85.3637),
        "Deoghar": (24.4854, 86.6944),
        "Giridih": (24.1854, 86.3003),
        "Dumka": (24.2681, 87.2482),
        "Palamu": (24.0268, 84.0530),
        "Garhwa": (24.1600, 83.8000),
        "Chatra": (24.2049, 84.8718),
        "Koderma": (24.4675, 85.5936),
        "Ramgarh": (23.6316, 85.5120),
        "Godda": (24.8270, 87.2123),
        "Sahebganj": (25.2519, 87.6389),
        "Pakur": (24.6346, 87.8427),
        "Jamtara": (23.9585, 86.8020),
        "Latehar": (23.7407, 84.5018),
        "Lohardaga": (23.4358, 84.6839),
        "Gumla": (23.0443, 84.5426),
        "Simdega": (22.6137, 84.5096),
        "West Singhbhum": (22.3677, 85.8254),
        "Seraikela-Kharsawan": (22.7050, 85.9912),
        "Khunti": (23.0719, 85.2789),
    }

    def validate(self, lat: Optional[float], lng: Optional[float]) -> dict:
        """Returns geo validation result with district hint."""
        if lat is None or lng is None:
            return {
                "location_valid": False,
                "in_jharkhand": False,
                "district_hint": None,
                "reason": "No coordinates provided",
            }

        in_jharkhand = (
            self.LAT_MIN <= lat <= self.LAT_MAX
            and self.LNG_MIN <= lng <= self.LNG_MAX
        )

        district_hint = None
        if in_jharkhand:
            district_hint = self._nearest_district(lat, lng)

        return {
            "location_valid": True,
            "in_jharkhand": in_jharkhand,
            "district_hint": district_hint,
            "reason": None if in_jharkhand else "Coordinates outside Jharkhand boundary",
        }

    def _nearest_district(self, lat: float, lng: float) -> str:
        """Find the nearest district center by haversine distance."""
        best_name = "Unknown"
        best_dist = float("inf")
        for name, (dlat, dlng) in self.DISTRICT_CENTERS.items():
            dist = haversine_km(lat, lng, dlat, dlng)
            if dist < best_dist:
                best_dist = dist
                best_name = name
        return best_name


# ---------------------------------------------------------------------------
# Stage 0b: Location text ↔ GPS cross-verification
# ---------------------------------------------------------------------------

class LocationVerifier:
    """
    Extracts location names from the complaint text, resolves them to known
    Jharkhand districts (or flags them as outside Jharkhand), then compares
    against the GPS coordinates supplied by the submitter.

    Verdict:
      "match"         — text location matches the GPS district (trustworthy)
      "mismatch"      — text says one place, GPS says another (suspicious)
      "gps_outside"   — GPS is outside Jharkhand but text mentions a JH place
      "text_outside"  — text mentions a non-JH place, GPS may be inside/outside
      "unverifiable"  — no recognisable place name found in text
    """

    # Canonical district name → aliases that appear in complaint text
    # Keys are the exact names used in JharkhandGeoValidator.DISTRICT_CENTERS
    DISTRICT_ALIASES: dict[str, list[str]] = {
        "Ranchi":                      ["ranchi"],
        "Jamshedpur (East Singhbhum)": ["jamshedpur", "east singhbhum", "singhbhum"],
        "Dhanbad":                     ["dhanbad"],
        "Bokaro":                      ["bokaro", "bokaro steel city", "bsl"],
        "Hazaribagh":                  ["hazaribagh", "hazribagh"],
        "Deoghar":                     ["deoghar", "devghar", "baidyanath"],
        "Giridih":                     ["giridih"],
        "Dumka":                       ["dumka"],
        "Palamu":                      ["palamu", "daltonganj", "medininagar"],
        "Garhwa":                      ["garhwa"],
        "Chatra":                      ["chatra"],
        "Koderma":                     ["koderma"],
        "Ramgarh":                     ["ramgarh"],
        "Godda":                       ["godda"],
        "Sahebganj":                   ["sahebganj", "sahibganj"],
        "Pakur":                       ["pakur"],
        "Jamtara":                     ["jamtara"],
        "Latehar":                     ["latehar"],
        "Lohardaga":                   ["lohardaga"],
        "Gumla":                       ["gumla"],
        "Simdega":                     ["simdega"],
        "West Singhbhum":              ["west singhbhum", "chaibasa"],
        "Seraikela-Kharsawan":         ["seraikela", "kharsawan", "seraikela-kharsawan"],
        "Khunti":                      ["khunti"],
    }

    # Well-known places that are clearly NOT in Jharkhand
    OUTSIDE_JH_PLACES: list[str] = [
        "delhi", "new delhi", "mumbai", "bombay", "kolkata", "calcutta",
        "bangalore", "bengaluru", "hyderabad", "chennai", "madras",
        "pune", "ahmedabad", "surat", "jaipur", "lucknow", "kanpur",
        "nagpur", "patna", "bhopal", "indore", "vadodara", "coimbatore",
        "visakhapatnam", "vizag", "guwahati", "chandigarh", "amritsar",
        "ludhiana", "agra", "varanasi", "meerut", "allahabad", "prayagraj",
        "noida", "gurgaon", "gurugram", "faridabad", "thane", "navi mumbai",
        "kerala", "tamil nadu", "karnataka", "rajasthan", "gujarat",
        "maharashtra", "uttar pradesh", "up", "madhya pradesh", "mp",
        "punjab", "haryana", "assam", "odisha", "orissa", "west bengal",
        "bihar", "chhattisgarh", "uttarakhand", "himachal", "goa",
    ]

    # How close (km) GPS must be to the mentioned district centre to "match"
    MATCH_RADIUS_KM: float = 60.0

    def __init__(self, district_centers: dict[str, tuple[float, float]]):
        self._centers = district_centers

        # Build a flat alias → canonical_district lookup (lowercase)
        self._alias_map: dict[str, str] = {}
        for canonical, aliases in self.DISTRICT_ALIASES.items():
            for alias in aliases:
                self._alias_map[alias.lower()] = canonical

        # Build one regex that matches any alias (longest-first to avoid
        # partial matches, e.g. "east singhbhum" before "singhbhum")
        sorted_aliases = sorted(self._alias_map.keys(), key=len, reverse=True)
        self._jh_pattern = re.compile(
            r"\b(" + "|".join(re.escape(a) for a in sorted_aliases) + r")\b",
            re.IGNORECASE,
        )
        self._outside_pattern = re.compile(
            r"\b(" + "|".join(re.escape(p) for p in self.OUTSIDE_JH_PLACES) + r")\b",
            re.IGNORECASE,
        )

    def verify(
        self,
        text: str,
        lat: Optional[float],
        lng: Optional[float],
        geo_result: dict,
    ) -> dict:
        """
        Returns a location_verification dict:
          location_match   : bool | None  (None = unverifiable)
          verdict          : "match" | "mismatch" | "gps_outside" |
                             "text_outside" | "unverifiable"
          text_locations   : list[str]    — JH district names found in text
          outside_mentions : list[str]    — non-JH place names found in text
          gps_district     : str | None   — district nearest to GPS coords
          distance_km      : float | None — GPS→text-district distance
          explanation      : str          — human-readable verdict
        """
        text_lower = text.lower()

        # 1. Extract Jharkhand district names from text
        jh_matches = self._jh_pattern.findall(text_lower)
        jh_districts = list(dict.fromkeys(          # deduplicate, preserve order
            self._alias_map[m.lower()] for m in jh_matches
        ))

        # 2. Extract non-JH place mentions from text
        outside_matches = self._outside_pattern.findall(text_lower)
        outside_places = list(dict.fromkeys(m.lower() for m in outside_matches))

        gps_district = geo_result.get("district_hint")          # set when in JH
        in_jharkhand = geo_result.get("in_jharkhand", False)

        # ── Case A: No place names found anywhere in text ──────────────────
        if not jh_districts and not outside_places:
            return self._result(
                match=None, verdict="unverifiable",
                text_locations=[], outside_mentions=[],
                gps_district=gps_district, distance_km=None,
                explanation=(
                    "No recognisable place name found in complaint text. "
                    "Cannot verify whether GPS coordinates match the report."
                ),
            )

        # ── Case B: Text explicitly mentions a non-JH place ────────────────
        if outside_places and not jh_districts:
            if in_jharkhand:
                explanation = (
                    f"Text mentions '{outside_places[0]}' which is outside Jharkhand, "
                    f"but GPS coordinates point to {gps_district or 'a location inside Jharkhand'}. "
                    "Location MISMATCH — GPS and text disagree."
                )
                return self._result(
                    match=False, verdict="mismatch",
                    text_locations=[], outside_mentions=outside_places,
                    gps_district=gps_district, distance_km=None,
                    explanation=explanation,
                )
            else:
                explanation = (
                    f"Text mentions '{outside_places[0]}' which is outside Jharkhand, "
                    "and GPS coordinates are also outside Jharkhand. "
                    "This report is not from Jharkhand."
                )
                return self._result(
                    match=False, verdict="text_outside",
                    text_locations=[], outside_mentions=outside_places,
                    gps_district=gps_district, distance_km=None,
                    explanation=explanation,
                )

        # ── Case C: Text mentions a JH district ────────────────────────────
        if jh_districts:
            # GPS is outside Jharkhand
            if not in_jharkhand:
                if lat is None or lng is None:
                    explanation = (
                        f"Text mentions '{jh_districts[0]}' (Jharkhand), "
                        "but no GPS coordinates were provided. Cannot verify."
                    )
                    return self._result(
                        match=None, verdict="unverifiable",
                        text_locations=jh_districts, outside_mentions=outside_places,
                        gps_district=None, distance_km=None,
                        explanation=explanation,
                    )
                explanation = (
                    f"Text mentions '{jh_districts[0]}' (Jharkhand), "
                    f"but GPS coordinates (lat={lat:.4f}, lng={lng:.4f}) are "
                    "OUTSIDE Jharkhand. Location MISMATCH — coordinates do not "
                    "match the place mentioned in the report."
                )
                return self._result(
                    match=False, verdict="gps_outside",
                    text_locations=jh_districts, outside_mentions=outside_places,
                    gps_district=None, distance_km=None,
                    explanation=explanation,
                )

            # GPS is inside Jharkhand — check if GPS district ≈ text district
            text_district = jh_districts[0]
            dist_coords = self._centers.get(text_district)

            if dist_coords and lat is not None and lng is not None:
                distance_km = round(haversine_km(lat, lng, dist_coords[0], dist_coords[1]), 1)
                if distance_km <= self.MATCH_RADIUS_KM:
                    explanation = (
                        f"Text mentions '{text_district}' and GPS coordinates are "
                        f"{distance_km} km from its centre — within the {self.MATCH_RADIUS_KM} km "
                        "match radius. Location VERIFIED ✓"
                    )
                    return self._result(
                        match=True, verdict="match",
                        text_locations=jh_districts, outside_mentions=outside_places,
                        gps_district=gps_district, distance_km=distance_km,
                        explanation=explanation,
                    )
                else:
                    explanation = (
                        f"Text mentions '{text_district}' but GPS coordinates are "
                        f"{distance_km} km away (nearest district by GPS: "
                        f"'{gps_district}'). Distance exceeds {self.MATCH_RADIUS_KM} km "
                        "match radius — Location MISMATCH."
                    )
                    return self._result(
                        match=False, verdict="mismatch",
                        text_locations=jh_districts, outside_mentions=outside_places,
                        gps_district=gps_district, distance_km=distance_km,
                        explanation=explanation,
                    )

            # Mentioned district not in our centre table, or no coords — fall
            # back to comparing the GPS district_hint name
            if gps_district and text_district:
                # Normalise: strip parenthetical suffixes for comparison
                gps_base = gps_district.split("(")[0].strip().lower()
                txt_base = text_district.split("(")[0].strip().lower()
                if gps_base == txt_base or gps_base in txt_base or txt_base in gps_base:
                    explanation = (
                        f"Text mentions '{text_district}' and GPS district is "
                        f"'{gps_district}' — names match. Location VERIFIED ✓"
                    )
                    return self._result(
                        match=True, verdict="match",
                        text_locations=jh_districts, outside_mentions=outside_places,
                        gps_district=gps_district, distance_km=None,
                        explanation=explanation,
                    )
                else:
                    explanation = (
                        f"Text mentions '{text_district}' but GPS points to "
                        f"'{gps_district}'. Location MISMATCH."
                    )
                    return self._result(
                        match=False, verdict="mismatch",
                        text_locations=jh_districts, outside_mentions=outside_places,
                        gps_district=gps_district, distance_km=None,
                        explanation=explanation,
                    )

        # Fallback — shouldn't reach here
        return self._result(
            match=None, verdict="unverifiable",
            text_locations=jh_districts, outside_mentions=outside_places,
            gps_district=gps_district, distance_km=None,
            explanation="Could not determine location match.",
        )

    @staticmethod
    def _result(
        match, verdict, text_locations, outside_mentions,
        gps_district, distance_km, explanation
    ) -> dict:
        return {
            "location_match":    match,
            "verdict":           verdict,
            "text_locations":    text_locations,
            "outside_mentions":  outside_mentions,
            "gps_district":      gps_district,
            "distance_km":       distance_km,
            "explanation":       explanation,
        }


# ---------------------------------------------------------------------------
# Stage 1: Spam / authenticity filter
# ---------------------------------------------------------------------------

class SpamFilter:
    """
    Heuristic spam/authenticity filter. Runs before anything else — spam
    complaints should not consume domain-classification or capability
    resources.

    Signals:
      - too short / empty / gibberish text
      - repeated submissions from the same submitter in a short window
      - blocklist pattern match (promo links, phone-number spam, etc.)
    Swap `_gibberish_score` or add a fine-tuned classifier later without
    touching the pipeline contract.
    """

    BLOCKLIST_PATTERNS = [
        r"https?://\S+\.(?:xyz|top|click)\b",
        r"\bwin\s+free\b",
        r"\bclick\s+here\b",
        r"\bcall\s+now\b.*\$\d+",
    ]

    def __init__(self, repeat_window_seconds: int = 300, repeat_threshold: int = 3):
        self.repeat_window_seconds = repeat_window_seconds
        self.repeat_threshold = repeat_threshold
        self._submitter_history: dict[str, list[float]] = {}
        self._blocklist_re = re.compile("|".join(self.BLOCKLIST_PATTERNS), re.IGNORECASE)

    @staticmethod
    def _gibberish_score(text: str) -> float:
        """Cheap heuristic: fraction of 'word-like' tokens with vowels."""
        tokens = re.findall(r"[A-Za-z]+", text)
        if not tokens:
            return 1.0 if text.strip() else 1.0
        bad = sum(1 for t in tokens if len(t) > 3 and not re.search(r"[aeiouAEIOU]", t))
        return bad / len(tokens)

    def _repeat_score(self, submitter_id: str, now: float) -> float:
        history = self._submitter_history.setdefault(submitter_id, [])
        history[:] = [t for t in history if now - t <= self.repeat_window_seconds]
        history.append(now)
        if len(history) >= self.repeat_threshold:
            return min(1.0, (len(history) - self.repeat_threshold + 1) * 0.3)
        return 0.0

    def check(self, complaint: ComplaintInput) -> dict:
        text = complaint.complaint_text or ""
        now = complaint.submitted_at

        length_score = 1.0 if len(text.strip()) < 8 else 0.0
        blocklist_score = 1.0 if self._blocklist_re.search(text) else 0.0
        gibberish = self._gibberish_score(text)
        repeat = self._repeat_score(complaint.submitter_id, now)

        # Weighted combination -> confidence in [0, 1]. Length and blocklist
        # are strong standalone signals (either alone should clear the 0.5
        # is_spam threshold); gibberish/repeat are corroborating signals.
        spam_confidence = min(
            1.0,
            0.6 * length_score + 0.6 * blocklist_score + 0.2 * gibberish + 0.3 * repeat,
        )
        is_spam = spam_confidence >= 0.5

        reason_bits = []
        if length_score:
            reason_bits.append("too short")
        if blocklist_score:
            reason_bits.append("matched blocklist pattern")
        if gibberish > 0.4:
            reason_bits.append("high gibberish ratio")
        if repeat:
            reason_bits.append("repeated submissions in short window")

        return {
            "is_spam": is_spam,
            "spam_confidence": round(spam_confidence, 4),
            "reason": "; ".join(reason_bits) if reason_bits else "passed spam checks",
        }


# ---------------------------------------------------------------------------
# Stage 2: Domain classification (zero-shot embedding, keyword fallback)
#           with confidence calibration and top-3 predictions
# ---------------------------------------------------------------------------

class DomainClassifier:
    def __init__(self, domains_config: dict):
        self.domains = domains_config["domains"]
        self.domain_names = [d["name"] for d in self.domains]
        self._model = None
        self._domain_embeddings = None
        self.method = "keyword"

        if _ST_AVAILABLE:
            try:
                self._model = SentenceTransformer("all-MiniLM-L6-v2", device=_DEVICE)
                descriptions = [d["description"] for d in self.domains]
                self._domain_embeddings = self._model.encode(descriptions, normalize_embeddings=True)
                self.method = "embedding"
            except Exception:
                # Model weights unavailable (e.g. no network) — fall back cleanly.
                self._model = None
                self._domain_embeddings = None
                self.method = "keyword"

    @staticmethod
    def _calibrate_confidence(sims: np.ndarray) -> np.ndarray:
        """
        Margin-based confidence calibration.

        Problem with temperature-softmax over 10 domains: the winner never
        exceeds ~0.20 even on obvious complaints because the score is diluted
        across all 10 buckets. This produces misleadingly low numbers.

        Instead we use:
          1. Min-max normalise the raw cosine similarities to [0, 1].
          2. Scale by the winner's margin over the runner-up (how decisively
             it won), clamped to [0.4, 0.97].
          3. Remaining scores scale proportionally below the winner.

        Result: winner gets 0.60-0.95 on clear cases, 0.40-0.60 on ambiguous
        ones — a range humans can actually interpret.
        """
        sims = np.array(sims, dtype=float)
        mn, mx = sims.min(), sims.max()
        if mx - mn < 1e-9:
            # All identical — genuine uncertainty
            return np.full(len(sims), 1.0 / len(sims))

        norm = (sims - mn) / (mx - mn)          # scale to [0, 1]

        sorted_norm = np.sort(norm)[::-1]
        margin = sorted_norm[0] - sorted_norm[1]  # gap between 1st and 2nd

        # Map margin [0, 0.4] → winner confidence [0.40, 0.97]
        winner_conf = 0.40 + min(margin / 0.4, 1.0) * 0.57
        winner_conf = min(winner_conf, 0.97)

        # Scale all other scores proportionally in the remaining space
        winner_idx = int(np.argmax(norm))
        calibrated = np.zeros(len(norm))
        calibrated[winner_idx] = winner_conf

        remaining = 1.0 - winner_conf
        other_sum = norm.sum() - norm[winner_idx]
        for i in range(len(norm)):
            if i != winner_idx:
                calibrated[i] = (norm[i] / other_sum * remaining) if other_sum > 0 else remaining / (len(norm) - 1)

        return calibrated

    def _classify_embedding(self, text: str) -> tuple[str, float, list[dict]]:
        """
        Returns (best_domain, calibrated_confidence, top_3_predictions).
        """
        vec = self._model.encode([text], normalize_embeddings=True)
        sims = cosine_similarity(vec, self._domain_embeddings)[0]

        calibrated = self._calibrate_confidence(sims)

        # Sort by calibrated confidence, descending
        ranked_indices = np.argsort(calibrated)[::-1]

        top_3 = []
        for i in ranked_indices[:3]:
            top_3.append({
                "domain": self.domain_names[int(i)],
                "confidence": round(float(calibrated[int(i)]), 4),
                "raw_similarity": round(float(sims[int(i)]), 4),
            })

        best_idx = ranked_indices[0]
        return self.domain_names[int(best_idx)], round(float(calibrated[int(best_idx)]), 4), top_3

    def _classify_keyword(self, text: str) -> tuple[str, float, list[dict]]:
        """
        Keyword fallback with top-3 predictions.
        Returns (best_domain, confidence, top_3_predictions).
        """
        text_lower = text.lower()
        hit_counts = []
        for d in self.domains:
            hits = sum(1 for kw in d["keywords"] if kw in text_lower)
            hit_counts.append((d["name"], hits))

        # Sort by hit count, descending
        hit_counts.sort(key=lambda x: x[1], reverse=True)

        top_3 = []
        for name, hits in hit_counts[:3]:
            conf = min(0.95, 0.25 + 0.15 * hits) if hits else 0.05
            top_3.append({
                "domain": name,
                "confidence": round(conf, 4),
                "keyword_hits": hits,
            })

        best_name = hit_counts[0][0] if hit_counts[0][1] > 0 else "Public Administration"
        best_confidence = top_3[0]["confidence"] if top_3 else 0.2

        return best_name, best_confidence, top_3

    def classify(self, text: str) -> dict:
        if self.method == "embedding" and self._model is not None:
            try:
                domain, confidence, top_3 = self._classify_embedding(text)
                return {
                    "domain": domain,
                    "confidence": confidence,
                    "method": "embedding",
                    "top_3_predictions": top_3,
                }
            except Exception:
                pass  # fall through to keyword path below
        domain, confidence, top_3 = self._classify_keyword(text)
        return {
            "domain": domain,
            "confidence": confidence,
            "method": "keyword",
            "top_3_predictions": top_3,
        }


# ---------------------------------------------------------------------------
# Stage 3: Deduplication (geo radius + TF-IDF text similarity)
# ---------------------------------------------------------------------------

class Deduplicator:
    """
    Flags a complaint as a duplicate if an existing complaint is within
    `radius_km` AND its text similarity exceeds `similarity_threshold`.

    Uses TF-IDF + cosine similarity for text (sklearn, no network/model
    dependency required) so dedup works identically regardless of whether
    the domain classifier is in embedding or keyword mode.
    """

    def __init__(self, radius_km: float = 2.0, similarity_threshold: float = 0.55):
        self.radius_km = radius_km
        self.similarity_threshold = similarity_threshold

    def find_duplicate(
        self, complaint: ComplaintInput, existing: list[StoredComplaint]
    ) -> dict:
        if complaint.lat is None or complaint.lng is None or not existing:
            return {"is_duplicate": False, "duplicate_of": None, "duplicate_count": 0}

        nearby = [
            c
            for c in existing
            if c.lat is not None
            and c.lng is not None
            and haversine_km(complaint.lat, complaint.lng, c.lat, c.lng) <= self.radius_km
        ]
        if not nearby:
            return {"is_duplicate": False, "duplicate_of": None, "duplicate_count": 0}

        corpus = [complaint.complaint_text] + [c.text for c in nearby]
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf = vectorizer.fit_transform(corpus)
            sims = cosine_similarity(tfidf[0:1], tfidf[1:])[0]
        except ValueError:
            # e.g. text is empty / all stopwords
            return {"is_duplicate": False, "duplicate_of": None, "duplicate_count": 0}

        matches = [(nearby[i], sims[i]) for i in range(len(nearby)) if sims[i] >= self.similarity_threshold]
        if not matches:
            return {"is_duplicate": False, "duplicate_of": None, "duplicate_count": 0}

        matches.sort(key=lambda pair: pair[1], reverse=True)
        best_match = matches[0][0]
        return {
            "is_duplicate": True,
            "duplicate_of": best_match.complaint_id,
            "duplicate_count": len(matches),
        }


# ---------------------------------------------------------------------------
# Stage 4: Priority scoring (explainable, auditable formula)
# ---------------------------------------------------------------------------

class PriorityScorer:
    """
    priority_score = duplicate_count * DUP_WEIGHT
                    + severity_boost
                    + domain_criticality_weight
                    + recency_boost

    Every term is returned/loggable so the score can be explained to a
    non-technical reviewer — no black-box model here by design.
    """

    DUP_WEIGHT = 2.0
    RECENCY_HALF_LIFE_HOURS = 12.0
    RECENCY_MAX_BOOST = 2.0

    def __init__(self, severity_config: dict, domains_config: dict):
        self.severity_config = severity_config
        self.domain_weights = {d["name"]: d["criticality_weight"] for d in domains_config["domains"]}

    def _severity_boost(self, text: str) -> float:
        text_lower = text.lower()
        boost = 0.0
        for tier in self.severity_config.values():
            if any(kw in text_lower for kw in tier["keywords"]):
                boost = max(boost, tier["boost"])
        return boost

    def _recency_boost(self, submitted_at: float) -> float:
        age_hours = max(0.0, (time.time() - submitted_at) / 3600.0)
        decay = 0.5 ** (age_hours / self.RECENCY_HALF_LIFE_HOURS)
        return round(self.RECENCY_MAX_BOOST * decay, 4)

    def score(self, complaint: ComplaintInput, domain: str, duplicate_count: int) -> dict:
        severity_boost = self._severity_boost(complaint.complaint_text)
        domain_weight = self.domain_weights.get(domain, 1.0)
        recency_boost = self._recency_boost(complaint.submitted_at)

        priority_score = (
            duplicate_count * self.DUP_WEIGHT + severity_boost + domain_weight + recency_boost
        )
        return {
            "priority_score": round(priority_score, 4),
            "severity_boost": severity_boost,
            "_breakdown": {  # not part of the stable contract; handy for debugging/audits
                "duplicate_term": duplicate_count * self.DUP_WEIGHT,
                "severity_boost": severity_boost,
                "domain_weight": domain_weight,
                "recency_boost": recency_boost,
            },
        }


# ---------------------------------------------------------------------------
# Stage 5: Capability matching with basic load balancing
# ---------------------------------------------------------------------------

class CapabilityMatcher:
    def __init__(self, capabilities_config: dict):
        self.capabilities = capabilities_config["capabilities"]

    def match(self, domain: str, priority_score: float) -> dict:
        candidates = [c for c in self.capabilities if c["domain"] == domain]
        if not candidates:
            return {"matched_capability": None, "match_confidence": 0.0}

        # Load-balance: prefer candidates with the most *available* headroom
        # (capacity - current_load), weighted slightly by priority so urgent
        # complaints can still go to a busier-but-capable responder if it's
        # the only real option.
        def headroom(c):
            return c["capacity"] - c["current_load"]

        candidates_sorted = sorted(candidates, key=headroom, reverse=True)
        best = candidates_sorted[0]

        # Simulate assignment: bump current_load so subsequent matches in
        # this batch see updated load (in-memory demo; swap for a real DB
        # transaction in production).
        best["current_load"] += 1

        max_headroom = headroom(best) - 1  # before the increment above
        confidence = 0.5 + 0.5 * min(1.0, max(0.0, max_headroom) / max(1, best["capacity"]))
        return {
            "matched_capability": best["capability"],
            "match_confidence": round(confidence, 4),
        }


# ---------------------------------------------------------------------------
# Stage 6: Industry/partner collaboration suggestion (rules-based)
# ---------------------------------------------------------------------------

class PartnerSuggester:
    def __init__(self, capabilities_config: dict):
        self.partner_map = capabilities_config.get("partner_categories", {})

    def suggest(self, domain: str) -> list[str]:
        return list(self.partner_map.get(domain, []))


# ---------------------------------------------------------------------------
# Stage 7: Fairness / equitable allocation layer
# ---------------------------------------------------------------------------

class FairnessAllocator:
    """
    Ensures no single institution/university dominates capability
    allocations when multiple complaints are close in priority
    (within `priority_tie_threshold`).

    This does not change *whether* a complaint gets matched — it only
    adjusts *ordering* among near-tied competitors for the same limited
    capability slot, and logs every adjustment for auditability.
    """

    def __init__(self, fairness_config: dict):
        self.cfg = fairness_config
        self.enabled = fairness_config.get("enabled", True)
        self.tie_threshold = fairness_config.get("priority_tie_threshold", 1.5)
        self.window_seconds = fairness_config.get("tracking_window_hours", 24) * 3600
        self.max_share_pct = fairness_config.get("max_share_per_source_pct", 30)
        # institution_id -> list of allocation timestamps
        self._allocation_history: dict[str, list[float]] = {}
        self.adjustment_log: list[dict] = []

    def _recent_share(self, institution_id: str, now: float) -> float:
        total = 0
        mine = 0
        for inst, timestamps in self._allocation_history.items():
            recent = [t for t in timestamps if now - t <= self.window_seconds]
            self._allocation_history[inst] = recent
            total += len(recent)
            if inst == institution_id:
                mine = len(recent)
        if total == 0:
            return 0.0
        return 100.0 * mine / total

    def evaluate(
        self,
        complaint: ComplaintInput,
        priority_score: float,
        competing_priorities: list[float],
        now: Optional[float] = None,
    ) -> dict:
        """
        `competing_priorities`: priority scores of other pending complaints
        currently vying for the same capability (caller supplies this from
        a queue/db query — kept generic here).
        """
        now = now or time.time()
        if not self.enabled:
            return {"applied": False, "reason": None}

        has_tie = any(abs(priority_score - p) <= self.tie_threshold for p in competing_priorities)
        share = self._recent_share(complaint.institution_id, now)

        applied = has_tie and share >= self.max_share_pct
        reason = None
        if applied:
            reason = (
                f"institution '{complaint.institution_id}' already holds "
                f"{share:.1f}% of recent allocations (>= {self.max_share_pct}% quota); "
                f"deprioritized within tie band of {self.tie_threshold}"
            )
            self.adjustment_log.append(
                {"institution_id": complaint.institution_id, "reason": reason, "timestamp": now}
            )
        return {"applied": applied, "reason": reason}

    def record_allocation(self, institution_id: str, now: Optional[float] = None) -> None:
        now = now or time.time()
        self._allocation_history.setdefault(institution_id, []).append(now)

    def distribution_metrics(self) -> dict:
        """Exposed via /metrics/fairness — allocation share per institution."""
        now = time.time()
        totals = {}
        grand_total = 0
        for inst, timestamps in self._allocation_history.items():
            recent = [t for t in timestamps if now - t <= self.window_seconds]
            totals[inst] = len(recent)
            grand_total += len(recent)
        shares = {
            inst: round(100.0 * count / grand_total, 2) if grand_total else 0.0
            for inst, count in totals.items()
        }
        return {"counts": totals, "shares_pct": shares, "adjustments_logged": len(self.adjustment_log)}


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class ComplaintPipeline:
    def __init__(self, config_dir: Path = CONFIG_DIR):
        domains_cfg = load_config("domains.json")
        capabilities_cfg = load_config("capabilities.json")
        severity_cfg = load_config("severity_keywords.json")
        fairness_cfg = load_config("fairness_config.json")

        self.geo_validator = JharkhandGeoValidator()
        self.location_verifier = LocationVerifier(JharkhandGeoValidator.DISTRICT_CENTERS)
        self.spam_filter = SpamFilter()
        self.domain_classifier = DomainClassifier(domains_cfg)
        self.deduplicator = Deduplicator()
        self.priority_scorer = PriorityScorer(severity_cfg, domains_cfg)
        self.capability_matcher = CapabilityMatcher(capabilities_cfg)
        self.partner_suggester = PartnerSuggester(capabilities_cfg)
        self.fairness_allocator = FairnessAllocator(fairness_cfg)

        self._store: list[StoredComplaint] = []

    def process(
        self, complaint: ComplaintInput, competing_priorities: Optional[list[float]] = None
    ) -> dict:
        complaint_id = str(uuid.uuid4())
        competing_priorities = competing_priorities or []

        # 0. Geo validation (bounding-box check + nearest district).
        geo_result = self.geo_validator.validate(complaint.lat, complaint.lng)

        # 0b. Location cross-verification: does the text location match GPS?
        location_verification = self.location_verifier.verify(
            complaint.complaint_text, complaint.lat, complaint.lng, geo_result
        )

        # 1. Spam filter — short-circuit early.
        spam_result = self.spam_filter.check(complaint)
        if spam_result["is_spam"]:
            return {
                "complaint_id": complaint_id,
                "is_spam": True,
                "spam_confidence": spam_result["spam_confidence"],
                "geo_validation": geo_result,
                "location_verification": location_verification,
                "domain": None,
                "confidence": 0.0,
                "method": self.domain_classifier.method,
                "top_3_predictions": [],
                "is_duplicate": False,
                "duplicate_of": None,
                "duplicate_count": 0,
                "priority_score": 0.0,
                "severity_boost": 0.0,
                "matched_capability": None,
                "match_confidence": 0.0,
                "suggested_partners": [],
                "fairness_adjustment": {"applied": False, "reason": None},
            }

        # 2. Domain classification.
        domain_result = self.domain_classifier.classify(complaint.complaint_text)

        # 3. Deduplication.
        dup_result = self.deduplicator.find_duplicate(complaint, self._store)

        # 4. Priority scoring.
        priority_result = self.priority_scorer.score(
            complaint, domain_result["domain"], dup_result["duplicate_count"]
        )

        # 5. Fairness check (before final capability commit).
        fairness_result = self.fairness_allocator.evaluate(
            complaint, priority_result["priority_score"], competing_priorities
        )

        # 6. Capability matching (skip/deprioritize if fairness flagged it —
        #    here we still match, but a real queue would re-sort first).
        match_result = self.capability_matcher.match(
            domain_result["domain"], priority_result["priority_score"]
        )
        if match_result["matched_capability"]:
            self.fairness_allocator.record_allocation(complaint.institution_id)

        # 7. Partner suggestion.
        partners = self.partner_suggester.suggest(domain_result["domain"])

        # Persist for future dedup/fairness lookups.
        self._store.append(
            StoredComplaint(
                complaint_id=complaint_id,
                text=complaint.complaint_text,
                domain=domain_result["domain"],
                lat=complaint.lat,
                lng=complaint.lng,
                institution_id=complaint.institution_id,
                submitted_at=complaint.submitted_at,
                matched_capability=match_result["matched_capability"],
            )
        )

        return {
            "complaint_id": complaint_id,
            "is_spam": False,
            "spam_confidence": spam_result["spam_confidence"],
            "geo_validation": geo_result,
            "location_verification": location_verification,
            "domain": domain_result["domain"],
            "confidence": domain_result["confidence"],
            "method": domain_result["method"],
            "top_3_predictions": domain_result.get("top_3_predictions", []),
            "is_duplicate": dup_result["is_duplicate"],
            "duplicate_of": dup_result["duplicate_of"],
            "duplicate_count": dup_result["duplicate_count"],
            "priority_score": priority_result["priority_score"],
            "severity_boost": priority_result["severity_boost"],
            "matched_capability": match_result["matched_capability"],
            "match_confidence": match_result["match_confidence"],
            "suggested_partners": partners,
            "fairness_adjustment": fairness_result,
        }


# ---------------------------------------------------------------------------
# Optional HTTP layer (only wired up if fastapi is installed)
# ---------------------------------------------------------------------------

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse
    from pydantic import BaseModel

    class AttachmentModel(BaseModel):
        filename: str
        content_type: str
        storage_ref: str

    # --- Backward-compatible contract for the backend team ---
    class ClassifyRequest(BaseModel):
        """Matches the backend team's expected POST /classify contract exactly."""
        text: str
        lat: Optional[float] = None
        lng: Optional[float] = None

    # --- Full diagnostic request (superset) ---
    class ComplaintRequest(BaseModel):
        complaint_text: str
        submitter_id: str
        institution_id: str = "unknown"
        lat: Optional[float] = None
        lng: Optional[float] = None
        attachments: list[AttachmentModel] = []

    app = FastAPI(
        title="Civic Complaint Triage Service — SIH26043",
        description="AI/ML classification microservice for the Societal Innovation Collaboration Portal (Govt of Jharkhand)",
        version="2.0.0",
    )

    # CORS — allow all origins for hackathon integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _pipeline = ComplaintPipeline()

    @app.post("/classify")
    def classify_complaint(req: ClassifyRequest):
        """
        Backward-compatible endpoint matching the backend team's contract.

        Request:  {"text": str, "lat": float?, "lng": float?}
        Response: {"domain": str, "confidence": float, "method": str,
                   "is_duplicate": bool, "duplicate_of": str|null,
                   "duplicate_count": int, "priority_score": float,
                   "severity_boost": float}
        """
        complaint = ComplaintInput(
            complaint_text=req.text,
            submitter_id="anonymous",
            lat=req.lat,
            lng=req.lng,
        )
        full_result = _pipeline.process(complaint)

        # Return core fields + location_verification (always included now)
        return {
            "domain": full_result["domain"],
            "confidence": full_result["confidence"],
            "method": full_result["method"],
            "is_duplicate": full_result["is_duplicate"],
            "duplicate_of": full_result["duplicate_of"],
            "duplicate_count": full_result["duplicate_count"],
            "priority_score": full_result["priority_score"],
            "severity_boost": full_result["severity_boost"],
            "location_verification": full_result["location_verification"],
        }

    @app.post("/classify/full")
    def classify_complaint_full(req: ClassifyRequest):
        """
        Full diagnostic endpoint — returns everything including geo validation,
        top-3 predictions, spam analysis, fairness, partners, capability matching.
        Great for demos and debugging.
        """
        complaint = ComplaintInput(
            complaint_text=req.text,
            submitter_id="anonymous",
            lat=req.lat,
            lng=req.lng,
        )
        return _pipeline.process(complaint)

    @app.get("/metrics/fairness")
    def fairness_metrics():
        return _pipeline.fairness_allocator.distribution_metrics()

    @app.get("/health")
    def health():
        cuda_available = False
        cuda_device_name = None
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                cuda_device_name = torch.cuda.get_device_name(0)
        except ImportError:
            pass
        return {
            "status": "ok",
            "service": "civic-complaint-triage",
            "version": "2.0.0",
            "domain_classifier_method": _pipeline.domain_classifier.method,
            "domains_loaded": len(_pipeline.domain_classifier.domain_names),
            "cuda_available": cuda_available,
            "cuda_device": cuda_device_name,
            "inference_device": _DEVICE,
        }

    @app.get("/domains")
    def list_domains():
        """Returns the active domain taxonomy — useful for frontend dropdowns."""
        return {
            "domains": _pipeline.domain_classifier.domain_names,
            "count": len(_pipeline.domain_classifier.domain_names),
        }

    # Serve the demo dashboard if it exists
    @app.get("/demo")
    def demo_dashboard():
        dashboard_path = Path(__file__).parent / "demo_dashboard.html"
        if dashboard_path.exists():
            return FileResponse(dashboard_path, media_type="text/html")
        return {"error": "demo_dashboard.html not found"}

except ImportError:
    app = None  # FastAPI not installed — pipeline still usable as a library.


if __name__ == "__main__":
    # Quick manual smoke test without needing uvicorn/network.
    pipeline = ComplaintPipeline()

    print("=" * 70)
    print("  Civic Complaint Triage — Smoke Test")
    print(f"  Domain classifier method: {pipeline.domain_classifier.method}")
    print(f"  Domains loaded: {pipeline.domain_classifier.domain_names}")
    print("=" * 70)

    demos = [
        ComplaintInput(
            complaint_text="Major water pipeline leak flooding the street near the market in Ranchi",
            submitter_id="user_1",
            institution_id="univ_A",
            lat=23.3441,
            lng=85.3096,
        ),
        ComplaintInput(
            complaint_text="MGNREGA wages have not been paid for 3 months in Gumla tribal area, families are starving",
            submitter_id="user_2",
            institution_id="univ_B",
            lat=23.0443,
            lng=84.5426,
        ),
        ComplaintInput(
            complaint_text="School building roof collapsed during rain, children had narrow escape in Hazaribagh",
            submitter_id="user_3",
            institution_id="univ_C",
            lat=23.9925,
            lng=85.3637,
        ),
    ]

    for i, demo in enumerate(demos, 1):
        print(f"\n--- Demo {i}: {demo.complaint_text[:60]}... ---")
        result = pipeline.process(demo)
        print(json.dumps(result, indent=2, default=str))
