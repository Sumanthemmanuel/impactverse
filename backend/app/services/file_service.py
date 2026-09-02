import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile

from app.config import settings
from app.core.constants import MediaType
from app.core.exceptions import ValidationError

class FileService:
    """Handles file uploads. Supports local storage and S3."""

    def __init__(self):
        self.storage_backend = settings.STORAGE_BACKEND
        self.local_path = Path(settings.LOCAL_STORAGE_PATH)
        self.local_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(self, file: UploadFile, folder: str = 'challenges') -> dict:
        self._validate_file(file)
        
        file_ext = file.filename.split('.')[-1] if file.filename else 'bin'
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        
        folder_path = self.local_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / unique_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_size = file_path.stat().st_size
        
        return {
            "file_url": f"/media/{folder}/{unique_filename}",
            "file_name": unique_filename,
            "file_type": self._get_media_type(file.content_type).value,
            "file_size": file_size
        }

    async def delete_file(self, file_url: str):
        pass

    def _get_media_type(self, content_type: str) -> MediaType:
        if content_type.startswith("image/"):
            return MediaType.IMAGE
        elif content_type.startswith("video/"):
            return MediaType.VIDEO
        elif content_type == "application/pdf":
            return MediaType.DOCUMENT
        return MediaType.OTHER

    def _validate_file(self, file: UploadFile):
        allowed_types = ["image/jpeg", "image/png", "image/webp", "video/mp4", "application/pdf"]
        if file.content_type not in allowed_types:
            raise ValidationError("File type not allowed")
