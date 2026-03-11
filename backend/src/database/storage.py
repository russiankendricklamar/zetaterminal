"""
Local file storage utilities.
"""
import os
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
        description: str | None = None,
    ) -> dict:
        full_path = os.path.join(self.base_dir, file_path)
        # Path traversal protection: ensure resolved path is within base_dir
        real_base = os.path.realpath(self.base_dir)
        real_full = os.path.realpath(full_path)
        if not real_full.startswith(real_base + os.sep) and real_full != real_base:
            raise ValueError("Path traversal detected")
        os.makedirs(os.path.dirname(real_full), exist_ok=True)
        data = file_data.read() if hasattr(file_data, "read") else file_data
        with open(real_full, "wb") as f:
            f.write(data)
        return {"path": file_path, "size": len(data), "type": file_type}

    @staticmethod
    def generate_file_path(file_type: str, file_name: str, subfolder: str | None = None) -> str:
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        if subfolder:
            return f"{file_type}/{subfolder}/{year}/{month}/{file_name}"
        return f"{file_type}/{year}/{month}/{file_name}"
