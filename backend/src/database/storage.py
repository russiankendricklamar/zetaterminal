"""
Supabase Storage utilities for file management.
"""
import os
from typing import Optional, BinaryIO
from datetime import datetime
from .client import get_supabase_client


class StorageService:
    """Service for managing files in Supabase Storage."""
    
    def __init__(self, bucket_name: str = "files"):
        self.client = get_supabase_client()
        self.bucket_name = bucket_name
    
    def upload_file(
        self,
        file_path: str,
        file_data: BinaryIO,
        file_type: str = "general",
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Upload file to Supabase Storage.
        
        Args:
            file_path: Path in storage (e.g., 'reports/2026/01/report.pdf')
            file_data: File-like object with binary data
            file_type: Type of file ('register', 'report', 'export', etc.)
            description: Optional description
            metadata: Optional metadata dictionary
            
        Returns:
            Dictionary with file info
        """
        # Ensure bucket exists (run once manually or in migration)
        # self.client.storage.create_bucket(self.bucket_name, public=False)
        
        # Read file data
        file_bytes = file_data.read() if hasattr(file_data, 'read') else file_data
        
        # Upload to storage
        response = self.client.storage.from_(self.bucket_name).upload(
            file_path,
            file_bytes,
            file_options={"content-type": self._get_mime_type(file_path)}
        )
        
        # Get file info
        file_info = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
        
        return {
            "path": file_path,
            "url": file_info,
            "size": len(file_bytes),
            "type": file_type
        }
    
    def download_file(self, file_path: str) -> bytes:
        """Download file from Supabase Storage."""
        response = self.client.storage.from_(self.bucket_name).download(file_path)
        return response
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from Supabase Storage."""
        try:
            self.client.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception:
            return False
    
    def list_files(self, folder: Optional[str] = None, limit: int = 100) -> list:
        """List files in storage."""
        path = folder or ""
        response = self.client.storage.from_(self.bucket_name).list(path)
        return response[:limit] if response else []
    
    def get_public_url(self, file_path: str) -> str:
        """Get public URL for file."""
        response = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
        return response
    
    def get_signed_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for private file."""
        response = self.client.storage.from_(self.bucket_name).create_signed_url(
            file_path,
            expires_in
        )
        return response.get("signedURL", "")
    
    @staticmethod
    def _get_mime_type(file_path: str) -> str:
        """Guess MIME type from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    @staticmethod
    def generate_file_path(file_type: str, file_name: str, subfolder: Optional[str] = None) -> str:
        """
        Generate structured file path.
        
        Example: reports/2026/01/report_2026-01-13.pdf
        """
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        
        if subfolder:
            return f"{file_type}/{subfolder}/{year}/{month}/{file_name}"
        return f"{file_type}/{year}/{month}/{file_name}"
