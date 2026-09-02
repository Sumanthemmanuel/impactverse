"""
Societal Problem Classification Service
SIH26043 — AI-enabled problem management module (Shanur's piece)

Given a citizen-submitted problem report, this service:
  1. Classifies it into one of 10 thematic domains (zero-shot, no training needed)
  2. Flags likely duplicates of existing nearby reports in the same domain
  3. Produces an explainable priority score

Exposes one endpoint: POST /classify

If sentence-transformers / its model weights can't be downloaded (e.g. no
internet at the venue), the service automatically falls back to a
keyword-based classifier so the demo never breaks. This mirrors the
fallback plan in the team playbook.
"""

import math
import re
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Societal Problem Classification Service", version="1.0")

# ---------------------------------------------------------------------------
# Domain reference descriptions — used for zero-shot classification.
# Each is a short sentence describing what belongs in that domain; the model
# never needs labelled training examples, it just measures how close the
# submitted text is to each description.
# ---------------------------------------------------------------------------
DOMAINS = {
    "Education": "Problems related to schools, colleges, teachers, students, "
                  "learning infrastructure, and access to education.",
    "Agriculture": "Problems related to farming, crops, irrigation, farmers, "
                    "livestock, and agricultural produce.",
    "Healthcare": "Problems related to hospitals, clinics, doctors, medicines, "
                   "disease outbreaks, and access to medical care.",
    "Water Resources": "Problems related to drinking water supply, handpumps, "
                        "water contamination, wells, and water scarcity.",
    "Environment": "Problems related to pollution, deforestation, waste "
                    "management, air quality, and environmental degradation.",
    "Energy": "Problems related to electricity supply, power outages, "
               "renewable energy, and energy infrastructure.",
    "Urban Development": "Problems related to roads, housing, urban planning, "
                          "drainage, and city infrastructure.",
    "Accessibility": "Problems related to disability access, ramps, and "
                      "accessible infrastructure for elderly and disabled people.",
    "Public Administration": "Problems related to government offices, public "
                              "services, corruption, and administrative delays.",
    "Rural Livelihoods": "Problems related to rural employment, income "
                          "generation, cottage industries, and village economy.",
}

# Keyword fallback used only if the embedding model can't be loaded.
DOMAIN_KEYWORDS = {
    "Education": ["school", "teacher", "student", "college", "classroom", "syllabus"],
    "Agriculture": ["crop", "farmer", "irrigation", "farm", "livestock", "harvest"],
    "Healthcare": ["hospital", "clinic", "doctor", "medicine", "disease", "patient"],
    "Water Resources": ["water", "handpump", "well", "contaminat", "drought", "borewell"],
    "Environment": ["pollution", "waste", "deforestation", "garbage", "air quality"],
    "Energy": ["electricity", "power outage", "transformer", "power cut", "voltage"],
    "Urban Development": ["road", "drainage", "housing", "streetlight", "pothole"],
    "Accessibility": ["disability", "ramp", "wheelchair", "accessib"],
    "Public Administration": ["office", "corruption", "delay", "government", "certificate"],
    "Rural Livelihoods": ["employment", "livelihood", "cottage industry", "wages", "village"],
}

SEVERITY_KEYWORDS = {
    "collapsed": 3, "contaminated": 3, "no water": 3, "unsafe": 2, "flooding": 3,
    "outbreak": 3, "urgent": 2, "critical": 3, "died": 3, "death": 3,
    "injury": 2, "injured": 2, "blocked": 1, "delay": 1, "shortage": 2,
    "broken": 1, "damaged": 1, "leaking": 1, "collapse": 3,
}

DEDUP_THRESHOLD = 0.80          # cosine similarity threshold (embedding method)
DEDUP_THRESHOLD_KEYWORD = 0.35  # word-overlap threshold (keyword fallback method) —
                                 # a much lower bar, since raw word overlap is a
                                 # cruder signal than semantic similarity
RADIUS_KM = 2.0                 # only compare against reports within this distance

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "and", "or", "of", "in",
    "on", "at", "to", "from", "our", "near", "several", "with", "for", "by",
    "this", "that", "it", "as", "has", "have", "had", "be", "been", "being",
}

# ---------------------------------------------------------------------------
# Try to load the embedding model. If it's unavailable (no internet on the
# venue wifi, etc.), fall back to keyword matching automatically instead of
# crashing the service.
# ---------------------------------------------------------------------------
_model = None
_domain_embeddings = None
_domain_names = list(DOMAINS.keys())
USE_EMBEDDINGS = True

