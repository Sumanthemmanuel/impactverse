# AI Coding Prompts — SIH26043 Team

## How to use these

- Paste your section as the **first message** in a fresh chat with whatever AI coding tool you're using (Claude, Claude Code, ChatGPT, Cursor). Starting fresh matters — a chat that's already wandered through other topics gives worse code than one that opens with full context.
- If you have access to **Claude Code**, hand it the prompt directly as a task — it'll create the files, run them, and fix its own errors, which is faster than copy-pasting code blocks by hand.
- If the assistant tries to dump everything into one giant response, tell it to give you one file at a time so you can sanity-check each before it builds the next thing on top.
- **Do not let the AI rename fields or endpoints.** Every prompt below uses identical field names for the same objects on purpose — that's what lets five people's code plug into each other without a painful integration afternoon. If a model suggests "cleaning up" a name, say no and move on.

---

## Santosh — Backend

```
You are helping me build the backend for a hackathon project (18-hour build,
FastAPI + Postgres via Supabase). Act as a senior backend engineer working
under a tight deadline — prioritize working code over completeness.

CONTEXT: We're building "Societal Innovation Collaboration Portal" for
SIH26043 (Govt of Jharkhand). Citizens submit local problems (photo,
location, description). An external AI microservice classifies, dedupes,
and prioritizes each submission. Universities get routed problems matching
their expertise. Industries can express interest in projects. A government
dashboard shows aggregate stats.

MY ROLE: backend API only. A teammate owns the frontend (calls my API) and
another teammate owns the classification microservice (I call their API).

DATABASE SCHEMA (Postgres, SQLAlchemy models matching this exactly — do not
rename fields):
Users(id, name, role[citizen|university|industry|govt], org_id, email)
Problems(id, title, description, photo_url, lat, lng, district, domain,
         priority_score, status, duplicate_count, submitted_by, created_at)
Universities(id, name, district, expertise_domains[])
  -- expertise_domains is an array of strings, e.g. ["Water Resources","Healthcare"]
Assignments(id, problem_id, university_id, status, team_members[])
IndustryInterests(id, problem_id, industry_name, status, created_at)
Notifications(id, problem_id, message, created_at)

EXTERNAL CLASSIFIER CONTRACT (already built by a teammate, call it exactly
as-is):
POST http://localhost:8001/classify
Request:  {"text": "<title + description>", "lat": <float>, "lng": <float>}
Response: {"domain": str, "confidence": float, "method": str,
           "is_duplicate": bool, "duplicate_of": str|null,
           "duplicate_count": int, "priority_score": float,
           "severity_boost": float}

ENDPOINTS TO BUILD — exactly these paths and behaviors:
1. POST /problems — accepts title, description, photo_url, lat, lng,
   submitted_by. Calls the classifier synchronously. If is_duplicate is
   true, increment duplicate_count on the existing problem (found via
   duplicate_of) instead of inserting a new row, and return that existing
   problem. Otherwise insert a new Problems row using the classifier's
   domain/priority_score, status defaults to "Submitted".
2. GET /problems — optional query params ?domain=&district=&status=
3. GET /problems/{id}
4. PATCH /problems/{id}/status — body {"status": "..."}, must be one of
   Submitted / Assigned to University / In Progress / Resolved
5. GET /universities
6. GET /problems/{id}/suggested-universities — ranks universities by plain
   set-intersection overlap between their expertise_domains and the
   problem's domain, returns top 3. Keep this simple — no ML here.
7. POST /universities/{id}/assign — body {"problem_id": ...}, creates an
   Assignments row, sets the problem's status to "Assigned to University"
8. GET /dashboard/stats — returns {"total_problems": int,
   "by_domain": {...}, "by_district": {...}, "by_status": {...},
   "universities_engaged": int, "industries_engaged": int}
9. POST /industry/interest — body {"problem_id":..., "industry_name":...}

AUTH: do NOT build real authentication. Four hardcoded demo users
(citizen_demo, university_demo, industry_demo, govt_demo), selectable from
a dropdown, no password. This is intentional hackathon scope — don't add
JWT/OAuth complexity.

DELIVER: FastAPI app with SQLAlchemy models, Pydantic schemas, a small
router-per-resource structure, requirements.txt, and a .env.example with
DATABASE_URL and CLASSIFIER_URL. Add CORS middleware allowing all origins.
Give me the models first, one message at a time, so I can check the schema
before you build routes on top of it.
```

