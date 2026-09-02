import time
import uuid
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import settings

logger = structlog.get_logger()

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Ensure we have request_id from RequestIDMiddleware
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Using structlog to bind context
        log = logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        
        try:
            response = await call_next(request)
            process_time_ms = (time.time() - start_time) * 1000
            
            log.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(process_time_ms, 2)
            )
            return response
        except Exception as e:
            process_time_ms = (time.time() - start_time) * 1000
            log.error(
                "request_failed",
                error=str(e),
                duration_ms=round(process_time_ms, 2)
            )
            raise

def setup_middleware(app: FastAPI):
    # Standard middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Custom middlewares (order matters - RequestID should be outer)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
