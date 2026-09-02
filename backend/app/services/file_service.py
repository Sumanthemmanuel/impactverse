import io
import struct
import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from app.config import settings
from app.core.constants import MediaType
from app.core.exceptions import ValidationError


def _rational_to_float(rational) -> float:
    """Convert an EXIF IFDRational (or (num, denom) tuple) to a plain float."""
    if hasattr(rational, 'numerator'):
        # IFDRational from Pillow's _getexif
        return rational.numerator / rational.denominator
    num, denom = rational
    return num / denom if denom else 0.0


def _dms_to_decimal(dms, ref: str) -> float:
    """Convert degrees/minutes/seconds tuple to decimal degrees."""
    degrees = _rational_to_float(dms[0])
    minutes = _rational_to_float(dms[1])
    seconds = _rational_to_float(dms[2])
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref in ('S', 'W'):
        decimal = -decimal
    return round(decimal, 7)


def extract_exif_gps(file_bytes: bytes) -> Optional[dict]:
    """
    Extract GPS latitude/longitude from JPEG/PNG EXIF data.
    Returns {"latitude": float, "longitude": float} or None if not present.
    """
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS

        img = Image.open(io.BytesIO(file_bytes))
        exif_data = img._getexif()
        if not exif_data:
            return None

        # Build a tag-name -> value map
        named = {TAGS.get(k, k): v for k, v in exif_data.items()}
        gps_info_raw = named.get('GPSInfo')
        if not gps_info_raw:
            return None

        # Decode GPS sub-IFD tag numbers into names
        gps = {GPSTAGS.get(k, k): v for k, v in gps_info_raw.items()}

        lat_dms = gps.get('GPSLatitude')
        lat_ref = gps.get('GPSLatitudeRef')
        lon_dms = gps.get('GPSLongitude')
        lon_ref = gps.get('GPSLongitudeRef')

        if not (lat_dms and lat_ref and lon_dms and lon_ref):
            return None

        latitude = _dms_to_decimal(lat_dms, lat_ref)
        longitude = _dms_to_decimal(lon_dms, lon_ref)
        return {"latitude": latitude, "longitude": longitude}
    except Exception:
        return None


class FileService:
    """Handles file uploads. Supports local storage. Extracts EXIF GPS from images."""

    ALLOWED_TYPES = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "video/mp4",
        "application/pdf",
    ]

    def __init__(self):
        self.storage_backend = settings.STORAGE_BACKEND
        self.local_path = Path(settings.LOCAL_STORAGE_PATH)
        self.local_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(self, file: UploadFile, folder: str = 'challenges') -> dict:
        self._validate_file(file)

        # Read the whole file into memory once so we can both extract EXIF
        # metadata and persist the bytes to disk.
        file_bytes = await file.read()

        unique_filename = f"{uuid.uuid4()}_{file.filename or 'upload'}"
        folder_path = self.local_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / unique_filename

        with open(file_path, "wb") as buffer:
            buffer.write(file_bytes)

        file_size = file_path.stat().st_size
        media_type = self._get_media_type(file.content_type)

        # Extract GPS geotag for images
        gps_coords: Optional[dict] = None
        if media_type == MediaType.IMAGE:
            gps_coords = extract_exif_gps(file_bytes)

        result = {
            "file_url": f"/media/{folder}/{unique_filename}",
            "file_name": unique_filename,
            "file_type": media_type.value,
            "file_size": file_size,
        }
        if gps_coords:
            result["gps_latitude"] = gps_coords["latitude"]
            result["gps_longitude"] = gps_coords["longitude"]

        return result

    async def delete_file(self, file_url: str):
        pass

    def _get_media_type(self, content_type: str) -> MediaType:
        if content_type and content_type.startswith("image/"):
            return MediaType.IMAGE
        elif content_type and content_type.startswith("video/"):
            return MediaType.VIDEO
        elif content_type == "application/pdf":
            return MediaType.DOCUMENT
        return MediaType.OTHER

    def _validate_file(self, file: UploadFile):
        if file.content_type not in self.ALLOWED_TYPES:
            raise ValidationError(
                f"File type '{file.content_type}' not allowed. "
                f"Allowed: {', '.join(self.ALLOWED_TYPES)}"
            )
