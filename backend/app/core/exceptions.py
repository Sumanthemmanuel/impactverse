from typing import Any, Dict, Optional

class ImpactverseException(Exception):
    """Base exception for Impactverse API"""
    def __init__(
        self,
        message: str,
        code: str = "internal_error",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

class NotFoundError(ImpactverseException):
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' not found.",
            code="not_found",
            status_code=404,
            details={"entity": entity_name, "identifier": str(identifier)}
        )

class UnauthorizedError(ImpactverseException):
    def __init__(self, message: str = "Authentication credentials were not provided or are invalid."):
        super().__init__(
            message=message,
            code="unauthorized",
            status_code=401
        )

class ForbiddenError(ImpactverseException):
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(
            message=message,
            code="forbidden",
            status_code=403
        )

class ValidationError(ImpactverseException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="validation_error",
            status_code=422,
            details=details
        )

class ConflictError(ImpactverseException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="conflict",
            status_code=409,
            details=details
        )

class RateLimitError(ImpactverseException):
    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(
            message=message,
            code="rate_limit_exceeded",
            status_code=429
        )

class ExternalServiceError(ImpactverseException):
    def __init__(self, service_name: str, message: str):
        super().__init__(
            message=f"External service '{service_name}' error: {message}",
            code="external_service_error",
            status_code=502,
            details={"service": service_name}
        )