---

## Shanur — AI/ML classifier

This one's already built and tested — you have the working files (`main.py`, `test_classify.py`, `requirements.txt`, `README.md`). Use the prompt below only if you want to extend it (e.g. add more domains, tune thresholds) in a fresh AI session, so the extension stays consistent with what's already running.

```
You are a machine learning engineer helping me extend an existing
classification microservice for an 18-hour hackathon. Here is the current
main.py [paste the file]. Keep the exact same response contract — do not
rename any field:
{"domain": str, "confidence": float, "method": "embedding"|"keyword",
 "is_duplicate": bool, "duplicate_of": str|null, "duplicate_count": int,
 "priority_score": float, "severity_boost": float}

The service uses sentence-transformers (all-MiniLM-L6-v2) for zero-shot
domain classification against 10 reference domain descriptions, cosine
similarity for deduplication within a 2km radius, and an explainable
priority formula (duplicate_count * 2 + severity_keyword_boost). It
auto-falls-back to keyword matching if the embedding model can't load.

My change: [describe what you want to add or tune]. Keep the fallback path
working after your change, and update test_classify.py to cover it.
```

---

## Poorna — Frontend, citizen side

```
You're a frontend engineer helping me build the citizen-facing part of a
React app for an 18-hour hackathon. Stack: React + Vite + Tailwind CSS +
shadcn/ui components. Use Leaflet.js with OpenStreetMap tiles for maps
(NOT Google Maps — no API key setup time available) and the free Nominatim
API to reverse-geocode a lat/lng pin into a district name.

CONTEXT: this is one route group (/citizen) inside a larger shared app — a
teammate is building /university and /admin route groups on the same
design system. First define a small shared theme (colors, spacing,
Button/Card/Badge components) in a way that's easy for them to reuse,
before building the screens below.

BACKEND API (already built by a teammate, base URL from env var
VITE_API_URL, call it exactly as specified):
POST /problems — body {title, description, photo_url, lat, lng,
  submitted_by}, returns {id, title, description, domain, priority_score,
  status, duplicate_count, lat, lng, district}
GET /problems?domain=&district=&status= — array of the same shape
GET /problems/{id}

BUILD TWO SCREENS:
1. Submission form — title, description, category dropdown (the 10
   domains listed below; let the citizen pick, the backend assigns the
   real domain after submission via the classifier, we are not wiring
   live AI suggestions into this form for v1), photo upload (plain
   <input type="file">, convert to base64 client-side, no cloud storage
   needed), a Leaflet map the citizen clicks to drop a pin (auto
   reverse-geocode via Nominatim into an editable district text field),
   submit button that POSTs to /problems and shows a success state with
   the returned status.
2. Public tracker — combined list + map view of all submitted problems
   (GET /problems), status badges color-coded by status, filter dropdowns
   for domain and district that add query params to the fetch.

Domains: Education, Agriculture, Healthcare, Water Resources, Environment,
Energy, Urban Development, Accessibility, Public Administration, Rural
Livelihoods.

This is the first screen judges click through, so prioritize clean visual
polish — generous spacing, clear hierarchy, no lorem ipsum — over extra
features. Give me the shared theme files first, then the submission form,
then the tracker, as separate messages.
```

---

## Kashvi — Frontend, institution/govt side

