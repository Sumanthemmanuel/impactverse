from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Any = None

class SuccessResponse(BaseModel):
    message: str
    data: Any = None

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime

class GeoPoint(BaseModel):
    latitude: float
    longitude: float

    @field_validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @field_validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v
