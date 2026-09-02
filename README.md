# Problem Classification Service — Shanur's piece (AI/ML)

Classifies a citizen-submitted problem into a thematic domain, flags likely
duplicates of nearby existing reports, and produces an explainable priority
score. This is a standalone microservice — Santosh's backend calls it over
HTTP, nothing about his stack has to match this one.

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

First run downloads the embedding model (`all-MiniLM-L6-v2`, ~90MB) from
Hugging Face, so do this once **before** the hackathon starts, on venue wifi
you trust, or on your phone hotspot the night before. After the first
successful download it's cached locally and works offline from then on.

**If there's no internet at all when it starts**, the service automatically
falls back to a keyword-based classifier instead of crashing — you'll see a
log line saying so, and `GET /health` will report
`"embedding_model_loaded": false`. This is the fallback described in the
team playbook; it's deliberately built in, not a bug.

## Test it

```bash
python3 test_classify.py
```

Runs four checks: correct domain classification, duplicate detection for two
differently-worded reports of the same issue, correct *non*-detection when
an identical report comes from far away, and priority scoring driven by
severity keywords. All should print `PASS`.

You can also poke it directly once the server's running:

```bash
curl -X POST http://127.0.0.1:8001/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Handpump water is contaminated, several people sick", "lat": 23.34, "lng": 85.31}'
```

Or open `http://127.0.0.1:8001/docs` for FastAPI's interactive Swagger UI —
useful for Santosh to try requests without writing any client code first.

## The one endpoint

`POST /classify`

**Request:**
```json
{ "text": "title + description combined", "lat": 23.3441, "lng": 85.3096 }
```

**Response:**
```json
{
  "domain": "Water Resources",
  "confidence": 0.82,
  "method": "embedding",
  "is_duplicate": false,
  "duplicate_of": null,
  "duplicate_count": 1,
  "priority_score": 5.0,
  "severity_boost": 3.0
}
```

## Integration note for Santosh

Call this from `POST /problems` right after you insert the new row — pass
`title + " " + description` as `text`. Store the returned `domain`,
`priority_score`, and `duplicate_count` on the problem record. If
`is_duplicate` is `true`, don't create a new problem row at all — increment
the `duplicate_count` on the existing one (`duplicate_of` gives you its id)
and let the citizen see "N others reported this" instead of a second entry
in the tracker.

## What to say if a judge asks how the classification works

It's zero-shot sentence-embedding classification: each of the 10 domains
has a short reference description, the incoming report is embedded with the
same model, and it's assigned to whichever domain description it's closest
to by cosine similarity — no labelled training data required, which is what
makes it feasible to build in a hackathon and still be a legitimate,
explainable ML technique rather than a black box.

## Known limitation, worth stating proactively rather than getting caught by it

The keyword fallback's duplicate detection is noticeably cruder than the
embedding version — it only catches duplicates that share enough literal
words, not ones that are semantically similar but phrased very differently.
That's an acceptable trade for "the demo still works with no internet," not
a claim that it's as good as the primary path. Say this upfront if asked
rather than letting a judge discover it by testing edge cases.