try:
    from sentence_transformers import SentenceTransformer, util as st_util
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    _domain_embeddings = _model.encode(list(DOMAINS.values()), convert_to_tensor=True)
except Exception as exc:  # noqa: BLE001 — intentionally broad: any load failure -> fallback
    USE_EMBEDDINGS = False
    print(f"[classifier] Embedding model unavailable ({exc}); using keyword fallback.")

# In-memory store standing in for Santosh's Problems table. In production,
# swap these two functions for real DB reads/writes — nothing else changes.
existing_problems: List[dict] = []


class ClassifyRequest(BaseModel):
    text: str = Field(..., description="Title + description combined")
    lat: float
    lng: float


class ClassifyResponse(BaseModel):
    domain: str
    confidence: float
    method: str                # "embedding" or "keyword" — shown for transparency
    is_duplicate: bool
    duplicate_of: Optional[str] = None
    duplicate_count: int
    priority_score: float
    severity_boost: float


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lng points, in kilometres."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def severity_boost(text: str) -> float:
    text_lower = text.lower()
    return float(sum(weight for kw, weight in SEVERITY_KEYWORDS.items() if kw in text_lower))


def classify_embedding(text: str):
    text_embedding = _model.encode(text, convert_to_tensor=True)
    sims = st_util.cos_sim(text_embedding, _domain_embeddings)[0]
    best_idx = int(sims.argmax())
    return _domain_names[best_idx], float(sims[best_idx]), text_embedding


def classify_keyword(text: str):
    text_lower = text.lower()
    scores = {domain: 0 for domain in DOMAIN_KEYWORDS}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[domain] += 1
    best_domain = max(scores, key=scores.get)
    total_hits = sum(scores.values())
    confidence = scores[best_domain] / total_hits if total_hits > 0 else 0.0
    if scores[best_domain] == 0:
        best_domain = "Public Administration"  # safe default bucket
    return best_domain, confidence, None


def similarity(embedding_a, embedding_b) -> float:
    if embedding_a is None or embedding_b is None:
        return 0.0
    return float(st_util.cos_sim(embedding_a, embedding_b)[0][0])


def text_overlap_ratio(text_a: str, text_b: str) -> float:
    """Crude keyword-overlap fallback for dedup when embeddings aren't available.
    Stopwords are stripped first so common words like 'the'/'near' don't dilute
    the signal — otherwise genuinely duplicate reports written in different
    phrasing score too low to be caught."""
    words_a = set(re.findall(r"\w+", text_a.lower())) - STOPWORDS
    words_b = set(re.findall(r"\w+", text_b.lower())) - STOPWORDS
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    # 1. Domain classification
    if USE_EMBEDDINGS:
        domain, confidence, text_embedding = classify_embedding(req.text)
        method = "embedding"
    else:
        domain, confidence, text_embedding = classify_keyword(req.text)
        method = "keyword"

    # 2. Deduplication — only check reports in the same domain, within radius
    is_duplicate = False
    duplicate_of = None
    duplicate_count = 1

    for p in existing_problems:
        if p["domain"] != domain:
            continue
        if haversine_km(req.lat, req.lng, p["lat"], p["lng"]) > RADIUS_KM:
            continue

        if USE_EMBEDDINGS:
            sim = similarity(text_embedding, p.get("embedding"))
            threshold = DEDUP_THRESHOLD
        else:
            sim = text_overlap_ratio(req.text, p["text"])
            threshold = DEDUP_THRESHOLD_KEYWORD

        if sim >= threshold:
            is_duplicate = True
            duplicate_of = p["id"]
            p["duplicate_count"] = p.get("duplicate_count", 1) + 1
            duplicate_count = p["duplicate_count"]
            break

    # 3. Priority score — simple and explainable on purpose
    sev_boost = severity_boost(req.text)
    priority_score = round(duplicate_count * 2 + sev_boost, 2)

    if not is_duplicate:
        existing_problems.append({
            "id": f"P{len(existing_problems) + 1}",
            "text": req.text,
            "domain": domain,
            "lat": req.lat,
            "lng": req.lng,
            "embedding": text_embedding if USE_EMBEDDINGS else None,
            "duplicate_count": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    return ClassifyResponse(
        domain=domain,
        confidence=round(confidence, 3),
        method=method,
        is_duplicate=is_duplicate,
        duplicate_of=duplicate_of,
        duplicate_count=duplicate_count,
        priority_score=priority_score,
        severity_boost=sev_boost,
    )


@app.get("/health")
def health():
    return {"status": "ok", "embedding_model_loaded": USE_EMBEDDINGS}


# Run with: uvicorn main:app --reload --port 8001
