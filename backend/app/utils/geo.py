import math
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from shapely.geometry import Point

def create_point(latitude: float, longitude: float) -> str:
    """Create a WKT point string from lat/lng."""
    return f'SRID=4326;POINT({longitude} {latitude})'

def create_wkt_element(latitude: float, longitude: float) -> WKTElement:
    """Create a GeoAlchemy2 WKTElement from lat/lng."""
    return WKTElement(f'POINT({longitude} {latitude})', srid=4326)

def extract_lat_lng(geometry) -> tuple[float, float] | None:
    """Extract (latitude, longitude) from a GeoAlchemy2 geometry."""
    if geometry is None:
        return None
    try:
        point = to_shape(geometry)
        return (point.y, point.x)  # lat, lng
    except Exception:
        return None

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate haversine distance in kilometers between two points."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
