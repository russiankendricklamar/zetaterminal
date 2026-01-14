"""
Repository pattern for database operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from .client import get_supabase_client
from .models import BondValuationRecord, PortfolioRecord, CalculationHistory, MarketDataDaily, FileRecord


class BondValuationRepository:
    """Repository for bond valuation records."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "bond_valuations"
    
    def create(self, record: BondValuationRecord) -> Dict[str, Any]:
        """Create a new bond valuation record."""
        data = record.model_dump(exclude={"id", "created_at", "updated_at"})
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        response = self.client.table(self.table).insert(data).execute()
        return response.data[0] if response.data else {}
    
    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Get bond valuation by ID."""
        response = self.client.table(self.table).select("*").eq("id", record_id).execute()
        return response.data[0] if response.data else None
    
    def get_by_secid(self, secid: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get bond valuations by ISIN."""
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("secid", secid)
            .order("valuation_date", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    
    def get_by_date_range(
        self, 
        start_date: str, 
        end_date: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get bond valuations by date range."""
        response = (
            self.client.table(self.table)
            .select("*")
            .gte("valuation_date", start_date)
            .lte("valuation_date", end_date)
            .order("valuation_date", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    
    def update(self, record_id: int, record: BondValuationRecord) -> Optional[Dict[str, Any]]:
        """Update bond valuation record."""
        data = record.model_dump(exclude={"id", "created_at"}, exclude_none=True)
        data["updated_at"] = datetime.utcnow().isoformat()
        
        response = (
            self.client.table(self.table)
            .update(data)
            .eq("id", record_id)
            .execute()
        )
        return response.data[0] if response.data else None
    
    def delete(self, record_id: int) -> bool:
        """Delete bond valuation record."""
        response = (
            self.client.table(self.table)
            .delete()
            .eq("id", record_id)
            .execute()
        )
        return len(response.data) > 0


class PortfolioRepository:
    """Repository for portfolio records."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "portfolios"
    
    def create(self, record: PortfolioRecord) -> Dict[str, Any]:
        """Create a new portfolio record."""
        data = record.model_dump(exclude={"id", "created_at", "updated_at"})
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        response = self.client.table(self.table).insert(data).execute()
        return response.data[0] if response.data else {}
    
    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all portfolios."""
        response = (
            self.client.table(self.table)
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    
    def get_by_id(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
        """Get portfolio by ID."""
        response = self.client.table(self.table).select("*").eq("id", portfolio_id).execute()
        return response.data[0] if response.data else None


class CalculationHistoryRepository:
    """Repository for calculation history."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "calculation_history"
    
    def create(self, record: CalculationHistory) -> Dict[str, Any]:
        """Create a new calculation history record."""
        data = record.model_dump(exclude={"id", "created_at"})
        data["created_at"] = datetime.utcnow().isoformat()
        
        response = self.client.table(self.table).insert(data).execute()
        return response.data[0] if response.data else {}
    
    def get_recent(self, calculation_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent calculation history."""
        query = self.client.table(self.table).select("*")
        
        if calculation_type:
            query = query.eq("calculation_type", calculation_type)
        
        response = (
            query
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data


class MarketDataRepository:
    """Repository for market data."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "market_data_daily"
    
    def create_or_update(self, record: "MarketDataDaily") -> Dict[str, Any]:
        """Create or update market data record (upsert)."""
        data = record.model_dump(exclude={"id", "created_at"}, exclude_none=True)
        
        # Use upsert to handle duplicates
        response = (
            self.client.table(self.table)
            .upsert(
                data,
                on_conflict="ticker,data_type,date"
            )
            .execute()
        )
        return response.data[0] if response.data else {}
    
    def get_by_ticker(
        self,
        ticker: str,
        data_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get market data by ticker."""
        query = self.client.table(self.table).select("*").eq("ticker", ticker)
        
        if data_type:
            query = query.eq("data_type", data_type)
        if start_date:
            query = query.gte("date", start_date)
        if end_date:
            query = query.lte("date", end_date)
        
        response = (
            query
            .order("date", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    
    def get_latest(self, ticker: str, data_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get latest market data for ticker."""
        query = self.client.table(self.table).select("*").eq("ticker", ticker)
        if data_type:
            query = query.eq("data_type", data_type)
        
        response = (
            query
            .order("date", desc=True)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None


class FileRepository:
    """Repository for file metadata."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "files"
    
    def create(self, record: FileRecord) -> Dict[str, Any]:
        """Create file metadata record."""
        data = record.model_dump(exclude={"id", "created_at", "updated_at"})
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        response = self.client.table(self.table).insert(data).execute()
        return response.data[0] if response.data else {}
    
    def get_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Get file metadata by ID."""
        response = self.client.table(self.table).select("*").eq("id", file_id).execute()
        return response.data[0] if response.data else None
    
    def get_by_type(self, file_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get files by type."""
        response = (
            self.client.table(self.table)
            .select("*")
            .eq("file_type", file_type)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    
    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all files."""
        response = (
            self.client.table(self.table)
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    
    def delete(self, file_id: int) -> bool:
        """Delete file metadata record."""
        response = (
            self.client.table(self.table)
            .delete()
            .eq("id", file_id)
            .execute()
        )
        return len(response.data) > 0
