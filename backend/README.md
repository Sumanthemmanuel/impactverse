# Impactverse Backend

Impactverse is a civic innovation operating system built with FastAPI.

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL with PostGIS and pgvector
- **ORM**: SQLAlchemy 2.0 (async)
- **Task Queue**: Celery & Redis
- **Auth**: JWT via PyJWT, passlib
- **Testing**: pytest, httpx

## Setup Instructions

### Environment Variables
Create a `.env` file based on `.env.example`. Make sure to set `DATABASE_URL` and `CELERY_BROKER_URL`.

### Docker (Recommended)
```bash
docker-compose up -d
```

### Local Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `alembic upgrade head`
5. Start server: `uvicorn app.main:app --reload`
6. Start Celery worker: `celery -A app.tasks.celery_app worker --loglevel=info`
7. Start Celery beat: `celery -A app.tasks.celery_app beat --loglevel=info`

## API Documentation
Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure
- `app/api/`: API routes (controllers)
- `app/core/`: Security, config, constants
- `app/models/`: SQLAlchemy ORM models
- `app/schemas/`: Pydantic models (DTOs)
- `app/services/`: Business logic
- `app/ai/`: AI/ML services and integrations
- `app/tasks/`: Celery background tasks
- `app/utils/`: Helper functions
- `alembic/`: Database migrations
- `tests/`: Pytest test suite

## Running Tests
```bash
pytest
```
