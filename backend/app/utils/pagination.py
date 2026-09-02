import math
from app.schemas.common import PaginatedResponse

def create_paginated_response(items: list, total: int, page: int, page_size: int) -> dict:
    """Create a standardized paginated response dict."""
    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
    }
