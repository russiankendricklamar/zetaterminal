"""
Local file storage utilities (replaces Supabase Storage).
"""
import os
from typing import Optional
from datetime import datetime


class StorageService:
    """Service for managing files on local filesystem."""

    def __init__(self, base_dir: str = "exports"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def upload_file(
        self,
        file_path: str,
        file_data: bytes,
        file_type: str = "general",
        description: Optional[str] = None,
    ) -> dict:
        full_path = os.path.join(self.base_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        data = file_data.read() if hasattr(file_data, "read") else file_data
        with open(full_path, "wb") as f:
            f.write(data)
        return {"path": full_path, "size": len(data), "type": file_type}

    @staticmethod
    def generate_file_path(file_type: str, file_name: str, subfolder: Optional[str] = None) -> str:
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        if subfolder:
            return f"{file_type}/{subfolder}/{year}/{month}/{file_name}"
        return f"{file_type}/{year}/{month}/{file_name}"
