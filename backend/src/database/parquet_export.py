"""
Utility functions for exporting data to Parquet format.
"""
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Any, List
from .repositories import MarketDataRepository, FileRepository
from .storage import StorageService
from .models import FileRecord


class ParquetExporter:
    """Export data to Parquet format and store in Supabase Storage."""
    
    def __init__(self, storage_bucket: str = "files"):
        self.storage = StorageService(bucket_name=storage_bucket)
        self.file_repo = FileRepository()
        self.market_repo = MarketDataRepository()
    
    def export_market_data_to_parquet(
        self,
        ticker: Optional[str] = None,
        data_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export market data to Parquet format.
        
        Args:
            ticker: Filter by ticker (optional)
            data_type: Filter by data type (optional)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            file_name: Custom file name (optional)
            
        Returns:
            Dictionary with file info and path
        """
        # Get data from repository
        data = self.market_repo.get_by_ticker(
            ticker or "",
            data_type,
            start_date,
            end_date,
            limit=10000
        )
        
        if not data:
            raise ValueError("No data found for export")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Convert date strings to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Generate file name
        if not file_name:
            date_str = datetime.now().strftime("%Y%m%d")
            ticker_str = f"_{ticker}" if ticker else ""
            type_str = f"_{data_type}" if data_type else ""
            file_name = f"market_data{ticker_str}{type_str}_{date_str}.parquet"
        
        # Generate file path
        file_path = self.storage.generate_file_path("exports", file_name, "parquet")
        
        # Convert DataFrame to Parquet bytes
        buffer = BytesIO()
        df.to_parquet(
            buffer,
            engine='pyarrow',
            compression='snappy',  # Good balance between size and speed
            index=False
        )
        buffer.seek(0)
        
        # Upload to Storage
        file_info = self.storage.upload_file(
            file_path=file_path,
            file_data=buffer,
            file_type="export",
            description=f"Market data export: {ticker or 'all'}"
        )
        
        # Save metadata to database
        file_record = FileRecord(
            file_name=file_name,
            file_path=file_path,
            file_type="export",
            file_size=file_info["size"],
            mime_type="application/octet-stream",
            description=f"Market data export: {len(data)} records",
            metadata={
                "ticker": ticker,
                "data_type": data_type,
                "start_date": start_date,
                "end_date": end_date,
                "records_count": len(data),
                "format": "parquet",
                "compression": "snappy"
            }
        )
        self.file_repo.create(file_record)
        
        return {
            "file_path": file_path,
            "file_name": file_name,
            "file_size": file_info["size"],
            "records_count": len(data),
            "url": file_info.get("url", "")
        }
    
    def export_table_to_parquet(
        self,
        table_name: str,
        filters: Optional[Dict[str, Any]] = None,
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export any table to Parquet format.
        
        Args:
            table_name: Name of the table to export
            filters: Optional filters (dict of column: value)
            file_name: Custom file name
            
        Returns:
            Dictionary with file info
        """
        from .client import get_supabase_client
        
        client = get_supabase_client()
        
        # Build query
        query = client.table(table_name).select("*")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        # Execute query
        response = query.execute()
        data = response.data
        
        if not data:
            raise ValueError(f"No data found in table {table_name}")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Generate file name
        if not file_name:
            date_str = datetime.now().strftime("%Y%m%d")
            file_name = f"{table_name}_{date_str}.parquet"
        
        # Generate file path
        file_path = self.storage.generate_file_path("exports", file_name, "parquet")
        
        # Convert to Parquet
        buffer = BytesIO()
        df.to_parquet(
            buffer,
            engine='pyarrow',
            compression='snappy',
            index=False
        )
        buffer.seek(0)
        
        # Upload to Storage
        file_info = self.storage.upload_file(
            file_path=file_path,
            file_data=buffer,
            file_type="export",
            description=f"Table export: {table_name}"
        )
        
        # Save metadata
        file_record = FileRecord(
            file_name=file_name,
            file_path=file_path,
            file_type="export",
            file_size=file_info["size"],
            mime_type="application/octet-stream",
            description=f"Table export: {table_name} ({len(data)} records)",
            metadata={
                "table_name": table_name,
                "records_count": len(data),
                "format": "parquet"
            }
        )
        self.file_repo.create(file_record)
        
        return {
            "file_path": file_path,
            "file_name": file_name,
            "file_size": file_info["size"],
            "records_count": len(data),
            "url": file_info.get("url", "")
        }
    
    def read_parquet_from_storage(self, file_path: str) -> pd.DataFrame:
        """
        Read Parquet file from Storage and return as DataFrame.
        
        Args:
            file_path: Path to file in Storage
            
        Returns:
            pandas DataFrame
        """
        file_data = self.storage.download_file(file_path)
        buffer = BytesIO(file_data)
        df = pd.read_parquet(buffer, engine='pyarrow')
        return df
