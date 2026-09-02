# ImpactVerse — AI/ML Civic Complaint Triage Microservice

> **SIH26043** — Societal Innovation Collaboration Portal for Govt of Jharkhand

An 8-stage AI pipeline that takes a raw citizen complaint and turns it into a
classified, deduplicated, priority-scored, fairness-checked assignment — built
for a hackathon, designed so every stage is swappable later.

```
intake → geo validation → spam filter → domain classification (embedding/keyword)
       → deduplication (TF-IDF + geo radius) → priority scoring (explainable formula)
       → capability matching (load-balanced) → partner suggestion → fairness allocation
```

## Quickstart

```bash
pip install -r requirements.txt

# Run the pipeline directly (no server needed):
python main.py

# Run tests:
pytest test_classify.py -v

# Run as an HTTP service:
uvicorn main:app --reload --port 8001
# then open: http://localhost:8001/demo         ← visual demo dashboard
#            POST http://localhost:8001/classify  ← backend integration
#            POST http://localhost:8001/classify/full ← full diagnostic
#            GET  http://localhost:8001/health
#            GET  http://localhost:8001/domains
#            GET  http://localhost:8001/metrics/fairness
```

The service works with **zero network access**. If `sentence-transformers`
isn't installed, or the `all-MiniLM-L6-v2` weights can't be downloaded, the
domain classifier automatically falls back to keyword matching. Check the
`method` field in any response (`"embedding"` or `"keyword"`) to see which
path was used — nothing else in the pipeline needs to know or care.

## SIH-Aligned Domain Taxonomy (10 Domains)

| Domain | Criticality | Example Keywords |
|--------|:-----------:|------------------|
| Education | 2.5 | school, teacher, scholarship, classroom, dropout |
| Agriculture | 3.5 | crop, irrigation, farmer, drought, seed, paddy |
| Healthcare | 4.5 | hospital, medicine, ambulance, malaria, anganwadi |
| Water Resources | 4.0 | water, pipeline, handpump, borewell, contaminated |
| Environment | 3.0 | pollution, mining, deforestation, forest, coal |
| Energy | 3.5 | power, transformer, solar, outage, voltage |
| Urban Development | 2.5 | pothole, road, drainage, sewage, streetlight |
| Accessibility | 2.0 | disability, wheelchair, ramp, assistive, inclusive |
| Public Administration | 2.0 | corruption, ration card, pension, land record, RTI |
| Rural Livelihoods | 3.0 | MGNREGA, tribal, SHG, livelihood, forest rights |

## API Endpoints

### `POST /classify` — Backend Integration

**This is the endpoint your backend teammate (Santosh) calls.** Matches the
agreed contract exactly.

```bash
curl -X POST http://localhost:8001/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Water pipeline burst near Ranchi market", "lat": 23.3441, "lng": 85.3096}'
```

Response:
```json
{
  "domain": "Water Resources",
  "confidence": 0.8234,
  "method": "embedding",
  "is_duplicate": false,
  "duplicate_of": null,
  "duplicate_count": 0,
  "priority_score": 9.5,
  "severity_boost": 3.0
}
```

### `POST /classify/full` — Diagnostic / Demo

Returns everything: geo validation, top-3 predictions, spam analysis,
capability matching, partner suggestions, fairness adjustment.

### `GET /health`

```json
{
  "status": "ok",
  "service": "civic-complaint-triage",
  "version": "2.0.0",
  "domain_classifier_method": "embedding",
  "domains_loaded": 10
}
```

### `GET /domains`

Returns the active domain taxonomy list.

### `GET /metrics/fairness`

Returns per-institution allocation shares and adjustment counts.

### `GET /demo`

Serves the interactive visual demo dashboard (for judges).

## Pipeline Stages

| # | Stage | Class | Notes |
|---|-------|-------|-------|
| 0 | Geo validation | `JharkhandGeoValidator` | Validates lat/lng against Jharkhand bounding box (21.97–25.35°N, 83.32–87.92°E), returns nearest district hint from 24 district centers. Non-blocking — adds context, doesn't reject. |
| 1 | Spam filter | `SpamFilter` | Heuristics: length, blocklist regex, gibberish ratio, repeat-submission burst detection. Short-circuits the pipeline for spam. |
| 2 | Domain classification | `DomainClassifier` | Zero-shot embedding similarity (all-MiniLM-L6-v2) against domain descriptions with temperature-scaled softmax calibration. Returns top-3 predictions. Automatic keyword fallback. |
| 3 | Deduplication | `Deduplicator` | Geo radius (haversine, default 2km) + TF-IDF text similarity. Uses TF-IDF (not the embedding model) so dedup behavior is identical regardless of classification path. |
| 4 | Priority scoring | `PriorityScorer` | `duplicate_count × 2 + severity_boost + domain_criticality_weight + recency_boost`. Every term is returned for audit — no black box. |
| 5 | Capability matching | `CapabilityMatcher` | Matches domain to a Jharkhand government responder (`config/capabilities.json`), load-balances by headroom. |
| 6 | Partner suggestion | `PartnerSuggester` | Rules-based domain → industry/NGO partner mapping. |
| 7 | Fairness allocation | `FairnessAllocator` | Tracks per-institution allocation share; deprioritizes dominant institutions within tie bands. |

## Demo Dashboard

Open `http://localhost:8001/demo` (or `demo_dashboard.html` directly) for a
visual, judge-facing demo with:

- 🔮 Dark-themed glassmorphism UI
- ⚡ 8 preset Jharkhand complaints (one-click load)
- 📊 Domain confidence bar chart (top-3 predictions)
- 🎯 Priority score breakdown visualization
- 🗺️ Geo validation with district hints
- 🤝 Industry partner suggestions
- 📋 Full JSON response viewer

## Configuration (all in `config/`)

- **`domains.json`** — the domain taxonomy. Each entry has `name`, `description` (for zero-shot embedding), `criticality_weight`, and `keywords`.
- **`capabilities.json`** — Jharkhand government responders and `partner_categories`.
- **`severity_keywords.json`** — tiered severity keyword → boost mapping.
- **`fairness_config.json`** — allocation fairness controls.

## Project Structure

```
Impactverse/
├── main.py                 # Pipeline classes + FastAPI endpoints
├── test_classify.py        # Comprehensive test suite (50+ tests)
├── demo_dashboard.html     # Visual demo UI for judges
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── config/
    ├── domains.json         # 10 SIH-aligned Jharkhand domains
    ├── capabilities.json    # Government responders + partner categories
    ├── severity_keywords.json # Tiered severity boosts
    └── fairness_config.json   # Allocation fairness controls
```

## Known Limitations (be upfront about these if asked in judging)

- In-memory storage only (`ComplaintPipeline._store`, `FairnessAllocator._allocation_history`) — swap for a real DB before any real deployment.
- Capability `current_load` increments are a simulation, not a real assignment system.
- Spam and domain classification are heuristic/zero-shot, not fine-tuned on real complaint data — accuracy improves with labeled data.
- Attachment content (image/video pixels) isn't analyzed yet — extension point for computer vision.
- Geo validator uses a bounding box approximation, not a precise boundary polygon.