```
You're a frontend engineer helping me build the institution/government
part of a React app for an 18-hour hackathon (same repo as a teammate's
/citizen route group — reuse their shared Tailwind theme and
Button/Card/Badge components exactly, don't start a second design system).
Stack: React + Vite + Tailwind + Recharts for charts.

BACKEND API (already built by a teammate, base URL from env var
VITE_API_URL):
GET /problems?domain=&district=&status= — array of {id, title,
  description, domain, priority_score, status, duplicate_count, lat, lng,
  district}
GET /problems/{id}/suggested-universities — array of matching universities
PATCH /problems/{id}/status — body {status}
POST /universities/{id}/assign — body {problem_id}
GET /dashboard/stats — {total_problems, by_domain: {...},
  by_district: {...}, by_status: {...}, universities_engaged,
  industries_engaged}
POST /industry/interest — body {problem_id, industry_name}

BUILD TWO SCREENS:
1. /university — list of problems assigned to "my" university (for the
   demo, just filter by a hardcoded domain profile), each with a "Form
   team" button that PATCHes status to "In Progress" and a text input to
   record team member names (local state is fine, no dedicated endpoint
   needed for team members in v1).
2. /admin — fetch GET /dashboard/stats and render: a pie chart of
   by_domain, a bar chart of by_district, a stacked bar or funnel of
   by_status, and 3-4 large single-number stat cards up top
   (total_problems, universities_engaged, industries_engaged). Include a
   simple industry-interest form (problem detail view is fine) that POSTs
   to /industry/interest.

Start with mock/hardcoded JSON matching the exact shapes above so I'm not
blocked waiting on the backend, then show me how to wrap the real fetch
calls in a small api.js so switching from mock to live is a one-line
change. Give me the /admin dashboard first — I need it earliest.
```

---

## Jayanth — DevOps / notifications / docs

```
You're helping me with deployment, a lightweight notification flow, and
integration glue for an 18-hour hackathon project (React frontend, FastAPI
backend, a separate FastAPI classifier microservice, Postgres via
Supabase).

1. Give me a Vercel deployment config for the React app and the two-command
   deploy flow.
2. Give me a render.yaml (or Railway equivalent) deploying two separate
   FastAPI services — the main backend and the classifier microservice —
   from one monorepo, each with its own start command and
   requirements.txt, plus env var placeholders (DATABASE_URL,
   CLASSIFIER_URL).
3. Write a small keep-warm script (Python + `requests`, or a scheduled
   GitHub Actions workflow) that pings both services' /health endpoints
   every 15 minutes in the hours before a demo, so free-tier cold starts
   don't stall in front of judges.
4. Build a minimal EmailJS integration: a JS function
   sendStatusEmail(toEmail, problemTitle, newStatus) callable from the
   frontend with no backend mail server, using EmailJS's browser SDK,
   firing once when a problem's status changes to "Assigned to
   University." Include the exact EmailJS dashboard setup steps (template
   variables needed) since I'll configure that separately.
5. A one-page docker-compose.yml running the backend, classifier, and a
   local Postgres together, so the whole team can run the full stack on
   one laptop with no cloud dependencies during the bug-bash hour.

Keep everything simple enough to set up in under an hour by someone who
isn't a full-time DevOps person.
```

---

## Sumanth — Integration smoke test

```
You're helping me, the technical lead on a 6-person hackathon team, write
an end-to-end smoke test script for our 18-hour build. Stack: FastAPI
backend, a separate FastAPI classifier microservice, React frontend,
Postgres.

Write a single Python script (using `requests`, no test framework — this
needs to be simple enough to run at 9pm when I'm tired) that walks the
full user journey against the live or localhost services and prints a
clear PASS/FAIL line for each step:

1. POST a new problem to /problems with a realistic Jharkhand
   water-contamination report — verify the response includes a domain,
   priority_score, and status "Submitted".
2. POST the same problem again with slightly different wording and
   coordinates within 2km — verify it's treated as a duplicate of the
   first (duplicate_count increments) rather than creating a second
   visible entry in GET /problems.
3. GET /problems/{id}/suggested-universities — verify at least one
   university comes back.
4. POST /universities/{id}/assign — verify GET /problems/{id} now shows
   status "Assigned to University".
5. PATCH status to "In Progress" then "Resolved" — verify each transition
   sticks.
6. POST /industry/interest for that problem.
7. GET /dashboard/stats — verify total_problems, universities_engaged,
   and industries_engaged are all >= 1 and consistent with what was just
   created.

Make base URLs configurable via environment variables so I can point it at
localhost during the bug-bash hour and the deployed URLs right before the
demo. Exit non-zero if any step fails, and print a short summary table at
the end.
```
