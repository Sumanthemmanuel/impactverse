import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import ImpactverseException

logger = logging.getLogger(__name__)

async def impactverse_exception_handler(request: Request, exc: ImpactverseException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    formatted_errors = [
        {
            "loc": err.get("loc", []),
            "msg": err.get("msg", ""),
            "type": err.get("type", "")
        }
        for err in errors
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": {"errors": formatted_errors}
            }
        }
    )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred.",
                "details": {}
            }
        }
    )

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(ImpactverseException, impactverse_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
