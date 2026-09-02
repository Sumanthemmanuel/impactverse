from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from app.config import settings
from app.database import check_db_connection
from app.core.middleware import setup_middleware
from app.core.error_handlers import register_exception_handlers
from app.api.v1.router import v1_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("Starting Impactverse API...")
    db_connected = await check_db_connection()
    if db_connected:
        logger.info("Database connection established successfully.")
    else:
        logger.error("Failed to connect to the database. Application may not function correctly.")
        
    yield
    # Shutdown event
    logger.info("Shutting down Impactverse API...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

setup_middleware(app)
register_exception_handlers(app)

app.include_router(v1_router, prefix=settings.API_PREFIX)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/health/db", tags=["Health"])
async def db_health_check():
    is_connected = await check_db_connection()
    if is_connected:
        return {"status": "healthy", "message": "Database connection is active"}
    return {"status": "unhealthy", "message": "Database connection failed"}

@app.get("/health/redis", tags=["Health"])
async def redis_health_check():
    import redis.asyncio as redis
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        await client.close()
        return {"status": "healthy", "message": "Redis connection is active"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Redis connection failed: {str(e)}"}
